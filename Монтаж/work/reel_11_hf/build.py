"""Reel 11: hidden kitchen bin — 10 hook variants for A/B testing (Instagram / TikTok).

python3 build.py <n>   -> cuts footage for variant n, writes index.html
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "../../Исходники/reel_11_src.mp4"
TMP = HERE / "../tmp_reel_11"
FULL = [(0.0, 23.4, 1.0)]
# n: (hook line 1, hook line 2 (accent), segments [(start, end, speed)], end-card question)
V = {
    1: ("Қоқысты әлі де", "есік ашып саласыз ба?", FULL, "Сізге де осындай керек пе?"),
    2: ("Ас үйдегі ең", "ыңғайлы шешім 👇", FULL, "Ұнаса — сақтап қойыңыз"),
    3: ("Қоқыс жәшігі", "осында жасырылған 😮", [(8.0, 11.0, 1.0), (0.0, 23.4, 1.0)], "Сіздің ас үйде бар ма?"),
    4: ("Бұл ас үйде", "қоқыс жәшігі көрінбейді", FULL, "Тапсырыспен жасаймыз"),
    5: ("15 секундта көріңіз:", "ыңғайлы қоқыс жәшігі", [(0.0, 18.6, 1.3)], "Директке жазыңыз"),
    6: ("Сізге осындай ас үй", "керек пе? Иә / Жоқ", FULL, "Комментарийге жазыңыз 👇"),
    7: ("Тапсырыспен ас үйде", "мұндай шешім бар", FULL, "Өлшеміңізді жіберіңіз"),
    8: ("Мусорное ведро", "без открывания двери", FULL, "Кухня на заказ · Астана"),
    9: ("Кухня на заказ Астана:", "скрытое мусорное ведро", [(7.3, 18.5, 1.0), (0.0, 7.3, 1.0)], "Пишите в директ"),
    10: ("Соңына дейін", "көріңіз 👀", [(0.0, 18.6, 1.0), (8.0, 11.0, 1.0)], "Қайта көріңіз 🔁"),
}
END = 2.6


def ffmpeg(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", *args], check=True)


def cut(n):
    TMP.mkdir(exist_ok=True)
    lst = []
    for k, (s, e, sp) in enumerate(V[n][2]):
        p = TMP / f"v{n}_{k}.mov"
        vf = f"scale=1080:1920:flags=lanczos,fps=30,setsar=1,eq=contrast=1.06:saturation=1.08:brightness=0.02,unsharp=5:5:0.5"
        af = "aresample=48000"
        if sp != 1.0:
            vf = f"setpts=PTS/{sp}," + vf
            af = f"atempo={sp}," + af
        ffmpeg(["-ss", str(s), "-to", str(e), "-i", str(SRC), "-vf", vf, "-af", af,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(p)])
        lst.append(f"file '{p.resolve()}'")
    (TMP / f"list{n}.txt").write_text("\n".join(lst) + "\n")
    out = HERE / "assets/video/main.mp4"
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(TMP / f"list{n}.txt"), "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "17", "-g", "30", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-18:TP=-2", "-c:a", "aac", "-b:a", "160k", str(out)])
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)]))
    return round(d - 0.05, 2)


def page(n, main):
    h1, h2, _, q = V[n]
    total = round(main + END, 2)
    html = f"""<!doctype html>
<html lang="kk"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family:"InterK"; font-weight:600; src:url("assets/fonts/Inter-SemiBold.otf"); }}
@font-face {{ font-family:"InterK"; font-weight:900; src:url("assets/fonts/Inter-Black.otf"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:#141414; }}
#root {{ position:relative; width:100%; height:100%; font-family:"InterK",sans-serif; }}
#main {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; }}
#hook {{ position:absolute; left:50px; right:150px; top:1120px; }}
#hook-in {{ display:inline-block; padding:22px 32px; border-radius:28px; background:rgba(20,20,20,.86); border-left:12px solid #f1c232; }}
#h1 {{ font-weight:600; font-size:52px; color:#f3ebe5; line-height:1.15; }}
#h2 {{ font-weight:900; font-size:70px; color:#f1c232; line-height:1.1; }}
#flash {{ position:absolute; inset:0; background:#fff; opacity:0; }}
#end {{ position:absolute; inset:0; }}
#e-bg {{ position:absolute; inset:0; background:radial-gradient(circle at 50% 40%, #3a2418 0%, #161311 55%, #0f0d0c 100%); }}
#e-q {{ position:absolute; left:40px; right:40px; top:500px; text-align:center; font-weight:900; font-size:66px; color:#f1c232; line-height:1.15; }}
#e-name {{ position:absolute; left:0; right:0; top:690px; text-align:center; font-weight:900; font-size:124px; letter-spacing:6px; color:#fff; }}
#e-name span {{ color:#d9825b; }}
#e-sub {{ position:absolute; left:0; right:0; top:860px; text-align:center; font-weight:600; font-size:52px; color:#e6d7cc; }}
#e-cta {{ position:absolute; left:190px; top:990px; width:700px; height:116px; border-radius:58px; background:#d9825b; color:#141414;
  font-weight:900; font-size:56px; display:flex; align-items:center; justify-content:center; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
<video id="main" class="clip" src="assets/video/main.mp4" data-start="0" data-duration="{main}" data-track-index="0" data-has-audio="true" data-volume="1" playsinline style="z-index:1"></video>
<div id="hook" class="clip" data-start="0" data-duration="3.2" data-track-index="1" style="z-index:20"><div id="hook-in"><div id="h1">{h1}</div><div id="h2">{h2}</div></div></div>
<div id="fl" class="clip" data-start="0" data-duration="0.4" data-track-index="2" style="z-index:25"><div id="flash"></div></div>
<div id="end" class="clip" data-start="{main}" data-duration="{END}" data-track-index="3" style="z-index:40">
  <div id="e-bg"></div>
  <div id="e-q">{q}</div>
  <div id="e-name">ERXAN <span>MEBEL</span></div>
  <div id="e-sub">Ас үй тапсырыс бойынша · Астана</div>
  <div id="e-cta">Директке жазыңыз</div>
</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused:true }});
tl.fromTo("#flash",{{opacity:.6}},{{opacity:0,duration:.35,ease:"power2.out"}},0);
tl.fromTo("#hook-in",{{x:-140,opacity:0}},{{x:0,opacity:1,duration:.4,ease:"back.out(1.7)"}},0.05);
tl.fromTo("#h2",{{scale:.85}},{{scale:1,duration:.3,ease:"back.out(2)",transformOrigin:"0% 50%"}},0.3);
tl.to("#hook-in",{{opacity:0,x:60,duration:.25,ease:"power2.in"}},2.9);
tl.fromTo("#e-bg",{{opacity:0}},{{opacity:1,duration:.3}},{main});
tl.fromTo("#e-q",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"power3.out"}},{main + .1:.2f});
tl.fromTo("#e-name",{{scale:1.5,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"power4.out"}},{main + .35:.2f});
tl.fromTo("#e-sub",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"power3.out"}},{main + .6:.2f});
tl.fromTo("#e-cta",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"back.out(2)"}},{main + .85:.2f});
tl.to("#e-cta",{{scale:1.07,duration:.3,yoyo:true,repeat:2,ease:"sine.inOut"}},{main + 1.35:.2f});
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    (HERE / "index.html").write_text(html, encoding="utf-8")
    return total


if __name__ == "__main__":
    n = int(sys.argv[1])
    m = cut(n)
    print(n, "total", page(n, m))
