<template>
  <div class="home-wrap">
    <div class="home-scroll">
      <section class="hero" :class="{ visible: mounted }">
        <div class="hero-grid">
          <div class="hero-copy">
            <div class="hero-overline">{{ SITE.heroOverline }}</div>
            <h1 class="hero-title">
              <span v-for="line in SITE.heroTitleLines" :key="line" class="hero-title-line">{{ line }}</span>
            </h1>
            <p class="hero-desc">{{ SITE.description }}</p>

            <div class="hero-actions">
              <button class="primary-btn" @click="$emit('showGraph')">打开知识图谱</button>
              <button class="ghost-btn" @click="$emit('navigate', SITE.recommendedPath[0])">从导读开始</button>
            </div>
          </div>

          <div class="hero-panel">
            <div class="panel-kicker">推荐阅读路径</div>
            <div class="path-row">
              <button
                v-for="(node, index) in SITE.recommendedPath"
                :key="node"
                class="path-chip"
                @click="$emit('navigate', node)"
              >
                <span class="path-num">{{ index + 1 }}</span>
                <span>{{ node }}</span>
              </button>
            </div>

            <div class="panel-divider"></div>

            <div class="panel-kicker">快捷入口</div>
            <div class="quick-links">
              <button
                v-for="node in SITE.quickLinks"
                :key="node"
                class="quick-link"
                @click="$emit('navigate', node)"
              >
                {{ node }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="journey-map" :class="{ visible: mounted }">
        <div class="journey-head">
          <div>
            <div class="journey-overline">{{ SITE.journeyOverline || 'Journey Map' }}</div>
            <h2 class="journey-title">{{ SITE.journeyTitle || '章节升级打怪地图' }}</h2>
            <p class="journey-desc">{{ SITE.journeyDescription }}</p>
          </div>
          <button class="journey-cta" @click="$emit('navigate', SITE.journeyMap[0].node)">{{ SITE.journeyEntryLabel || '从起点进入' }}</button>
        </div>

        <div class="journey-track">
          <div class="track-line"></div>

          <article
            v-for="(stage, index) in SITE.journeyMap"
            :key="stage.node"
            class="journey-stage"
            :class="index % 2 === 0 ? 'left' : 'right'"
          >
            <button class="stage-card" @click="$emit('navigate', stage.node)">
              <div class="stage-thumb-wrap">
                <img :src="stage.image" :alt="`${stage.node} 缩略图`" class="stage-thumb" />
                <span class="stage-badge">{{ stage.level }}</span>
              </div>

              <div class="stage-copy">
                <div class="stage-kicker">{{ stage.stage }}</div>
                <h3 class="stage-title">{{ stage.node }}</h3>
                <p class="stage-summary">{{ stage.summary }}</p>
              </div>
            </button>

            <div v-if="stage.bridgeToNext" class="stage-bridge">
              {{ stage.bridgeToNext }}
            </div>
          </article>
        </div>
      </section>

      <section class="stats-grid" :class="{ visible: mounted }">
        <article v-for="stat in SITE.stats" :key="stat.label" class="stat-card">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </article>
      </section>

      <section class="sections-grid" :class="{ visible: mounted }">
        <article
          v-for="section in HOME_SECTIONS"
          :key="section.id"
          class="section-card"
          :style="{ '--section-color': section.color }"
        >
          <div class="section-head">
            <span class="section-kicker">{{ section.subtitle }}</span>
            <h2 class="section-title">{{ section.title }}</h2>
            <p class="section-desc">{{ section.desc }}</p>
          </div>

          <div class="section-nodes">
            <button
              v-for="node in section.nodes"
              :key="node"
              class="node-chip"
              @click="$emit('navigate', node)"
            >
              <span class="chip-dot"></span>
              <span>{{ node }}</span>
            </button>
          </div>
        </article>
      </section>
    </div>

    <button class="follow-fab" @click="followOpen = true">
      <span class="follow-fab-kicker">Follow</span>
      <span class="follow-fab-title">{{ SITE.followTitle }}</span>
    </button>

    <Transition name="follow-layer">
      <div v-if="followOpen" class="follow-overlay" @click="followOpen = false"></div>
    </Transition>

    <Transition name="follow-drawer">
      <aside v-if="followOpen" class="follow-drawer" @click.stop>
        <div class="drawer-head">
          <div>
            <div class="follow-overline">Follow Creator</div>
            <h2 class="drawer-title">{{ SITE.followTitle }}</h2>
          </div>

          <button class="drawer-close" @click="followOpen = false" aria-label="关闭关注面板">
            ×
          </button>
        </div>

        <div class="drawer-intro">
          <div class="brand-name">{{ SITE.creatorName }}</div>
          <p class="drawer-desc">{{ SITE.followDescription }}</p>
        </div>

        <div class="drawer-list">
          <article v-for="channel in SITE.socialChannels" :key="channel.id" class="follow-card">
            <div class="follow-channel">{{ channel.label }}</div>

            <div class="follow-preview">
              <img
                v-if="channel.qrImage && !brokenQrIds.has(channel.id)"
                :src="qrSrc(channel.qrImage)"
                :alt="`${channel.label}二维码`"
                class="follow-qr"
                @error="markQrBroken(channel.id)"
              />
              <div v-else class="follow-qr-fallback">
                <div class="fallback-text">{{ channel.fallbackText }}</div>
              </div>
            </div>
          </article>
        </div>
      </aside>
    </Transition>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { HOME_SECTIONS, SITE } from '../data/graphData.js'

defineEmits(['navigate', 'showGraph'])

const mounted = ref(false)
const brokenQrIds = ref(new Set())
const followOpen = ref(false)

onMounted(() => {
  requestAnimationFrame(() => {
    mounted.value = true
  })
})

function markQrBroken(id) {
  brokenQrIds.value = new Set([...brokenQrIds.value, id])
}

function qrSrc(path) {
  if (!path) return ''
  const version = SITE.assetVersion ? `?v=${SITE.assetVersion}` : ''
  return `${path}${version}`
}
</script>

<style scoped>
.home-wrap {
  height: 100%;
  overflow-y: auto;
}

.home-wrap::-webkit-scrollbar {
  width: 4px;
}

.home-wrap::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 999px;
}

.home-scroll {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px 80px;
}

.hero,
.journey-map,
.stats-grid,
.sections-grid {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.62s ease, transform 0.62s ease;
}

.hero.visible,
.journey-map.visible,
.stats-grid.visible,
.sections-grid.visible {
  opacity: 1;
  transform: translateY(0);
}

.hero {
  padding: 48px 0 24px;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.9fr);
  gap: 18px;
  align-items: stretch;
}

.hero-copy,
.hero-panel,
.journey-map,
.stat-card,
.section-card {
  border: 1px solid var(--border-default);
  box-shadow: var(--shadow-sm);
}

.hero-copy,
.hero-panel {
  padding: 32px;
  border-radius: 28px;
  background: rgba(247, 245, 240, 0.88);
}

.hero-copy {
  background:
    radial-gradient(circle at top right, rgba(32, 79, 103, 0.12) 0%, rgba(247, 245, 240, 0.88) 42%),
    rgba(247, 245, 240, 0.92);
}

.hero-overline,
.panel-kicker,
.journey-overline {
  margin-bottom: 16px;
  font-size: 10px;
  letter-spacing: 0.22em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.hero-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 20px;
}

.hero-title-line {
  font-family: var(--font-serif);
  font-size: clamp(36px, 5vw, 62px);
  line-height: 1.05;
  color: var(--text-primary);
}

.hero-title-line:last-child {
  color: var(--brand);
}

.hero-desc,
.journey-desc {
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.85;
}

.hero-desc {
  max-width: 620px;
}

.hero-actions {
  margin-top: 28px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.primary-btn,
.ghost-btn,
.path-chip,
.quick-link,
.node-chip,
.journey-cta,
.stage-card {
  cursor: pointer;
  transition: transform 0.16s ease, border-color 0.16s ease, background 0.16s ease, color 0.16s ease;
}

.primary-btn,
.ghost-btn,
.journey-cta {
  border-radius: 999px;
  padding: 11px 18px;
  font-size: 13px;
}

.primary-btn {
  border: 1px solid transparent;
  background: var(--brand);
  color: var(--text-on-dark);
}

.primary-btn:hover,
.journey-cta:hover {
  transform: translateY(-1px);
}

.ghost-btn,
.journey-cta {
  border: 1px solid rgba(32, 79, 103, 0.18);
  background: rgba(255, 255, 255, 0.72);
  color: var(--brand);
}

.ghost-btn:hover,
.journey-cta:hover {
  background: rgba(32, 79, 103, 0.08);
}

.path-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.path-chip {
  width: 100%;
  border: 1px solid rgba(32, 79, 103, 0.14);
  background: rgba(255, 255, 255, 0.78);
  border-radius: 18px;
  padding: 12px 14px;
  display: flex;
  gap: 10px;
  align-items: center;
  text-align: left;
  color: var(--text-secondary);
}

.path-chip:hover {
  transform: translateY(-1px);
  border-color: rgba(32, 79, 103, 0.26);
  color: var(--text-primary);
}

.path-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(32, 79, 103, 0.1);
  color: var(--brand);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.panel-divider {
  height: 1px;
  margin: 18px 0;
  background: var(--border-default);
}

.quick-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-link {
  border: 1px solid var(--border-default);
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.76);
  color: var(--text-secondary);
  font-size: 12px;
}

.quick-link:hover {
  border-color: rgba(191, 111, 63, 0.28);
  color: var(--accent);
}

.journey-map {
  margin-bottom: 18px;
  padding: 28px;
  border-radius: 30px;
  background:
    radial-gradient(circle at top left, rgba(109, 92, 147, 0.08) 0%, rgba(247, 245, 240, 0.95) 36%),
    linear-gradient(180deg, rgba(247, 245, 240, 0.98) 0%, rgba(239, 243, 243, 0.98) 100%);
}

.follow-overline {
  margin-bottom: 12px;
  font-size: 10px;
  letter-spacing: 0.22em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.follow-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.follow-card {
  padding: 18px;
  border-radius: 24px;
  border: 1px solid rgba(32, 79, 103, 0.12);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 14px 32px rgba(18, 28, 36, 0.06);
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
  text-align: center;
}

.follow-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.follow-channel {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(32, 79, 103, 0.1);
  color: var(--brand);
  font-size: 11px;
  letter-spacing: 0.05em;
}

.follow-id {
  font-size: 12px;
  color: var(--text-muted);
}

.follow-fab {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
  border: 1px solid rgba(32, 79, 103, 0.14);
  border-right: none;
  border-radius: 22px 0 0 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(245, 242, 236, 0.98) 100%);
  box-shadow: 0 18px 42px rgba(18, 28, 36, 0.12);
  padding: 14px 16px 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
  cursor: pointer;
}

.follow-fab:hover {
  background: rgba(255, 255, 255, 0.98);
}

.follow-fab-kicker {
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.follow-fab-title {
  font-family: var(--font-serif);
  font-size: 18px;
  color: var(--text-primary);
}

.follow-overlay {
  position: fixed;
  inset: 0;
  background: rgba(16, 23, 29, 0.3);
  backdrop-filter: blur(3px);
  z-index: 29;
}

.follow-drawer {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: min(420px, calc(100vw - 24px));
  z-index: 30;
  border-left: 1px solid var(--border-default);
  background:
    radial-gradient(circle at top right, rgba(191, 111, 63, 0.12) 0%, rgba(247, 245, 240, 0.96) 34%),
    linear-gradient(180deg, rgba(248, 244, 237, 0.99) 0%, rgba(242, 241, 236, 0.99) 100%);
  box-shadow: -18px 0 42px rgba(18, 28, 36, 0.14);
  padding: 24px 20px 28px;
  overflow-y: auto;
}

.follow-drawer::-webkit-scrollbar {
  width: 4px;
}

.follow-drawer::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 999px;
}

.drawer-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.drawer-title {
  margin-bottom: 10px;
  font-family: var(--font-serif);
  font-size: 34px;
  color: var(--text-primary);
}

.drawer-desc {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.8;
}

.drawer-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border-default);
  background: rgba(255, 255, 255, 0.78);
  color: var(--text-secondary);
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
}

.drawer-intro {
  margin-bottom: 18px;
  padding: 18px 16px;
  border-radius: 20px;
  border: 1px solid rgba(32, 79, 103, 0.1);
  background: rgba(255, 255, 255, 0.74);
  text-align: center;
}

.brand-name {
  font-family: var(--font-serif);
  font-size: 24px;
  color: var(--text-primary);
}

.drawer-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.follow-preview {
  display: flex;
  justify-content: center;
  width: 100%;
}

.follow-qr {
  display: block;
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: contain;
  border-radius: 18px;
  border: 1px solid rgba(32, 79, 103, 0.1);
  background: #fff;
}

.follow-qr-fallback {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 20px;
  border: 1px dashed rgba(32, 79, 103, 0.18);
  background:
    linear-gradient(135deg, rgba(32, 79, 103, 0.08) 0%, rgba(191, 111, 63, 0.08) 100%),
    rgba(255, 255, 255, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  text-align: center;
}

.fallback-text {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.follow-layer-enter-active,
.follow-layer-leave-active {
  transition: opacity 0.22s ease;
}

.follow-layer-enter-from,
.follow-layer-leave-to {
  opacity: 0;
}

.follow-drawer-enter-active,
.follow-drawer-leave-active {
  transition: transform 0.26s ease, opacity 0.26s ease;
}

.follow-drawer-enter-from,
.follow-drawer-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.journey-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
}

.journey-title {
  font-family: var(--font-serif);
  font-size: 34px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.journey-track {
  position: relative;
  display: grid;
  gap: 16px;
  padding: 10px 0;
}

.track-line {
  position: absolute;
  left: 50%;
  top: 12px;
  bottom: 12px;
  width: 4px;
  transform: translateX(-50%);
  background:
    linear-gradient(180deg, rgba(32, 79, 103, 0.14) 0%, rgba(191, 111, 63, 0.24) 100%);
  border-radius: 999px;
}

.journey-stage {
  position: relative;
  width: calc(50% - 28px);
}

.journey-stage.left {
  justify-self: start;
}

.journey-stage.right {
  justify-self: end;
}

.stage-card {
  width: 100%;
  border: 1px solid rgba(32, 79, 103, 0.12);
  background: rgba(255, 255, 255, 0.84);
  border-radius: 24px;
  padding: 14px;
  display: grid;
  grid-template-columns: 108px minmax(0, 1fr);
  gap: 14px;
  text-align: left;
  box-shadow: 0 12px 28px rgba(18, 28, 36, 0.06);
}

.stage-card:hover {
  transform: translateY(-2px);
  border-color: rgba(32, 79, 103, 0.24);
}

.stage-thumb-wrap {
  position: relative;
}

.stage-thumb {
  display: block;
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
  border-radius: 16px;
  border: 1px solid rgba(32, 79, 103, 0.08);
}

.stage-badge {
  position: absolute;
  left: 8px;
  top: 8px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(23, 48, 65, 0.82);
  color: #fff;
  font-size: 10px;
  letter-spacing: 0.06em;
}

.stage-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: center;
}

.stage-kicker {
  font-size: 11px;
  color: var(--accent);
  letter-spacing: 0.06em;
}

.stage-title {
  font-family: var(--font-serif);
  font-size: 22px;
  color: var(--text-primary);
  line-height: 1.25;
}

.stage-summary {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.stage-bridge {
  margin-top: 10px;
  padding: 10px 14px;
  border-radius: 16px;
  background: rgba(32, 79, 103, 0.06);
  color: var(--text-tertiary);
  font-size: 12px;
  line-height: 1.7;
}

.journey-stage.left::after,
.journey-stage.right::after {
  content: '';
  position: absolute;
  top: 74px;
  width: 24px;
  height: 2px;
  background: rgba(32, 79, 103, 0.18);
}

.journey-stage.left::after {
  right: -26px;
}

.journey-stage.right::after {
  left: -26px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.stat-card {
  padding: 18px 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
}

.stat-value {
  font-family: var(--font-serif);
  font-size: 30px;
  color: var(--brand);
}

.stat-label {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.sections-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.section-card {
  padding: 24px;
  border-radius: 24px;
  background: rgba(247, 245, 240, 0.9);
}

.section-head {
  margin-bottom: 18px;
}

.section-kicker {
  display: inline-block;
  margin-bottom: 8px;
  font-size: 11px;
  color: var(--section-color);
  letter-spacing: 0.05em;
}

.section-title {
  font-family: var(--font-serif);
  font-size: 24px;
  color: var(--text-primary);
}

.section-desc {
  margin-top: 10px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.8;
}

.section-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.node-chip {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  padding: 9px 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

.node-chip:hover {
  border-color: color-mix(in srgb, var(--section-color) 32%, transparent);
  color: var(--section-color);
  transform: translateY(-1px);
}

.chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--section-color);
}

@media (max-width: 1080px) {
  .journey-stage {
    width: calc(50% - 18px);
  }

  .stage-card {
    grid-template-columns: 92px minmax(0, 1fr);
  }

  .stage-title {
    font-size: 18px;
  }
}

@media (max-width: 960px) {
  .hero-grid,
  .sections-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .journey-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .track-line {
    left: 14px;
    transform: none;
  }

  .journey-stage,
  .journey-stage.left,
  .journey-stage.right {
    width: 100%;
    justify-self: stretch;
    padding-left: 28px;
  }

  .journey-stage.left::after,
  .journey-stage.right::after {
    left: 6px;
    right: auto;
    width: 20px;
  }
}

@media (max-width: 720px) {
  .home-scroll {
    padding: 0 14px 40px;
  }

  .hero {
    padding-top: 20px;
  }

  .hero-copy,
  .hero-panel,
  .journey-map,
  .section-card {
    padding: 20px;
    border-radius: 22px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .hero-desc,
  .journey-desc,
  .section-desc {
    font-size: 13px;
  }

  .journey-title {
    font-size: 28px;
  }

  .follow-fab {
    right: 10px;
    top: auto;
    bottom: 18px;
    transform: none;
    border-radius: 18px;
    border-right: 1px solid rgba(32, 79, 103, 0.14);
    padding: 12px 14px;
  }

  .follow-fab-title {
    font-size: 16px;
  }

  .follow-drawer {
    width: calc(100vw - 8px);
    padding: 18px 14px 22px;
  }

  .drawer-title {
    font-size: 28px;
  }

  .brand-name {
    font-size: 22px;
  }

  .stage-card {
    grid-template-columns: 82px minmax(0, 1fr);
    gap: 12px;
  }

  .stage-title {
    font-size: 17px;
  }
}
</style>
