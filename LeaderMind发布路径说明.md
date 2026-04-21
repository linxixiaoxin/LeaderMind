# LeaderMind 发布路径说明

这套站点以后更新到 GitHub 时，固定沿用这条路径，不直接在外层 `E:\RedBook` 大仓库里推。

## 固定路径

- 源目录：
  `E:\RedBook\04_operations\07_skill_lib\book-kb-领导者的意识进化`
- 临时发布仓库：
  `C:\Users\zz\AppData\Local\Temp\LeaderMind_publish`
- 远端仓库：
  `https://github.com/linxixiaoxin/LeaderMind.git`
- 目标分支：
  `main`

## 为什么这样发

这个目录挂在 `E:\RedBook` 大仓库下面，当前环境里的 Git 默认会被父仓库接管。

为了避免把外层仓库的无关改动一起提交到 GitHub，发布时不直接在源目录里 `git push`，而是：

1. 在源目录里完成内容修改、生成和构建
2. 把这一个目录镜像同步到临时发布仓库
3. 只在临时发布仓库里提交并推送到 `LeaderMind`

## 标准更新步骤

### 1. 在源目录完成修改

工作目录：

```powershell
E:\RedBook\04_operations\07_skill_lib\book-kb-领导者的意识进化
```

常用校验命令：

```powershell
python -m py_compile .\generate_site.py
python -X utf8 .\generate_site.py
cd .\web
npm run build
```

说明：

- `generate_site.py` 会刷新 `vault/`、`web/public/vault/`、`web/src/data/graphData.js`
- `npm run build` 会刷新 `web/dist/`
- 如果替换了 `web/public/social/*.png`，也建议重跑一次生成和构建，确保二维码缓存版本号一起更新

### 2. 同步到临时发布仓库

在 `E:\RedBook` 下执行：

```powershell
$src='E:\RedBook\04_operations\07_skill_lib\book-kb-领导者的意识进化'
$dst='C:\Users\zz\AppData\Local\Temp\LeaderMind_publish'
robocopy $src $dst /MIR /XD .git __pycache__ web\node_modules web\dist /XF web\vite-preview.stdout.log web\vite-preview.stderr.log
```

说明：

- `/.git` 不同步，保留临时发布仓库自己的 Git 历史
- `web/node_modules`、`web/dist`、预览日志不需要从源目录拷过去
- `web/dist` 可以在临时发布仓库里重新构建

### 3. 在临时发布仓库拉最新并校验

```powershell
git -C "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish" pull --ff-only
python -m py_compile "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish\generate_site.py"
cd "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish\web"
npm run build
```

### 4. 在临时发布仓库提交并推送

```powershell
git -C "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish" status --short
git -C "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish" add -A
git -C "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish" commit -m "你的提交信息"
git -C "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish" push origin main
```

## 这次已经验证过的发布方式

最近一次成功发布：

- 仓库：`LeaderMind`
- 分支：`main`
- 提交：`3853c11`
- 提交信息：`refresh public site content and social section`

## 常见问题

### 1. 为什么不能直接在源目录里推

因为源目录不是真正独立的 Git 仓库，`git` 会回退到父级 `E:\RedBook`，容易把别的改动一起带上去。

### 2. 如果临时发布仓库不见了怎么办

重新 clone 一份：

```powershell
git clone https://github.com/linxixiaoxin/LeaderMind.git C:\Users\zz\AppData\Local\Temp\LeaderMind_publish
```

然后再按上面的同步步骤走。

### 3. 如果提交时报 `index.lock`

先确认没有别的 Git 进程占用，再重试：

```powershell
Get-Process | Where-Object { $_.ProcessName -like 'git*' }
```

如果确认没有卡住的 Git 进程，再删除锁文件：

```powershell
Remove-Item "C:\Users\zz\AppData\Local\Temp\LeaderMind_publish\.git\index.lock" -Force
```

然后重新执行 `git add -A`、`git commit`、`git push`。

## 后续约定

后面这套站点如果你再让我“推到 LeaderMind”，默认就按这份说明里的路径和流程来做，不再走外层大仓库。
