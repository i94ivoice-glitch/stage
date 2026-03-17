# 94iVoice 完整製作流程

## Step 1｜準備素材

### TTS 語音合成

```bash
python3 ~/workspace/gen_tts_ssml.py script_clean.txt /tmp/{project}
# 輸出：audio.mp3 + subtitles.srt
```

- 聲音：`zh-CN-YunjianNeural`（低沉有力男聲）
- 輸入：Markdown 格式腳本（`##`、`**` 自動清除）
- 發音修正：TEXT_RULES 純文字替換（AI→A I、沒→梅、覺得→感到）

### 背景圖生成（DALL-E 3）

```python
from openai import OpenAI
import requests
client = OpenAI()

resp = client.images.generate(
    model="dall-e-3",
    prompt="{prompt}",
    size="1792x1024",
    quality="standard",
    n=1
)
img = requests.get(resp.data[0].url).content
open("bg_00_opening.png", "wb").write(img)
```

**背景圖原則：**
- 溫暖色調：amber、gold、warm orange
- 底部 1/3 深色（字幕可讀）
- 禁止文字、禁止純白背景

---

## Step 2｜解析章節時間

```python
import subprocess
result = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration',
                         '-of','csv=p=0','audio.mp3'], capture_output=True, text=True)
total_dur = float(result.stdout.strip())

# 從腳本字元位置估算章節時間
script = open('script_clean.txt').read()
for keyword, name in chapters:
    idx = script.find(keyword)
    t = (idx / len(script)) * total_dur
```

---

## Step 3｜字幕斷句

```bash
python3 ~/workspace/split_srt.py subtitles.srt subtitles_split.srt --max-width 54
```

**斷句規則：**
1. 中文標點後斷（，。；！？）
2. 中英文邊界空格處斷
3. 英文單字群保持完整
4. 視覺寬度上限 54（中文=2，ASCII=1）
5. 移除標點（保留問號）

---

## Step 4｜Ken Burns 影片片段

```bash
KB_VF="scale=w='1280*(1+0.2*(1-abs(2*mod(t,46)/46-1)))':h='720*(1+0.2*(1-abs(2*mod(t,46)/46-1)))':eval=frame,crop=1280:720,format=yuv420p,fps=24"

ffmpeg -y -loop 1 -i bg_00.png -t 30 -r 24 -vf "$KB_VF" -c:v libx264 seg_00.mp4
```

效果：1.0× → 1.2× → 1.0× 循環，46 秒一個完整循環

---

## Step 5｜合併片段 + 加音訊

```bash
# concat.txt
cat > concat.txt << EOF
file 'seg_00.mp4'
file 'seg_01.mp4'
...
EOF

ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video_raw.mp4
ffmpeg -y -i video_raw.mp4 -i audio.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -shortest video_with_audio.mp4
```

---

## Step 6｜燒入字幕 + 章節標題

```bash
FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc

# 章節小標題
DT0="drawtext=fontfile=${FONT}:text='開場':fontsize=28:fontcolor=white:x=w-tw-30:y=30:box=1:boxcolor=0x00000080:boxborderw=12:enable='between(t,0,30)'"

# 主字幕
SUBS="subtitles=/absolute/path/subtitles_split.srt:force_style='Alignment=2,MarginV=40,MarginL=60,MarginR=60,FontSize=38,FontName=Noto Sans CJK TC,PrimaryColour=&H00FFFFFF,Bold=1,Outline=3,OutlineColour=&H00000000'"

ffmpeg -y -i video_with_audio.mp4 -vf "${DT0},${SUBS}" -c:v libx264 -c:a copy with_subs.mp4
```

---

## Step 7｜加片尾 Logo

```bash
LOGO=~/workspace/94ivoice_logo_outro_v2.mp4

ffmpeg -y -i "$LOGO" -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -r 24 -c:a aac logo_scaled.mp4

ffmpeg -y -i with_subs.mp4 -i logo_scaled.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" -c:v libx264 -c:a aac {project}_stage.mp4
```

---

## Step 8｜生成 YouTube 文案

```python
from openai import OpenAI
import json
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"""根據以下腳本輸出 JSON：
{{
  "title": "YouTube標題（60字內）",
  "description": "描述（含重點、章節時間碼、訂閱呼籲）",
  "tags": ["標籤1",...],
  "category": "Science & Technology"
}}
腳本：{script[:2000]}"""}]
)
meta = json.loads(resp.choices[0].message.content.strip('```json').strip('```'))
json.dump(meta, open('youtube_meta.json','w'), ensure_ascii=False, indent=2)
```

---

## Step 9｜推送 Stage 預覽

```bash
cd /tmp/stage_repo
mkdir -p {project}
cp /tmp/{project}/*.mp4 /tmp/{project}/*.png /tmp/{project}/*.srt /tmp/{project}/*.json {project}/
# 建立 index.html（見 references/stage-template.md）
git add {project}/ index.html
git commit -m "stage: {project}"
git push
```

Stage URL: `https://i94ivoice-glitch.github.io/stage/{project}/`

---

## Step 10｜YouTube 上傳

```bash
python3 ~/workspace/youtube_upload.py \
  --file {project}_stage.mp4 \
  --title "..." \
  --desc "..." \
  --tags "..." \
  --private
```

審閱後改公開，更新 Stage index.html 狀態 tag。
