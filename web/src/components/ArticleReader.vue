<template>
  <div class="reader-wrap">
    <div class="reader-header">
      <button class="back-btn" @click="$emit('close')">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
          <path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        返回
      </button>

      <div class="reader-breadcrumb">
        <span class="breadcrumb-type" :style="{ color: typeMeta.color }">{{ typeMeta.label }}</span>
        <span class="breadcrumb-sep">›</span>
        <span class="breadcrumb-title">{{ nodeId }}</span>
      </div>

      <span class="reader-tagline">{{ nodeTagline }}</span>
    </div>

    <div class="reader-body">
      <div v-if="loading" class="reader-state">
        <div class="loading-spinner"></div>
        <span>正在加载这张卡片…</span>
      </div>

      <div v-else-if="error" class="reader-state">
        <div class="state-icon">📄</div>
        <div class="state-title">暂无对应内容</div>
        <div class="state-desc">“{{ nodeId }}” 还没有对应 Markdown 文件，可以先回到图谱继续查看相关节点。</div>
        <button class="back-btn-lg" @click="$emit('close')">返回上一步</button>
      </div>

      <div v-else>
        <div v-if="nodeImage" class="article-hero">
          <img :src="nodeImage" :alt="`${nodeId} 对应配图`" class="hero-image" />
        </div>

        <div v-if="frontmatter.tags.length || frontmatter.created" class="article-meta">
          <div v-if="frontmatter.tags.length" class="meta-tags">
            <span v-for="tag in frontmatter.tags" :key="tag" class="meta-tag">{{ tag }}</span>
          </div>
          <span v-if="frontmatter.created" class="meta-created">{{ frontmatter.created }}</span>
        </div>

        <article class="md-content" v-html="renderedHtml" @click.prevent="onArticleClick"></article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { marked } from 'marked'
import { FILE_MAP, NODE_IMAGES, NODES, NODE_TYPE_META } from '../data/graphData.js'

const props = defineProps({
  nodeId: String,
})

const emit = defineEmits(['close', 'navigate'])

const loading = ref(false)
const error = ref(false)
const renderedHtml = ref('')
const frontmatter = ref({ tags: [], created: '', layer: '' })

const currentNode = computed(() => NODES.find((node) => node.id === props.nodeId))
const typeMeta = computed(() => NODE_TYPE_META[currentNode.value?.type] || { label: '', color: '#7f8790' })
const nodeTagline = computed(() => currentNode.value?.tagline || '')
const nodeImage = computed(() => NODE_IMAGES[props.nodeId] || '')

async function loadContent(id) {
  if (!id) return

  loading.value = true
  error.value = false
  renderedHtml.value = ''
  frontmatter.value = { tags: [], created: '', layer: '' }

  const path = FILE_MAP[id]
  if (!path) {
    loading.value = false
    error.value = true
    return
  }

  try {
    const response = await fetch(path)
    if (!response.ok) throw new Error('not found')
    let text = await response.text()

    const match = text.match(/^(?:\uFEFF)?---\r?\n([\s\S]*?)\r?\n---\r?\n?/)
    if (match) {
      const raw = match[1]
      const tagsLine = raw.match(/^tags:\s*(.+)$/m)
      const layerLine = raw.match(/^layer:\s*(.+)$/m)
      const createdLine = raw.match(/^created:\s*(.+)$/m)

      if (tagsLine) {
        const value = tagsLine[1].trim()
        frontmatter.value.tags = value.startsWith('[')
          ? value.slice(1, -1).split(',').map((item) => item.trim().replace(/^['"]|['"]$/g, ''))
          : value.split(',').map((item) => item.trim())
      }
      if (layerLine) frontmatter.value.layer = layerLine[1].trim()
      if (createdLine) frontmatter.value.created = createdLine[1].trim()

      text = text.slice(match[0].length)
    }

    text = text.replace(/^(\*\*[^*\n]+\*\*)\n(?!\n)/gm, '$1\n\n')

    let processed = text.replace(/\[\[([^\]]+)\]\]/g, (_, name) => {
      return `<a href="#" class="wiki-link" data-wiki="${name}">${name}</a>`
    })
    processed = processed.replace(/\*\*(问|答)\*\*：/g, (_, label) => {
      return `<span class="qa-label">${label}</span>：`
    })

    renderedHtml.value = marked.parse(processed, { breaks: true })
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

function onArticleClick(event) {
  const link = event.target.closest('a.wiki-link')
  if (!link) return
  const target = link.dataset.wiki
  if (target) emit('navigate', target)
}

watch(
  () => props.nodeId,
  (id) => {
    loadContent(id)
  },
  { immediate: true },
)
</script>

<style scoped>
.reader-wrap {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.reader-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 26px;
  border-bottom: 1px solid var(--border-default);
  background: rgba(247, 245, 240, 0.86);
  backdrop-filter: blur(8px);
}

.back-btn {
  border: 1px solid var(--border-default);
  border-radius: 999px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 7px 12px;
  cursor: pointer;
}

.back-btn:hover,
.back-btn-lg:hover {
  color: var(--brand);
  border-color: rgba(32, 79, 103, 0.24);
}

.reader-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.breadcrumb-type {
  font-size: 11px;
  font-weight: 700;
}

.breadcrumb-sep {
  color: var(--text-muted);
}

.breadcrumb-title {
  font-family: var(--font-serif);
  font-size: 15px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reader-tagline {
  margin-left: auto;
  color: var(--text-muted);
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 320px;
}

.reader-body {
  flex: 1;
  overflow-y: auto;
  padding: 34px 48px 48px;
}

.reader-body::-webkit-scrollbar {
  width: 4px;
}

.reader-body::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 999px;
}

.reader-state {
  padding-top: 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-default);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.state-icon {
  font-size: 38px;
}

.state-title {
  font-size: 17px;
  color: var(--text-primary);
}

.state-desc {
  max-width: 360px;
  line-height: 1.7;
}

.back-btn-lg {
  border: 1px solid var(--border-default);
  border-radius: 999px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  padding: 8px 16px;
  cursor: pointer;
}

.article-meta {
  max-width: 760px;
  margin: 0 auto 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.article-hero {
  max-width: 760px;
  margin: 0 auto 22px;
}

.hero-image {
  display: block;
  width: 100%;
  border-radius: 20px;
  border: 1px solid var(--border-default);
  box-shadow: var(--shadow-sm);
  background: rgba(255, 255, 255, 0.72);
}

.meta-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-tag {
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--border-default);
  color: var(--text-tertiary);
  font-size: 11px;
}

.meta-created {
  color: var(--text-muted);
  font-size: 11px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 720px) {
  .reader-header {
    padding: 10px 14px;
    gap: 10px;
  }

  .reader-tagline {
    display: none;
  }

  .reader-body {
    padding: 22px 18px 36px;
  }
}
</style>

<style>
.md-content {
  max-width: 760px;
  margin: 0 auto;
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.82;
}

.md-content h1 {
  margin-bottom: 10px;
  font-family: var(--font-serif);
  font-size: 31px;
  line-height: 1.2;
  color: var(--text-primary);
}

.md-content h2 {
  margin-top: 34px;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-default);
  font-family: var(--font-serif);
  font-size: 20px;
  color: var(--text-primary);
}

.md-content h3 {
  margin-top: 20px;
  margin-bottom: 8px;
  font-size: 15px;
  color: var(--text-primary);
}

.md-content p,
.md-content ul,
.md-content ol,
.md-content blockquote,
.md-content pre {
  margin-bottom: 14px;
}

.md-content ul,
.md-content ol {
  padding-left: 22px;
}

.md-content li {
  margin-bottom: 6px;
}

.md-content blockquote {
  padding: 12px 16px;
  border-left: 3px solid var(--accent);
  background: rgba(191, 111, 63, 0.08);
  border-radius: 0 10px 10px 0;
}

.md-content strong {
  color: var(--text-primary);
}

.md-content hr {
  border: none;
  border-top: 1px solid var(--border-default);
  margin: 22px 0;
}

.md-content a {
  color: var(--brand);
  text-decoration: none;
}

.md-content .wiki-link {
  border-bottom: 1px dashed rgba(32, 79, 103, 0.35);
}

.md-content .wiki-link:hover {
  color: var(--accent);
  border-bottom-color: rgba(191, 111, 63, 0.45);
}

.md-content code {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(32, 79, 103, 0.08);
  color: var(--brand);
}

.md-content pre {
  padding: 16px;
  border-radius: 14px;
  background: var(--bg-deep);
  overflow-x: auto;
}

.md-content pre code {
  background: transparent;
  color: var(--text-on-dark);
  padding: 0;
}

.md-content .qa-label {
  display: inline;
  font-weight: 700;
  color: var(--text-primary);
}

.md-content p:not(li p) > strong:first-child {
  display: block;
  margin-bottom: 4px;
  margin-top: 18px;
}

.md-content p:first-of-type > strong:first-child {
  margin-top: 0;
}

@media (max-width: 720px) {
  .md-content {
    font-size: 14px;
    line-height: 1.76;
  }

  .md-content h1 {
    font-size: 24px;
  }

  .md-content h2 {
    font-size: 18px;
  }
}
</style>
