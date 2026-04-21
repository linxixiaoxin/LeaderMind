<template>
  <div class="graph-layout">
    <div ref="graphEl" class="graph-wrap">
      <svg ref="svgEl" class="graph-svg"></svg>

      <div class="filter-bar">
        <button
          v-for="filter in FILTERS"
          :key="filter.type"
          class="filter-btn"
          :class="{ active: activeFilters.has(filter.type) }"
          :style="buttonStyle(filter)"
          @click="toggleFilter(filter.type)"
        >
          {{ filter.label }}
        </button>
      </div>

      <div class="legend">
        <div v-for="filter in FILTERS" :key="filter.type" class="legend-item">
          <span class="legend-dot" :style="{ background: filter.color }"></span>
          <span>{{ filter.label }}</span>
        </div>
        <div class="legend-hint">拖拽 · 缩放 · 点节点看详情</div>
      </div>

      <div
        v-if="tooltip.visible && !cardNode"
        class="tooltip"
        :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
      >
        {{ tooltip.text }}
      </div>
    </div>

    <Transition name="panel">
      <aside v-if="cardNode" class="detail-panel" @click.stop>
        <div class="panel-header">
          <span class="card-type-dot" :style="{ background: typeMeta(cardNode.type).color }"></span>
          <span class="card-title" @click="$emit('openReader', cardNode.id)">{{ cardNode.id }}</span>
          <button class="card-close" @click="closeCard">✕</button>
        </div>

        <p class="card-tagline" @click="$emit('openReader', cardNode.id)">{{ cardNode.tagline }}</p>

        <div class="card-meta">
          <span class="meta-chip">{{ typeMeta(cardNode.type).label }}</span>
        </div>

        <div class="card-relations">
          <div class="card-section-title">关联节点</div>
          <div class="card-relation-list">
            <button
              v-for="relation in cardRelations"
              :key="relation.id"
              class="relation-item"
              @click="$emit('openReader', relation.id)"
            >
              <span class="rel-dot" :style="{ background: typeMeta(relation.type).color }"></span>
              <span class="rel-main">
                <span class="rel-name">{{ relation.id }}</span>
                <span class="rel-desc">{{ relation.desc }}</span>
              </span>
            </button>
          </div>
        </div>
      </aside>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as d3 from 'd3'
import { FILTERS, LINKS, LINK_LABELS, NODES, NODE_TYPE_META } from '../data/graphData.js'

const props = defineProps({
  activeNode: String,
})

const emit = defineEmits(['selectNode', 'openReader'])

const graphEl = ref(null)
const svgEl = ref(null)
const tooltip = ref({ visible: false, x: 0, y: 0, text: '' })
const cardNode = ref(null)
const activeFilters = ref(new Set(FILTERS.map((item) => item.type)))

const degree = {}
LINKS.forEach((link) => {
  degree[link.source] = (degree[link.source] || 0) + 1
  degree[link.target] = (degree[link.target] || 0) + 1
})

const cardRelations = computed(() => {
  if (!cardNode.value) return []
  const seen = new Set()
  const relations = []
  LINKS.forEach((link) => {
    const source = typeof link.source === 'object' ? link.source.id : link.source
    const target = typeof link.target === 'object' ? link.target.id : link.target
    let other = null
    let labelKey = null
    if (source === cardNode.value.id) {
      other = target
      labelKey = `${source}→${target}`
    } else if (target === cardNode.value.id) {
      other = source
      labelKey = `${source}→${target}`
    }
    if (!other || seen.has(other)) return
    seen.add(other)
    const node = NODES.find((item) => item.id === other)
    relations.push({
      id: other,
      type: node?.type || 'topic',
      desc: LINK_LABELS[labelKey] || '相关节点',
    })
  })
  return relations
})

function typeMeta(type) {
  return NODE_TYPE_META[type] || { label: type, color: '#7f8790', size: 9 }
}

function buttonStyle(filter) {
  if (!activeFilters.value.has(filter.type)) {
    return {}
  }
  return {
    borderColor: filter.color,
    color: filter.color,
    background: `${filter.color}1A`,
  }
}

function nodeRadius(node) {
  return (typeMeta(node.type).size || 9) + Math.min((degree[node.id] || 0) * 0.45, 6)
}

let svg
let group
let zoom
let simulation
let linkSelection
let nodeSelection

function initGraph() {
  const width = graphEl.value.offsetWidth
  const height = graphEl.value.offsetHeight

  svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()

  zoom = d3.zoom().scaleExtent([0.18, 5]).on('zoom', (event) => {
    group.attr('transform', event.transform)
  })
  svg.call(zoom)

  group = svg.append('g')

  const nodes = NODES.map((item) => ({ ...item }))
  const links = LINKS.map((item) => ({ ...item }))

  simulation = d3
    .forceSimulation(nodes)
    .force(
      'link',
      d3
        .forceLink(links)
        .id((d) => d.id)
        .distance((d) => {
          const sourceType = typeof d.source === 'object' ? d.source.type : NODES.find((item) => item.id === d.source)?.type
          const targetType = typeof d.target === 'object' ? d.target.type : NODES.find((item) => item.id === d.target)?.type
          if (sourceType === 'chapter' || targetType === 'chapter') return 110
          if (sourceType === 'topic' || targetType === 'topic') return 96
          return 82
        })
        .strength(0.45),
    )
    .force('charge', d3.forceManyBody().strength(-230))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius((d) => nodeRadius(d) + 14))

  linkSelection = group
    .append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#cbbfb0')
    .attr('stroke-opacity', 0.48)
    .attr('stroke-width', 1.2)

  nodeSelection = group
    .append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .attr('class', 'node')
    .style('cursor', 'pointer')
    .call(
      d3
        .drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on('drag', (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        }),
    )

  nodeSelection
    .append('circle')
    .attr('r', (d) => nodeRadius(d))
    .attr('fill', (d) => typeMeta(d.type).color)
    .attr('fill-opacity', 0.86)
    .attr('stroke', '#ffffff')
    .attr('stroke-width', 1.6)

  nodeSelection
    .append('text')
    .text((d) => (d.id.length > 10 ? `${d.id.slice(0, 9)}…` : d.id))
    .attr('dy', (d) => nodeRadius(d) + 14)
    .attr('text-anchor', 'middle')
    .style('font-size', '10.5px')
    .style('fill', '#6e7a83')
    .style('pointer-events', 'none')

  simulation.on('tick', () => {
    linkSelection
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y)

    nodeSelection.attr('transform', (d) => `translate(${d.x},${d.y})`)
  })

  nodeSelection
    .on('click', (event, d) => {
      event.stopPropagation()
      switchCard(d.id)
    })
    .on('mouseover', (event, d) => {
      if (!cardNode.value) {
        tooltip.value = {
          visible: true,
          x: event.clientX + 12,
          y: event.clientY - 8,
          text: d.id,
        }
      }
    })
    .on('mousemove', (event) => {
      tooltip.value.x = event.clientX + 12
      tooltip.value.y = event.clientY - 8
    })
    .on('mouseout', () => {
      tooltip.value.visible = false
    })

  svg.on('click', () => {
    cardNode.value = null
    emit('selectNode', null)
    highlight(null)
  })
}

function switchCard(id) {
  const node = NODES.find((item) => item.id === id)
  if (!node) return
  cardNode.value = node
  emit('selectNode', id)
  highlight(id)
  focusNode(id)
}

function closeCard() {
  cardNode.value = null
  emit('selectNode', null)
  highlight(null)
}

function highlight(id) {
  if (!nodeSelection) return
  if (!id) {
    nodeSelection.style('opacity', 1)
    linkSelection.attr('stroke', '#cbbfb0').attr('stroke-opacity', 0.48).attr('stroke-width', 1.2)
    return
  }

  const connected = new Set([id])
  LINKS.forEach((link) => {
    const source = typeof link.source === 'object' ? link.source.id : link.source
    const target = typeof link.target === 'object' ? link.target.id : link.target
    if (source === id) connected.add(target)
    if (target === id) connected.add(source)
  })

  nodeSelection.style('opacity', (d) => (connected.has(d.id) ? 1 : 0.1))
  linkSelection
    .attr('stroke', (d) => {
      const source = typeof d.source === 'object' ? d.source.id : d.source
      const target = typeof d.target === 'object' ? d.target.id : d.target
      return source === id || target === id ? '#bf6f3f' : '#cbbfb0'
    })
    .attr('stroke-opacity', (d) => {
      const source = typeof d.source === 'object' ? d.source.id : d.source
      const target = typeof d.target === 'object' ? d.target.id : d.target
      return source === id || target === id ? 0.92 : 0.08
    })
    .attr('stroke-width', (d) => {
      const source = typeof d.source === 'object' ? d.source.id : d.source
      const target = typeof d.target === 'object' ? d.target.id : d.target
      return source === id || target === id ? 2.2 : 1.1
    })
}

function focusNode(id) {
  if (!nodeSelection || !svg || !zoom) return
  const node = nodeSelection.data().find((item) => item.id === id)
  if (!node || node.x === undefined) return
  const width = graphEl.value.offsetWidth
  const height = graphEl.value.offsetHeight
  const scale = 1.45
  const translateX = width / 2 - node.x * scale
  const translateY = height / 2 - node.y * scale
  svg.transition().duration(560).call(zoom.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale))
}

function toggleFilter(type) {
  if (activeFilters.value.has(type)) {
    activeFilters.value.delete(type)
  } else {
    activeFilters.value.add(type)
  }

  nodeSelection.style('display', (d) => (activeFilters.value.has(d.type) ? null : 'none'))
  linkSelection.style('display', (d) => {
    const source = typeof d.source === 'object' ? d.source.id : d.source
    const target = typeof d.target === 'object' ? d.target.id : d.target
    const sourceNode = NODES.find((item) => item.id === source)
    const targetNode = NODES.find((item) => item.id === target)
    return sourceNode && targetNode && activeFilters.value.has(sourceNode.type) && activeFilters.value.has(targetNode.type)
      ? null
      : 'none'
  })
}

watch(
  () => props.activeNode,
  (id) => {
    highlight(id)
    if (id) focusNode(id)
    if (!id) cardNode.value = null
  },
)

const resizeObserver = new ResizeObserver(() => {
  if (!graphEl.value || !simulation) return
  const width = graphEl.value.offsetWidth
  const height = graphEl.value.offsetHeight
  simulation.force('center', d3.forceCenter(width / 2, height / 2)).alpha(0.06).restart()
})

onMounted(() => {
  initGraph()
  resizeObserver.observe(graphEl.value)
})

onUnmounted(() => {
  resizeObserver.disconnect()
  simulation?.stop()
})
</script>

<style scoped>
.graph-layout {
  width: 100%;
  height: 100%;
  display: flex;
  overflow: hidden;
}

.graph-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
  height: 100%;
}

.graph-svg {
  width: 100%;
  height: 100%;
}

.filter-bar {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  max-width: min(720px, calc(100% - 40px));
  padding: 8px 12px;
  border: 1px solid var(--border-default);
  border-radius: 999px;
  background: rgba(247, 245, 240, 0.9);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(10px);
}

.filter-btn {
  border: 1px solid var(--border-default);
  background: transparent;
  color: var(--text-tertiary);
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  cursor: pointer;
}

.legend {
  position: absolute;
  left: 20px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border: 1px solid var(--border-default);
  border-radius: 16px;
  background: rgba(247, 245, 240, 0.92);
  box-shadow: var(--shadow-sm);
  font-size: 11px;
  color: var(--text-secondary);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 7px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-hint {
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 10px;
}

.detail-panel {
  width: 300px;
  flex-shrink: 0;
  padding: 18px;
  border-left: 1px solid var(--border-default);
  background: rgba(247, 245, 240, 0.94);
  backdrop-filter: blur(14px);
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: -12px 0 30px rgba(18, 28, 36, 0.08);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-type-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.card-title {
  flex: 1;
  font-family: var(--font-serif);
  font-size: 17px;
  color: var(--text-primary);
  cursor: pointer;
}

.card-title:hover,
.card-tagline:hover {
  color: var(--brand);
}

.card-close {
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.card-tagline {
  color: var(--text-secondary);
  line-height: 1.65;
  font-size: 13px;
  cursor: pointer;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-chip {
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--border-default);
  background: rgba(255, 255, 255, 0.74);
  color: var(--text-tertiary);
  font-size: 11px;
}

.card-relations {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
}

.card-relations::-webkit-scrollbar {
  width: 4px;
}

.card-relations::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 999px;
}

.card-section-title {
  margin-bottom: 10px;
  color: var(--text-muted);
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.card-relation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.relation-item {
  width: 100%;
  border: 1px solid transparent;
  background: transparent;
  border-radius: 12px;
  padding: 9px 10px;
  display: flex;
  gap: 9px;
  align-items: flex-start;
  text-align: left;
  cursor: pointer;
  transition: background 0.16s ease, border-color 0.16s ease;
}

.relation-item:hover {
  background: rgba(32, 79, 103, 0.06);
  border-color: rgba(32, 79, 103, 0.16);
}

.rel-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.rel-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rel-name {
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
}

.rel-desc {
  color: var(--text-tertiary);
  font-size: 11px;
  line-height: 1.45;
}

.tooltip {
  position: fixed;
  z-index: 40;
  pointer-events: none;
  padding: 6px 10px;
  border-radius: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  box-shadow: var(--shadow-sm);
  font-size: 12px;
  color: var(--text-primary);
}

.panel-enter-active, .panel-leave-active {
  transition: width 0.24s ease, opacity 0.2s ease, padding 0.24s ease;
}

.panel-enter-from, .panel-leave-to {
  width: 0;
  opacity: 0;
  padding: 0;
}

@media (max-width: 960px) {
  .detail-panel {
    width: 270px;
  }
}

@media (max-width: 720px) {
  .legend {
    left: 12px;
    bottom: 12px;
    max-width: calc(100% - 24px);
  }

  .filter-bar {
    top: 12px;
    max-width: calc(100% - 24px);
  }
}
</style>
