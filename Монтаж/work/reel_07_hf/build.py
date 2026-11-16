"""Reel 07: «Қымбат стол арзанға түседі» — animated explainer (HyperFrames).

Generates index.html. Run: python3 build.py  (inside this folder), then npx hyperframes render.
"""
from pathlib import Path

W, H = 1080, 1920
INK, PAPER, RED, GREEN, COPPER, MUTE = "#3b2a1e", "#f3ead9", "#c0533a", "#4f8a57", "#d9825b", "#8c7a68"


def desk(w=360, worn=False, color="#d9b98c", body="#efe6d8"):
    """Simple desk SVG (top, left panel, right cabinet with door)."""
    h = w * 0.62
    top_y = 0
    t = w * 0.06
    rot = ' transform="rotate(-4 0 0)"' if worn else ""
    door_tf = f' transform="rotate(-18 {w*0.62} {t})"' if worn else ""
    cracks = (f'<path d="M{w*0.2} {t*0.4} l20 6 l-8 8 l24 4" stroke="{INK}" stroke-width="3" fill="none"/>'
              f'<path d="M{w*0.06} {h*0.5} l10 18 l-6 14" stroke="{INK}" stroke-width="3" fill="none"/>') if worn else ""
    return (f'<svg viewBox="-20 -20 {w+40} {h+40}" width="{w}" height="{h}">'
            f'<ellipse cx="{w/2}" cy="{h+4}" rx="{w*0.48}" ry="10" fill="#000" opacity=".12"/>'
            f'<g{rot}>'
            f'<rect x="{w*0.04}" y="{t}" width="{w*0.08}" height="{h-t}" fill="{body}" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{w*0.6}" y="{t}" width="{w*0.36}" height="{h-t}" fill="{body}" stroke="{INK}" stroke-width="3"/>'
            f'<g{door_tf}><rect x="{w*0.62}" y="{t+h*0.18}" width="{w*0.32}" height="{h*0.74}" fill="{body}" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{w*0.66}" y="{t+h*0.5}" width="6" height="{h*0.14}" rx="3" fill="{INK}"/></g>'
            f'<rect x="{w*0.62}" y="{t+h*0.04}" width="{w*0.32}" height="{h*0.12}" fill="{body}" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="0" y="{top_y}" width="{w}" height="{t}" rx="4" fill="{color}" stroke="{INK}" stroke-width="3"/>'
            f'{cracks}</g></svg>')


def board(dense):
    """Chipboard cross-section: loose (big chips) or dense."""
    import random
    rnd = random.Random(3 if dense else 7)
    dots = "".join(
        f'<circle cx="{rnd.uniform(8, 332):.0f}" cy="{rnd.uniform(18, 92):.0f}" r="{rnd.uniform(1.5, 3) if dense else rnd.uniform(3, 9):.1f}" fill="{"#b48a5a" if dense else "#9b6b3f"}" opacity=".8"/>'
        for _ in range(140 if dense else 45))
    return (f'<svg viewBox="0 0 340 110" width="340" height="110"><rect x="0" y="0" width="340" height="12" fill="#e9d2a8" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="0" y="12" width="340" height="86" fill="{"#d8b98a" if dense else "#e4c79c"}" stroke="{INK}" stroke-width="3"/>{dots}'
            f'<rect x="0" y="98" width="340" height="12" fill="#e9d2a8" stroke="{INK}" stroke-width="3"/></svg>')


def edge(thick):
    e = 22 if thick else 6
    return (f'<svg viewBox="0 0 340 140" width="340" height="140"><rect x="0" y="10" width="300" height="90" fill="#e4c79c" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="300" y="10" width="{e}" height="90" fill="{COPPER}" stroke="{INK}" stroke-width="3"/>'
            f'<text x="150" y="134" font-size="30" text-anchor="middle" fill="{INK}" font-family="InterK" font-weight="800">{"қалың" if thick else "жұқа"}</text></svg>')


def drawer(good):
    return (f'<svg viewBox="0 0 340 150" width="340" height="150"><rect x="20" y="20" width="300" height="90" rx="6" fill="#efe6d8" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="150" y="55" width="40" height="8" rx="4" fill="{INK}"/>'
            f'<rect x="10" y="120" width="320" height="14" rx="7" fill="{"#a7b0b6" if good else "#cfc6b8"}" stroke="{INK}" stroke-width="3"/>'
            + "".join(f'<circle cx="{40 + i * 40}" cy="127" r="4" fill="{INK}"/>' for i in range(8 if good else 3)) + "</svg>")


def calendar(n):
    return (f'<svg viewBox="0 0 200 210" width="200" height="210"><rect x="10" y="30" width="180" height="170" rx="16" fill="#fff" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="10" y="30" width="180" height="46" rx="16" fill="{RED}" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="50" y="10" width="12" height="40" rx="6" fill="{INK}"/><rect x="138" y="10" width="12" height="40" rx="6" fill="{INK}"/>'
            f'<text x="100" y="168" font-size="90" text-anchor="middle" fill="{INK}" font-family="InterK" font-weight="900">{n}</text></svg>')


# ------------------------------------------------------------------ timeline
# captions: (start, end, text)
CAPS = [
    (0.3, 3.3, "Қымбат деп ойлаған жиһазыңыз шын мәнінде арзанға түседі."),
    (3.4, 6.0, "Ал арзан деп алғаныңыз — қымбатқа."),
    (6.1, 9.0, "Сенбейсіз бе? Соңына дейін көріңіз."),
    (9.2, 12.0, "Мына екі стол сырттай бірдей."),
    (12.1, 15.0, "Бірақ біреуі екі есе қымбат."),
    (15.1, 17.4, "Бұл ақша қайда кетеді?"),
    (17.6, 20.0, "Бірінші айырма — плитада."),
    (20.1, 23.0, "Тығыз плита ылғалдан ісінбейді."),
    (23.1, 27.4, "Оған бұралған бұрандалар жылдар өтсе де босамайды."),
    (27.6, 31.0, "Сосын кромка — жиһаздың шетіне жапсырылатын лента."),
    (31.1, 33.6, "Қалың кромка соққыға шыдайды."),
    (33.7, 36.8, "Жұқасы әдетте бірінші болып көшеді."),
    (37.0, 41.0, "Тартпалар мен есіктер мыңдаған рет ашылып-жабылады."),
    (41.1, 44.6, "Бұл жүкті сапалы рельстер мен петлялар көтереді."),
    (44.7, 47.6, "Арзандары тез бұзылады."),
    (47.8, 50.2, "Ең соңғысы — шебердің еңбегі."),
    (50.3, 53.6, "Әр деталь миллиметрге дейін дәл кесілсе,"),
    (53.7, 57.6, "есіктер тегіс жабылады, бұрыштар бірдей шығады."),
    (57.8, 60.2, "Енді 2 жыл өтті делік."),
    (60.3, 62.8, "Арзан стол мына күйге келеді."),
    (62.9, 65.8, "Сапалысы — бірінші күндегідей."),
    (66.0, 68.4, "Енді есептейік."),
    (68.5, 71.6, "Арзан стол 2 жылда істен шықты —"),
    (71.7, 74.6, "жылына 45 000 ₸-ге түсті."),
    (74.7, 78.6, "Сапалы стол 10 жыл қызмет етеді — жылына 18 000 ₸."),
    (78.7, 81.8, "10 жылда арзан столды 5 рет ауыстырасыз —"),
    (81.9, 84.4, "450 000 ₸ жұмсайсыз."),
    (84.5, 87.6, "Сапалысы 180 000 ₸ — бір-ақ рет алынады."),
    (87.8, 90.8, "Қайсысы арзан екенін енді өзіңіз көрдіңіз."),
    (90.9, 94.8, "Директке өлшеміңізді жазыңыз — бағасын есептеп береміз."),
]
TOTAL = 96.0

# scenes: (id, start, end, inner html, gsap lines using T(t) offsets inside scene)
scenes = []


def scene(sid, start, end, html, js):
    scenes.append((sid, start, end, html, js))


def price(sid, a, b):
    return (f'<div id="{sid}-pr" class="price"><span class="pa">{a}</span> <span class="arrow">→</span> '
            f'<span class="pb">{b}</span> <span class="cur">₸</span></div>')


def compare(sid, title, left, right, pa, pb, extra_js=""):
    html = (f'<div id="{sid}-t" class="title">{title}</div>'
            f'<div class="cols"><div id="{sid}-l" class="col"><div class="lbl bad">АРЗАН</div>{left}</div>'
            f'<div class="divider"></div>'
            f'<div id="{sid}-r" class="col"><div class="lbl good">САПАЛЫ</div>{right}</div></div>'
            + price(sid, pa, pb))
    js = (f'tl.fromTo("#{sid}-t",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"power3.out"}},S+.1);'
          f'tl.fromTo("#{sid}-l",{{x:-80,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"back.out(1.6)"}},S+.4);'
          f'tl.fromTo("#{sid}-r",{{x:80,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"back.out(1.6)"}},S+.7);'
          f'tl.fromTo("#{sid}-pr",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"back.out(2)"}},S+1.6);'
          + extra_js)
    return html, js


# 1. hook
scene("s1", 0, 9.1,
      f'<div class="pair" style="position:relative"><div id="s1-a" class="dk">{desk()}</div><div id="s1-b" class="dk">{desk()}</div>'
      f'<div id="s1-sa" class="stamp good" style="left:180px">ҚЫМБАТ</div><div id="s1-sb" class="stamp bad" style="left:600px">АРЗАН</div></div>'
      f'<div id="s1-q" class="big">Қайсысы<br>арзан?</div>',
      'tl.fromTo("#s1-a",{y:120,opacity:0},{y:0,opacity:1,duration:.6,ease:"back.out(1.5)"},S+.0);'
      'tl.fromTo("#s1-b",{y:120,opacity:0},{y:0,opacity:1,duration:.6,ease:"back.out(1.5)"},S+.25);'
      'tl.fromTo("#s1-sa",{scale:2.4,opacity:0,rotation:-20},{scale:1,opacity:1,rotation:-6,duration:.35,ease:"power4.in"},S+1.0);'
      'tl.fromTo("#s1-sb",{scale:2.4,opacity:0,rotation:20},{scale:1,opacity:1,rotation:5,duration:.35,ease:"power4.in"},S+1.5);'
      'tl.to("#s1-sa",{x:420,duration:.6,ease:"power2.inOut"},S+3.6);'
      'tl.to("#s1-sb",{x:-420,duration:.6,ease:"power2.inOut"},S+3.6);'
      'tl.fromTo("#s1-q",{scale:.6,opacity:0},{scale:1,opacity:1,duration:.4,ease:"back.out(2)"},S+6.1);')

# 2. price tags
tag = lambda sid, v, c: (f'<div id="{sid}" class="tag"><svg viewBox="0 0 220 300" width="220" height="300">'
                         f'<path d="M110 10 C 90 40, 130 60, 110 90" stroke="{INK}" stroke-width="4" fill="none"/>'
                         f'<path d="M40 90 h140 l20 30 v160 h-180 v-160 z" fill="#fffaf0" stroke="{INK}" stroke-width="5"/>'
                         f'<circle cx="110" cy="118" r="10" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>'
                         f'<text x="110" y="205" font-size="40" text-anchor="middle" fill="{c}" font-family="InterK" font-weight="900">{v}</text>'
                         f'<text x="110" y="245" font-size="30" text-anchor="middle" fill="{INK}" font-family="InterK" font-weight="800">₸</text></svg></div>')
scene("s2", 9.1, 17.5,
      f'<div class="pair tags">{tag("s2-ta", "90 000", RED)}{tag("s2-tb", "180 000", GREEN)}</div>'
      f'<div class="pair"><div class="dk">{desk(300)}</div><div class="dk">{desk(300)}</div></div>'
      f'<div id="s2-q" class="big">Ақша<br>қайда кетеді?</div>',
      'tl.fromTo("#s2-ta",{y:-400,rotation:-25},{y:0,rotation:0,duration:1,ease:"elastic.out(1,.45)"},S+.1);'
      'tl.fromTo("#s2-tb",{y:-400,rotation:25},{y:0,rotation:0,duration:1,ease:"elastic.out(1,.45)"},S+.5);'
      'tl.fromTo("#s2-q",{scale:.6,opacity:0},{scale:1,opacity:1,duration:.4,ease:"back.out(2)"},S+6.0);')

h, j = compare("s3", "1. ПЛИТА", board(False), board(True), "45 000", "75 000")
scene("s3", 17.5, 27.5, h, j)
h, j = compare("s4", "2. КРОМКА", edge(False), edge(True), "5 000", "15 000")
scene("s4", 27.5, 36.9, h, j)
h, j = compare("s5", "3. ФУРНИТУРА",
               f'{drawer(False)}<div id="s5-cl" class="cnt bad">×140</div>',
               f'{drawer(True)}<div id="s5-cr" class="cnt good">×5 000</div>', "10 000", "40 000",
               'tl.fromTo("#s5-cl",{opacity:0,scale:.5},{opacity:1,scale:1,duration:.4,ease:"back.out(2)"},S+3.0);'
               'tl.fromTo("#s5-cr",{opacity:0,scale:.5},{opacity:1,scale:1,duration:.4,ease:"back.out(2)"},S+3.4);')
scene("s5", 36.9, 47.7, h, j)
scene("s6", 47.7, 57.7,
      f'<div id="s6-t" class="title">4. ЕҢБЕК</div>'
      f'<div id="s6-d" class="solo">{desk(520)}<div id="s6-mm" class="mm">← 3 мм →</div></div>'
      + price("s6", "30 000", "50 000"),
      'tl.fromTo("#s6-t",{y:-40,opacity:0},{y:0,opacity:1,duration:.4,ease:"power3.out"},S+.1);'
      'tl.fromTo("#s6-d",{scale:.8,opacity:0},{scale:1,opacity:1,duration:.5,ease:"back.out(1.6)"},S+.4);'
      'tl.fromTo("#s6-mm",{scaleX:0},{scaleX:1,duration:.5,ease:"power3.out"},S+2.8);'
      'tl.fromTo("#s6-pr",{scale:.5,opacity:0},{scale:1,opacity:1,duration:.45,ease:"back.out(2)"},S+1.6);')
scene("s7", 57.7, 65.9,
      f'<div id="s7-c" class="cal">{calendar(2)}<div class="big small">2 ЖЫЛДАН КЕЙІН</div></div>'
      f'<div class="pair"><div id="s7-a" class="dk"><div class="lbl bad">АРЗАН</div>{desk(330, worn=True, color="#c9a678", body="#e2d6c2")}</div>'
      f'<div id="s7-b" class="dk"><div class="lbl good">САПАЛЫ</div>{desk(330)}</div></div>',
      'tl.fromTo("#s7-c",{scale:.4,opacity:0},{scale:1,opacity:1,duration:.5,ease:"back.out(2)"},S+.1);'
      'tl.fromTo("#s7-a",{y:100,opacity:0},{y:0,opacity:1,duration:.5,ease:"power3.out"},S+2.6);'
      'tl.fromTo("#s7-a",{rotation:0},{rotation:-3,duration:.15,yoyo:true,repeat:5,ease:"sine.inOut"},S+3.2);'
      'tl.fromTo("#s7-b",{y:100,opacity:0},{y:0,opacity:1,duration:.5,ease:"power3.out"},S+5.2);')
scene("s8", 65.9, 87.7,
      f'<div id="s8-r1" class="calc"><span class="bad">90 000 ₸</span> ÷ 2 жыл = <b id="s8-v1" class="bad">45 000 ₸</b><span class="per">/жыл</span></div>'
      f'<div id="s8-r2" class="calc"><span class="good">180 000 ₸</span> ÷ 10 жыл = <b id="s8-v2" class="good">18 000 ₸</b><span class="per">/жыл</span></div>'
      f'<div id="s8-line" class="tline">'
      + "".join(f'<div id="s8-d{i}" class="mini">{desk(130, color="#d9b98c")}</div>' for i in range(5))
      + '<div class="axis">' + "".join(f'<span>{n}</span>' for n in (0, 2, 4, 6, 8, 10)) + '</div></div>'
      f'<div id="s8-sum" class="sum"><span class="bad">450 000 ₸</span><span class="vs">vs</span><span class="good">180 000 ₸</span></div>',
      'tl.fromTo("#s8-r1",{x:-120,opacity:0},{x:0,opacity:1,duration:.5,ease:"power3.out"},S+2.6);'
      'tl.fromTo("#s8-v1",{scale:1.2},{scale:1,duration:.4,ease:"back.out(2)"},S+5.8);'
      'tl.fromTo("#s8-r2",{x:-120,opacity:0},{x:0,opacity:1,duration:.5,ease:"power3.out"},S+8.8);'
      + "".join(f'tl.fromTo("#s8-d{i}",{{y:-200,opacity:0}},{{y:0,opacity:1,duration:.45,ease:"bounce.out"}},S+{12.9 + i * 0.45:.2f});' for i in range(5))
      + 'tl.fromTo("#s8-sum",{scale:.5,opacity:0},{scale:1,opacity:1,duration:.5,ease:"back.out(2)"},S+16.0);')
scene("s9", 87.7, TOTAL,
      f'<div id="s9-q" class="big">Қайсысы арзан?</div>'
      f'<div id="s9-d" class="solo">{desk(420)}</div>'
      f'<div id="s9-n" class="brand">ERXAN <span>MEBEL</span></div>'
      f'<div id="s9-h" class="handle">@erxan_mebel</div>'
      f'<div id="s9-c" class="cta">Директке жазыңыз</div>',
      'tl.fromTo("#s9-q",{y:-40,opacity:0},{y:0,opacity:1,duration:.4,ease:"power3.out"},S+.1);'
      'tl.fromTo("#s9-d",{scale:.8,opacity:0},{scale:1,opacity:1,duration:.5,ease:"back.out(1.6)"},S+.5);'
      'tl.fromTo("#s9-n",{scale:1.4,opacity:0},{scale:1,opacity:1,duration:.45,ease:"power4.out"},S+3.2);'
      'tl.fromTo("#s9-h",{y:30,opacity:0},{y:0,opacity:1,duration:.4,ease:"power3.out"},S+3.6);'
      'tl.fromTo("#s9-c",{scale:.6,opacity:0},{scale:1,opacity:1,duration:.45,ease:"back.out(2)"},S+4.0);'
      'tl.to("#s9-c",{scale:1.06,duration:.3,yoyo:true,repeat:5,ease:"sine.inOut"},S+4.6);')

# ------------------------------------------------------------------ assemble
body, js = [], []
for k, (sid, st, en, html, sj) in enumerate(scenes):
    body.append(f'<div id="{sid}" class="clip scene" data-start="{st}" data-duration="{en - st:.2f}" data-track-index="0" '
                f'style="z-index:{k + 1}" data-layout-allow-overlap><div id="{sid}-in" class="scene-in">{html}</div></div>')
    js.append(f'S={st};tl.fromTo("#{sid}-in",{{opacity:0}},{{opacity:1,duration:.25}},S);{sj}')
for i, (st, en, txt) in enumerate(CAPS):
    body.append(f'<div id="c{i}" class="clip cap" data-start="{st}" data-duration="{en - st:.2f}" data-track-index="1" style="z-index:50">'
                f'<div id="c{i}-in" class="cap-in">{txt}</div></div>')
    js.append(f'tl.fromTo("#c{i}-in",{{y:16,opacity:0}},{{y:0,opacity:1,duration:.18,ease:"power2.out"}},{st});')

page = f"""<!doctype html>
<html lang="kk">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family: "InterK"; font-weight: 600; src: url("assets/fonts/Inter-SemiBold.otf"); }}
@font-face {{ font-family: "InterK"; font-weight: 800; src: url("assets/fonts/Inter-ExtraBold.otf"); }}
@font-face {{ font-family: "InterK"; font-weight: 900; src: url("assets/fonts/Inter-Black.otf"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:{PAPER}; }}
#root {{ position:relative; width:100%; height:100%; font-family:"InterK",sans-serif; color:{INK}; }}
#paper {{ position:absolute; inset:0; background:
  radial-gradient(circle at 30% 20%, rgba(255,255,255,.55), rgba(255,255,255,0) 60%),
  radial-gradient(circle at 80% 85%, rgba(160,120,80,.12), rgba(0,0,0,0) 55%), {PAPER}; }}
.scene {{ position:absolute; inset:0; }}
.scene-in {{ position:absolute; left:0; right:0; top:200px; height:1000px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:44px; }}
.title {{ font-weight:900; font-size:76px; letter-spacing:2px; }}
.pair {{ display:flex; gap:60px; align-items:flex-end; }}
.dk {{ position:relative; display:flex; flex-direction:column; align-items:center; gap:14px; }}
.solo {{ position:relative; }}
.stamp {{ position:absolute; left:50%; top:62%; margin-left:-130px; width:260px; text-align:center; font-weight:900; font-size:46px; padding:6px 0;
  border:6px solid currentColor; border-radius:14px; background:rgba(243,234,217,.9); z-index:5; }}
.good {{ color:{GREEN}; }} .bad {{ color:{RED}; }}
#s1-a {{ z-index:3; }}
.big {{ font-weight:900; font-size:96px; text-align:center; line-height:1.05; }}
.big.small {{ font-size:64px; margin-top:16px; }}
.cols {{ display:flex; gap:40px; align-items:flex-start; }}
.col {{ display:flex; flex-direction:column; align-items:center; gap:24px; width:400px; }}
.divider {{ width:4px; height:340px; background:{MUTE}; opacity:.4; border-radius:2px; }}
.lbl {{ font-weight:900; font-size:44px; letter-spacing:3px; }}
.price {{ font-weight:900; font-size:84px; }} .price .pa {{ color:{RED}; }} .price .pb {{ color:{GREEN}; }}
.price .arrow {{ color:{MUTE}; }} .price .cur {{ font-size:56px; }}
.cnt {{ font-weight:900; font-size:66px; }}
.mm {{ position:absolute; left:50%; top:-14%; font-weight:900; font-size:40px; color:{RED}; transform-origin:50% 50%; }}
.cal {{ display:flex; flex-direction:column; align-items:center; }}
.calc {{ font-weight:800; font-size:50px; white-space:nowrap; }} .calc b {{ display:inline-block; font-size:62px; }}
.calc .per {{ font-size:40px; color:{MUTE}; }}
.tline {{ position:relative; width:900px; height:240px; }}
.mini {{ position:absolute; bottom:56px; }}
""" + "".join(f"#s8-d{i} {{ left:{i * 170 + 20}px; }}\n" for i in range(5)) + f"""
.axis {{ position:absolute; left:0; right:0; bottom:0; height:46px; border-top:5px solid {INK}; display:flex; justify-content:space-between;
  font-weight:800; font-size:34px; padding-top:6px; }}
.sum {{ display:flex; gap:30px; align-items:center; font-weight:900; font-size:76px; white-space:nowrap; }} .sum .vs {{ font-size:50px; color:{MUTE}; }}
.brand {{ font-weight:900; font-size:120px; letter-spacing:6px; }} .brand span {{ color:{COPPER}; }}
.handle {{ font-weight:800; font-size:54px; color:{MUTE}; }}
.cta {{ font-weight:900; font-size:60px; color:#fff; background:{COPPER}; padding:20px 50px; border-radius:60px; }}
.cap {{ position:absolute; left:60px; right:60px; top:1190px; height:150px; display:flex; align-items:center; justify-content:center; }}
.cap-in {{ text-align:center; font-weight:800; font-size:50px; line-height:1.18; color:#fff; background:rgba(59,42,30,.88);
  padding:14px 28px; border-radius:22px; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
<div id="paper"></div>
{chr(10).join(body)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); let S = 0;
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
Path(__file__).with_name("index.html").write_text(page, encoding="utf-8")
print("ok", len(scenes), "scenes,", len(CAPS), "captions")
