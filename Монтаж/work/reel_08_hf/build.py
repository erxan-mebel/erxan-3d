"""Reel 08: wardrobe tour — cut footage + Kazakh captions + icon cards + end card (HyperFrames)."""
from pathlib import Path

SEGS = [(0.0, 9.4), (10.6, 12.8), (18.8, 29.9), (30.9, 53.0), (58.5, 68.3)]
offs, acc = [], 0.0
for s, e in SEGS:
    offs.append(acc)
    acc += e - s
MAIN = round(acc, 2)
END = 3.4
TOTAL = round(MAIN + END, 2)


def cut(t):
    for (s, e), o in zip(SEGS, offs):
        if s <= t <= e:
            return round(o + t - s, 2)
    for (s, e), o in zip(SEGS, offs):
        if t < s:
            return round(o, 2)
    return MAIN


# captions in SOURCE time
CAPS = [
    (0.0, 2.5, "Бұл клиентіміздің гардеробының мебелін жасап жатырмыз."),
    (2.5, 5.6, "Өрнектері бәрі бірдей — көрсетейін."),
    (6.1, 9.3, "Мінеки, шкафымыз — төрт есікті."),
    (10.7, 12.7, "Стилі — модерн."),
    (22.1, 24.3, "Жан-жағынан планка қойған жоқпыз,"),
    (24.3, 26.0, "біреуінің бетіне ғана планка қойдық."),
    (26.0, 29.8, "Кейін келесісін, ішкі бөлігін көрсетемін."),
    (30.9, 34.3, "Мынау — прихожка, жанына планка салдық."),
    (34.9, 37.6, "«Планканы не үшін қоясыздар?» деп сұрайды."),
    (37.8, 40.0, "Қараңыздар:"),
    (40.7, 43.4, "асты 1,5 сантиметр, үсті 3 сантиметр —"),
    (43.4, 46.0, "стенасы қисық."),
    (46.0, 49.8, "Сондықтан мына планканы"),
    (49.9, 52.9, "орнында подгонка жасап кесеміз."),
    (58.6, 60.0, "Төрт есікті болды."),
    (60.1, 63.9, "Үсті push арқылы, асты ручкамен ашылады."),
    (66.2, 68.2, "Мынау — суырмасы."),
]
WRENCH = '<path d="M44 8a12 12 0 0 0-11 16L10 47a5 5 0 0 0 7 7l23-23a12 12 0 0 0 16-11l-7 4-6-3-1-7z" fill="#141414"/>'
DOORS = '<g fill="none" stroke="#141414" stroke-width="4"><rect x="6" y="8" width="52" height="48" rx="3"/><line x1="19" y1="8" x2="19" y2="56"/><line x1="32" y1="8" x2="32" y2="56"/><line x1="45" y1="8" x2="45" y2="56"/></g>'
ARCH = '<path d="M14 56V26a18 18 0 0 1 36 0v30z" fill="none" stroke="#141414" stroke-width="5"/><line x1="10" y1="56" x2="54" y2="56" stroke="#141414" stroke-width="5"/>'
RULER = '<rect x="4" y="22" width="56" height="20" rx="3" fill="#141414"/><g stroke="#d9825b" stroke-width="3">' + "".join(f'<line x1="{10 + i * 8}" y1="22" x2="{10 + i * 8}" y2="{32 if i % 2 else 36}"/>' for i in range(7)) + '</g>'
PUSH = '<circle cx="32" cy="32" r="22" fill="none" stroke="#141414" stroke-width="5"/><path d="M32 18v20M24 30l8 8 8-8" stroke="#141414" stroke-width="5" fill="none" stroke-linecap="round"/>'
DRAWER = '<rect x="6" y="14" width="52" height="36" rx="4" fill="none" stroke="#141414" stroke-width="5"/><rect x="24" y="28" width="16" height="6" rx="3" fill="#141414"/>'
# cards in CUT time (start, end, line1, line2, icon, action)
CARDS = [
    (cut(6.1), cut(9.4) - 0.05, "Гардероб", "4 есікті", DOORS, "pulse"),
    (cut(19.0), cut(22.0), "Фасад", "арка өрнекті", ARCH, "pop"),
    (cut(41.0), cut(46.0), "Саңылау", "асты 1,5 см · үсті 3 см", RULER, "slide"),
    (cut(46.2), cut(52.9), "Стена қисық", "планка — подгонкамен", WRENCH, "pulse"),
    (cut(60.1), cut(64.0), "Үсті — push", "асты — ручка", PUSH, "pulse"),
    (cut(66.0), MAIN - 0.05, "Суырма", "доводчикпен", DRAWER, "pop"),
]

body, js = [], []
for i, (s, e, t) in enumerate(CAPS):
    a, b = cut(s), cut(e)
    if b - a < 0.3:
        continue
    body.append(f'<div id="c{i}" class="clip cap" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="2" style="z-index:30">'
                f'<div id="c{i}-in" class="cap-in">{t}</div></div>')
    js.append(f'tl.fromTo("#c{i}-in",{{y:14,opacity:0}},{{y:0,opacity:1,duration:.16,ease:"power2.out"}},{a});')
for i, (s, e, l1, l2, ic, act) in enumerate(CARDS):
    body.append(f'<div id="k{i}" class="clip card" data-start="{s}" data-duration="{e - s:.2f}" data-track-index="3" style="z-index:20">'
                f'<div id="k{i}-in" class="card-in"><div id="k{i}-ic" class="ic"><svg id="k{i}-svg" viewBox="0 0 64 64" width="80" height="80">{ic}</svg></div>'
                f'<div class="tx"><div class="l1">{l1}</div><div class="l2">{l2}</div></div></div></div>')
    js.append(f'tl.fromTo("#k{i}-in",{{x:-120,opacity:0}},{{x:0,opacity:1,duration:.4,ease:"back.out(1.7)"}},{s});')
    js.append(f'tl.fromTo("#k{i}-ic",{{scale:0,rotation:-120}},{{scale:1,rotation:0,duration:.4,ease:"back.out(2)"}},{s + .08:.2f});')
    js.append(f'tl.to("#k{i}-in",{{opacity:0,x:50,duration:.22,ease:"power2.in"}},{e - .26:.2f});')
    if act == "pulse":
        js.append(f'tl.fromTo("#k{i}-svg",{{scale:1}},{{scale:1.15,duration:.25,yoyo:true,repeat:3,ease:"sine.inOut",transformOrigin:"50% 50%"}},{s + .5:.2f});')
    if act == "slide":
        js.append(f'tl.fromTo("#k{i}-svg",{{x:-6}},{{x:6,duration:.3,yoyo:true,repeat:5,ease:"sine.inOut"}},{s + .5:.2f});')

E0 = MAIN
page = f"""<!doctype html>
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
.cap {{ position:absolute; left:60px; right:150px; top:1240px; height:150px; display:flex; align-items:center; justify-content:center; }}
.cap-in {{ text-align:center; font-weight:900; font-size:58px; line-height:1.15; color:#fff;
  text-shadow:0 4px 0 #141414, 0 0 14px rgba(0,0,0,.85), 3px 0 0 #141414, -3px 0 0 #141414; }}
.card {{ position:absolute; left:50px; right:150px; top:1040px; height:160px; }}
.card-in {{ display:inline-flex; align-items:center; gap:22px; padding:16px 30px 16px 16px; border-radius:26px;
  background:rgba(20,20,20,.85); border-left:10px solid #d9825b; }}
.ic {{ flex:0 0 112px; height:112px; border-radius:50%; background:#d9825b; display:flex; align-items:center; justify-content:center; }}
.l1 {{ font-weight:600; font-size:40px; color:#f0e4dc; }} .l2 {{ font-weight:900; font-size:52px; color:#fff; }}
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
  <div id="e-sub">Шкаф · гардероб тапсырыс бойынша</div>
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
Path(__file__).with_name("index.html").write_text(page, encoding="utf-8")
print("ok total", TOTAL, "cards at", [c[0] for c in CARDS])
