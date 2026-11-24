"""Reel 10: «Ас үйдегі қымбат қателіктер» — 3 photo pairs, ❌ → ✅ wipe (HyperFrames)."""
from pathlib import Path

PAIRS = [
    ("1", "Үстелге плинтус", "Кафель тура үстелге", "50% 50%", "50% 60%"),
    ("2", "Үстінен салынған мойка", "Астынан орнатылған мойка", "50% 60%", "22% 50%"),
    ("3", "Шкаф төбеге жетпейді", "Шкаф төбеге дейін", "50% 45%", "50% 40%"),
]
INTRO, STEP, END = 1.6, 4.6, 3.2
MAIN = INTRO + STEP * len(PAIRS)
TOTAL = round(MAIN + END, 2)
X = '<path d="M20 20 80 80M80 20 20 80" stroke="#fff" stroke-width="14" stroke-linecap="round" fill="none"/>'
CHECK = '<path id="{id}" d="M18 54 40 76 84 26" stroke="#fff" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" fill="none" stroke-dasharray="110" stroke-dashoffset="110"/>'

body, js = [], []
for i, (n, bad, good, pb, pg) in enumerate(PAIRS):
    t0 = INTRO + i * STEP
    bs = 0 if i == 0 else t0 - 0.35
    body.append(f'<div id="b{n}" class="clip ph" data-start="{bs:.2f}" data-duration="{t0 + 2.6 - bs:.2f}" data-track-index="0" style="z-index:{2 * i + 1}">'
                f'<div id="b{n}-in" class="ph-in" style="background-image:url(assets/img/{n}_bad.jpg);background-position:{pb}"></div></div>')
    body.append(f'<div id="g{n}" class="clip ph" data-start="{t0 + 2.2:.2f}" data-duration="{STEP - 2.2 + .4:.2f}" data-track-index="1" style="z-index:{2 * i + 2}">'
                f'<div id="g{n}-in" class="ph-in" style="background-image:url(assets/img/{n}_good.jpg);background-position:{pg}"></div></div>')
    body.append(f'<div id="x{n}" class="clip mark" data-start="{t0 + .3:.2f}" data-duration="1.95" data-track-index="2" style="z-index:30">'
                f'<div id="x{n}-in" class="mark-in bad"><svg viewBox="0 0 100 100" width="120" height="120">{X}</svg></div></div>')
    body.append(f'<div id="v{n}" class="clip mark" data-start="{t0 + 2.5:.2f}" data-duration="1.95" data-track-index="2" style="z-index:30">'
                f'<div id="v{n}-in" class="mark-in good"><svg viewBox="0 0 100 100" width="120" height="120">{CHECK.format(id=f"v{n}-p")}</svg></div></div>')
    body.append(f'<div id="cb{n}" class="clip cap" data-start="{t0 + .3:.2f}" data-duration="1.95" data-track-index="3" style="z-index:31">'
                f'<div id="cb{n}-in" class="cap-in"><span class="num">{n}</span>{bad}</div></div>')
    body.append(f'<div id="cg{n}" class="clip cap" data-start="{t0 + 2.5:.2f}" data-duration="1.95" data-track-index="3" style="z-index:31">'
                f'<div id="cg{n}-in" class="cap-in"><span class="num ok">{n}</span>{good}</div></div>')
    js += [
        f'tl.fromTo("#b{n}-in",{{scale:1.0}},{{scale:1.08,duration:{t0 + 2.6 - bs:.2f},ease:"none"}},{bs:.2f});',
        f'tl.fromTo("#g{n}-in",{{clipPath:"inset(0% 100% 0% 0%)",scale:1.06}},{{clipPath:"inset(0% 0% 0% 0%)",scale:1.0,duration:.45,ease:"power3.inOut"}},{t0 + 2.2:.2f});',
        f'tl.to("#g{n}-in",{{scale:1.06,duration:2.2,ease:"none"}},{t0 + 2.65:.2f});',
        f'tl.fromTo("#x{n}-in",{{scale:2.2,opacity:0,rotation:-25}},{{scale:1,opacity:1,rotation:0,duration:.3,ease:"power4.in"}},{t0 + .3:.2f});',
        f'tl.fromTo("#x{n}-in",{{x:-8}},{{x:8,duration:.06,yoyo:true,repeat:5,ease:"none"}},{t0 + .62:.2f});',
        f'tl.fromTo("#v{n}-in",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},{t0 + 2.5:.2f});',
        f'tl.fromTo("#v{n}-p",{{strokeDashoffset:110}},{{strokeDashoffset:0,duration:.4,ease:"power2.out"}},{t0 + 2.65:.2f});',
        f'tl.fromTo("#cb{n}-in",{{y:24,opacity:0}},{{y:0,opacity:1,duration:.25,ease:"power3.out"}},{t0 + .35:.2f});',
        f'tl.fromTo("#cg{n}-in",{{y:24,opacity:0}},{{y:0,opacity:1,duration:.25,ease:"power3.out"}},{t0 + 2.55:.2f});',
    ]

page = f"""<!doctype html>
<html lang="kk"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family:"InterK"; font-weight:600; src:url("assets/fonts/Inter-SemiBold.otf"); }}
@font-face {{ font-family:"InterK"; font-weight:800; src:url("assets/fonts/Inter-ExtraBold.otf"); }}
@font-face {{ font-family:"InterK"; font-weight:900; src:url("assets/fonts/Inter-Black.otf"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:#141414; }}
#root {{ position:relative; width:100%; height:100%; font-family:"InterK",sans-serif; overflow:hidden; }}
.ph {{ position:absolute; inset:0; overflow:hidden; }}
.ph-in {{ position:absolute; inset:0; background-size:cover; background-repeat:no-repeat; }}
#shade {{ position:absolute; left:0; right:0; bottom:0; height:900px; z-index:20;
  background:linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.35) 45%, rgba(0,0,0,.6) 100%); }}
#title {{ position:absolute; left:0; right:0; top:1000px; text-align:center; z-index:32; }}
#title-in {{ display:inline-block; font-weight:900; font-size:54px; color:#fff; letter-spacing:1px; padding:10px 28px; border-radius:16px;
  background:rgba(20,20,20,.55); }}
#title-in b {{ color:#f1c232; }}
.mark {{ position:absolute; left:0; right:0; top:820px; height:160px; display:flex; justify-content:center; }}
.mark-in {{ width:150px; height:150px; border-radius:30px; display:flex; align-items:center; justify-content:center; box-shadow:0 10px 30px rgba(0,0,0,.35); }}
.mark-in.bad {{ background:#d9342b; }} .mark-in.good {{ background:#2f9e55; }}
.cap {{ position:absolute; left:60px; right:150px; top:1110px; height:180px; display:flex; align-items:center; justify-content:center; }}
.cap-in {{ display:flex; align-items:center; gap:22px; font-weight:900; font-size:62px; line-height:1.1; color:#fff; text-align:left;
  text-shadow:0 4px 0 #141414, 0 0 16px rgba(0,0,0,.8); }}
.num {{ flex:0 0 84px; height:84px; border-radius:50%; background:#d9342b; display:flex; align-items:center; justify-content:center;
  font-size:52px; text-shadow:none; }} .num.ok {{ background:#2f9e55; }}
#intro {{ position:absolute; left:60px; right:60px; top:640px; text-align:center; z-index:35; }}
#intro-in {{ font-weight:900; font-size:118px; line-height:1.02; color:#fff; text-shadow:0 6px 0 #141414, 0 0 30px rgba(0,0,0,.7); }}
#intro-in span {{ color:#f1c232; }}
#end {{ position:absolute; inset:0; }}
#e-bg {{ position:absolute; inset:0; background:radial-gradient(circle at 50% 40%, #3a2418 0%, #161311 55%, #0f0d0c 100%); }}
#e-q {{ position:absolute; left:0; right:0; top:470px; text-align:center; font-weight:900; font-size:64px; color:#f1c232; line-height:1.15; }}
#e-name {{ position:absolute; left:0; right:0; top:690px; text-align:center; font-weight:900; font-size:124px; letter-spacing:6px; color:#fff; }}
#e-name span {{ color:#d9825b; }}
#e-sub {{ position:absolute; left:0; right:0; top:860px; text-align:center; font-weight:600; font-size:54px; color:#e6d7cc; }}
#e-cta {{ position:absolute; left:190px; top:990px; width:700px; height:116px; border-radius:58px; background:#d9825b; color:#141414;
  font-weight:900; font-size:56px; display:flex; align-items:center; justify-content:center; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(body)}
<div id="shade" class="clip" data-start="0" data-duration="{MAIN:.2f}" data-track-index="4"></div>
<div id="intro" class="clip" data-start="0" data-duration="{INTRO + .2:.2f}" data-track-index="5"><div id="intro-in">Ас үйдегі<br><span>қымбат</span><br>қателіктер</div></div>
<div id="title" class="clip" data-start="{INTRO:.2f}" data-duration="{MAIN - INTRO:.2f}" data-track-index="6"><div id="title-in">Ас үйдегі <b>қымбат</b> қателіктер</div></div>
<div id="end" class="clip" data-start="{MAIN:.2f}" data-duration="{END}" data-track-index="7" style="z-index:40">
  <div id="e-bg"></div>
  <div id="e-q">Ас үйді<br>қателіксіз жасаймыз</div>
  <div id="e-name">ERXAN <span>MEBEL</span></div>
  <div id="e-sub">Ас үй тапсырыс бойынша · Астана</div>
  <div id="e-cta">Директке жазыңыз</div>
</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused:true }});
tl.fromTo("#intro-in",{{scale:1.4,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"power4.out"}},0.05);
tl.to("#intro-in",{{opacity:0,y:-40,duration:.25,ease:"power2.in"}},{INTRO - .2:.2f});
tl.fromTo("#title-in",{{y:20,opacity:0}},{{y:0,opacity:1,duration:.3,ease:"power3.out"}},{INTRO:.2f});
{chr(10).join(js)}
tl.fromTo("#e-bg",{{opacity:0}},{{opacity:1,duration:.3}},{MAIN:.2f});
tl.fromTo("#e-q",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"power3.out"}},{MAIN + .1:.2f});
tl.fromTo("#e-name",{{scale:1.5,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"power4.out"}},{MAIN + .35:.2f});
tl.fromTo("#e-sub",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"power3.out"}},{MAIN + .6:.2f});
tl.fromTo("#e-cta",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"back.out(2)"}},{MAIN + .85:.2f});
tl.to("#e-cta",{{scale:1.07,duration:.3,yoyo:true,repeat:3,ease:"sine.inOut"}},{MAIN + 1.35:.2f});
window.__timelines["main"] = tl;
</script>
</body></html>
"""
Path(__file__).with_name("index.html").write_text(page, encoding="utf-8")
print("ok total", TOTAL)
