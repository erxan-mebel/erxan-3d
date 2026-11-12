"""Reel 04: СТО — "Мықты құдаларым" (no speech: footage + text cards + music + SFX).

Run from the repo root: python3 Монтаж/work/build_reel_04_sto.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from audio_fx import music, sfx  # noqa: E402

SRC = Path("Монтаж/Исходники/СТО")
OUT = Path("Монтаж/Готовые/reel_04_СТО_мықты_құдаларым.mp4")
TMP = Path("Монтаж/work/tmp_reel_04")
ASS = TMP / "cards.ass"

# (clip, start, end, card text)
SHOTS = [
    ("IMG_5417.mov", 0.3, 2.8, "Таныс болыңыз:\\Nмықты құдаларым"),
    ("IMG_5411.mov", 0.0, 3.0, "Өздерінің СТО-сы бар"),
    ("IMG_5414.mov", 0.0, 3.0, "Екеуі — бір команда"),
    ("IMG_5412.mov", 3.8, 6.8, "Кузовты тегістейді"),
    ("IMG_5414.mov", 12.2, 15.2, "Бояуға дайындайды"),
    ("IMG_5412.mov", 0.0, 2.2, "Қолдары — алтын"),
    ("IMG_5416.mov", 0.2, 3.2, "Барлық көлікті жөндейді"),
    ("IMG_5415.mov", 0.0, 3.2, "Нәтижесі — көз тоймайды"),
]
END_CARD = 2.8


def ts(x):
    cs = int(round(x * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", *args], check=True)


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    lst, t, ev, cuts = [], 0.0, [], []
    for k, (f, s, e, text) in enumerate(SHOTS):
        d = e - s
        part = TMP / f"shot{k}.mov"
        run(["-ss", f"{s}", "-i", str(SRC / f), "-t", f"{d}",
             "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,eq=contrast=1.06:saturation=1.12",
             "-af", "aresample=48000", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(part)])
        lst.append(f"file '{part.resolve()}'")
        pop = r"{\an2\pos(540,1560)\fad(120,120)\fscx70\fscy70\t(0,160,\fscx106\fscy106)\t(160,260,\fscx100\fscy100)}"
        ev.append(f"Dialogue: 1,{ts(t + 0.15)},{ts(t + d - 0.05)},Card,,0,0,0,,{pop}{text}")
        cuts.append(t)
        t += d
    speech_end = t
    total = t + END_CARD
    ev.append(f"Dialogue: 2,{ts(speech_end + 0.1)},{ts(total)},Svc,,0,0,0,,{{\\an5\\pos(540,820)\\fad(200,0)}}МОТОР · БОЯУ\\NКУЗОВ · ЖӨНДЕУ")
    ev.append(f"Dialogue: 2,{ts(speech_end + 0.5)},{ts(total)},EndSub,,0,0,0,,{{\\an5\\pos(540,1060)\\fad(200,0)}}Машинаңызды сеніп тапсырыңыз")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Card,Inter ExtraBold,74,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,1,0,3,20,0,2,60,60,0,1
Style: Svc,Inter Black,92,&H005B82D9,&H005B82D9,&H00141414,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1
Style: EndSub,Inter SemiBold,58,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ASS.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    (TMP / "list.txt").write_text("\n".join(lst) + "\n")
    joined = TMP / "joined.mov"
    run(["-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c", "copy", str(joined)])
    music(total, TMP / "music.wav", bpm=112, seed=11)
    sfx([(c, "whoosh") for c in cuts[1:]] + [(speech_end, "whoosh"), (speech_end + 0.5, "pop")], total, TMP / "sfx.wav")
    vf = (f"tpad=stop_mode=clone:stop_duration={END_CARD},"
          f"boxblur=22:enable='gte(t,{speech_end})',"
          f"drawbox=x=0:y=0:w=iw:h=ih:color=0x141414@0.75:t=fill:enable='gte(t,{speech_end})',"
          f"subtitles={ASS}")
    fc = (f"[0:v]{vf}[v];"
          f"[0:a]volume=0.22,apad=whole_dur={total:.2f}[amb];[1:a]volume=0.8[m];[2:a]volume=0.6[f];"
          f"[amb][m][f]amix=inputs=3:normalize=0,alimiter=limit=0.9[a]")
    run(["-i", str(joined), "-i", str(TMP / "music.wav"), "-i", str(TMP / "sfx.wav"), "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])
    print(OUT, f"{total:.1f}s")


if __name__ == "__main__":
    main()
