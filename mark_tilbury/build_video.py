#!/usr/bin/env python3
"""Build mark_tilbury video: Steps 2-6"""
import re
import subprocess
import sys
import os

os.chdir("/tmp/stage_repo/mark_tilbury")

# ── Step 2: Parse chapter times from SRT ──────────────────────────────────────
print("=== Step 2: Parsing chapter times from SRT ===")

def srt_time_to_ms(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h)*3600000 + int(m)*60000 + int(s)*1000 + int(ms)

with open("subtitles.srt", encoding="utf-8") as f:
    content = f.read()

# Parse all subtitle entries
entries = re.split(r'\n\n+', content.strip())
subs = []
for entry in entries:
    lines = entry.strip().split("\n")
    if len(lines) >= 3:
        times = lines[1]
        text = " ".join(lines[2:])
        m = re.match(r'(\S+) --> (\S+)', times)
        if m:
            start_ms = srt_time_to_ms(m.group(1))
            subs.append({"start_ms": start_ms, "text": text})

# Find chapter start times
chapter_keywords = [
    "每 1 元投資在 S&P 500",   # ch00
    "Mark 提到了當前",           # ch01
    "Mark 轉而談到全球分散",     # ch02
    "Mark 提到另一層保護措施",   # ch03
]

chapter_times_ms = []
for kw in chapter_keywords:
    found = None
    for sub in subs:
        if kw in sub["text"]:
            found = sub["start_ms"]
            break
    if found is None:
        print(f"ERROR: Could not find keyword: {kw}", file=sys.stderr)
        sys.exit(1)
    chapter_times_ms.append(found)
    print(f"  Found '{kw}' at {found}ms ({found/1000:.3f}s)")

audio_duration_ms = int(241.392 * 1000)

# Calculate durations
durations_sec = []
for i in range(4):
    if i < 3:
        dur = (chapter_times_ms[i+1] - chapter_times_ms[i]) / 1000.0
    else:
        dur = (audio_duration_ms - chapter_times_ms[i]) / 1000.0
    # Add small buffer for last segment to not cut early
    if i == 3:
        dur += 0.5
    durations_sec.append(dur)
    print(f"  Chapter {i:02d}: start={chapter_times_ms[i]/1000:.3f}s, dur={dur:.3f}s")

print("\n✅ Step 2 complete")

# ── Step 3: Ken Burns segments ─────────────────────────────────────────────────
print("\n=== Step 3: Generating Ken Burns segments ===")

# Use zoompan for Ken Burns effect (slow zoom + subtle pan)
# zoompan: zoom from 1.0 to 1.2, pan from center
# z: zoom level per frame, d: duration in frames, s: output size
def kb_vf(dur_sec):
    n_frames = int(dur_sec * 24)
    return (
        f"zoompan=z='min(zoom+0.0005,1.15)':d={n_frames}:"
        f"x='iw/2-(iw/zoom/2)+50*sin(2*3.14159*on/{n_frames})':"
        f"y='ih/2-(ih/zoom/2)':s=1280x720:fps=24,"
        f"format=yuv420p"
    )

bg_files = [
    "bg_00_opening.png",
    "bg_01_sp500.png",
    "bg_02_global.png",
    "bg_03_gold.png",
]

for i, (bg, dur) in enumerate(zip(bg_files, durations_sec)):
    seg = f"seg_{i:02d}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", bg,
        "-t", str(dur),
        "-vf", kb_vf(dur),
        "-c:v", "libx264", "-crf", "18",
        seg
    ]
    print(f"  Generating {seg} ({dur:.2f}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr[-2000:]}", file=sys.stderr)
        sys.exit(1)
    print(f"  ✅ {seg} done")

print("\n✅ Step 3 complete")

# ── Step 4: Concat + audio ─────────────────────────────────────────────────────
print("\n=== Step 4: Concat + audio ===")

with open("concat.txt", "w") as f:
    for i in range(4):
        f.write(f"file 'seg_{i:02d}.mp4'\n")

# Concat
cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "video_raw.mp4"]
print("  Concatenating segments...")
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR: {result.stderr[-2000:]}", file=sys.stderr)
    sys.exit(1)
print("  ✅ video_raw.mp4 done")

# Add audio
cmd = [
    "ffmpeg", "-y",
    "-i", "video_raw.mp4",
    "-i", "audio.mp3",
    "-map", "0:v", "-map", "1:a",
    "-c:v", "copy", "-c:a", "aac",
    "-shortest",
    "video_with_audio.mp4"
]
print("  Adding audio...")
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR: {result.stderr[-2000:]}", file=sys.stderr)
    sys.exit(1)
print("  ✅ video_with_audio.mp4 done")
print("\n✅ Step 4 complete")

# ── Step 5: Burn subtitles + chapter titles ────────────────────────────────────
print("\n=== Step 5: Burn subtitles + chapter titles ===")

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SRT_PATH = "/tmp/stage_repo/mark_tilbury/subtitles.srt"

chapter_names = ["S&P 500 開場", "S&P 500 風險", "全球分散", "黃金與現金"]
chapter_starts_sec = [t/1000.0 for t in chapter_times_ms]
chapter_ends_sec = [chapter_starts_sec[i] + durations_sec[i] for i in range(4)]

# Build drawtext filters for chapter titles (right-top corner)
drawtext_filters = []
for i, (name, start, end) in enumerate(zip(chapter_names, chapter_starts_sec, chapter_ends_sec)):
    # Escape special characters for ffmpeg
    safe_name = name.replace("'", "\\'").replace(":", "\\:")
    dt = (
        f"drawtext=fontfile={FONT}:text='{safe_name}':"
        f"fontsize=28:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=6:"
        f"x=w-tw-20:y=20:"
        f"enable='between(t,{start:.3f},{end:.3f})'"
    )
    drawtext_filters.append(dt)

# Subtitle filter
sub_style = "FontSize=38,FontName=Noto Sans CJK TC,PrimaryColour=&H0000FFFF,Bold=1,Outline=3,OutlineColour=&H00000000,Alignment=2,MarginV=40,MarginL=60,MarginR=60"
sub_filter = f"subtitles={SRT_PATH}:force_style='{sub_style}'"

all_filters = sub_filter + "," + ",".join(drawtext_filters)

cmd = [
    "ffmpeg", "-y",
    "-i", "video_with_audio.mp4",
    "-vf", all_filters,
    "-c:v", "libx264", "-c:a", "copy",
    "with_subs.mp4"
]
print("  Burning subtitles + chapter titles...")
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR: {result.stderr[-3000:]}", file=sys.stderr)
    sys.exit(1)
print("  ✅ with_subs.mp4 done")
print("\n✅ Step 5 complete")

# ── Step 6: Add logo outro ─────────────────────────────────────────────────────
print("\n=== Step 6: Add logo outro ===")

LOGO = "/home/jovie/.openclaw/workspace/skills/94ivoice-video/media/94ivoice_logo_outro_v2.mp4"

# Scale logo
cmd = [
    "ffmpeg", "-y",
    "-i", LOGO,
    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac",
    "logo_scaled.mp4"
]
print("  Scaling logo...")
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR: {result.stderr[-2000:]}", file=sys.stderr)
    sys.exit(1)
print("  ✅ logo_scaled.mp4 done")

# Concat with filter_complex
cmd = [
    "ffmpeg", "-y",
    "-i", "with_subs.mp4",
    "-i", "logo_scaled.mp4",
    "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]",
    "-map", "[outv]", "-map", "[outa]",
    "-c:v", "libx264", "-c:a", "aac",
    "mark_tilbury_stage.mp4"
]
print("  Concatenating with logo...")
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR: {result.stderr[-2000:]}", file=sys.stderr)
    sys.exit(1)
print("  ✅ mark_tilbury_stage.mp4 done")
print("\n✅ Step 6 complete")

# ── Final info ─────────────────────────────────────────────────────────────────
print("\n=== Final Output Info ===")
import shutil
size = os.path.getsize("mark_tilbury_stage.mp4")
print(f"  File size: {size/1024/1024:.1f} MB")

result = subprocess.run(
    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", "mark_tilbury_stage.mp4"],
    capture_output=True, text=True
)
duration = float(result.stdout.strip())
mins = int(duration // 60)
secs = duration % 60
print(f"  Duration: {mins}m {secs:.1f}s ({duration:.2f}s)")

print("\n  Chapter times:")
for i, (name, start) in enumerate(zip(chapter_names, chapter_starts_sec)):
    m = int(start // 60)
    s = start % 60
    print(f"    {i:02d} {name}: {m:02d}:{s:05.2f} ({start:.3f}s)")

print("\n🎉 All steps complete!")
