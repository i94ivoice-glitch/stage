---
name: 94ivoice-video
description: 94iVoice 愛播客 YouTube 影片製作流程。使用時機：(1) 製作新的 94iVoice 影片、(2) 從英文影片來源製作繁中解說影片、(3) TTS 語音合成+字幕+Ken Burns 動態背景、(4) YouTube 上傳與 Stage 預覽頁發布。觸發詞：94iVoice、愛播客、做影片、製作影片、YouTube影片、TTS影片。
---

# 94iVoice 影片製作 Skill

製作 94iVoice 愛播客 YouTube 頻道的 AI 解說影片。

## Step 0｜來源影片 → 逐字稿

### 下載來源影片音訊

```bash
# 只下載音訊（最快）
yt-dlp -x --audio-format mp3 -o "source_audio.%(ext)s" "{YouTube URL}"

# 若需要影片資訊（Speaker 名稱、頻道）
yt-dlp --write-info-json --skip-download -o "meta" "{YouTube URL}"
# Speaker 名稱從 meta.info.json 的 channel 欄位取得
```

### Whisper 語音轉文字（英文逐字稿）

```bash
# 方法 A：OpenAI Whisper API（推薦，速度快）
python3 - <<'EOF'
from openai import OpenAI
client = OpenAI()
with open("source_audio.mp3", "rb") as f:
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        language="en",
        response_format="text"
    )
open("transcript_en.txt", "w").write(result)
EOF

# 方法 B：本機 whisper CLI（較慢，不需網路）
whisper source_audio.mp3 --language en --output_format txt --output_dir .
mv source_audio.txt transcript_en.txt
```

### GPT-4o 批次翻譯（英文 → 繁體中文）

```python
from openai import OpenAI
client = OpenAI()

with open('transcript_en.txt') as f:
    transcript = f.read()

chunk_size = 3000
chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
translated = []

for chunk in chunks:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "將英文逐字稿翻譯成繁體中文，口語流暢，忠實原意。直接輸出翻譯，不需說明。"},
            {"role": "user", "content": chunk}
        ]
    )
    translated.append(resp.choices[0].message.content)

open('transcript_zh.txt', 'w').write('\n'.join(translated))
```

> 翻譯完成的 `transcript_zh.txt` 是製作播客腳本的參考素材，**不是直接使用的腳本**。
> 需再依 94iVoice 文案風格（見 `references/script-style.md`）改寫為播客腳本。

---

## 快速開始

```bash
# 1. 建立工作目錄
mkdir -p /tmp/{project_name} && cd /tmp/{project_name}

# 2. 準備腳本 → TTS 語音
python3 ~/workspace/gen_tts_ssml.py script_clean.txt .
# 輸出：audio.mp3 + subtitles.srt

# 3. 字幕斷句
python3 ~/workspace/split_srt.py subtitles.srt subtitles_split.srt --max-width 54

# 4. 生成背景圖（DALL-E 3，每章節一張）
# 5. Ken Burns 影片片段 + 合併 + 燒字幕 + 加片尾
# 6. 推送 Stage 預覽 + YouTube 上傳
```

## 固定規格

| 項目 | 設定 |
|------|------|
| TTS 聲音 | `zh-CN-YunjianNeural` |
| 影片 | 1280×720 · 24fps · H.264 |
| 字幕 | FontSize 38 · 底部置中 · 白字黑邊 |
| 片尾 | `94ivoice_logo_outro_v2.mp4`（6.04s）|
| YouTube | 預設私人，審閱後改公開 |

## 詳細流程

見 `references/workflow.md`（完整 10 步驟流程）

## 腳本設計

見 `references/script-style.md`（文案風格指南）

## 關鍵腳本

| 腳本 | 用途 |
|------|------|
| `~/workspace/gen_tts_ssml.py` | TTS 語音合成 + 發音修正 |
| `~/workspace/split_srt.py` | 字幕智能斷句 |
| `~/workspace/youtube_upload.py` | YouTube 上傳 |
| `~/workspace/make_thumbnail.py` | 封面生成 |

## GitHub Stage Repo

- 本機：`/tmp/stage_repo/`
- 遠端：`https://github.com/i94ivoice-glitch/stage`
- Pages：`https://i94ivoice-glitch.github.io/stage/`

## Ken Burns 濾鏡（唯一正確寫法）

```bash
KB_VF="scale=w='1280*(1+0.2*(1-abs(2*mod(t,46)/46-1)))':h='720*(1+0.2*(1-abs(2*mod(t,46)/46-1)))':eval=frame,crop=1280:720,format=yuv420p,fps=24"

ffmpeg -y -loop 1 -i bg.png -t 30 -r 24 -vf "$KB_VF" -c:v libx264 seg.mp4
```

⚠️ 禁止使用 `zoompan` 或 `eval=init`，會造成抖動。

## 片尾合併（唯一正確寫法）

```bash
LOGO=~/workspace/94ivoice_logo_outro_v2.mp4

# Logo 先統一格式
ffmpeg -y -i "$LOGO" -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -r 24 -c:a aac logo_scaled.mp4

# filter_complex concat（禁止用 -f concat -c copy）
ffmpeg -y -i main.mp4 -i logo_scaled.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" -c:v libx264 -c:a aac output.mp4
```

## 常見錯誤

| 問題 | 解法 |
|------|------|
| 音訊 2 倍長 | 用 `filter_complex concat`，不要 `-f concat -c copy` |
| 字幕跑到中間 | 先執行 `split_srt.py` 斷句 |
| Ken Burns 抖動 | 用 `scale(t) eval=frame`，禁止 `zoompan` |
| 字幕不顯示 | subtitles 路徑用絕對路徑 |
