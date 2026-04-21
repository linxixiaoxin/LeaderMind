<template>
  <aside class="sidebar" :class="{ collapsed: !open }">
    <div class="sidebar-inner">
      <div class="sidebar-head">
        <span class="sidebar-title">目录</span>
        <button class="collapse-btn" @click="$emit('toggle')" :title="open ? '收起' : '展开'">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
      </div>

      <div class="graph-entry" :class="{ active: isGraphActive }" @click="onShowGraph">
        <div class="graph-entry-icon">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="3" r="1.8" fill="currentColor" opacity="0.7" />
            <circle cx="3" cy="11" r="1.8" fill="currentColor" opacity="0.7" />
            <circle cx="13" cy="11" r="1.8" fill="currentColor" opacity="0.7" />
            <line x1="8" y1="4.8" x2="3.8" y2="9.5" stroke="currentColor" stroke-width="1.2" opacity="0.5" />
            <line x1="8" y1="4.8" x2="12.2" y2="9.5" stroke="currentColor" stroke-width="1.2" opacity="0.5" />
            <line x1="4.8" y1="11" x2="11.2" y2="11" stroke="currentColor" stroke-width="1.2" opacity="0.5" />
          </svg>
        </div>
        <span class="graph-entry-label">知识图谱</span>
        <span class="graph-entry-count">{{ LINKS.length }} 条链接</span>
      </div>

      <div class="toc-scroll">
        <section v-for="group in TOC" :key="group.id" class="toc-group">
          <button
            class="group-header"
            :class="{ open: !collapsed[group.id] }"
            @click="toggleGroup(group.id)"
          >
            <span class="group-dot" :style="{ background: group.color }"></span>
            <span class="group-label">{{ group.label }}</span>
            <span class="group-count">{{ groupCount(group) }}</span>
            <svg class="group-chevron" :class="{ rotated: !collapsed[group.id] }" width="12" height="12" viewBox="0 0 16 16" fill="none">
              <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>

          <div v-show="!collapsed[group.id]" class="group-body">
            <div v-for="section in group.sections" :key="section.label" class="toc-section">
              <div class="section-label">{{ section.label }}</div>
              <button
                v-for="item in section.items"
                :key="item"
                class="toc-item"
                :class="{ active: activeNode === item, 'no-content': !FILE_MAP[item] }"
                @click="onSelectNode(item)"
              >
                <span class="item-indicator" :style="indicatorStyle(group.color, item)"></span>
                <span class="item-name">{{ item }}</span>
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { FILE_MAP, LINKS, TOC } from '../data/graphData.js'

defineProps({
  open: Boolean,
  activeNode: String,
  isGraphActive: Boolean,
})

const emit = defineEmits(['toggle', 'selectNode', 'showGraph'])
const collapsed = ref(Object.fromEntries(TOC.map((group) => [group.id, false])))

function toggleGroup(id) {
  collapsed.value[id] = !collapsed.value[id]
}

function groupCount(group) {
  return group.sections.reduce((sum, section) => sum + section.items.length, 0)
}

function indicatorStyle(color, item) {
  return {
    background: FILE_MAP[item] ? color : 'var(--border-default)',
  }
}

function isMobile() {
  return window.innerWidth <= 720
}

function onSelectNode(item) {
  emit('selectNode', item)
  if (isMobile()) emit('toggle')
}

function onShowGraph() {
  emit('showGraph')
  if (isMobile()) emit('toggle')
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid var(--border-default);
  background: linear-gradient(180deg, rgba(240, 237, 230, 0.95) 0%, rgba(246, 243, 237, 0.98) 100%);
  overflow: hidden;
  transition: width 0.24s ease, opacity 0.24s ease;
}

.sidebar.collapsed {
  width: 0;
  opacity: 0;
  pointer-events: none;
}

.sidebar-inner {
  width: 280px;
  min-width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-head {
  display: flex;
  align-items: center;
  padding: 16px 18px 12px;
  border-bottom: 1px solid var(--border-default);
}

.sidebar-title {
  flex: 1;
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.collapse-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
}

.collapse-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-primary);
}

.graph-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-bottom: 1px solid var(--border-default);
  cursor: pointer;
  transition: background 0.16s ease;
}

.graph-entry:hover {
  background: rgba(32, 79, 103, 0.06);
}

.graph-entry.active {
  background: rgba(32, 79, 103, 0.1);
}

.graph-entry-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(32, 79, 103, 0.08);
  color: var(--brand);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.graph-entry-label {
  flex: 1;
  font-size: 13px;
  color: var(--text-secondary);
}

.graph-entry-count {
  font-size: 10px;
  color: var(--text-muted);
}

.toc-scroll {
  flex: 1;
  overflow-y: auto;
}

.toc-scroll::-webkit-scrollbar {
  width: 4px;
}

.toc-scroll::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 999px;
}

.toc-group {
  border-bottom: 1px solid rgba(221, 214, 202, 0.7);
}

.group-header {
  width: 100%;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  cursor: pointer;
  text-align: left;
}

.group-header:hover {
  background: rgba(0, 0, 0, 0.025);
}

.group-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.group-label {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.group-count {
  font-size: 10px;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--border-default);
  padding: 1px 6px;
  border-radius: 999px;
}

.group-chevron {
  color: var(--text-muted);
  transition: transform 0.2s ease;
}

.group-chevron.rotated {
  transform: rotate(180deg);
}

.group-body {
  padding-bottom: 8px;
}

.toc-section {
  padding-bottom: 4px;
}

.section-label {
  font-size: 11px;
  color: var(--text-muted);
  padding: 6px 18px 4px 34px;
}

.toc-item {
  width: 100%;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 6px 18px 6px 34px;
  cursor: pointer;
  text-align: left;
  transition: background 0.14s ease;
}

.toc-item:hover {
  background: rgba(32, 79, 103, 0.05);
}

.toc-item.active {
  background: rgba(32, 79, 103, 0.08);
}

.item-indicator {
  width: 4px;
  height: 14px;
  border-radius: 999px;
  flex-shrink: 0;
}

.item-name {
  font-size: 12.5px;
  color: var(--text-secondary);
  line-height: 1.45;
}

.toc-item.active .item-name {
  color: var(--text-primary);
  font-weight: 600;
}

.toc-item.no-content .item-name {
  color: var(--text-muted);
}

@media (max-width: 720px) {
  .sidebar {
    position: fixed;
    top: 56px;
    bottom: 38px;
    left: 0;
    z-index: 10;
    box-shadow: var(--shadow-md);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 0;
  }
}
</style>
