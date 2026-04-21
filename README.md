# 领导者的意识进化 · 单书互动站

基于 `dyp-kb-main` / 单书站骨架重做的《领导者的意识进化》网页版本，把这本书的：

- 全书资产
- 书 K 卡 / 主题 K 卡
- N 概念卡 / N 方法卡
- 八章深入提取
- 现实场景
- 小红书图

统一生成到一个可点击、可搜索、可看图谱的本地网站里。

## 目录结构

- `generate_site.py`
  负责把书资产、K/N 卡和章节图重新编译成站内 `vault`、`graphData.js`、章节配图。
- `vault/`
  生成后的 Markdown 母本。
- `web/public/vault/`
  前端直接消费的 Markdown 镜像。
- `web/public/chapter-images/`
  章节配图与总览缩略图。
- `web/src/data/graphData.js`
  图谱、目录、首页区块和路由数据。

## 本地生成

```powershell
cd E:\RedBook\04_operations\07_skill_lib\book-kb-领导者的意识进化
python .\generate_site.py
```

## 本地预览

开发模式：

```powershell
cd E:\RedBook\04_operations\07_skill_lib\book-kb-领导者的意识进化\web
npm run dev
```

生产预览：

```powershell
cd E:\RedBook\04_operations\07_skill_lib\book-kb-领导者的意识进化\web
npm run build
npm run preview
```

## 当前内容来源

- 书资产：`01_sources/01_books/03_领导管理与组织教练/领导者的意识进化/assets`
- N 卡：`02_collections/2_N_concepts/N_notes`
- K 卡：`02_collections/3_K_themes`
- 配图：`03_outputs/04_by_book/领导者的意识进化/小红书图`
