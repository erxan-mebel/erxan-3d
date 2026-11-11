"""Reel 02: IMG_5368 (b then a) -> AI detailing story; pauses cut, subtitles, motion cards.

Run from the repo root: python3 Монтаж/work/build_reel_01.py
"""
import subprocess
from pathlib import Path

SRC = Path("Монтаж/Исходники")
OUT = Path("Монтаж/Готовые/reel_02_ЖИ_деталировка.mp4")
ASS = Path("Монтаж/work/reel_02.ass")

# Speech segments kept (source seconds); gaps longer than 0.1 s are cut.
A, B = "IMG_5368_b.mov", "IMG_5368_a.mov"  # A = first half, B = second half
SEGMENTS = [
    (A, 0.81, 6.42), (A, 7.18, 9.46), (A, 10.13, 12.85), (A, 13.36, 16.63),
    (A, 17.39, 19.83), (A, 20.94, 25.00),
    (B, 0.56, 2.42), (B, 2.61, 3.54), (B, 3.69, 6.67), (B, 7.25, 8.24), (B, 8.85, 10.45),
    (B, 11.63, 15.86), (B, 16.24, 17.01), (B, 17.65, 18.99), (B, 19.63, 19.83),
    (B, 21.58, 22.00), (B, 22.16, 22.48),
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


# Subtitle groups: (source, [(word, start, end)]) in source seconds.
GROUPS = [
    (A, [("Жасанды", 0.81, 1.34), ("интеллекттің", 1.34, 1.92), ("көмегімен", 1.92, 2.48)]),
    (A, [("мебельдің", 2.48, 3.12), ("деталировкасын", 3.12, 3.84)]),
    (A, [("шығаруға", 3.84, 4.28), ("болады", 4.28, 4.66), ("екен,", 4.66, 4.84)]),
    (A, [("мен", 4.84, 5.00), ("оны", 5.00, 5.24), ("жаңа", 5.24, 5.48)]),
    (A, [("жасап", 5.48, 5.84), ("көрдім.", 5.84, 6.42)]),
    (A, [("Негізі,", 7.18, 7.92), ("біз", 7.94, 8.16), ("алдында", 8.16, 8.60)]),
    (A, [("бірінші", 8.60, 9.46), ("проектіні", 10.13, 11.00)]),
    (A, [("осылай", 11.00, 11.24), ("3D-да", 11.24, 11.62)]),
    (A, [("сызып", 11.62, 12.04), ("алатынбыз,", 12.04, 12.85)]),
    (A, [("мебельдің", 13.36, 13.76), ("проектісін", 13.76, 14.24)]),
    (A, [("сызып", 14.24, 14.54), ("алғаннан", 14.54, 15.02), ("кейін,", 15.02, 15.30)]),
    (A, [("оны", 15.30, 15.48), ("распечатать", 15.48, 16.00), ("етіп,", 16.00, 16.63)]),
    (A, [("былай", 17.39, 17.54), ("детальдарды", 17.54, 18.42)]),
    (A, [("қолмен", 18.42, 18.68), ("жазатынбыз.", 18.68, 19.83)]),
    (A, [("Енді", 20.94, 21.06), ("қазір", 21.06, 21.34), ("жаңа", 21.34, 21.56)]),
    (A, [("жасанды", 21.56, 22.00), ("интеллектпен", 22.00, 22.40)]),
    (A, [("сөйлесе", 22.40, 23.02), ("отырып,", 23.02, 23.38)]),
    (A, [("осылай", 23.38, 23.84), ("детальдарын,", 23.84, 25.00)]),
    (B, [("керек", 0.56, 0.80), ("фурнитураларын,", 0.80, 1.46)]),
    (B, [("ХДФ,", 1.46, 2.42), ("айна,", 2.61, 3.54)]),
    (B, [("фасадтардың", 3.69, 5.24), ("детальдарын", 5.24, 6.02)]),
    (B, [("шығардық.", 6.02, 6.67)]),
    (B, [("Так,", 7.25, 7.66), ("мінеки,", 7.66, 8.24)]),
    (B, [("бізде", 8.85, 9.16), ("сызбасы.", 9.16, 10.45)]),
    (B, [("Бұл", 11.63, 11.72), ("мен", 11.72, 11.88), ("ноутта", 11.88, 12.44)]),
    (B, [("жасаған", 12.44, 12.98), ("сызба.", 12.98, 13.68)]),
    (B, [("Мынау", 13.72, 14.20), ("мен", 14.20, 14.60), ("жаңа", 14.60, 15.04)]),
    (B, [("распечатать", 15.04, 15.50), ("еткен", 15.50, 15.86)]),
    (B, [("фурнитураларым.", 16.24, 17.01)]),
    (B, [("Енді", 17.65, 17.90), ("шкафтың", 17.90, 18.99)]),
    (B, [("дизайны", 19.63, 19.83), ("осылай", 21.58, 22.00), ("шықты.", 22.16, 22.48)]),
]

# Motion cards: (text, start, end) on the cut timeline.
CARDS = [
    ("ЖИ → ДЕТАЛИРОВКА", cut(A, 0.81), cut(A, 6.42), 1000),
    ("БҰРЫН: 3D + ҚОЛМЕН ✍", cut(A, 7.18), cut(A, 19.83), 1000),
    ("ҚАЗІР: ЖИ-МЕН ⚡", cut(A, 20.94), cut(A, 25.0), 1000),
    ("✓ ФУРНИТУРА", cut(B, 0.80), cut(B, 6.67), 680),
    ("✓ ХДФ", cut(B, 1.46), cut(B, 6.67), 790),
    ("✓ АЙНА", cut(B, 2.61), cut(B, 6.67), 900),
    ("✓ ФАСАД", cut(B, 3.69), cut(B, 6.67), 1010),
]
GRAY = (cut(A, 7.18), cut(A, 19.83))  # "before" part in black & white

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
    for text, s, e, yk in CARDS:
        anim = r"{\an8\pos(540," + str(yk) + r")\fad(80,120)\fscx70\fscy70\t(0,160,\fscx106\fscy106)\t(160,260,\fscx100\fscy100)}"
        ev.append(f"Dialogue: 2,{ts(s)},{ts(e)},Card,,0,0,0,,{anim}{text}")
    # Top header: blog title.
    ev.append(f"Dialogue: 3,{ts(0)},{ts(SPEECH_END)},Tag,,0,0,0,,{{\\an7\\pos(60,160)}}✳ МЕБЕЛЬШІНІҢ БЛОГЫ")
    ev.append(f"Dialogue: 3,{ts(0)},{ts(SPEECH_END)},TagSub,,0,0,0,,{{\\an7\\pos(60,232)}}уақытылы және сапалы")
    # End card.
    e0 = SPEECH_END
    ev.append(f"Dialogue: 4,{ts(e0)},{ts(TOTAL)},End,,0,0,0,,{{\\an5\\pos(540,880)\\fad(200,0)\\fscx80\\fscy80\\t(0,250,\\fscx100\\fscy100)}}ERXAN MEBEL")
    ev.append(f"Dialogue: 4,{ts(e0 + 0.25)},{ts(TOTAL)},EndSub,,0,0,0,,{{\\an5\\pos(540,1010)\\fad(200,0)}}Тапсырыс бойынша жиһаз")
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00141414,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,2,40,40,560,1
Style: Card,Inter ExtraBold,78,&H00141414,&H00141414,&H005B82D9,&H005B82D9,-1,0,0,0,100,100,1,0,3,18,0,8,70,70,0,1
Style: Tag,JetBrains Mono ExtraBold,38,&H005B82D9,&H00FFFFFF,&H00141414,&H80141414,-1,0,0,0,100,100,0,0,3,10,0,7,0,0,0,1
Style: TagSub,Inter SemiBold,40,&H00FFFFFF,&H00FFFFFF,&H00141414,&H80141414,-1,0,0,0,100,100,0,0,3,10,0,7,0,0,0,1
Style: End,Inter Black,120,&H005B82D9,&H005B82D9,&H00141414,&H00000000,-1,0,0,0,100,100,4,0,1,0,0,5,0,0,0,1
Style: EndSub,Inter SemiBold,60,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ASS.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


def run(args: list) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", *args], check=True)


def render() -> None:
    tmp = Path("Монтаж/work/tmp_reel_02")
    tmp.mkdir(exist_ok=True)
    # 1. Cut each speech segment into its own small file (low memory).
    lst = []
    for k, (f, s, e) in enumerate(SEGMENTS):
        part = tmp / f"seg{k:02}.mp4"
        d = e - s
        run(["-ss", f"{s:.3f}", "-i", str(SRC / f), "-t", f"{d:.3f}",
             "-vf", "scale=1080:1920,fps=30,setsar=1",
             "-af", f"aresample=48000,afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
             "-c:a", "pcm_s16le", "-f", "mov", str(part)])
        lst.append(f"file '{part.resolve()}'")
    (tmp / "list.txt").write_text("\n".join(lst) + "\n")
    joined = tmp / "joined.mov"
    run(["-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(joined)])
    # 2. Graphics, end card and audio clean-up on the joined cut.
    end = SPEECH_END
    vf = (
        f"tpad=stop_mode=clone:stop_duration={END_CARD},"
        f"hue=s=0:enable='between(t,{GRAY[0]:.2f},{GRAY[1]:.2f})',"
        f"boxblur=20:enable='gte(t,{end})',"
        f"drawbox=x=0:y=0:w=iw:h=ih:color=0x141414@0.72:t=fill:enable='gte(t,{end})',"
        f"drawbox=x=0:y=120:w=iw:h=8:color=0x3a3a3a@0.8:t=fill:enable='lt(t,{end})',"
        f"drawbox=x=0:y=120:w='iw*t/{end}':h=8:color=0xD9825B:t=fill:enable='lt(t,{end})',"
        f"subtitles={ASS}"
    )
    af = f"highpass=f=90,afftdn=nf=-22,loudnorm=I=-14:TP=-1.5:LRA=11,apad=whole_dur={TOTAL:.2f}"
    run(["-i", str(joined), "-vf", vf, "-af", af, "-t", f"{TOTAL:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)])


if __name__ == "__main__":
    build_ass()
    render()
    print(OUT, f"{TOTAL:.2f}s")
