# Stage 預覽頁模板

## 目錄結構

```
stage/{project}/
  index.html           ← 預覽頁
  {project}_stage.mp4  ← 影片
  bg_00_opening.png    ← 章節背景圖
  bg_01_xxx.png
  ...
  thumbnail.jpg        ← YouTube 封面
  script_zh.txt        ← 中文腳本
  subtitles_split.srt  ← 斷句字幕
  youtube_meta.json    ← YouTube 文案
```

## 必要區塊

### ⓪ 返回索引
```html
<div style="margin-bottom:20px;">
  <a href="../" style="color:#555;text-decoration:none;font-size:0.82em;
     padding:6px 12px;background:#141414;border:1px solid #222;border-radius:6px;">
    ← Stage 索引
  </a>
</div>
```

### ① 頁首 + 狀態
```html
<h1>影片標題 <span class="badge stage">Stage 審閱中</span></h1>
<!-- 私人：<span class="badge private">🔒 已上傳</span> -->
<!-- 公開：<span class="badge live">✅ 已公開</span> -->
```

### ② 影片播放器
```html
<video controls preload="metadata" poster="thumbnail.jpg">
  <source src="{project}_stage.mp4" type="video/mp4">
</video>
```

### ③ 章節背景圖 Grid
```html
<div class="chapter-grid">
  <div class="chapter-card">
    <img src="bg_00.png" loading="lazy">
    <div class="chapter-info">
      <div class="chapter-num">00 · 開場</div>
      <div class="chapter-title">章節標題</div>
      <div class="chapter-dur">0:00 → 0:30</div>
    </div>
  </div>
</div>
```

### ④ YouTube 文案區
```html
<div class="yt-section">
  <div class="yt-header">
    <span class="yt-logo">▶</span>
    <h2>愛播客 — YouTube 發布文案</h2>
    <span class="yt-pill pending">⏳ 待審閱</span>
  </div>
  <div class="yt-field">
    <label>標題</label>
    <div class="val title-val">{title}</div>
  </div>
  <div class="yt-field">
    <label>描述</label>
    <div class="val" id="ytDesc">{description}</div>
  </div>
</div>
```

## 狀態 Badge CSS

```css
.badge { font-size:0.68em; padding:3px 8px; border-radius:4px; }
.badge.stage  { background:#e63946; color:white; }
.badge.private { background:#f4a261; color:#111; }
.badge.live   { background:#22c55e; color:#fff; }
```

## Stage 索引卡片模板

```html
<a class="card" href="{project}/">
  <img class="card-thumb" src="{project}/thumbnail.jpg">
  <div class="card-body">
    <div class="title">{標題}</div>
    <div class="desc">{一句話摘要}</div>
    <div class="card-footer">
      <span class="tag stage">Stage</span>
      <span class="dur">X 分鐘</span>
    </div>
  </div>
</a>
```

## 推送流程

```bash
cd /tmp/stage_repo
git add {project}/ index.html
git commit -m "stage: {project}"
git push
```

Pages URL: `https://i94ivoice-glitch.github.io/stage/{project}/`
