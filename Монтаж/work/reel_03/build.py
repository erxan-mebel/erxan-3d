"""Reel 03: 3D animation "how a wardrobe is made" + music and sound effects.

Run from the repo root: python3 Монтаж/work/reel_03/build.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from audio_fx import music, sfx  # noqa: E402

TOTAL = 33.0
TMP = Path("Монтаж/work/tmp_reel_03")
OUT = Path("Монтаж/Готовые/reel_03_шкаф_қалай_жасалады.mp4")
STEP_TIMES = [3, 7, 12, 17, 20, 26]

TMP.mkdir(parents=True, exist_ok=True)
video = TMP / "video.mp4"
subprocess.run(["node", "Монтаж/work/reel_03/render.js", str(video), str(TOTAL), "30", "1"], check=True)
music(TOTAL, TMP / "music.wav")
events = [(0.4, "whoosh")] + [(t, "whoosh") for t in STEP_TIMES] + [(30.0, "whoosh"), (30.4, "pop")]
sfx(events, TOTAL, TMP / "sfx.wav")
fc = "[1:a]volume=0.75[m];[2:a]volume=0.6[f];[m][f]amix=inputs=2:normalize=0,alimiter=limit=0.9[a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(TMP / "music.wav"), "-i", str(TMP / "sfx.wav"),
                "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-t", str(TOTAL), "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)], check=True)
print(OUT)
