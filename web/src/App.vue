<template>
  <div class="app-shell">
    <header class="topbar">
      <button class="icon-btn" @click="sidebarOpen = !sidebarOpen" title="目录">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <rect x="2" y="4" width="12" height="1.3" rx="0.65" fill="currentColor" />
          <rect x="2" y="7.4" width="9" height="1.3" rx="0.65" fill="currentColor" />
          <rect x="2" y="10.8" width="11" height="1.3" rx="0.65" fill="currentColor" />
        </svg>
      </button>

      <div class="brand" @click="goHome">
        <span class="brand-kicker">{{ SITE.creatorLabel }}</span>
        <span class="brand-name">{{ SITE.shortTitle }}</span>
      </div>

      <nav class="nav-tabs">
        <button class="nav-btn" :class="{ active: view === 'home' }" @click="goHome">阅读地图</button>
        <button class="nav-btn" :class="{ active: view === 'graph' }" @click="onShowGraph">知识图谱</button>
      </nav>

      <div class="topbar-right">
        <div class="search-wrap" ref="searchWrapRef">
          <svg class="search-icon" width="13" height="13" viewBox="0 0 16 16" fill="none">
            <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.4" />
            <path d="M10.5 10.5L14 14" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
          </svg>
          <input
            v-model="searchQuery"
            class="search-input"
            :placeholder="SITE.searchPlaceholder"
            @keydown.escape="clearSearch"
            @keydown.enter="onSearchEnter"
            @keydown.down.prevent="onSearchArrow(1)"
            @keydown.up.prevent="onSearchArrow(-1)"
            @focus="searchFocused = true"
          />

          <div v-if="searchFocused && searchQuery && searchResults.length > 0" class="search-dropdown">
            <button
              v-for="(item, idx) in searchResults"
              :key="item.id"
              class="search-result"
              :class="{ highlighted: idx === searchHighlight }"
              @mousedown.prevent="onSearchSelect(item.id)"
            >
              <span class="result-type" :style="{ color: typeMeta(item.type).color }">
                {{ typeMeta(item.type).label }}
              </span>
              <span class="result-main">
                <span class="result-name">{{ item.id }}</span>
                <span class="result-tagline">{{ item.tagline }}</span>
              </span>
            </button>
          </div>

          <div v-if="searchFocused && searchQuery && searchResults.length === 0" class="search-dropdown search-empty">
            没找到和“{{ searchQuery }}”相关的节点
          </div>
        </div>

        <span class="node-count">{{ NODES.length }} 个节点</span>
      </div>
    </header>

    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <div class="main">
      <Sidebar
        :open="sidebarOpen"
        :active-node="activeNode"
        :is-graph-active="view === 'graph'"
        @toggle="sidebarOpen = !sidebarOpen"
        @select-node="onSidebarSelect"
        @show-graph="onShowGraph"
      />

      <main class="content">
        <HomeView v-if="view === 'home'" @navigate="onNavigate" @show-graph="onShowGraph" />
        <KnowledgeGraph
          v-if="view === 'graph'"
          :active-node="activeNode"
          @select-node="onGraphSelect"
          @open-reader="onSidebarSelect"
        />
        <ArticleReader
          v-if="view === 'reader' && activeNode"
          :node-id="activeNode"
          @close="onReaderClose"
          @navigate="onNavigate"
        />
      </main>
    </div>

    <footer class="footer-banner">
      <span class="footer-label">{{ SITE.creatorLabel }}</span>
      <span class="footer-brand">{{ SITE.creatorName }}</span>
      <span class="footer-dot">·</span>
      <span class="footer-note">{{ SITE.footerNote }}</span>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import ArticleReader from './components/ArticleReader.vue'
import HomeView from './components/HomeView.vue'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import Sidebar from './components/Sidebar.vue'
import { FILE_MAP, NODES, NODE_TYPE_META, SITE } from './data/graphData.js'

const sidebarOpen = ref(window.innerWidth > 720)
const view = ref('home')
const activeNode = ref(null)
const searchQuery = ref('')
const searchFocused = ref(false)
const searchHighlight = ref(-1)
const searchWrapRef = ref(null)
const historyStack = ref([])
const aliasMap = ref({})

function parseRoute(pathname) {
  const normalized = pathname.replace(/\/+$/, '') || '/'
  if (normalized === '/') return { view: 'home', nodeId: null }
  if (normalized === '/graph') return { view: 'graph', nodeId: null }
  const noteMatch = normalized.match(/^\/note\/(.+)$/)
  if (noteMatch) {
    try {
      return { view: 'reader', nodeId: decodeURIComponent(noteMatch[1]) }
    } catch {
      return { view: 'reader', nodeId: noteMatch[1] }
    }
  }
  return { view: 'home', nodeId: null }
}

function routeToUrl(targetView, nodeId) {
  if (targetView === 'graph') return '/graph'
  if (targetView === 'reader' && nodeId) return `/note/${encodeURIComponent(nodeId)}`
  return '/'
}

function applyRouteFromUrl(replace = false) {
  const route = parseRoute(window.location.pathname)
  view.value = route.view
  activeNode.value = route.nodeId
  if (replace) {
    const nextUrl = routeToUrl(route.view, route.nodeId)
    if (nextUrl !== window.location.pathname) {
      window.history.replaceState({ view: route.view, nodeId: route.nodeId }, '', nextUrl)
    }
  }
}

function pushRoute(targetView, nodeId) {
  const url = routeToUrl(targetView, nodeId)
  const current = window.location.pathname + window.location.search
  if (url !== current) {
    window.history.pushState({ view: targetView, nodeId }, '', url)
  }
}

function onPopState() {
  const route = parseRoute(window.location.pathname)
  view.value = route.view
  activeNode.value = route.nodeId
  historyStack.value = []
}

const searchResults = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return []
  return NODES.filter((node) => {
    const haystack = `${node.id} ${node.tagline}`.toLowerCase()
    return haystack.includes(query)
  }).slice(0, 8)
})

function onClickOutside(event) {
  if (searchWrapRef.value && !searchWrapRef.value.contains(event.target)) {
    searchFocused.value = false
    searchHighlight.value = -1
  }
}

function typeMeta(type) {
  return NODE_TYPE_META[type] || { label: type, color: '#7f8790' }
}

onMounted(async () => {
  document.addEventListener('mousedown', onClickOutside)
  window.addEventListener('popstate', onPopState)
  applyRouteFromUrl(true)

  const aliases = {}
  await Promise.all(
    Object.entries(FILE_MAP).map(async ([nodeId, path]) => {
      try {
        const response = await fetch(path)
        if (!response.ok) return
        const text = await response.text()
        const frontmatter = text.match(/^(?:\uFEFF)?---\r?\n([\s\S]*?)\r?\n---/)
        if (!frontmatter) return
        const aliasLine = frontmatter[1].match(/^aliases:\s*(.+)$/m)
        if (!aliasLine) return
        const raw = aliasLine[1].trim()
        const values = raw.startsWith('[')
          ? raw.slice(1, -1).split(',').map((item) => item.trim().replace(/^['"]|['"]$/g, ''))
          : raw.split(',').map((item) => item.trim())
        values.forEach((alias) => {
          if (alias) aliases[alias] = nodeId
        })
      } catch {
        // ignore malformed note
      }
    }),
  )
  aliasMap.value = aliases
})

onUnmounted(() => {
  document.removeEventListener('mousedown', onClickOutside)
  window.removeEventListener('popstate', onPopState)
})

function goHome() {
  historyStack.value = []
  view.value = 'home'
  activeNode.value = null
  pushRoute('home', null)
}

function onShowGraph() {
  historyStack.value = []
  view.value = 'graph'
  pushRoute('graph', null)
}

function onGraphSelect(id) {
  activeNode.value = id
}

function pushReader(id) {
  historyStack.value.push({ view: view.value, nodeId: activeNode.value })
  activeNode.value = id
  view.value = 'reader'
  pushRoute('reader', id)
}

function onSidebarSelect(id) {
  pushReader(id)
}

function onNavigate(id) {
  const exact = NODES.find((node) => node.id === id)
  if (exact) {
    pushReader(exact.id)
    return
  }
  const aliasTarget = aliasMap.value[id]
  if (aliasTarget) {
    pushReader(aliasTarget)
    return
  }
  pushReader(id)
}

function onReaderClose() {
  const previous = historyStack.value.pop()
  if (previous) {
    view.value = previous.view
    activeNode.value = previous.nodeId
    pushRoute(previous.view, previous.nodeId)
    return
  }
  goHome()
}

function onSearchSelect(id) {
  clearSearch()
  onNavigate(id)
}

function onSearchEnter() {
  if (searchResults.value.length === 0) return
  const index = searchHighlight.value >= 0 ? searchHighlight.value : 0
  onSearchSelect(searchResults.value[index].id)
}

function onSearchArrow(direction) {
  const length = searchResults.value.length
  if (length === 0) return
  searchHighlight.value = (searchHighlight.value + direction + length) % length
}

function clearSearch() {
  searchQuery.value = ''
  searchFocused.value = false
  searchHighlight.value = -1
}
</script>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #app {
  height: 100%;
  min-height: 100dvh;
}

:root {
  --bg-page: #edf1f1;
  --bg-surface: #f7f5f0;
  --bg-elevated: #ffffff;
  --bg-sidebar: #f0ede6;
  --bg-topbar: rgba(247, 245, 240, 0.96);
  --bg-deep: #173041;

  --text-primary: #15222b;
  --text-secondary: #4a5b68;
  --text-tertiary: #75838c;
  --text-muted: #9aa6ad;
  --text-on-dark: #f7f5f0;

  --brand: #204f67;
  --brand-soft: #dce7eb;
  --accent: #bf6f3f;

  --border-subtle: #ece7dc;
  --border-default: #ddd6ca;
  --border-strong: #c7beb2;

  --hover-bg: rgba(32, 79, 103, 0.08);
  --active-bg: rgba(32, 79, 103, 0.12);
  --shadow-sm: 0 4px 16px rgba(17, 27, 34, 0.06);
  --shadow-md: 0 12px 36px rgba(17, 27, 34, 0.1);

  --font-serif: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", "Songti SC", serif;
  --font-sans: "Aptos", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

body {
  font-family: var(--font-sans);
  background: radial-gradient(circle at top left, #f7f5f0 0%, #edf1f1 55%, #e6ecec 100%);
  color: var(--text-primary);
}
</style>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100dvh;
}

.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 18px;
  background: var(--bg-topbar);
  border-bottom: 1px solid var(--border-default);
  backdrop-filter: blur(10px);
  z-index: 20;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border: 1px solid var(--border-default);
  border-radius: 10px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
}

.icon-btn:hover {
  color: var(--brand);
  border-color: rgba(32, 79, 103, 0.24);
  background: var(--brand-soft);
}

.brand {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  min-width: 0;
}

.brand-kicker {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.brand-name {
  font-family: var(--font-serif);
  font-size: 18px;
  line-height: 1.1;
  color: var(--text-primary);
}

.nav-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 6px;
}

.nav-btn {
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.18s ease, background 0.18s ease;
}

.nav-btn:hover {
  color: var(--text-primary);
  background: rgba(0, 0, 0, 0.03);
}

.nav-btn.active {
  color: var(--brand);
  background: var(--brand-soft);
}

.topbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-wrap {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 260px;
  padding: 10px 14px 10px 34px;
  border: 1px solid var(--border-default);
  border-radius: 999px;
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.search-input:focus {
  border-color: rgba(32, 79, 103, 0.35);
  box-shadow: 0 0 0 3px rgba(32, 79, 103, 0.08);
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
  z-index: 50;
}

.search-result {
  width: 100%;
  border: none;
  background: transparent;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  text-align: left;
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.14s ease;
}

.search-result:hover,
.search-result.highlighted {
  background: rgba(32, 79, 103, 0.06);
}

.result-type {
  min-width: 34px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.result-main {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.result-name {
  color: var(--text-primary);
  font-size: 13px;
  line-height: 1.35;
}

.result-tagline {
  color: var(--text-tertiary);
  font-size: 11px;
  line-height: 1.5;
}

.search-empty {
  padding: 14px;
  color: var(--text-tertiary);
  font-size: 12px;
}

.node-count {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
}

.main {
  flex: 1;
  min-height: 0;
  display: flex;
  overflow: hidden;
}

.content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.sidebar-overlay {
  display: none;
}

.footer-banner {
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-top: 1px solid var(--border-default);
  background: rgba(247, 245, 240, 0.92);
  color: var(--text-tertiary);
  font-size: 12px;
}

.footer-label {
  color: var(--text-muted);
}

.footer-brand {
  color: var(--accent);
  font-weight: 700;
}

.footer-dot {
  color: var(--border-strong);
}

@media (max-width: 900px) {
  .search-input {
    width: 200px;
  }
}

@media (max-width: 720px) {
  .topbar {
    padding: 0 12px;
    gap: 10px;
  }

  .brand-kicker,
  .nav-tabs,
  .node-count,
  .footer-dot,
  .footer-note {
    display: none;
  }

  .brand-name {
    font-size: 16px;
  }

  .search-input {
    width: 150px;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 56px 0 38px;
    background: rgba(12, 21, 28, 0.3);
    z-index: 9;
  }

  .footer-banner {
    gap: 6px;
    font-size: 11px;
  }
}
</style>
