"""Reel 05: finished kitchen (IMG_3766 talk + IMG_3771 pan) — subtitles, kinetic cards, transition, music.

Run from the repo root: python3 Монтаж/work/build_reel_05_kitchen.py [dombra|trap|lofi|none]
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from audio_fx import music, music_dombra, music_trap, sfx  # noqa: E402

STYLE = sys.argv[1] if len(sys.argv) > 1 else "dombra"
SRC = Path("Монтаж/Исходники")
SUFFIX = {"dombra": "", "none": "_музыкасыз", "trap": "_энергиялы", "lofi": "_лофи"}[STYLE]
OUT = Path(f"Монтаж/Готовые/reel_05_кухня_МДФ{SUFFIX}.mp4")
TMP = Path("Монтаж/work/tmp_reel_05")
ASS = TMP / "subs.ass"
XF = 0.35
END_CARD = 3.2

A = ("IMG_3766.mov", 0.80, 5.38)   # talking, then turns to the kitchen
B = ("IMG_3771.mov", 0.00, 6.48)   # kitchen pan (its audio is muted: off-topic talk)
# subtitle groups, source times of A
GROUPS = [
    [("Мінеки,", 0.84, 1.52), ("біздің", 1.54, 2.14)],
    [("кезекті", 2.14, 2.66), ("бітірген", 2.66, 3.12)],
    [("тапсырысымыз", 3.12, 4.32)],
    [("МДФ", 4.32, 4.72), ("плёнкадан.", 4.72, 5.38)],
]
# cards over B, times relative to the start of B
CARDS = [(0.25, 2.0, "Ақ МДФ фасадтар"), (2.0, 3.8, "Мәрмәр фартук · подсветка"), (3.8, 6.2, "Алтын түсті мойка")]
GRADE = "eq=contrast=1.05:saturation=1.08,unsharp=5:5:0.4,vignette=angle=0.45"
WHITE, COPPER = "&H00FFFFFF", "&H005B82D9"


def ts(x):
    cs = int(round(x * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", *args], check=True)


def kinetic(text):
    head = r"{\an2\move(470,1560,540,1560,0,260)\fad(120,120)\fscx92\fscy92\t(0,260,\fscx100\fscy100)}"
    words = []
    for k, w in enumerate(text.split(" ")):
        a, b = 120 + k * 140, 300 + k * 140
        words.append(f"{{\\1a&HFF&\\t({a},{b},\\1a&H00&)}}{w}")
    return head + " ".join(words)


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    shots = []
    for k, (f, s, e) in enumerate((A, B)):
        d = e - s
        n = int(round(d * 30))
        z = f"1+0.05*on/{n}" if k == 0 else f"1.06-0.06*on/{n}"
        part = TMP / f"shot{k}.mov"
        af = "highpass=f=90,afftdn=nf=-22,loudnorm=I=-16:TP=-2:LRA=11,aresample=48000" if k == 0 else "volume=0,aresample=48000"
        run(["-ss", f"{s}", "-i", str(SRC / f), "-t", f"{d}",
             "-vf", ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,"
                     f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,{GRADE}"),
             "-af", af, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
             "-c:a", "pcm_s16le", str(part)])
        shots.append((part, d))
    dA = shots[0][1]
    b0 = dA - XF
    speech_end = b0 + shots[1][1]
    total = speech_end + END_CARD

    ev = []
    for g in GROUPS:
        cw = [(w, s - A[1], e - A[1]) for w, s, e in g]
        for i, (_, s, e) in enumerate(cw):
            txt = " ".join((r"{\c" + COPPER + r"&}" + w + r"{\c" + WHITE + r"&}") if j == i else w for j, (w, _, _) in enumerate(cw))
            pop = r"{\fscx92\fscy92\t(0,120,\fscx100\fscy100)}" if i == 0 else ""
            ev.append(f"Dialogue: 1,{ts(max(0, s))},{ts(min(e, dA - XF / 2))},Sub,,0,0,0,,{pop}{txt}")
    for s, e, text in CARDS:
        ev.append(f"Dialogue: 1,{ts(b0 + s)},{ts(b0 + e)},Card,,0,0,0,,{kinetic(text)}")
    end = [(0.1, 780, "Name", "ERXAN MEBEL"), (0.45, 900, "EndSub", "Кухня тапсырыс бойынша"),
           (0.8, 1060, "Cta", "Директке жазыңыз")]
    for dt, y, style, text in end:
        ev.append(f"Dialogue: 2,{ts(speech_end + dt)},{ts(total)},{style},,0,0,0,,{{\\an5\\move(540,{y + 70},540,{y},0,320)\\fad(220,0)}}{text}")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,80,&H00FFFFFF,&H00FFFFFF,&H00141414,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,2,40,40,330,1
Style: Card,Inter ExtraBold,72,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,1,0,3,20,0,2,60,60,0,1
Style: Name,Inter Black,124,&H005B82D9,&H005B82D9,&H00141414,&H00000000,-1,0,0,0,100,100,6,0,1,0,0,5,0,0,0,1
Style: EndSub,Inter SemiBold,60,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Cta,Inter ExtraBold,60,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,0,0,3,22,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ASS.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")

    joined = TMP / "joined.mov"
    run(["-i", str(shots[0][0]), "-i", str(shots[1][0]), "-filter_complex",
         f"[0:v][1:v]xfade=transition=smoothleft:duration={XF}:offset={b0:.3f}[v];[0:a][1:a]acrossfade=d={XF}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(joined)])
    if STYLE == "none":
        run(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{total}", str(TMP / "music.wav")])
    else:
        {"lofi": lambda: music(total, TMP / "music.wav", bpm=100, seed=4),
         "trap": lambda: music_trap(total, TMP / "music.wav"),
         "dombra": lambda: music_dombra(total, TMP / "music.wav")}[STYLE]()
    sfx([(b0 + XF / 2, "whoosh"), (speech_end, "whoosh"), (speech_end + 0.8, "pop")], total, TMP / "sfx.wav")
    vf = (f"tpad=stop_mode=clone:stop_duration={END_CARD},"
          f"boxblur=22:enable='gte(t,{speech_end})',"
          f"drawbox=x=0:y=0:w=iw:h=ih:color=0x141414@0.72:t=fill:enable='gte(t,{speech_end})',"
          f"subtitles={ASS}")
    fc = (f"[0:v]{vf}[v];"
          f"[0:a]apad=whole_dur={total:.2f},asplit=2[voice][key];"
          f"[1:a]volume=0.45[mus];[mus][key]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=350[duck];"
          f"[2:a]volume=0.55[fx];[voice][duck][fx]amix=inputs=3:normalize=0,alimiter=limit=0.9[a]")
    run(["-i", str(joined), "-i", str(TMP / "music.wav"), "-i", str(TMP / "sfx.wav"), "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])
    print(OUT, f"{total:.1f}s")


if __name__ == "__main__":
    main()
