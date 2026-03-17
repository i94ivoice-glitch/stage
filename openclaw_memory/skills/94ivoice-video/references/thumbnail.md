# YouTube 封面設計

## 規格

- 尺寸：1280×720 JPEG
- 腳本：`~/workspace/make_thumbnail.py`

## 版面結構

```
┌─────────────────────────┬─────────────────┐
│  LEFT 3/5（0~768px）    │  RIGHT 2/5      │
│  深紫漸層背景           │  (768~1280px)   │
│                         │  人物照片        │
│  [NAME]                 │  512×720        │
│  ── 粉底線              │                 │
│  [BIG 160px] [SUFFIX]   │                 │
│  [MAIN] [ACCENT yellow] │                 │
│  ── 紫底線              │                 │
│  [SUB 淡紫]             │                 │
│  [DURATION 琥珀]        │                 │
└─────────────────────────┴─────────────────┘
```

## 使用方式

```bash
python3 ~/workspace/make_thumbnail.py \
  --photo person.jpg \
  --name "SPEAKER NAME" \
  --big "10" \
  --big-suffix "年後" \
  --main "經濟翻" \
  --main-accent "10倍" \
  --sub "但金錢會失去意義" \
  --duration "9 分鐘精華解析" \
  --output thumbnail.jpg
```

## 設計規格

| 元素 | 規格 |
|------|------|
| 左側背景 | 深紫 #120226 → 亮紫 #370A5A |
| 照片區 | x=768~1280，512×720 |
| 過渡融合 | 照片左緣 110px cosine fade |
| 名字 | 白色 max 56px，粉紅底線 #FF567E |
| 大字 | 白色 max 160px，自動縮放 |
| 主標 | 白色 ~74px + 黃色強調 #FFB500 |
| 副標 | 淡紫 #D2CDFF ~46px |
| 時長 | 琥珀 #FF9B00 28px |

## Speaker 照片來源（優先順序）

1. **YouTube 頻道頭像**
```python
import requests, re
r = requests.get(f"https://www.youtube.com/watch?v={VIDEO_ID}", 
    headers={"User-Agent": "Mozilla/5.0"})
urls = re.findall(r'https://yt3\.ggpht\.com/[^"]+', r.text)
# 取 s800 版本
```

2. **Wikipedia Commons**
3. **YouTube 影片縮圖裁切**
4. **無人物** → 用 DALL-E 背景圖，省略 `--name`
