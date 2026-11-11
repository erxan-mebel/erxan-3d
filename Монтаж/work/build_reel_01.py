"""Reel 01: IMG_5302 + IMG_5305 -> pauses cut, Kazakh subtitles, motion cards, end card.

Run from the repo root: python3 Монтаж/work/build_reel_01.py
"""
import subprocess
from pathlib import Path

SRC = Path("Монтаж/Исходники")
OUT = Path("Монтаж/Готовые/reel_01_клиент_алданды.mp4")
ASS = Path("Монтаж/work/reel_01.ass")

# Speech segments kept (source seconds); gaps longer than 0.1 s are cut.
SEGMENTS = [
    ("IMG_5302.mov", 0.37, 4.08),
    ("IMG_5302.mov", 4.94, 8.56),
    ("IMG_5305.mov", 0.01, 1.04),
    ("IMG_5305.mov", 1.77, 5.49),
    ("IMG_5305.mov", 6.38, 9.46),
    ("IMG_5305.mov", 10.16, 12.56),
]
END_CARD = 1.6

# Cut-timeline offset of each segment.
offsets, acc = [], 0.0
for _, s, e in SEGMENTS:
    offsets.append(acc)
    acc += e - s
SPEECH_END = acc
TOTAL = SPEECH_END + END_CARD


def cut(src: str, t: float) -> float:
    """Map a source time to the cut timeline (clamped into the kept segment)."""
    best = None
    for (f, s, e), off in zip(SEGMENTS, offsets):
        if f != src:
            continue
        if s <= t <= e:
            return off + t - s
        if t < s and best is None:
            return off
        best = off + e - s
    return best


A, B = "IMG_5302.mov", "IMG_5305.mov"
# Subtitle groups: (source, [(word, start, end)]) in source seconds.
GROUPS = [
    (A, [("Менің", 0.37, 0.62), ("клиентім", 0.62, 1.00)]),
    (A, [("3", 1.00, 1.50), ("миллион", 1.50, 1.80), ("теңгеге", 1.80, 2.34)]),
    (A, [("алданып", 2.34, 3.14), ("қалыпты.", 3.14, 4.08)]),
    (A, [("Енді", 4.94, 5.22), ("маған", 5.22, 5.54), ("айтады:", 5.54, 5.92)]),
    (A, [("«Сендер", 5.92, 6.18), ("де", 6.18, 6.40), ("алаяқ", 6.40, 7.54)]),
    (A, [("емессіңдер", 7.54, 8.12), ("ме?»", 8.12, 8.30), ("деп.", 8.30, 8.56)]),
    (B, [("Бізге", 0.01, 0.55), ("бір", 0.55, 1.04)]),
    (B, [("мүмкіндік", 1.77, 2.82), ("беріңіз,", 2.82, 3.72)]),
    (B, [("офисіміз", 3.88, 4.52), ("бар,", 4.52, 5.49)]),
    (B, [("цехіміз", 6.38, 6.70), ("бар,", 6.70, 7.00)]),
    (B, [("келіңіз", 7.00, 7.42), ("деймін.", 7.42, 7.72)]),
    (B, [("Жоқ,", 7.72, 7.96), ("олар", 7.96, 8.36), ("да", 8.36, 8.50)]),
    (B, [("солай", 8.50, 8.84), ("айтыпты.", 8.84, 9.46)]),
    (B, [("Қалай", 10.16, 10.38), ("алдағанын,", 10.38, 11.02)]),
    (B, [("қалай", 11.02, 11.66), ("алдап", 11.66, 11.88), ("кеткенін…", 11.88, 12.56)]),
]

# Motion cards: (text, start, end) on the cut timeline.
CARDS = [
    ("−3 000 000 ₸", cut(A, 1.00), cut(A, 4.08)),
    ("АЛАЯҚ?", cut(A, 6.40), cut(A, 8.56)),
    ("✓ ОФИС БАР", cut(B, 3.88), cut(B, 9.46)),
    ("✓ ЦЕХ БАР", cut(B, 6.38), cut(B, 9.46)),
]

WHITE, COPPER, DARK = "&H00FFFFFF", "&H005B82D9", "&H00141414"


def ts(x: float) -> str:
    cs = int(round(x * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def build_ass() -> None:
    ev = []
    # Subtitles: whole group visible, the spoken word in copper.
    for src, words in GROUPS:
        cw = [(w, cut(src, s), cut(src, e)) for w, s, e in words]
        for i, (_, s, e) in enumerate(cw):
            if e - s < 0.04:
                continue
            txt = " ".join(
                (r"{\c" + COPPER + r"&}" + w + r"{\c" + WHITE + r"&}") if j == i else w
                for j, (w, _, _) in enumerate(cw)
            )
            pop = r"{\fscx92\fscy92\t(0,120,\fscx100\fscy100)}" if i == 0 else ""
            ev.append(f"Dialogue: 1,{ts(s)},{ts(e)},Sub,,0,0,0,,{pop}{txt}")
    # Cards (stacked when overlapping).
    y = {0: 1100, 1: 1100, 2: 1000, 3: 1120}
    for k, (text, s, e) in enumerate(CARDS):
        anim = r"{\an8\pos(540," + str(y[k]) + r")\fad(80,120)\fscx70\fscy70\t(0,160,\fscx106\fscy106)\t(160,260,\fscx100\fscy100)}"
        ev.append(f"Dialogue: 2,{ts(s)},{ts(e)},Card,,0,0,0,,{anim}{text}")
    # Top tag.
    ev.append(f"Dialogue: 3,{ts(0)},{ts(SPEECH_END)},Tag,,0,0,0,,{{\\an7\\pos(60,175)}}✳ erxan-mebel {{\\c&H00B4B4B4&}}~/цех")
    # End card.
    e0 = SPEECH_END
    ev.append(f"Dialogue: 4,{ts(e0)},{ts(TOTAL)},End,,0,0,0,,{{\\an5\\pos(540,880)\\fad(200,0)\\fscx80\\fscy80\\t(0,250,\\fscx100\\fscy100)}}ERXAN MEBEL")
    ev.append(f"Dialogue: 4,{ts(e0 + 0.25)},{ts(TOTAL)},EndSub,,0,0,0,,{{\\an5\\pos(540,1010)\\fad(200,0)}}Цехқа келіп, өз көзіңізбен көріңіз")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,86,&H00FFFFFF,&H00FFFFFF,&H00141414,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,2,70,70,560,1
Style: Card,Inter ExtraBold,78,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,1,0,3,18,0,8,70,70,0,1
Style: Tag,JetBrains Mono SemiBold,38,&H00FFFFFF,&H00FFFFFF,&H00141414,&H80141414,-1,0,0,0,100,100,0,0,3,10,0,7,0,0,0,1
Style: End,Inter Black,120,&H005B82D9,&H005B82D9,&H00141414,&H00000000,-1,0,0,0,100,100,4,0,1,0,0,5,0,0,0,1
Style: EndSub,Inter SemiBold,60,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ASS.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


def render() -> None:
    inputs = sorted({f for f, _, _ in SEGMENTS})
    idx = {f: i for i, f in enumerate(inputs)}
    parts, labels = [], []
    for k, (f, s, e) in enumerate(SEGMENTS):
        i = idx[f]
        d = e - s
        parts.append(
            f"[{i}:v]trim={s}:{e},setpts=PTS-STARTPTS,scale=1080:1920,fps=30,setsar=1[v{k}];"
            f"[{i}:a]atrim={s}:{e},asetpts=PTS-STARTPTS,aresample=48000,"
            f"afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{k}];"
        )
        labels.append(f"[v{k}][a{k}]")
    n = len(SEGMENTS)
    end = SPEECH_END
    fc = "".join(parts) + "".join(labels) + f"concat=n={n}:v=1:a=1[cv][ca];"
    fc += (
        f"[cv]tpad=stop_mode=clone:stop_duration={END_CARD},"
        f"boxblur=20:enable='gte(t,{end})',"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=0x141414@0.72:t=fill:enable='gte(t,{end})',"
        f"drawbox=x=0:y=120:w=iw:h=8:color=0x3a3a3a@0.8:t=fill:enable='lt(t,{end})',"
        f"drawbox=x=0:y=120:w='iw*t/{end}':h=8:color=0xD9825B:t=fill:enable='lt(t,{end})',"
        f"subtitles={ASS}[outv];"
        f"[ca]highpass=f=90,afftdn=nf=-25,loudnorm=I=-14:TP=-1.5:LRA=11,apad=whole_dur={TOTAL}[outa]"
    )
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for f in inputs:
        cmd += ["-i", str(SRC / f)]
    cmd += ["-filter_complex", fc, "-map", "[outv]", "-map", "[outa]", "-t", f"{TOTAL:.2f}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build_ass()
    render()
    print(OUT, f"{TOTAL:.2f}s")
