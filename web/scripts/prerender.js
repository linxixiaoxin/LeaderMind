#!/usr/bin/env node

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { marked } from 'marked'
import { NODE_IMAGES, SITE } from '../src/data/graphData.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const WEB_DIR = path.resolve(__dirname, '..')
const DIST_DIR = path.resolve(WEB_DIR, 'dist')
const VAULT_DIR = path.resolve(WEB_DIR, 'public/vault')
const SITE_URL = process.env.SITE_URL || 'https://your-domain.example'
const CREATOR_NAME = SITE.creatorName

const templatePath = path.join(DIST_DIR, 'index.html')
if (!fs.existsSync(templatePath)) {
  console.error('[prerender] dist/index.html 不存在，请先运行 vite build')
  process.exit(1)
}
const template = fs.readFileSync(templatePath, 'utf-8')

const CATEGORY_LABEL = {
  主题: '主题',
  章节: '章节',
  概念: '概念',
  方法: '方法',
  场景: '场景',
  人物: '人物',
}

function walk(dir, acc = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      if (entry.name.startsWith('_')) continue
      walk(full, acc)
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      if (entry.name.startsWith('00_')) continue
      acc.push(full)
    }
  }
  return acc
}

function parseFrontmatter(raw) {
  const defaults = { tags: [], aliases: [], layer: '', created: '' }
  const match = raw.match(/^---\n([\s\S]*?)\n---\n?/)
  if (!match) return { fm: defaults, body: raw }

  const block = match[1]
  const readList = (value) => {
    const trimmed = value.trim()
    if (!trimmed) return []
    if (trimmed.startsWith('[')) {
      return trimmed
        .slice(1, -1)
        .split(',')
        .map((item) => item.trim().replace(/^['"]|['"]$/g, ''))
        .filter(Boolean)
    }
    return trimmed.split(',').map((item) => item.trim()).filter(Boolean)
  }

  const tagsLine = block.match(/^tags:\s*(.+)$/m)
  const aliasesLine = block.match(/^aliases:\s*(.+)$/m)
  const layerLine = block.match(/^layer:\s*(.+)$/m)
  const createdLine = block.match(/^created:\s*(.+)$/m)

  return {
    fm: {
      tags: tagsLine ? readList(tagsLine[1]) : [],
      aliases: aliasesLine ? readList(aliasesLine[1]) : [],
      layer: layerLine ? layerLine[1].trim() : '',
      created: createdLine ? createdLine[1].trim() : '',
    },
    body: raw.slice(match[0].length),
  }
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function stripForDesc(body) {
  return body
    .replace(/\[\[([^\]]+)\]\]/g, '$1')
    .replace(/^#+\s*/gm, '')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/[`*_>#-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 160)
}

function renderMarkdown(body) {
  let text = body.replace(/^(\*\*[^*\n]+\*\*)\n(?!\n)/gm, '$1\n\n')
  text = text.replace(/\[\[([^\]]+)\]\]/g, (_, name) => {
    return `<a href="/note/${encodeURIComponent(name)}" class="wiki-link" data-wiki="${escapeHtml(name)}">${escapeHtml(name)}</a>`
  })
  text = text.replace(/\*\*(问|答)\*\*：/g, (_, label) => `<span class="qa-label">${label}</span>：`)
  return marked.parse(text, { breaks: true })
}

function writeSeoPage(mdPath) {
  const raw = fs.readFileSync(mdPath, 'utf-8')
  const { fm, body } = parseFrontmatter(raw)
  const name = path.basename(mdPath, '.md')
  const category = path.relative(VAULT_DIR, mdPath).split(path.sep)[0] || ''
  const categoryLabel = CATEGORY_LABEL[category] || category
  const title = `${name} · ${categoryLabel} · ${SITE.title}`
  const description = stripForDesc(body) || `${SITE.title}中关于“${name}”的阅读卡片。`
  const url = `${SITE_URL}/note/${encodeURIComponent(name)}`
  const renderedHtml = renderMarkdown(body)
  const heroImage = NODE_IMAGES[name] || ''

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: name,
    description,
    url,
    inLanguage: 'zh-CN',
    author: { '@type': 'Person', name: CREATOR_NAME },
    publisher: { '@type': 'Organization', name: CREATOR_NAME, url: SITE_URL },
    keywords: [...fm.tags, name, SITE.title].join(','),
    articleSection: categoryLabel,
    mainEntityOfPage: url,
  }

  let html = template
  html = html.replace(/<title>[\s\S]*?<\/title>/i, `<title>${escapeHtml(title)}</title>`)
  html = html.replace(/<meta\s+name=["']description["'][^>]*>/i, `<meta name="description" content="${escapeHtml(description)}" />`)
  html = html.replace(/<meta\s+property=["']og:title["'][^>]*>/i, `<meta property="og:title" content="${escapeHtml(title)}" />`)
  html = html.replace(/<meta\s+property=["']og:description["'][^>]*>/i, `<meta property="og:description" content="${escapeHtml(description)}" />`)
  html = html.replace(/<meta\s+property=["']og:url["'][^>]*>/i, `<meta property="og:url" content="${escapeHtml(url)}" />`)
  html = html.replace(/<meta\s+name=["']twitter:title["'][^>]*>/i, `<meta name="twitter:title" content="${escapeHtml(title)}" />`)
  html = html.replace(/<meta\s+name=["']twitter:description["'][^>]*>/i, `<meta name="twitter:description" content="${escapeHtml(description)}" />`)

  const headExtras = [
    `<link rel="canonical" href="${escapeHtml(url)}" />`,
    `<script type="application/ld+json">${JSON.stringify(jsonLd)}</script>`,
  ].join('\n    ')

  html = html.replace(/<\/head>/i, `    ${headExtras}\n  </head>`)
  html = html.replace(
    /<div id="app"><\/div>/i,
    `<div id="app"><div class="ssr-article" style="max-width:760px;margin:40px auto;padding:24px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Segoe UI',sans-serif;line-height:1.8;color:#33424d;">${heroImage ? `<img src="${heroImage}" alt="${escapeHtml(name)} 对应配图" style="display:block;width:100%;margin:0 0 20px;border-radius:20px;border:1px solid #ddd6ca;" />` : ''}${renderedHtml}</div></div>`,
  )

  const outputDir = path.join(DIST_DIR, 'note', encodeURIComponent(name))
  fs.mkdirSync(outputDir, { recursive: true })
  fs.writeFileSync(path.join(outputDir, 'index.html'), html, 'utf-8')

  return url
}

const urls = walk(VAULT_DIR).map(writeSeoPage)

const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>${SITE_URL}</loc></url>
  <url><loc>${SITE_URL}/graph</loc></url>
${urls.map((url) => `  <url><loc>${escapeHtml(url)}</loc></url>`).join('\n')}
</urlset>
`

fs.writeFileSync(path.join(DIST_DIR, 'sitemap.xml'), sitemapXml, 'utf-8')
fs.writeFileSync(path.join(DIST_DIR, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${SITE_URL}/sitemap.xml\n`, 'utf-8')

console.log(`[prerender] 完成，共生成 ${urls.length} 个静态详情页`)
