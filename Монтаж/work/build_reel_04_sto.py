"""Reel 04: СТО — "Мықты құдаларым" (no speech: footage + text cards + music + SFX).

Run from the repo root: python3 Монтаж/work/build_reel_04_sto.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from audio_fx import music, music_dombra, music_trap, sfx  # noqa: E402

STYLE = sys.argv[1] if len(sys.argv) > 1 else "lofi"  # lofi | trap | dombra | none

SRC = Path("Монтаж/Исходники/СТО")
OUT = Path(f"Монтаж/Готовые/reel_04_СТО_мықты_құдаларым{'' if STYLE == 'lofi' else '_' + STYLE}.mp4")
TMP = Path("Монтаж/work/tmp_reel_04")
ASS = TMP / "cards.ass"

# (clip, start, end, card text)
SHOTS = [
    ("IMG_5417.mov", 0.3, 2.8, "Таныс болыңыз:\\Nмықты құдаларым"),
    ("IMG_5411.mov", 0.0, 3.0, "Өздерінің СТО-сы бар"),
    ("IMG_5414.mov", 0.0, 3.0, "Екеуі — бір команда"),
    ("IMG_5412.mov", 3.8, 6.8, "Кузовты тегістейді"),
    ("IMG_5414.mov", 12.2, 15.2, "Бояуға дайындайды"),
    ("IMG_5412.mov", 0.0, 2.2, "Мықты моторист —\\Nқолы алтын"),
    ("IMG_5416.mov", 0.2, 3.2, "Барлық көлікті жөндейді"),
    ("IMG_5415.mov", 0.0, 3.2, "Нәтижесі — көз тоймайды"),
]
END_CARD = 4.6


def ts(x):
    cs = int(round(x * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def kinetic(text):
    """Card slides in from the left, then the words appear one by one."""
    head = r"{\an2\move(470,1560,540,1560,0,260)\fad(120,120)\fscx92\fscy92\t(0,260,\fscx100\fscy100)}"
    out, k = [], 0
    for line in text.split("\\N"):
        words = []
        for w in line.split(" "):
            a, b = 120 + k * 140, 300 + k * 140
            words.append(f"{{\\1a&HFF&\\t({a},{b},\\1a&H00&)}}{w}")
            k += 1
        out.append(" ".join(words))
    return head + "\\N".join(out)


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", *args], check=True)


XF = 0.35  # transition length
TRANSITIONS = ["smoothup", "smoothleft", "zoomin", "slideup", "circleopen", "smoothright", "fade"]
GRADE = ("eq=contrast=1.10:saturation=1.22:brightness=0.01,"
         "colorbalance=rs=0.05:bs=-0.05:rm=0.03:bm=-0.03,unsharp=5:5:0.5,vignette=angle=0.55")


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    parts, ev, starts = [], [], []
    t = 0.0
    for k, (f, s, e, text) in enumerate(SHOTS):
        d = e - s
        n = int(round(d * 30))
        z = f"1+0.07*on/{n}" if k % 2 == 0 else f"1.07-0.07*on/{n}"  # slow push-in / pull-out
        part = TMP / f"shot{k}.mov"
        run(["-ss", f"{s}", "-i", str(SRC / f), "-t", f"{d}",
             "-vf", ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,"
                     f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,{GRADE}"),
             "-af", "aresample=48000", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(part)])
        parts.append((part, d))
        starts.append(t)
        a0 = t + (XF / 2 if k else 0) + 0.1
        ev.append(f"Dialogue: 1,{ts(a0)},{ts(t + d - XF / 2 - 0.05)},Card,,0,0,0,,{kinetic(text)}")
        t += d - XF
    speech_end = t + XF
    total = speech_end + END_CARD
    e0 = speech_end
    end_lines = [
        (0.1, 600, "Name", "СТО «БУМЕР»"),
        (0.4, 750, "Svc", "МОТОР · ХОДОВКА · БОЯУ · КУЗОВ"),
        (0.6, 825, "EndSub", "және барлық жөндеу жұмыстары"),
        (0.9, 960, "EndSub", "Бас шеберлер, мықты мотористер:"),
        (0.9, 1040, "Master", "Төрехан мен Тулеухан"),
        (1.2, 1160, "EndSub", "Қосшы қаласы, Ақан сері, 5"),
        (1.4, 1270, "Phone", "+7 778 737 38 85"),
        (1.8, 1420, "Cta", "Машинаңызды сеніп тапсырыңыз"),
    ]
    for dt, y, style, text in end_lines:
        anim = f"{{\\an5\\move(540,{y + 70},540,{y},0,320)\\fad(220,0)}}"
        if style == "Phone":  # heartbeat pulse
            anim = anim[:-1] + "".join(
                f"\\t({600 + i * 900},{750 + i * 900},\\fscx112\\fscy112)\\t({750 + i * 900},{950 + i * 900},\\fscx100\\fscy100)"
                for i in range(4)) + "}"
        ev.append(f"Dialogue: 2,{ts(e0 + dt)},{ts(total)},{style},,0,0,0,,{anim}{text}")
    tick = "МОТОР  •  ХОДОВКА  •  БОЯУ  •  КУЗОВ  •  ЖӨНДЕУ  •  " * 2
    ev.append(f"Dialogue: 2,{ts(e0 + 0.3)},{ts(total)},Ticker,,0,0,0,,{{\\an4\\move(1080,1600,-1900,1600)}}{tick}")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Card,Inter ExtraBold,74,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,1,0,3,20,0,2,60,60,0,1
Style: Name,Inter Black,120,&H005B82D9,&H005B82D9,&H00141414,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1
Style: Master,Inter ExtraBold,64,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Phone,Inter Black,84,&H005B82D9,&H005B82D9,&H00141414,&H00000000,-1,0,0,0,100,100,1,0,1,0,0,5,0,0,0,1
Style: Cta,Inter ExtraBold,56,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,0,0,3,20,0,5,0,0,0,1
Style: Svc,Inter ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1
Style: Ticker,Inter ExtraBold,46,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,2,0,3,16,0,4,0,0,0,1
Style: EndSub,Inter SemiBold,58,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ASS.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    ins, fc, prev_v, prev_a, off = [], [], "0:v", "0:a", 0.0
    for i, (part, d) in enumerate(parts):
        ins += ["-i", str(part)]
        if i == 0:
            off = d - XF
            continue
        tr = TRANSITIONS[(i - 1) % len(TRANSITIONS)]
        fc.append(f"[{prev_v}][{i}:v]xfade=transition={tr}:duration={XF}:offset={off:.3f}[v{i}]")
        fc.append(f"[{prev_a}][{i}:a]acrossfade=d={XF}[a{i}]")
        prev_v, prev_a = f"v{i}", f"a{i}"
        off += d - XF
    joined = TMP / "joined.mov"
    run([*ins, "-filter_complex", ";".join(fc), "-map", f"[{prev_v}]", "-map", f"[{prev_a}]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(joined)])
    gen = {"lofi": lambda: music(total, TMP / "music.wav", bpm=112, seed=11),
           "trap": lambda: music_trap(total, TMP / "music.wav"),
           "dombra": lambda: music_dombra(total, TMP / "music.wav")}
    if STYLE == "none":
        run(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{total}", str(TMP / "music.wav")])
    else:
        gen[STYLE]()
    sfx([(c, "whoosh") for c in starts[1:]] + [(speech_end, "whoosh"), (speech_end + 0.5, "pop")], total, TMP / "sfx.wav")
    # ASMR: in the no-music version the workshop sound is the soundtrack
    AMB = "highpass=f=60,loudnorm=I=-16:TP=-2:LRA=11" if STYLE == "none" else "volume=0.22"
    vf = (f"tpad=stop_mode=clone:stop_duration={END_CARD},"
          f"boxblur=22:enable='gte(t,{speech_end})',"
          f"drawbox=x=0:y=0:w=iw:h=ih:color=0x141414@0.75:t=fill:enable='gte(t,{speech_end})',"
          f"subtitles={ASS}")
    fc = (f"[0:v]{vf}[v];"
          f"[0:a]{AMB},apad=whole_dur={total:.2f}[amb];[1:a]volume=0.8[m];[2:a]volume=0.6[f];"
          f"[amb][m][f]amix=inputs=3:normalize=0,alimiter=limit=0.9[a]")
    run(["-i", str(joined), "-i", str(TMP / "music.wav"), "-i", str(TMP / "sfx.wav"), "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])
    print(OUT, f"{total:.1f}s")


if __name__ == "__main__":
    main()
