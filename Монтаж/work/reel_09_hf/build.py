"""Reel 09: «Мебельге тапсырыс бергенде жасалатын қателік» — two parts of IMG_5847 joined.

python3 build.py         -> cuts footage (assets/video/main.mp4) and writes index.html
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "../../Исходники"
TMP = HERE / "../tmp_reel_09"
A, B = "IMG_5847_1.mov", "IMG_5847_2.mov"
# (file, start, end, punch-in zoom)
SEGS = [
    (A, 0.45, 6.65, 1.00), (A, 7.45, 13.15, 1.12), (A, 13.15, 19.6, 1.00), (A, 19.6, 25.0, 1.12),
    (B, 0.25, 3.35, 1.00), (B, 3.6, 6.8, 1.12), (B, 7.25, 11.25, 1.00), (B, 11.25, 22.0, 1.12),
]
offs, acc = [], 0.0
for f, s, e, z in SEGS:
    offs.append(acc)
    acc += e - s
MAIN = round(acc, 2)
END = 3.4
TOTAL = round(MAIN + END, 2)


def cut(f, t):
    for (ff, s, e, z), o in zip(SEGS, offs):
        if ff == f and s <= t <= e:
            return round(o + t - s, 2)
    for (ff, s, e, z), o in zip(SEGS, offs):
        if ff == f and t < s:
            return round(o, 2)
    return MAIN


CAPS = [
    (A, 0.45, 3.9, "Мебельшіге мебель заказ береді,"),
    (A, 4.0, 6.6, "бірақ көбісі осы қателікті жасайды."),
    (A, 7.45, 11.3, "Біз замерге барамыз, өлшемін алғаннан кейін"),
    (A, 11.3, 15.7, "бағамызды айтқанда, клиенттер оны қымбат деп ойлайды."),
    (A, 15.75, 17.2, "Бұл — нарықтың бағасы."),
    (A, 17.35, 22.5, "Сосын олар арзанға береді — мебелі уақытылы келмейді, сапасыз жасалады."),
    (B, 0.25, 3.3, "Соңынан желіге жазады: «Мебельші мені алдап кетті» деп."),
    (B, 3.6, 6.8, "Мебельге заказ беретін болсаңыз,"),
    (B, 7.25, 9.9, "жақсы маман, жақсы фирма таба білсеңіз,"),
    (B, 9.9, 14.6, "мебеліңіз уақытылы, сапалы, жауапкершілікпен жасалады."),
    (B, 14.7, 18.9, "Сондықтан мебельдің бағасына емес,"),
    (B, 19.0, 21.95, "жауапкершілігі мен сапасына мән беріңіздер."),
]
WARN = '<path d="M32 6 60 56H4z" fill="none" stroke="#141414" stroke-width="5" stroke-linejoin="round"/><rect x="29" y="22" width="6" height="18" rx="3" fill="#141414"/><circle cx="32" cy="47" r="3.5" fill="#141414"/>'
TAG = '<path d="M8 32 32 8h22v22L30 54z" fill="none" stroke="#141414" stroke-width="5" stroke-linejoin="round"/><circle cx="44" cy="20" r="4" fill="#141414"/>'
CLOCK = '<circle cx="32" cy="32" r="24" fill="none" stroke="#141414" stroke-width="5"/><path d="M32 18v15l10 6" stroke="#141414" stroke-width="5" fill="none" stroke-linecap="round"/>'
CHAT = '<path d="M10 12h44a4 4 0 0 1 4 4v24a4 4 0 0 1-4 4H26l-12 10V44h-4a4 4 0 0 1-4-4V16a4 4 0 0 1 4-4z" fill="none" stroke="#141414" stroke-width="5"/><path d="M24 24l16 12M40 24 24 36" stroke="#141414" stroke-width="5" stroke-linecap="round"/>'
STAR = '<path d="M32 6l7.6 16 17.4 2.2-12.8 12 3.3 17.3L32 45l-15.5 8.5L19.8 36 7 24.2 24.4 22z" fill="#141414"/>'
CARDS = [
    (cut(A, 3.9), cut(A, 6.65) - .05, "Көп адам жасайтын", "1 ҚАТЕЛІК", WARN, "pulse"),
    (cut(A, 15.6), cut(A, 17.3), "Бұл —", "нарықтың бағасы", TAG, "pop"),
    (cut(A, 17.4), cut(A, 25.0) - .05, "Арзан мебель =", "кешігу · сапасыз", CLOCK, "shake"),
    (cut(B, 0.3), cut(B, 3.35) - .05, "Соңынан:", "«алдап кетті»", CHAT, "shake"),
    (cut(B, 14.7), cut(B, 22.0) - .05, "Бағаға емес —", "сапаға қараңыз", STAR, "pulse"),
]


def ffmpeg(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", *args], check=True)


def cut_footage():
    TMP.mkdir(exist_ok=True)
    lst = []
    for k, (f, s, e, z) in enumerate(SEGS):
        d = e - s
        w, h = int(1404 * z) // 2 * 2, int(2496 * z) // 2 * 2
        x, y = (w - 1080) // 2, int((h - 1920) * (0.97 if z == 1 else 0.9))  # face sits upper-centre; keep chin above captions
        p = TMP / f"p{k}.mov"
        ffmpeg(["-ss", str(s), "-to", str(e), "-i", str(SRC / f),
                "-vf", f"scale={w}:{h},crop=1080:1920:{x}:{y},fps=30,setsar=1,eq=contrast=1.05:saturation=1.08:brightness=0.03,unsharp=5:5:0.4",
                "-af", f"aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.3f}:d=0.03",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", str(p)])
        lst.append(f"file '{p.resolve()}'")
    (TMP / "list.txt").write_text("\n".join(lst) + "\n")
    voice = ("highpass=f=90,afftdn=nf=-25,equalizer=f=120:t=q:w=1:g=2.5,equalizer=f=350:t=q:w=1.2:g=-2.5,"
             "equalizer=f=3500:t=q:w=1.5:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
             "aecho=0.8:0.5:35:0.05,loudnorm=I=-15:TP=-1.5:LRA=9")
    (HERE / "assets/video").mkdir(parents=True, exist_ok=True)
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
            "-g", "30", "-pix_fmt", "yuv420p", "-af", voice, "-c:a", "aac", "-b:a", "192k", str(HERE / "assets/video/main.mp4")])


def page():
    body, js = [], []
    for i, (f, s, e, t) in enumerate(CAPS):
        a, b = cut(f, s), cut(f, e)
        body.append(f'<div id="c{i}" class="clip cap" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="2" style="z-index:30">'
                    f'<div id="c{i}-in" class="cap-in">{t}</div></div>')
        js.append(f'tl.fromTo("#c{i}-in",{{y:14,opacity:0}},{{y:0,opacity:1,duration:.16,ease:"power2.out"}},{a});')
    for i, (s, e, l1, l2, ic, act) in enumerate(CARDS):
        body.append(f'<div id="k{i}" class="clip card" data-start="{s}" data-duration="{e - s:.2f}" data-track-index="3" style="z-index:20">'
                    f'<div id="k{i}-in" class="card-in"><div id="k{i}-ic" class="ic"><svg id="k{i}-svg" viewBox="0 0 64 64" width="78" height="78">{ic}</svg></div>'
                    f'<div class="tx"><div class="l1">{l1}</div><div class="l2">{l2}</div></div></div></div>')
        js.append(f'tl.fromTo("#k{i}-in",{{x:-120,opacity:0}},{{x:0,opacity:1,duration:.4,ease:"back.out(1.7)"}},{s});')
        js.append(f'tl.fromTo("#k{i}-ic",{{scale:0,rotation:-120}},{{scale:1,rotation:0,duration:.4,ease:"back.out(2)"}},{s + .08:.2f});')
        js.append(f'tl.to("#k{i}-in",{{opacity:0,x:50,duration:.22,ease:"power2.in"}},{e - .26:.2f});')
        if act == "pulse":
            js.append(f'tl.fromTo("#k{i}-svg",{{scale:1}},{{scale:1.15,duration:.25,yoyo:true,repeat:3,ease:"sine.inOut",transformOrigin:"50% 50%"}},{s + .5:.2f});')
        if act == "shake":
            js.append(f'tl.fromTo("#k{i}-svg",{{rotation:-10}},{{rotation:10,duration:.12,yoyo:true,repeat:7,ease:"sine.inOut",transformOrigin:"50% 50%"}},{s + .5:.2f});')
    E0 = MAIN
    html = f"""<!doctype html>
<html lang="kk"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family:"InterK"; font-weight:600; src:url("assets/fonts/Inter-SemiBold.otf"); }}
@font-face {{ font-family:"InterK"; font-weight:800; src:url("assets/fonts/Inter-ExtraBold.otf"); }}
@font-face {{ font-family:"InterK"; font-weight:900; src:url("assets/fonts/Inter-Black.otf"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:#141414; }}
#root {{ position:relative; width:100%; height:100%; font-family:"InterK",sans-serif; }}
#main {{ position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover; }}
.cap {{ position:absolute; left:60px; right:150px; top:1350px; height:150px; display:flex; align-items:center; justify-content:center; }}
.cap-in {{ text-align:center; font-weight:900; font-size:56px; line-height:1.15; color:#fff;
  text-shadow:0 4px 0 #141414, 0 0 14px rgba(0,0,0,.85), 3px 0 0 #141414, -3px 0 0 #141414; }}
.card {{ position:absolute; left:50px; right:150px; top:1195px; height:150px; }}
.card-in {{ display:inline-flex; align-items:center; gap:22px; padding:14px 30px 14px 14px; border-radius:26px;
  background:rgba(20,20,20,.86); border-left:10px solid #d9825b; }}
.ic {{ flex:0 0 104px; height:104px; border-radius:50%; background:#d9825b; display:flex; align-items:center; justify-content:center; }}
.l1 {{ font-weight:600; font-size:38px; color:#f0e4dc; }} .l2 {{ font-weight:900; font-size:52px; color:#fff; }}
#end {{ position:absolute; inset:0; }}
#e-bg {{ position:absolute; inset:0; background:radial-gradient(circle at 50% 40%, #3a2418 0%, #161311 55%, #0f0d0c 100%); }}
#e-name {{ position:absolute; left:0; right:0; top:560px; text-align:center; font-weight:900; font-size:124px; letter-spacing:6px; color:#fff; }}
#e-name span {{ color:#d9825b; }}
#e-sub {{ position:absolute; left:0; right:0; top:730px; text-align:center; font-weight:600; font-size:54px; color:#e6d7cc; }}
#e-list {{ position:absolute; left:0; right:0; top:840px; text-align:center; font-weight:900; font-size:44px; color:#d9825b; letter-spacing:2px; }}
#e-cta {{ position:absolute; left:190px; top:980px; width:700px; height:116px; border-radius:58px; background:#d9825b; color:#141414;
  font-weight:900; font-size:56px; display:flex; align-items:center; justify-content:center; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
<video id="main" class="clip" src="assets/video/main.mp4" data-start="0" data-duration="{MAIN}" data-track-index="0" data-has-audio="true" data-volume="1" playsinline style="z-index:1"></video>
{chr(10).join(body)}
<div id="end" class="clip" data-start="{E0}" data-duration="{END}" data-track-index="4" style="z-index:40">
  <div id="e-bg"></div>
  <div id="e-name">ERXAN <span>MEBEL</span></div>
  <div id="e-sub">Уақытылы · сапалы · жауапкершілікпен</div>
  <div id="e-list">КУХНЯ · ШКАФ · ГАРДЕРОБ</div>
  <div id="e-cta">Директке жазыңыз</div>
</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused:true }});
{chr(10).join(js)}
tl.fromTo("#e-bg",{{opacity:0}},{{opacity:1,duration:.3}},{E0});
tl.fromTo("#e-name",{{scale:1.5,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"power4.out"}},{E0 + .15});
tl.fromTo("#e-sub",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"power3.out"}},{E0 + .45});
tl.fromTo("#e-list",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"power3.out"}},{E0 + .65});
tl.fromTo("#e-cta",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"back.out(2)"}},{E0 + .9});
tl.to("#e-cta",{{scale:1.07,duration:.3,yoyo:true,repeat:3,ease:"sine.inOut"}},{E0 + 1.4});
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    (HERE / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    import sys
    if "--no-cut" not in sys.argv:
        cut_footage()
    page()
    print("ok total", TOTAL)
