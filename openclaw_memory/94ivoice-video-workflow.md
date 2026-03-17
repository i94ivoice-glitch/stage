# 94iVoice YouTube 影片製作流程

> 最終版｜更新：2026-03-17（Ken Burns 正確寫法加強；禁止清單補充「先放大再平移」錯誤模式）

---

## ⚙️ 固定規格速查

| 項目 | 設定值 |
|------|--------|
| 🎙 TTS 聲音 | `zh-CN-YunjianNeural` |
| 🎙 TTS 語速 | 預設（不加 --rate）|
| 🎙 TTS 工具 | `gen_tts_ssml.py`（SSML 版，自動修正發音）|
| 🖼 背景圖生成 | DALL-E 3 · 1792×1024 · standard |
| 🎬 影片解析度 | 1280×720 · 24fps · H.264 |
| 🎞 Ken Burns | `scale(t)+crop eval=frame`，1.0→1.2→1.0，30s 循環 |
| 📝 字幕字體大小 | FontSize **38** |
| 📝 字幕最大寬度 | 54 視覺單位（約 27 中文字，最多 3 行）|
| 📝 字幕標點 | 移除 `，。；：、！…—` / 保留 `？` |
| 📝 字幕位置 | Alignment=2（底部置中），MarginV=40，MarginL/R=60 |
| 📝 字幕樣式 | 白字 Bold，黑色邊框 Outline=3 |
| 🎬 片尾 Logo | 6.04s，filter_complex concat（v2 版本） |
| 📺 YouTube 隱私 | 預設 `--private`（私人審閱後改公開）|
| 🖼 封面尺寸 | 1280×720 JPEG（YouTube 標準）|
| 🖼 封面風格 | 左 3/5 深紫背景＋文字 / 右 2/5 人物特寫 / 110px cosine 過渡融合 |
| 📺 YouTube 頻道 | 愛播客 UC3rJy84_9aDSovvJ0Xw0bfQ |

---

## 📁 固定路徑

```
本機工作區（臨時，重開機消失）:
  /tmp/{影片名}/              ← 每集的工作目錄

GitHub Stage Repo（永久）:
  本機 clone:  /tmp/stage_repo/
  遠端:        https://github.com/i94ivoice-glitch/stage
  Pages URL:   https://i94ivoice-glitch.github.io/stage/

固定素材:
  片尾 Logo:   /home/jovie/.openclaw/workspace/94ivoice_logo_outro_v2.mp4
               （6.04s · 1504×832 · 含原始音效，re-encode 至 1280×720 使用）
  字體:        /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc
  斷句腳本:    /home/jovie/.openclaw/workspace/split_srt.py
  TTS 腳本:    /home/jovie/.openclaw/workspace/gen_tts_ssml.py   ← SSML 版（主要使用）
  TTS 預處理:  /home/jovie/.openclaw/workspace/tts_preprocess.py ← 輔助模組
```

---

## 📂 GitHub 每集目錄結構

```
stage/
  {影片名}/
    index.html               ← 預覽頁（播放器 + 章節背景圖縮圖 + YouTube 文案 + 素材連結）
    {影片名}_stage.mp4       ← Stage 版（每次改動覆蓋，固定檔名）
    {影片名}.mp4             ← 正式版（Jovie 確認後才推）
    bg_00_opening.png        ← 章節背景圖（1280x720）
    bg_01_xxx.png
    ...
    subtitles.srt            ← 原始字幕（整句版）
    subtitles_split.srt      ← 斷句版（燒入用）
    audio.mp3
    youtube_meta.json        ← YouTube 發布文案
    script_zh.html
```

### 命名規則
- ✅ 固定檔名，**不加版本號**（v1/v2/v3 只在本機用，不推到 GitHub）
- ✅ 每次改動覆蓋 `_stage.mp4`，確認後再推 `.mp4`

---

## 🎬 完整製作步驟

### Step 1｜準備素材

#### 🎙 TTS 固定設定（所有影片統一使用）

**✅ 標準指令（SSML 版，所有影片統一使用）：**
```bash
python3 ~/workspace/gen_tts_ssml.py script_clean.txt /tmp/{影片名}
# 輸出：/tmp/{影片名}/audio.mp3（自動套用 SSML 發音修正）
```

| 參數 | 值 | 說明 |
|------|-----|------|
| voice | `zh-CN-YunjianNeural` | 低沉有力男聲（激情感） |
| rate | 預設 | edge-tts 預設語速，自然流暢 |
| 輸入 | `script_clean.txt` | Markdown 格式（`##`、`**` 由腳本自動清除）|

**⚠️ 注意：SSML 模式不輸出詞級字幕**，字幕需後續執行 `split_srt.py`（流程不變）。

---

#### 🔤 SSML 自動發音修正規則（`gen_tts_ssml.py`）

**英文縮寫 → 個別字母（`ABBR_MAP`）：**

| 詞 | TTS 唸法 |
|---|---|
| AI | A・I |
| OpenAI | Open・A・I |
| ChatGPT / ChatGPT-4 | Chat・G・P・T（/4）|
| GPT / GPT-4 / GPT-4o | G・P・T（/4/4o）|
| API | A・P・I |
| CEO / CTO / CFO | C・E・O … |
| IPO / ETF / GDP / ROI | 各字母個別唸 |

**多音字 → 強制指定聲調（`SSML_RULES` + `SSML_PHONEMES`）：**

| 詞 | 錯誤發音 | 正確發音 |
|---|---|---|
| 醒覺 | jiào ❌ | jué ✅ |
| 睡覺 / 一覺 | jué ❌ | jiào ✅ |
| 覺得 / 感覺 / 察覺 / 自覺 / 覺悟 | jiào ❌ | jué ✅ |
| 重複 / 重新 / 重建 | zhòng ❌ | chóng ✅ |
| 重要 / 重量 | chóng ❌ | zhòng ✅ |
| 成長 / 生長 / 長大 | 可能混淆 | zhang3 ✅ |
| 漫長 / 長期 | 可能混淆 | chang2 ✅ |

**稱謂縮寫（文字替換，進 SSML 前處理）：**

| 原文 | TTS 輸入 |
|---|---|
| Dr. Waku / Dr. Xxx | Doctor Waku / Doctor Xxx |
| Mr. / Mrs. / Ms. | Mister / Misses / Miss |
| vs. | versus |
| OpenClaw | Open Claw |

**新增規則方式：**
```python
# 英文縮寫：在 ABBR_MAP 新增
"LLM": "L L M",
"RAG": "R A G",

# 多音字：在 SSML_RULES 新增（文字替換）或 SSML_PHONEMES（phoneme 標籤）
("著作", "著作"),  # 視需求加強制 phoneme
```

**舊版 CLI（備用，不建議）：**
```bash
edge-tts --voice zh-CN-YunjianNeural \
  --text "$(cat script_clean.txt)" \
  --write-media audio.mp3 --write-subtitles audio.vtt
cp audio.vtt subtitles.srt
```

#### DALL-E 3 背景圖生成

```python
from openai import OpenAI
import requests
client = OpenAI()

resp = client.images.generate(
    model="dall-e-3",
    prompt="{依下方原則撰寫的 prompt}",
    size="1792x1024",   # 最接近 16:9
    quality="standard",
    n=1
)
img_data = requests.get(resp.data[0].url, timeout=30).content
open(f"bg_{i:02d}_{name}.png", "wb").write(img_data)
```

> 每章節生成一張，命名規則：`bg_00_opening.png`、`bg_01_xxx.png`…

---

#### 🎨 背景圖生成原則（2026-03-16 定版）

**風格方向：**
- ✅ 溫暖色調：amber（琥珀）、gold（金）、warm orange（暖橙）、ochre（赭黃）、warm teal（暖青）
- ✅ 插畫/油畫質感：painterly, illustrated digital art（非寫實暗黑賽博龐克）
- ✅ 每張圖凸顯該章節的**核心視覺比喻**（鑰匙、裂縫、網絡、金庫…）
- ❌ 禁止純白或亮色大面積背景（字幕無法顯示）
- ❌ 禁止含有任何文字

**字幕可讀性規則（關鍵）：**
- 底部 1/3 必須保持**深色**（深棕、深藍、深褐、近黑）
- 主要視覺元素集中在**畫面中上部**
- 白色字幕 + 黑色邊框在這樣的底色下一定清楚

**Prompt 模板：**
```
{具體視覺描述（主體 + 動作/狀態）}, {色調：warm amber and gold tones / warm orange glow},
painterly digital illustration style, {補充細節},
dark {color} shadow at bottom third, no text, 4K
```

**各類章節對應視覺比喻（參考）：**
| 章節類型 | 建議視覺比喻 |
|----------|------------|
| 開場/鉤子 | 象徵性物件（鑰匙、門、鏡子）浮在暮色城市上空 |
| 技術漏洞 | 放大鏡 + 裂縫電路、破碎的盾牌 |
| AI 攻擊/自動化 | 光網連接全球節點、指揮中心俯視圖 |
| 財務損失 | 金庫破裂、硬幣崩落 |
| 品牌/工具 | 品牌吉祥物或工具圖示在聚光燈下 |
| 世界/社會影響 | 城市俯瞰、基礎設施網絡、局部熄燈 |

---

### Step 2｜解析章節時間點

從腳本字元位置估算章節時間（以音訊總秒數為基準）：

```python
import subprocess, re

# 取得音訊總長
result = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration',
                         '-of','csv=p=0','audio.mp3'], capture_output=True, text=True)
total_dur = float(result.stdout.strip())

# 找各章節在腳本中的位置 → 換算時間
script = open('script_clean.txt').read()
for keyword, chapter_name in chapters:
    idx = script.find(keyword)
    t = (idx / len(script)) * total_dur
```

---

### Step 3｜智能字幕斷句

> ⚠️ **Edge TTS 輸出整句一條，不斷句，遇到長句 FontSize=38 會換行到中間。**
> 必須先執行斷句，再燒入影片。

```bash
python3 /home/jovie/.openclaw/workspace/split_srt.py \
  subtitles.srt \
  subtitles_split.srt \
  --max-width 54
```

**斷句規則（依優先序）：**
1. 中文標點後斷（，。；！？…）
2. 中英文邊界空格處斷
3. **英文單字群保持完整**（不切斷 "Dwarkesh Patel"）
4. 視覺寬度上限 54（中文字 =2 寬度，ASCII =1）
5. 移除標點符號（顯示更乾淨）— **問號（？?）除外，保留**

---

### Step 4｜Ken Burns 影片片段

> ✅ **唯一正確寫法：`scale(t) + crop eval=frame`**（連續時間戳，完全平滑）

**效果：1.0× → 1.2× → 1.0× 循環，30 秒一個完整循環**

```bash
# ✅ 正確 Ken Burns 濾鏡（三角波循環公式）
# zoom = 1.0 + 0.2 × (1 - |2×(t mod 30)/30 - 1|)
KB_FILTER="scale=w='1280*(1+0.2*(1-abs(2*mod(t,30)/30-1)))':h='720*(1+0.2*(1-abs(2*mod(t,30)/30-1)))':eval=frame,crop=1280:720,format=yuv420p"

# 每章節套用（每張背景圖都要）
ffmpeg -y -loop 1 -i bg_00_opening.png -t {秒數} -r 24 \
  -vf "$KB_FILTER" \
  -c:v libx264 -pix_fmt yuv420p -r 24 seg_00_opening.mp4
```

**關鍵時間點：**
```
t=  0s → 1.0× (起始)
t=7.5s → 1.1×
t= 15s → 1.2× (最大)
t=22.5s → 1.1×
t= 30s → 1.0× (回到起點，開始下一循環)
```

長章節（>30s）會自動循環；短章節（<30s）走部分循環亦可。

---

### 🚫 Ken Burns 禁止寫法（三種，都會造成抖動）

#### ❌ 禁止 1：`zoompan` 濾鏡
```bash
# ❌ 絕對禁止
-vf "zoompan=z='zoom+0.001':d=25:s=1280x720"
```
原因：逐幀離散整數計算，天生抖動，無法平滑。

#### ❌ 禁止 2：先 scale 放大到固定尺寸，再用 crop 移動位置
```bash
# ❌ 絕對禁止（看起來像 Ken Burns，實際上是「位置移動」不是「縮放」）
-vf "scale=2560:1472, crop=1280:720:'(iw-1280)/2*(1+0.2*sin(2*3.14*t/30))':'(ih-720)/2'"
```
原因：影像是固定放大的，`crop` 偏移量用三角函數控制，結果是**鏡頭在平移**，不是平滑縮放，會產生位移抖動感。

#### ❌ 禁止 3：`eval=init`（每段只算一次）
```bash
# ❌ 禁止：eval=init 讓縮放值只在開頭計算一次，整段固定比例，沒有 Ken Burns 效果
"scale=w='...':h='...':eval=init"
```
原因：`eval=frame` 才會每幀重新計算 `t`，產生連續動態縮放。

---

### ✅ Python 腳本中的正確寫法（複製貼上用）

```python
# Ken Burns vf — 複製貼上，不要自己改公式
KB_VF = (
    "scale=w='1280*(1+0.2*(1-abs(2*mod(t,30)/30-1)))':"
    "h='720*(1+0.2*(1-abs(2*mod(t,30)/30-1)))':"
    "eval=frame,"
    "crop=1280:720,"
    "format=yuv420p,"
    "fps=24"
)

subprocess.run([
    "ffmpeg", "-y", "-loop", "1", "-i", str(img),
    "-t", str(dur), "-r", "24",
    "-vf", KB_VF,
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-preset", "veryfast",
    str(out)
], check=True, capture_output=True)
```

---

### Step 5｜合併片段 + 加音訊

```bash
# 產生 concat.txt
cat > concat.txt << EOF
file '/tmp/{影片名}/video/seg_00_opening.mp4'
file '/tmp/{影片名}/video/seg_01_xxx.mp4'
...
EOF

# 合併純視訊
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video_raw.mp4

# 加入音訊
ffmpeg -y -i video_raw.mp4 -i audio.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -shortest \
  video_with_audio.mp4
```

---

### Step 6｜燒入字幕 + 章節標題

```bash
FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc

# 章節小標題（右上角，黑底半透明框）
DT0="drawtext=fontfile=${FONT}:text='開場':fontsize=28:fontcolor=white:x=w-tw-30:y=30:box=1:boxcolor=0x00000080:boxborderw=12:enable='between(t,0,XX.XXX)'"
DT1="drawtext=fontfile=${FONT}:text='01 章節名':fontsize=28:fontcolor=white:x=w-tw-30:y=30:box=1:boxcolor=0x00000080:boxborderw=12:enable='between(t,XX.XXX,YY.YYY)'"
# ...每章節一條...

# 主字幕（底部，FontSize=38，最多3行）
SUBS="subtitles=/絕對路徑/subtitles_split.srt:force_style='Alignment=2,MarginV=40,MarginL=60,MarginR=60,FontSize=38,FontName=Noto Sans CJK TC,PrimaryColour=&H00FFFFFF,Bold=1,Outline=3,OutlineColour=&H00000000,Shadow=0,BorderStyle=1'"

ffmpeg -y -i video_with_audio.mp4 \
  -vf "${DT0},${DT1},...,${SUBS}" \
  -c:v libx264 -c:a copy with_subs.mp4
```

> ⚠️ subtitles 路徑必須是**絕對路徑**

**字幕規格（固定）：**
| 參數 | 值 |
|------|-----|
| FontSize | **38** |
| Alignment | 2（底部水平置中）|
| MarginV | 40 |
| MarginL/R | 60 |
| Bold | 1 |
| Outline | 3（黑色邊框）|
| 最大視覺寬度 | 54（約 27 個中文字，最多 3 行）|

---

### Step 7｜加片尾 Logo（含原始音效）

> ⚠️ **必須用 `filter_complex concat`，禁止用 `-f concat -c copy`**
> 後者會造成音訊時間軸 2 倍長 bug

```bash
LOGO=/home/jovie/.openclaw/workspace/94ivoice_logo_outro.mp4

# Logo 先 re-encode 統一格式
ffmpeg -y -i "$LOGO" \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -pix_fmt yuv420p -r 24 -c:a aac logo_scaled.mp4

# 合併主影片 + Logo
ffmpeg -y \
  -i with_subs.mp4 \
  -i logo_scaled.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" \
  -c:v libx264 -c:a aac \
  {影片名}_stage.mp4
```

---

### Step 2.5｜94iVoice 單口播客文案設計風格

> 適用：腳本撰寫（Step 2）與 YouTube 描述（Step 7.5）  
> 分析基礎：vampire（最佳範本）/ dankoe / anthropic_dod 三支腳本對照

---

#### 🎯 目標語感

**像一個讀了很多書、但說話很直的朋友**，在你通勤路上把一件你沒空研究的事情說清楚。  
不是老師在上課，不是記者在播報，不是顧問在簡報——是朋友在聊天。

---

#### 🎙 有 Speaker 時的語感模式（2026-03-16 定版）

> 當來源影片有具體 Speaker 時，**主角是 Speaker，播客是翻譯者/朋友**。

**核心語感轉換：**

| ❌ 播客自己說 | ✅ 轉達 Speaker 說 |
|------------|-----------------|
| 「AI 現在可以自動入侵企業」 | 「Dr. Waku 說，AI 現在已經可以自動入侵企業了」 |
| 「我認為這件事很重要」 | 「他說，這件事讓整個資安圈都嚇到了」 |
| 「我整理了三個重點」 | 「他在影片裡提了三件事，我覺得每一件都值得說清楚」 |

**三種歸因句式（自然輪換，不要每句都一樣）：**
- 直接歸因：「Dr. Waku 說...」「他說...」「他提到...」
- 間接歸因：「根據他的分析...」「他的觀察是...」「他舉了一個例子...」
- 評論歸因：「他說了一句話我覺得很有意思——」「他的結論是...，這讓我想到...」

**細節轉換原則：**
- 技術術語 → 生活比喻（zero-day = 「軟體廠商自己還不知道的漏洞，就像鎖還沒壞但鑰匙已經在賊手上」）
- 統計數字 → 具體感受（「80-90% 全自動」= 「駭客只要選好目標按確認，其他 AI 全部包辦」）
- 抽象概念 → 場景描述（「攻防不對等」= 「防守的人要每一球都守住，攻擊的人只需要進一球」）

**播客定位（有 Speaker 時）：**
> 我不是專家，我是替你把專家說的東西翻成人話的那個朋友。

---

#### ✅ 腳本結構公式

**無 Speaker（原創/評論型）：**
```
[開頭：鉤子場景（你的日常 + 反直覺觀察）]
  ↓
[第1-2章：問題定義 + 背景]
  ↓
[第3-4章：影響深化（具體例子）]
  ↓
[第5章：核心洞察]
  ↓
[結尾：行動號召]
```

**有 Speaker（轉述/解析型）：**
```
[開頭：衝擊鉤子 → Speaker 是誰 → 他談了哪些精彩主題 → 我來整理]
  ↓
[依 Speaker 原始結構走，每個重點都歸因給 Speaker]
  ↓
[穿插播客自己的翻譯/感想（「這讓我想到...」「用台灣的角度來說...」）]
  ↓
[結尾：總結 Speaker 的核心觀點 + CTA]
```

---

#### 🟢 開頭公式（4 種）

> ⚠️ **2026-03-16 新增規則：開場必須介紹來源 Speaker 的精彩主題**
> 當來源影片有具體 Speaker 時，開場第一段要：
> 1. 先用鉤子抓住注意力（衝擊數字或場景）
> 2. 點出「這個人是誰、他談了什麼精彩主題」
> 3. 用「我整理了他的核心觀點，重點說給你聽」作為橋接
>
> 範例：「[衝擊鉤子]… Dr. Waku 是 AI 安全研究員，他這支影片談的是 [精彩主題1]、[精彩主題2]，還有 [主題3]。我把他說的重點整理好了，今天帶你在七分鐘內搞懂這件事。」

**A. 來源 Speaker 介紹（有具體人物時優先用）**（2026-03-16 新增）
> 「[衝擊事件/數字]。說這話的是 [Speaker 名字]，[一句話介紹身份]。
> 他在這支影片裡談到了 [精彩主題1]、[精彩主題2]，還有 [主題3]。
> 我把重點整理好了，[X] 分鐘說清楚。」

**B. 你的行為映射（最強，無具體人物時用）**
> 「你上次完整看完一支15分鐘教學影片，是什麼時候？」  
> 「你有沒有注意到，你最近問AI的次數，比問Google多了？」

**C. 反直覺陳述**
> 「你可以請AI幫你摘要這支影片——但你沒有。這個選擇本身就是今天的答案。」

**D. 數字/事件衝擊**
> 「Stack Overflow在2024年裁員。原因不是公司經營不善——是因為工程師不再需要它了。」

❌ **禁用開頭**：
- 「大家好，歡迎收聽94iVoice播客。今天我們要聊聊...」（太公式化）
- 「在這個數位化和科技驅動的時代...」（學術腔）
- 「本集我們將深入探討...」（念稿感）

✅ **品牌入場時機**：在鉤子之後（第2-3句），不在第一句：
> 「[鉤子]……這就是今天94iVoice要談的主題。」

---

#### 🟢 句子節奏原則（音頻最重要）

| 用途 | 建議長度 | 例子 |
|------|---------|------|
| 關鍵論點 | 10–20 字 | 「AI的進步，是以月為單位。」|
| 解釋說明 | 20–35 字 | 「Stack Overflow的工程師流量大幅下滑，因為開發者直接問AI就好了。」|
| 場景鋪陳 | 最多 45 字 | 長句拆成兩句說，中間加停頓 |

❌ **禁用句式**：
- 「不僅僅…更是…」（過度使用）
- 「這不僅僅是一場技術革命，更是一場社會、政治和倫理的挑戰。」（empty rhetoric）
- 「深思問題：」「我們需要思考...」（像作業，不像對話）
- 「接著，」「首先，其次，最後」（條列感，不是播客感）

---

#### 🟢 具體例子原則（vampire 的強項）

每個抽象觀點，配一個**可感知的具體場景**：

| 抽象觀點 | 具體例子（好） |
|---------|--------------|
| AI衝擊創作者 | Stack Overflow 裁員、新聞媒體廣告消失、插畫師委託量驟減 |
| 職場影響 | 行銷企劃在薪資談判時，老闆心裡有AI的參照點 |
| 知識簽名 | 兩個人讀同一本書，畫線的地方完全不同 |
| 後現代虛無 | 你刷手機30分鐘，沒有進步，也沒有連結 |

**例子選取優先序**：  
1. 台灣/亞洲日常（最有共鳴）  
2. 全球知名案例（Stack Overflow、Reddit、Elon Musk）  
3. 虛構但真實感的場景（「假設你是行銷企劃...」）

---

#### 🟢 章節收尾 + 過渡

每章結尾要有「橋」，帶出下一章：

```
❌ 直接結束：「這些，都是吸血鬼效應的直接受害者。」（硬切）

✅ 加橋：「這些是內容創作者的傷亡，但真正讓我擔心的，
   是那些根本沒意識到自己已經被吸的人——那就是職場上的我們。」
   （自然導向下一章「你的工作也在被吸」）
```

---

#### 🟢 主持人聲音（Personal Voice）

偶爾加入主持人的感受或立場，讓聽眾感受到是真人在說：

- 「說真的，第一次看到這個數字，我也愣了一下。」
- 「這裡有個地方我覺得很有意思——」
- 「你可能會想說：好，那又怎樣？」（預設聽眾問題）

---

#### 🟢 結尾公式

```
[一句話收尾論點] + [具體行動建議] + [固定結尾語]
```

**固定結尾語（每集統一使用）：**
> 「AI在改變世界，我們一起慢慢搞懂它。下次見。」

✅ 好例子：
「金絲雀還在唱歌，提醒我們採取行動。
 如果你覺得今天有幫助，分享給一個你覺得需要聽這些的朋友。
 AI在改變世界，我們一起慢慢搞懂它。下次見。」

❌ 禁用：
「希望你能以獨特的行動，開創一個屬於自己的意義世界。」（空泛）
「讓我們繼續保持開放的心態和批判的思維...未來在我們手中」（政府宣傳感）
「我們下次再見！」加驚嘆號（太刻意活潑）

---

#### 📐 腳本長度參考

| 目標時長 | 腳本字數 |
|---------|---------|
| 3–4 分鐘 | 650–850 字 |
| 5–7 分鐘 | 1,050–1,450 字 |
| 8–10 分鐘 | 1,650–2,100 字 |

> 中文 TTS（YunjianNeural +10%）約 **200–220 字/分鐘**

---

#### 📢 YouTube 標題設計規則

```
格式一（有數字）：「X件事／X個原因」+ 結果
  例：AI複製不了的5件事，你的護城河在這裡

格式二（問句）：直接問出觀眾心中的疑惑
  例：AI吸血鬼效應：正在吸走你的工作與收入？

格式三（強烈陳述）：反直覺 or 衝突感
  例：Anthropic 拒絕了國防部——這才是真正的警訊

規則：
- 60 字以內
- 含主題關鍵字（AI、科技、工作、未來…）
- 不加「94iVoice｜」前綴（除非系列化）
- 避免點擊農場式誇大（「震驚」「不得不看」）
```

#### 📝 YouTube 描述結構（固定模板）

```
（1-2 句摘要，直接說本集在講什麼，口語化）

🔑 本集重點：
1. （第一章核心觀點，一句話）
2. （第二章）
...

📌 時間章節：
00:00 [開頭章節]
MM:SS [章節名]
...（對應實際影片時間，不能亂填）

📺 原始來源：
[原作者] — [原始影片標題]
[原始影片 URL]

🔗 相關參考：
• [作者官網或頻道]
• [相關延伸資源]

🎙 94iVoice — AI 與科技深度解析
歡迎訂閱 → https://www.youtube.com/@94ivoice

#主題1 #主題2 #94iVoice
```

> ⚠️ 原始來源為英文時，必須附上原始影片連結；Stage 頁面連結不放入 YouTube 描述

#### 🏷️ 標籤選取原則

- 8–15 個標籤，中文為主
- 必包含：`94iVoice`、`AI`、`科技`
- 加入影片核心概念詞（護城河、吸血鬼效應、後勞動時代…）
- 不加過度通用詞（播客、Podcast → 優先級低）

---

### Step 7.5｜生成 YouTube 發布文案

```python
from openai import OpenAI
import json
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"""根據以下播客腳本，輸出 JSON：
{{
  "title": "YouTube標題（60字內，有關鍵字，吸引人）",
  "description": "描述（300字，含重點3-5條、章節時間碼、訂閱呼籲）",
  "tags": ["標籤1",...],  // 10-15個，中英文混合
  "category": "Science & Technology"
}}
腳本：{script[:2000]}"""}]
)
meta = json.loads(resp.choices[0].message.content.strip().strip('```json').strip('```'))
json.dump(meta, open('youtube_meta.json','w'), ensure_ascii=False, indent=2)
```

**預設發布設定：**
- 隱私：🔒 **私人**（審閱後再改公開）
- 頻道：愛播客（UC3rJy84_9aDSovvJ0Xw0bfQ）

---


### Step 7.6｜設計 YouTube 封面（Thumbnail）

**封面規格：** 1280×720 · JPEG · 95% quality

**參考範例：** `workspace/thumbnail_reference_elon.jpg`（Elon Musk 版，標準風格）

**生成腳本：** `workspace/make_thumbnail.py`（v8，2026-03-15 定版）

```bash
python3 ~/workspace/make_thumbnail.py \
  --photo  person.jpg \           # 人物照片或 DALL-E 概念圖
  --name   "SPEAKER NAME" \       # ⚠️ 有具體人物時才填；概念型影片省略（不顯示名字區塊）
  --big    "10" \                 # 大字（max 160px，自動縮小至符合寬度）
  --big-suffix "年後" \           # 大字右側的中字（~80px，自動對齊）
  --main   "經濟翻" \              # 主標白色部分
  --main-accent "10倍" \          # 主標黃色強調部分（自動縮放）
  --sub    "但金錢會失去意義" \     # 副標（淡紫）
  --duration "9 分鐘精華解析" \    # 時長（琥珀色）
  --output thumbnail.jpg
```

---

#### 版面結構（固定）

```
┌─────────────────────────┬─────────────────┐
│  LEFT 3/5（0~768px）    │  RIGHT 2/5      │
│  純紫漸層背景           │  (768~1280px)   │
│                         │  人物照片        │
│  [NAME]                 │  512×720        │
│  ── 粉底線              │  填滿，臉部      │
│  [BIG 160px] [SUFFIX]   │  完整顯示        │
│  [MAIN] [ACCENT yellow] │                 │
│  ── 紫底線              │                 │
│  [SUB 淡紫]             │                 │
│  [DURATION 琥珀]        │                 │
└─────────────────────────┴─────────────────┘
```

**過渡處理（關鍵）：**
- 照片從 x=768 開始，左緣 110px cosine ease 漸層透出紫色背景
- 無任何分割線 — 過渡完全由照片的 alpha mask 控制
- 結果：左側看不到照片（純紫+文字），右側完整人物特寫

---

#### 精確設計規格

| 元素 | 規格 |
|------|------|
| 左側背景 | 深紫 #120226 → 亮紫 #370A5A（漸層至 x=768）|
| 照片區 | x=768~1280，512×720，臉部完整顯示 |
| 照片裁切 | 人像：寬=512px 縮放，取頂部（臉）；橫式：高=720px 縮放，取右側 |
| 過渡融合 | 照片左緣 110px cosine fade（無硬邊、無暗條）|
| 名字 | 白色，max 56px，自動縮至符合寬度，粉紅底線 #FF567E |
| 大字 | **max 160px 白色**，自動縮，右側接中字（約大字 50% 大小）|
| 主標 | 白色 ~74px + **黃色強調 #FFB500** ~94px，紫色底線 #7D3CF0 |
| 副標 | 淡紫 #D2CDFF，~46px，自動縮 |
| 時長 | 琥珀 #FF9B00，28px |
| 右側 | 無任何 Logo 或文字（保留人物完整呈現）|

---

#### Speaker 自動識別規則（Step 10 前必須執行）

> ⚠️ 每支影片製作時，**必須先判斷 Speaker**，再決定封面設計方式。

**判斷流程：**
1. 從 yt-dlp metadata 取得頻道名稱（`channel` 欄位）
2. 若頻道名稱是個人名稱（非機構/媒體）→ 視為 Speaker，需取得照片
3. 若是機構頻道（CNN, TED, Lex Fridman Podcast 等）→ 從影片本身找 Speaker

**Speaker 照片取得優先順序：**

1. **YouTube 頻道頭像**（最快最準）
   ```python
   import requests, re
   from PIL import Image
   import io

   headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
   r = requests.get(f"https://www.youtube.com/watch?v={VIDEO_ID}", headers=headers, timeout=15)
   # 找最高解析度頻道頭像
   urls = re.findall(r'https://yt3\.ggpht\.com/[A-Za-z0-9_\-]+=s\d+[^"\'<>\s]*', r.text)
   # 取 s800 或最大尺寸
   avatar_base = urls[0].split('=s')[0] if urls else None
   if avatar_base:
       r2 = requests.get(avatar_base + "=s800-c-k-c0x00ffffff-no-rj", headers=headers)
       img = Image.open(io.BytesIO(r2.content))
       img.save("speaker_photo.jpg", quality=95)
   ```

2. **Wikipedia Commons**（有維基條目的知名人士）
   ```python
   r = requests.get(f"https://en.wikipedia.org/wiki/{人名}",
       headers={"User-Agent": "Mozilla/5.0"})
   imgs = re.findall(r'//upload\.wikimedia\.org[^\s"\'<>]+(?:jpg|jpeg|png)', r.text)
   ```

3. **YouTube 影片縮圖裁切**（頭像取不到時的備用方案）
   ```python
   vid = "{VIDEO_ID}"
   r = requests.get(f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg")
   img = Image.open(io.BytesIO(r.content))
   w, h = img.size
   face = img.crop((w // 2, 0, w, h))
   face.save("speaker_photo.jpg", quality=95)
   ```

4. **無人物時** → 使用 DALL-E 3 背景圖作為右側圖（`bg_02.png` 等），省略 `--name`

> 💡 **Dr. Waku 案例**（2026-03-16）：YouTube 頻道頭像方案成功，取得 800×800 清晰人像。Wikipedia 無條目，不適用。

#### 照片填充規則（make_thumbnail.py）

> `make_thumbnail.py` 使用 **fill 模式**（2026-03-16 更新）

- 人像/概念圖不論比例，**一律填滿右側面板（512×720），無黑邊**
- 縮放取 `max(scale_w, scale_h)` 確保完整覆蓋
- 裁切：水平置中，垂直偏上（臉部優先）

**封面輸出路徑：** `stage/{影片名}/thumbnail.jpg`

---

### Step 8｜建立預覽頁面（Stage Preview）

> 標準參考：`/tmp/stage_repo/dankoe/index.html`（最新完整版本，2026-03-16）  
> Stage URL：`https://i94ivoice-glitch.github.io/stage/{project}/`

---

#### CSS 設計系統（完整規格）

```css
/* 全域 */
* { box-sizing: border-box; }
body { font-family: -apple-system, sans-serif; background: #0f0f0f; color: #eee; margin: 0; padding: 20px; }
.container { max-width: 960px; margin: 0 auto; }

/* 頁首 */
h1 { font-size: 1.4em; color: #fff; border-bottom: 2px solid #222; padding-bottom: 12px; margin-bottom: 24px; }

/* 狀態 Badge */
.badge { font-size: 0.68em; padding: 3px 8px; border-radius: 4px; vertical-align: middle; margin-left: 8px; font-weight: 600; }
.badge.stage  { background: #e63946; color: white; }          /* 審閱中 */
.badge.private { background: #f4a261; color: #111; }          /* 私人已上傳 */
.badge.live   { background: #22c55e; color: #fff; }           /* 已公開 */

/* Section */
.section { margin: 32px 0; }
.section-title {
  font-size: 0.75em; color: #555; text-transform: uppercase;
  letter-spacing: 1.8px; margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}
.section-title::after { content: ''; flex: 1; height: 1px; background: #222; }

/* Chip（小標籤）*/
.chip { background: #1e1e1e; border: 1px solid #2a2a2a; padding: 4px 12px; border-radius: 20px; font-size: 0.78em; color: #999; }
.video-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }

/* 影片 */
video { width: 100%; border-radius: 10px; background: #000; display: block; }

/* 來源卡片 */
.source-card { background: #141414; border: 1px solid #222; border-radius: 10px; padding: 16px; }
.source-card a { color: #4ea8de; text-decoration: none; font-size: 0.95em; font-weight: 500; }

/* 章節背景圖 Grid */
.chapter-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
@media (max-width: 600px) { .chapter-grid { grid-template-columns: repeat(2, 1fr); } }
.chapter-card { background: #141414; border: 1px solid #222; border-radius: 10px; overflow: hidden; }
.chapter-card img { width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; }
.chapter-info { padding: 10px 12px; }
.chapter-num   { font-size: 0.68em; color: #555; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }
.chapter-title { font-size: 0.82em; color: #ccc; margin-top: 3px; line-height: 1.4; }
.chapter-dur   { font-size: 0.72em; color: #555; margin-top: 4px; }

/* 素材檔案 Grid */
.files { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px; }
.files a { display: block; padding: 10px 14px; background: #141414; border: 1px solid #222; border-radius: 8px; color: #4ea8de; text-decoration: none; font-size: 0.85em; }

/* 腳本區塊 */
.script-block { background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 10px; padding: 20px; line-height: 1.9; font-size: 0.88em; color: #ccc; white-space: pre-wrap; max-height: 500px; overflow-y: auto; }
.copy-btn { margin-top: 10px; padding: 7px 16px; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; color: #aaa; font-size: 0.8em; cursor: pointer; }

/* YouTube 區塊 */
.yt-section { background: #141414; border: 1px solid #222; border-radius: 12px; padding: 24px; }
.yt-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.yt-logo { color: #ff0000; font-size: 1.5em; }
.yt-header h2 { margin: 0; font-size: 1em; color: #fff; font-weight: 600; }
.yt-pill { font-size: 0.75em; padding: 3px 10px; border-radius: 20px; margin-left: auto; }
.yt-pill.pending  { background: #2a2015; color: #f4a261; border: 1px solid #3a3020; }  /* ⏳ 待審閱 */
.yt-pill.private  { background: #1a1a2a; color: #93c5fd; border: 1px solid #2a2a4a; }  /* 🔒 私人 */
.yt-pill.public   { background: #052e16; color: #22c55e; border: 1px solid #14532d; }  /* ✅ 公開 */
.yt-field { margin-bottom: 16px; }
.yt-field label { display: block; font-size: 0.72em; color: #666; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1.2px; }
.yt-field .val { background: #0d0d0d; border: 1px solid #222; border-radius: 6px; padding: 10px 14px; font-size: 0.88em; color: #ddd; line-height: 1.7; white-space: pre-wrap; }
.yt-field .val.title-val { font-size: 1em; font-weight: 600; color: #fff; }
.yt-tags { display: flex; flex-wrap: wrap; gap: 6px; padding: 10px 14px; background: #0d0d0d; border: 1px solid #222; border-radius: 6px; }
.yt-tag { background: #1e1e1e; padding: 3px 10px; border-radius: 20px; font-size: 0.75em; color: #bbb; }
.yt-actions { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
.yt-btn { padding: 10px 20px; border-radius: 8px; border: none; font-size: 0.88em; cursor: pointer; font-weight: 600; }
.yt-btn.primary   { background: #ff0000; color: white; }
.yt-btn.secondary { background: #1e1e1e; color: #888; border: 1px solid #2a2a2a; }
.yt-note { font-size: 0.76em; color: #444; margin-top: 10px; }

/* 逐字稿按鈕（來源區，英文來源專用）*/
.transcript-btn {
  display: inline-block; padding: 7px 16px; background: #1e1e1e;
  border: 1px solid #2a2a2a; border-radius: 6px; text-decoration: none; font-size: 0.82em; margin-right: 8px;
}
.transcript-btn.en { color: #a0c4ff; }
.transcript-btn.zh { color: #86efac; }

/* 頁尾 */
.meta { font-size: 0.75em; color: #3a3a3a; margin-top: 40px; border-top: 1px solid #1a1a1a; padding-top: 12px; }
.meta a { color: #555; text-decoration: none; }
```

---

#### 必要區塊（按順序，缺一不可）

**⓪ 返回 Stage 索引（頁面最頂部，H1 之前）**
```html
<div style="margin-bottom:20px;">
  <a href="../" style="color:#555;text-decoration:none;font-size:0.82em;
     display:inline-flex;align-items:center;gap:6px;padding:6px 12px;
     background:#141414;border:1px solid #222;border-radius:6px;">
    ← Stage 索引
  </a>
</div>
```
> 每個 preview 頁面都必須有，方便從各影片頁回到索引總覽。

**① 頁首 H1 + 狀態 Badge**
```html
<h1>影片標題 <span class="badge stage">Stage 審閱中</span></h1>
<!-- 私人：<span class="badge private">🔒 已上傳（私人）</span> -->
<!-- 公開：<span class="badge live">✅ 已公開</span> -->
```

**② 🎬 Stage 影片播放器**
```html
<div class="section">
  <div class="section-title">🎬 Stage 影片</div>
  <video controls preload="metadata" poster="thumbnail.jpg">
    <source src="{影片名}_stage.mp4" type="video/mp4">
    <track kind="subtitles" src="subtitles_split.srt" srclang="zh" label="中文字幕" default>
  </video>
  <div class="video-meta">
    <span class="chip">⏱ 約 X 分鐘</span>
    <span class="chip">🎙 YunjianNeural +10%</span>
    <span class="chip">🖼 DALL-E 3 × 6</span>
    <span class="chip">📝 FontSize 44</span>
    <span class="chip">🎬 Logo 片尾 v2</span>
  </div>
</div>
```

**③ 📺 原始來源**
```html
<div class="section">
  <div class="section-title">📺 原始影片</div>
  <div class="source-card">
    <a href="{原始URL}" target="_blank">▶ {影片標題} — {頻道名}</a>
    <div class="video-meta" style="margin-top:10px;">
      <span class="chip">⏱ {時長}</span>
      <span class="chip">🎙 {頻道}</span>
      <span class="chip">📅 {日期}</span>
      <span class="chip">👁 {觀看數}</span>
    </div>
    <!-- 英文來源才加以下兩個按鈕 -->
    <div style="margin-top:12px;">
      <a href="transcript_en.txt" target="_blank" class="transcript-btn en">📄 英文逐字稿（X,XXX words）</a>
      <a href="transcript_zh.txt" target="_blank" class="transcript-btn zh">📄 繁體中文逐字稿</a>
    </div>
  </div>
</div>
```

**④ 🖼 章節背景圖**
```html
<div class="chapter-grid">
  <div class="chapter-card">
    <img src="bg_00.png" alt="章節名" loading="lazy">
    <div class="chapter-info">
      <div class="chapter-num">00 · 開場</div>
      <div class="chapter-title">章節標題</div>
      <div class="chapter-dur">0:00 → ~X:XX</div>
    </div>
  </div>
  <!-- bg_01 ~ bg_05 同樣格式 -->
</div>
```
> 章節時間範圍：用實際音頻時長 ÷ 6 估算，格式 `M:SS → ~M:SS`

**⑤ 🖼 YouTube 封面（2欄佈局）**
```html
<div style="display:grid; grid-template-columns:1.6fr 1fr; gap:20px; align-items:start;">
  <div>
    <a href="thumbnail.jpg" target="_blank">
      <img src="thumbnail.jpg" style="width:100%;border-radius:8px;border:1px solid #2a2a2a;" alt="Thumbnail">
    </a>
    <div class="video-meta" style="margin-top:8px;">
      <span class="chip">📐 1280×720</span>
      <span class="chip">🎨 深紫漸層</span>
      <!-- 有真人照片：<span class="chip">📸 {照片來源}</span> -->
      <!-- DALL-E概念圖：<span class="chip">🤖 DALL-E 3 概念圖</span> -->
    </div>
    <a href="thumbnail.jpg" download="94ivoice_{影片名}_thumbnail.jpg"
       style="display:inline-block;margin-top:10px;padding:8px 18px;background:#1e1e1e;border:1px solid #333;border-radius:6px;color:#aaa;text-decoration:none;font-size:0.82em;">
      ⬇ 下載封面
    </a>
  </div>
  <div style="background:#111;border:1px solid #222;border-radius:10px;padding:18px;font-size:0.82em;line-height:2;">
    <div style="color:#555;font-size:0.72em;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;">設計說明</div>
    <div><span style="color:#555;">背景</span> 深紫→黑漸層</div>
    <div><span style="color:#555;">照片</span> {照片來源說明}</div>
    <div><span style="color:#555;">大標</span> <span style="color:#fff;font-weight:700;">{大標文字}</span></div>
    <div><span style="color:#555;">強調</span> <span style="color:#FFD700;font-weight:700;">{強調文字}</span></div>
    <div><span style="color:#555;">副標</span> {副標文字}</div>
    <div><span style="color:#555;">Speaker</span> {姓名 or「無（概念型）」}</div>
  </div>
</div>
```

**⑥ ✍️ 中文腳本（動態載入）**
```html
<div class="script-block" id="scriptContent">載入中...</div>
<button class="copy-btn"
  onclick="navigator.clipboard.writeText(document.getElementById('scriptContent').textContent)">
  📋 複製腳本
</button>

<script>
fetch('script_zh.txt').then(r=>r.text()).then(t=>{
  document.getElementById('scriptContent').textContent = t;
}).catch(()=>{
  document.getElementById('scriptContent').textContent = '（腳本載入失敗）';
});
</script>
```

**⑦ 📁 素材檔案（固定順序）**
```html
<div class="files">
  <a href="script_zh.txt">✍️ 播客腳本（中文）</a>
  <a href="transcript_en.txt">📄 逐字稿（英文）</a>       <!-- 英文來源才顯示 -->
  <a href="transcript_zh.txt">📄 逐字稿（繁體中文）</a>   <!-- 英文來源才顯示 -->
  <a href="subtitles_split.srt">✂️ 字幕 SRT（斷句版）</a>
  <a href="youtube_meta.json">📋 YouTube 文案 JSON</a>
  <a href="thumbnail.jpg" download>🖼 封面圖</a>
  <a href="{影片名}_stage.mp4">🎬 影片檔案</a>
</div>
```

**⑧ 📺 YouTube 發布設定**
```html
<div class="yt-section">
  <div class="yt-header">
    <span class="yt-logo">▶</span>
    <h2>愛播客 — YouTube 發布文案</h2>
    <span class="yt-pill pending">⏳ 待審閱發布</span>
    <!-- 私人：<span class="yt-pill private">🔒 已上傳（私人）</span> -->
    <!-- 公開：<span class="yt-pill public">✅ 已公開發布</span> -->
  </div>

  <div class="yt-field">
    <label>影片標題</label>
    <div class="val title-val">{標題}</div>
  </div>

  <div class="yt-field">
    <label>影片描述</label>
    <div class="val" id="ytDesc">{完整描述，含🔑重點+📌章節時間碼+🎙訂閱CTA+hashtag}</div>
  </div>

  <div class="yt-field">
    <label>標籤</label>
    <div class="yt-tags">
      <span class="yt-tag">94iVoice</span>
      <!-- ... 其他標籤 ... -->
    </div>
  </div>

  <div class="yt-field">
    <label>類別 / 隱私</label>
    <div class="val">科技與科學（Science &amp; Technology）｜🔒 私人（審閱後改公開）</div>
  </div>

  <div class="yt-actions">
    <button class="yt-btn primary"
      onclick="navigator.clipboard.writeText(document.getElementById('ytDesc').innerText)">
      📋 複製描述
    </button>
    <div class="yt-btn secondary">🔒 發布前請先審閱</div>
    <!-- 已發布時改為：<a href="https://youtu.be/{ID}" class="yt-btn primary" target="_blank">▶ 觀看影片</a> -->
  </div>
  <div class="yt-note">⚠️ 發布時請告知 Javis 執行上傳（記得設 --private）</div>
</div>
```

**⑨ 頁尾（含 timestamp JS）**
```html
<div class="meta">
  94iVoice Stage Preview · 原始來源：<a href="{原始URL}" style="color:#3a5a7a">{來源說明}</a> ·
  <span id="ts"></span>
  <script>document.getElementById('ts').textContent = new Date().toLocaleString('zh-TW')</script>
</div>
```

#### Stage Repo 目錄結構（含逐字稿）

```
stage/{影片名}/
  index.html               ← 預覽頁
  {影片名}_stage.mp4       ← 影片
  bg_00.png ～ bg_05.png   ← 章節背景圖（1024×1024 原圖）
  bg_00_hd.png ～ ...      ← 1280×720 縮放版（可選）
  thumbnail.jpg            ← YouTube 封面
  script_zh.txt            ← 中文腳本
  subtitles_split.srt      ← 斷句字幕
  youtube_meta.json        ← YouTube 文案
  transcript_en.txt        ← 英文逐字稿（英文來源時必備）
  transcript_zh.txt        ← 繁體中文逐字稿（英文來源時必備，GPT-4o 翻譯）
```

#### 逐字稿翻譯方式（英文來源）

```python
import os, requests
api_key = os.environ.get("OPENAI_API_KEY")
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

with open('transcript_en.txt') as f:
    transcript = f.read()

# 分段（每段 ~3000 字）
chunk_size = 3000
chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]

translated = []
for chunk in chunks:
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "將英文逐字稿翻譯成繁體中文，口語流暢，忠實原意。直接輸出翻譯，不需說明。"},
            {"role": "user", "content": chunk}
        ],
        "max_tokens": 2000, "temperature": 0.3
    }
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    translated.append(resp.json()['choices'][0]['message']['content'])

open('transcript_zh.txt', 'w').write('\n'.join(translated))
```

---

### Step 9｜推 Stage 預覽（含更新索引頁）

> ⚠️ 建立新影片目錄時，**必須同時更新 `/tmp/stage_repo/index.html`**

#### 9a. 更新 Stage 首頁索引

在 index.html 的「近期影片」grid 最前面插入新卡片：

```html
<a class="card" href="{影片名}/">
  <img class="card-thumb" src="{影片名}/thumbnail.jpg" alt="{標題}" onerror="this.style.background='#1a1a2e'">
  <div class="card-body">
    <div class="title">{標題}</div>
    <div class="desc">{一句話摘要，約 40 字}</div>
    <div class="card-footer">
      <!-- 狀態 tag 選一個 -->
      <span class="tag stage">Stage 審閱中</span>
      <!-- <span class="tag private">🔒 已上傳（私人）</span> -->
      <!-- <span class="tag live">✅ 已公開</span> + YouTube 連結 -->
      <span class="dur">X 分鐘</span>
    </div>
  </div>
</a>
```

**發布後同步更新 tag 狀態：**
- Stage → `tag.stage`（紅）
- 已上傳私人 → `tag.private`（橘）
- 公開後 → `tag.live`（綠）+ 加 YouTube 連結

#### 9b. 推送

```bash
cd /tmp/stage_repo
git add {影片名}/ index.html    # ← index.html 一定要加
git commit -m "stage: {影片名} - {改動說明}"
git pull --rebase
git push

# 首頁：https://i94ivoice-glitch.github.io/stage/
# 影片：https://i94ivoice-glitch.github.io/stage/{影片名}/
```

---

### Step 10｜Jovie 確認後正式發布

#### A. YouTube 上傳（先私人審閱）
```bash
python3 ~/workspace/youtube_upload.py \
  --file {影片名}_stage.mp4 \
  --title "$(python3 -c \"import json; d=json.load(open('{影片名}/youtube_meta.json')); print(d['title'])\")" \
  --desc  "$(python3 -c \"import json; d=json.load(open('{影片名}/youtube_meta.json')); print(d['description'])\")" \
  --tags  "$(python3 -c \"import json; d=json.load(open('{影片名}/youtube_meta.json')); print(','.join(d['tags']))\")" \
  --private
```

#### B. Jovie 確認後改公開
- YouTube Studio → 影片 → 改為「公開」
- 或告知 Javis，用 API 自動更新

#### C. GitHub Pages 正式版
```bash
cp {影片名}_stage.mp4 {影片名}.mp4
git add {影片名}.mp4
git commit -m "release: {影片名} 正式版"
git pull --rebase && git push
```

---

## 📋 目前影片專案

| 專案 | 狀態 | YouTube | 預覽頁 |
|------|------|---------|--------|
| elon | ✅ 已發布 | — | [stage/elon/](https://i94ivoice-glitch.github.io/stage/elon/) |
| anthropic_dod | ✅ 已公開 | [Q0LXBx1TxxY](https://youtu.be/Q0LXBx1TxxY) | [stage/anthropic_dod/](https://i94ivoice-glitch.github.io/stage/anthropic_dod/) |
| ai_hackers | Stage（YouTube 私人） | [EZ5gcHLJT_4](https://youtu.be/EZ5gcHLJT_4) | [stage/ai_hackers/](https://i94ivoice-glitch.github.io/stage/ai_hackers/) |
| vampire（AI吸血鬼效應）| 🔒 已上傳私人 | [fDyC_t4pKv0](https://youtu.be/fDyC_t4pKv0) | [stage/vampire/](https://i94ivoice-glitch.github.io/stage/vampire/) |
| dankoe（AI時代護城河）| Stage（YouTube 私人） | [0dXtEk-3PaE](https://youtu.be/0dXtEk-3PaE) | [stage/dankoe/](https://i94ivoice-glitch.github.io/stage/dankoe/) |
| palantir | Stage（YouTube 私人） | [hy96g8FwHrM](https://youtu.be/hy96g8FwHrM) | [stage/palantir/](https://i94ivoice-glitch.github.io/stage/palantir/) |

---

## ⚡ 常見錯誤與解法

| 問題 | 原因 | 解法 |
|------|------|------|
| 音訊時長 2 倍長 | 用了 `-f concat -c copy` 合併片尾 | 改用 `filter_complex concat` |
| 字幕跑到畫面中間 | 整句字幕 + 大字體換行 | 先執行 `split_srt.py --max-width 54` |
| Ken Burns 抖動（方式1）| 使用了 `zoompan` 濾鏡 | 改用 `scale(t)+crop eval=frame` |
| Ken Burns 抖動（方式2）| `scale=固定大尺寸` + `crop` 平移 | 改用 `scale(t) eval=frame`，不要固定放大再平移 |
| Ken Burns 無效果 | `eval=init` 只算一次 | 改用 `eval=frame` 每幀重算 |
| 字幕不顯示 | subtitles 路徑用相對路徑 | 改用絕對路徑 |
| git push 失敗 | 未先 pull | `git pull --rebase` 後再 push |
| drawtext bold 不生效 | 未指定 Bold 字體檔 | 使用 `NotoSansCJK-Bold.ttc` |
| 英文名字斷句 | 空格被視為斷點 | `split_srt.py` 已處理，勿手動修改 |
| 問號消失 | 誤將 `？?` 加入移除清單 | `split_srt.py` 只移除 `，。；：、！…—,.;:!`，保留 `？?` |
