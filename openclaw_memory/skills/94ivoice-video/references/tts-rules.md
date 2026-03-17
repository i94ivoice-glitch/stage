# TTS 發音修正規則

> 維護位置：`~/workspace/gen_tts_ssml.py` 的 `TEXT_RULES` 和 `REVERSE_RULES`

## 雙向替換機制

1. **TEXT_RULES**：腳本 → TTS（發音修正，如「沒」→「梅」）
2. **REVERSE_RULES**：TTS → 字幕（文字還原，如「梅」→「沒」）

⚠️ 新增發音規則時，**必須同時更新兩個表**，否則字幕會顯示錯誤文字。

## 英文縮寫 → 字母加空格

| 原文 | 替換後 |
|------|--------|
| AI（獨立）| A I |
| OpenAI | Open A I |
| ChatGPT | Chat G P T |
| GPT-4o | G P T 4 O |
| API | A P I |
| CEO/CTO/CFO | C E O / C T O / C F O |
| LLM | L L M |
| UI | U I |

## 稱謂縮寫 → 全稱

| 原文 | 替換後 |
|------|--------|
| Dr. Waku | Doctor Waku |
| Dr. | Doctor |
| Mr. | Mister |
| Mrs. | Misses |
| Ms. | Miss |
| vs. | versus |
| OpenClaw | Open Claw |

## 破音字 → 同義詞

### 覺（jiào / jué）

| 原文 | 替換後 | 說明 |
|------|--------|------|
| 睡覺 | 睡叫 | 「叫」固定 jiào |
| 一覺 | 一叫 | |
| 覺得 | 感到 | 避免唸 jiào |
| 感覺 | 感受 | |
| 察覺 | 發現 | |

### 沒（méi / mò）

| 原文 | 替換後 |
|------|--------|
| 沒有 | 梅有 |
| 沒辦法 | 梅辦法 |
| 沒關係 | 梅關係 |
| 沒（兜底）| 梅 |

### 其他破音字

| 原文 | 替換後 | 說明 |
|------|--------|------|
| 著名 | 知名 | zhù → 同義詞 |
| 著急 | 焦急 | zháo → 同義詞 |
| 行業 | 產業 | háng → 同義詞 |
| 重複 | 再重複 | chóng 強制 |
| 愛好 | 興趣 | hào → 同義詞 |

## 新增規則方式

編輯 `~/workspace/gen_tts_ssml.py`，在 `TEXT_RULES` 列表中加入：

```python
TEXT_RULES = [
    # 長詞放前面，避免被短詞截斷
    ("原文長詞",  "替換後"),
    ("原文短詞",  "替換後"),
    ...
]
```
