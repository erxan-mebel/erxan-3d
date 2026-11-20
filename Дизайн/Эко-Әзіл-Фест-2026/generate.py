"""Эко Әзіл Фест 2026 — 10 дизайн дипломдары (I, II, III орын).
Іске қосу: python3 generate.py  ->  html/, png/, pdf/ папкалары."""
import pathlib, asyncio
from playwright.async_api import async_playwright

import glob
CHROME = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome") or ["/opt/pw-browsers/chromium"])[0]
OUT = pathlib.Path(__file__).parent
PLACES = {1: ("I", "#D4A017", "#F7E08A", "Алтын"), 2: ("II", "#8E9AA6", "#E3E8EC", "Күміс"), 3: ("III", "#B8732E", "#F0C79B", "Қола")}
FONTS = ("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&family=Playfair+Display:wght@700;900"
         "&family=Comfortaa:wght@400;700&family=Unbounded:wght@400;700;900&family=Caveat:wght@700&family=Nunito:wght@400;700;900"
         "&family=Rubik:wght@400;700;900&family=Russo+One&family=Oswald:wght@400;700&family=Cormorant+Garamond:wght@500;700"
         "&family=PT+Serif:wght@400;700&family=Lobster&display=swap")

def medal(p, size=150):
    r, c, light, _ = PLACES[p]
    return f'''<svg width="{size}" height="{size*1.3:.0f}" viewBox="0 0 100 130">
  <path d="M30 0 L50 40 L70 0 L85 0 L60 50 L40 50 L15 0Z" fill="#2E8B57"/>
  <path d="M38 0 L50 25 L62 0Z" fill="#7BC67E"/>
  <circle cx="50" cy="82" r="40" fill="{c}"/><circle cx="50" cy="82" r="33" fill="{light}"/>
  <circle cx="50" cy="82" r="33" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="3 3"/>
  <path d="M35 66 q15 -12 30 0 q-6 4 -15 4 q-9 0 -15 -4Z" fill="#2E8B57" opacity=".85"/>
  <text x="50" y="96" text-anchor="middle" font-family="Montserrat" font-weight="900" font-size="26" fill="#3b2a05">{r}</text>
  <text x="50" y="108" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="7" fill="#3b2a05">ОРЫН</text>
</svg>'''

def leaf(color="#4CAF50", size=60, rot=0, face=True):
    f = ('<circle cx="42" cy="45" r="4" fill="#1b3d1f"/><circle cx="58" cy="45" r="4" fill="#1b3d1f"/>'
         '<path d="M38 58 q12 12 24 0" stroke="#1b3d1f" stroke-width="3.5" fill="none" stroke-linecap="round"/>') if face else ""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" style="transform:rotate({rot}deg)">'
            f'<path d="M50 5 C85 20 95 60 50 95 C5 60 15 20 50 5Z" fill="{color}"/>'
            f'<path d="M50 12 L50 92" stroke="rgba(255,255,255,.45)" stroke-width="2"/>{f}</svg>')

def globe(size=170):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="46" fill="#3FA9F5"/>
  <path d="M20 25 q10 -8 22 -2 q6 8 -2 14 q-10 4 -8 14 q2 10 -8 10 q-8 -6 -10 -18 q-2 -10 6 -18Z" fill="#5CC860"/>
  <path d="M60 15 q14 4 22 18 q-6 6 -14 2 q-8 -2 -10 -10Z M62 60 q12 -4 20 6 q-4 14 -16 18 q-6 -10 -4 -24Z" fill="#5CC860"/>
  <circle cx="38" cy="48" r="5" fill="#fff"/><circle cx="62" cy="48" r="5" fill="#fff"/>
  <circle cx="39" cy="49" r="2.6" fill="#123"/><circle cx="63" cy="49" r="2.6" fill="#123"/>
  <path d="M34 62 q16 16 32 0" stroke="#123" stroke-width="3.5" fill="#fff" stroke-linecap="round"/>
</svg>'''

def sun(size=160):
    rays = "".join(f'<rect x="47" y="0" width="6" height="18" rx="3" fill="#FFB300" transform="rotate({a} 50 50)"/>' for a in range(0, 360, 30))
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100">{rays}<circle cx="50" cy="50" r="30" fill="#FFD54F"/>'
            '<circle cx="40" cy="45" r="3.5" fill="#5d3a00"/><circle cx="60" cy="45" r="3.5" fill="#5d3a00"/>'
            '<path d="M38 57 q12 12 24 0" stroke="#5d3a00" stroke-width="3.5" fill="none" stroke-linecap="round"/></svg>')

def ornament(color, size=90):
    # стильденген қошқар мүйіз
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round">'
            '<path d="M50 90 L50 45 C50 20 20 15 18 38 C16 55 38 55 36 42"/><path d="M50 45 C50 20 80 15 82 38 C84 55 62 55 64 42"/>'
            '<path d="M50 70 C35 70 28 80 30 90 M50 70 C65 70 72 80 70 90"/></svg>')

def body(p, cls=""):
    r = PLACES[p][0]
    return f'''<div class="content {cls}">
  <div class="org">Мектепаралық байқау · 8–11 сыныптар</div>
  <div class="fest">«ЭКО ӘЗІЛ ФЕСТ – 2026»</div>
  <div class="title">ДИПЛОМ</div>
  <div class="degree">{r} дәрежелі</div>
  <div class="award">марапатталады</div>
  <div class="line name"></div>
  <div class="small"><span class="line short"></span> мектебінің <span class="line tiny"></span> сынып оқушысы</div>
  <div class="reason">«Эко Әзіл Фест – 2026» мектепаралық байқауында<br><b>{r} орынды</b> жеңіп алғаны үшін</div>
  <div class="sign">
    <div><span class="line sig"></span><br>Қазылар алқасының төрағасы</div>
    <div class="mo">М.О.</div>
    <div><span class="line sig"></span><br>Ұйымдастыру комитеті</div>
  </div>
  <div class="date">2026 жыл</div>
</div>'''

BASE = '''*{margin:0;padding:0;box-sizing:border-box}
@page{size:297mm 210mm;margin:0}
html,body{width:297mm;height:210mm}
body{position:relative;overflow:hidden;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.content{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24mm 40mm}
.org{font-size:12pt;letter-spacing:2px;text-transform:uppercase;opacity:.85}
.fest{font-size:22pt;font-weight:800;margin-top:2mm}
.title{font-size:66pt;line-height:1;margin-top:3mm}
.degree{font-size:20pt;font-weight:700;margin-top:1mm}
.award{font-size:14pt;margin-top:4mm;font-style:italic}
.line{display:inline-block;border-bottom:1.5px solid currentColor;opacity:.75}
.line.name{width:150mm;height:11mm;display:block}
.line.short{width:50mm}.line.tiny{width:14mm}.line.sig{width:48mm;height:8mm}
.small{font-size:12pt;margin-top:4mm}
.reason{font-size:13pt;margin-top:4mm;line-height:1.45}
.sign{display:flex;justify-content:space-between;align-items:flex-end;width:100%;margin-top:7mm;font-size:10pt}
.sign>div{text-align:center}
.mo{width:22mm;height:22mm;border:1.5px dashed currentColor;border-radius:50%;display:flex;align-items:center;justify-content:center;opacity:.5}
.date{font-size:10pt;margin-top:2mm;opacity:.8}
.abs{position:absolute}
'''

def theme(n, p):
    r, c, light, metal = PLACES[p]
    if n == 1:  # Жасыл классика
        css = f'''body{{background:#FBF8EE;color:#1E4D2B;font-family:"PT Serif",serif}}
.frame{{position:absolute;inset:8mm;border:3mm solid #1E4D2B;outline:1.2mm solid {c};outline-offset:-6mm}}
.frame2{{position:absolute;inset:16mm;border:.6mm solid {c}}}
.title{{font-family:"Playfair Display";font-weight:900;color:{c};text-shadow:1px 1px 0 #1E4D2B}}
.fest{{font-family:"Playfair Display"}} .content{{padding:28mm 45mm}}'''
        deco = '<div class="frame"></div><div class="frame2"></div>' + "".join(
            f'<div class="abs" style="{pos}">{leaf("#2E7D32",55,rot,False)}</div>'
            for pos, rot in [("left:12mm;top:12mm", -45), ("right:12mm;top:12mm", 45), ("left:12mm;bottom:12mm", -135), ("right:12mm;bottom:12mm", 135)]
        ) + f'<div class="abs" style="right:28mm;top:50mm">{medal(p,110)}</div>'
    elif n == 2:  # Күлкі жапырақтары
        css = f'''body{{background:linear-gradient(135deg,#E8F8E0,#FFFDE7);color:#24502A;font-family:Comfortaa,sans-serif}}
.title{{font-family:Unbounded;font-weight:900;color:#2E9E45;-webkit-text-stroke:2px #1d6b2c}}
.fest{{color:#F57C00}} .degree{{color:{c}}}
.edge{{position:absolute;inset:7mm;border:2.5mm dashed #7BC67E;border-radius:10mm}}'''
        spots = [("left:4mm;top:6mm",-20,"#66BB6A",80),("left:30mm;top:2mm",15,"#AED581",50),("right:6mm;top:8mm",25,"#43A047",85),
                 ("left:6mm;bottom:10mm",-160,"#9CCC65",70),("right:8mm;bottom:6mm",160,"#66BB6A",80),("right:40mm;bottom:2mm",190,"#C5E1A5",50),
                 ("left:4mm;top:90mm",-80,"#81C784",55),("right:4mm;top:95mm",80,"#AED581",55)]
        deco = '<div class="edge"></div>' + "".join(f'<div class="abs" style="{s}">{leaf(col,sz,rot)}</div>' for s,rot,col,sz in spots) \
               + f'<div class="abs" style="left:24mm;top:40mm">{medal(p,105)}</div>'
    elif n == 3:  # Күлетін жер шары
        css = f'''body{{background:radial-gradient(circle at 80% 20%,#E3F4FF 0,#fff 45%,#E9F9EC 100%);color:#0F3C5C;font-family:Montserrat,sans-serif}}
.title{{font-weight:900;background:linear-gradient(90deg,#1E88E5,#43A047);-webkit-background-clip:text;color:transparent}}
.content{{align-items:flex-start;text-align:left;padding:22mm 30mm 22mm 95mm}} .line.name{{width:140mm}}
.band{{position:absolute;left:0;top:0;bottom:0;width:78mm;background:linear-gradient(180deg,#1E88E5,#43A047)}}
.sign{{width:170mm}} .degree{{color:{c}}}'''
        deco = f'<div class="band"></div><div class="abs" style="left:4mm;top:18mm">{globe(250)}</div>' \
               f'<div class="abs" style="left:20mm;top:118mm">{medal(p,100)}</div>'
    elif n == 4:  # Минимал
        css = f'''body{{background:#fff;color:#1d1d1d;font-family:Montserrat,sans-serif}}
.title{{font-family:Unbounded;font-weight:700;letter-spacing:10px;font-size:58pt}} .fest{{color:#2E7D32;font-family:Unbounded;font-weight:400}}
.big{{position:absolute;right:16mm;bottom:-10mm;font-family:"Playfair Display";font-weight:900;font-size:230pt;opacity:.35;color:{light};line-height:1;z-index:0}}
.content{{z-index:1}} .bar{{position:absolute;left:14mm;top:14mm;bottom:14mm;width:2.5mm;background:#2E7D32}}
.bar2{{position:absolute;left:19mm;top:14mm;bottom:14mm;width:.8mm;background:{c}}} .degree{{color:{c}}}'''
        deco = f'<div class="big">{r}</div><div class="bar"></div><div class="bar2"></div>' \
               f'<div class="abs" style="right:20mm;top:16mm">{leaf("#2E7D32",50,20,False)}</div>'
    elif n == 5:  # Акварель
        blobs = [("left:-30mm;top:-30mm;width:120mm;height:110mm","#A5D6A7"),("right:-25mm;top:-20mm;width:100mm;height:90mm","#FFF59D"),
                 ("left:-20mm;bottom:-40mm;width:110mm;height:100mm","#B3E5FC"),("right:-30mm;bottom:-30mm;width:130mm;height:110mm","#C5E1A5")]
        css = f'''body{{background:#FFFEF9;color:#33402F;font-family:Nunito,sans-serif}}
.blob{{position:absolute;border-radius:50%;filter:blur(14px);opacity:.75}}
.title{{font-family:Caveat;font-size:96pt;color:#2E7D32}} .fest{{font-family:Caveat;font-size:32pt;color:#E65100}}
.degree{{color:{c};font-family:Caveat;font-size:30pt}}'''
        deco = "".join(f'<div class="blob" style="{s};background:radial-gradient(circle,{col} 0,{col}aa 50%,transparent 72%)"></div>' for s,col in blobs) \
               + f'<div class="abs" style="right:30mm;top:58mm">{medal(p,100)}</div>' \
               + f'<div class="abs" style="left:28mm;top:62mm">{leaf("#81C784",80,-20)}</div>'
    elif n == 6:  # Комикс
        css = f'''body{{background:#FFF176;color:#111;font-family:Rubik,sans-serif;
background-image:radial-gradient(#F9A825 1.3px,transparent 1.4px);background-size:5mm 5mm}}
.panel{{position:absolute;inset:10mm;background:#fff;border:2mm solid #111;box-shadow:4mm 4mm 0 #111}}
.title{{font-family:"Russo One";font-size:70pt;color:#43A047;-webkit-text-stroke:2.5px #111;text-shadow:3px 3px 0 #111}}
.fest{{font-family:"Russo One";color:#E53935}} .degree{{background:{c};border:1mm solid #111;padding:0 6mm;border-radius:3mm}}
.bubble{{position:absolute;right:22mm;top:20mm;background:#fff;border:1.2mm solid #111;border-radius:50%;padding:6mm 9mm;font-family:"Russo One";font-size:22pt;color:#E53935;transform:rotate(8deg)}}
.bubble:after{{content:"";position:absolute;left:8mm;bottom:-6mm;border:4mm solid transparent;border-top:6mm solid #111}}'''
        deco = '<div class="panel"></div><div class="bubble">ХА-ХА!</div>' \
               f'<div class="abs" style="left:22mm;top:24mm">{globe(110)}</div>' \
               f'<div class="abs" style="left:24mm;top:72mm">{medal(p,90)}</div>'
    elif n == 7:  # Таспа мен медаль
        css = f'''body{{background:linear-gradient(180deg,#F1F8E9,#fff);color:#1B5E20;font-family:Oswald,sans-serif}}
.title{{font-weight:700;letter-spacing:12px;color:#fff;background:#2E7D32;padding:2mm 22mm;position:relative;font-size:52pt}}
.title:before,.title:after{{content:"";position:absolute;top:4mm;border:13mm solid #1B5E20;z-index:-1}}
.title:before{{left:-16mm;border-left-color:transparent}} .title:after{{right:-16mm;border-right-color:transparent}}
.content{{z-index:1}} .degree{{color:{c};font-size:24pt;margin-top:3mm}} .fest{{font-weight:700}}
.corner{{position:absolute;width:70mm;height:70mm;border:2mm solid {c}}}'''
        deco = ('<div class="corner" style="left:10mm;top:10mm;border-right:0;border-bottom:0"></div>'
                '<div class="corner" style="right:10mm;bottom:10mm;border-left:0;border-top:0"></div>'
                f'<div class="abs" style="right:22mm;top:16mm">{medal(p,95)}</div>'
                f'<div class="abs" style="left:22mm;bottom:20mm">{leaf("#43A047",60,-30,False)}</div>')
    elif n == 8:  # Күн мен гүл
        css = f'''body{{background:linear-gradient(160deg,#FFF8E1 0,#FFECB3 60%,#C8E6C9 100%);color:#5D3A00;font-family:Rubik,sans-serif}}
.title{{font-weight:900;color:#EF6C00;text-shadow:3px 3px 0 #FFD54F}} .fest{{color:#2E7D32;font-weight:900}} .degree{{color:{c}}}
.hill{{position:absolute;left:-10%;right:-10%;bottom:-60mm;height:100mm;background:#81C784;border-radius:50%}}
.hill2{{position:absolute;left:30%;right:-20%;bottom:-70mm;height:100mm;background:#66BB6A;border-radius:50%}}
.content{{padding:18mm 50mm 30mm}} .sign{{color:#1B3D1F}} .date{{color:#1B3D1F}}'''
        deco = f'<div class="hill"></div><div class="hill2"></div><div class="abs" style="left:10mm;top:8mm">{sun(150)}</div>' \
               f'<div class="abs" style="right:18mm;top:18mm">{medal(p,100)}</div>'
    elif n == 9:  # Түнгі орман (премиум)
        css = f'''body{{background:radial-gradient(circle at 50% 40%,#1F5130,#0C2615);color:#F3E9C6;font-family:"Cormorant Garamond",serif}}
.title{{font-family:"Playfair Display";font-weight:900;letter-spacing:8px;background:linear-gradient(180deg,#FFF3B0,{c} 60%,#8a6a10);-webkit-background-clip:text;color:transparent}}
.fest{{font-family:"Playfair Display";color:{c}}} .org,.small,.reason,.award{{font-size:14pt}} .degree{{color:{light}}}
.fr{{position:absolute;inset:9mm;border:.8mm solid {c}}} .fr2{{position:absolute;inset:12mm;border:.3mm solid {c}}}'''
        deco = '<div class="fr"></div><div class="fr2"></div>' + "".join(
            f'<div class="abs" style="{s}">{ornament(c,60)}</div>' for s in
            ["left:16mm;top:16mm;transform:rotate(-45deg)","right:16mm;top:16mm;transform:rotate(45deg)",
             "left:16mm;bottom:16mm;transform:rotate(-135deg)","right:16mm;bottom:16mm;transform:rotate(135deg)"]) \
            + f'<div class="abs" style="right:34mm;top:60mm">{medal(p,95)}</div>'
    else:  # 10 Ұлттық ою
        orn = "".join(f'<div style="display:inline-block;margin:0 1mm">{ornament("#fff",40)}</div>' for _ in range(16))
        css = f'''body{{background:#FFFDF5;color:#0D3B4C;font-family:"PT Serif",serif}}
.strip{{position:absolute;left:0;right:0;height:22mm;background:#0E7C61;overflow:hidden;white-space:nowrap;padding-top:2.5mm;border-bottom:1.5mm solid {c}}}
.strip.b{{bottom:0;top:auto;border-bottom:0;border-top:1.5mm solid {c}}}
.title{{font-family:Lobster;font-size:80pt;color:#0E7C61}} .fest{{color:#0E7C61}} .degree{{color:{c}}}
.content{{padding:30mm 45mm}}'''
        deco = f'<div class="strip" style="top:0">{orn}</div><div class="strip b">{orn}</div>' \
               f'<div class="abs" style="left:20mm;top:60mm">{medal(p,95)}</div>' \
               f'<div class="abs" style="right:20mm;top:66mm">{ornament("#0E7C61",90)}</div>'
    return f'''<!doctype html><html lang="kk"><head><meta charset="utf-8"><title>Диплом {n} — {r} орын</title>
<link rel="stylesheet" href="{FONTS}"><style>{BASE}{css}</style></head><body>{deco}{body(p)}</body></html>'''

NAMES = {1:"Жасыл классика",2:"Күлкі жапырақтары",3:"Күлетін жер шары",4:"Минимал",5:"Акварель",
         6:"Комикс",7:"Таспа мен медаль",8:"Күн мен гүл",9:"Түнгі орман",10:"Ұлттық ою"}

async def main():
    for d in ("html", "png", "pdf"): (OUT / d).mkdir(exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=CHROME)
        pg = await b.new_page(viewport={"width": 1123, "height": 794}, device_scale_factor=2)
        for n in range(1, 11):
            pages = []
            for p in (1, 2, 3):
                f = OUT / "html" / f"{n:02d}_{p}-orin.html"
                f.write_text(theme(n, p), encoding="utf-8")
                await pg.goto(f.as_uri()); await pg.evaluate("document.fonts.ready")
                await pg.screenshot(path=str(OUT / "png" / f"{n:02d}_{NAMES[n]}_{p}-орын.png"))
                pages.append(f)
            # бір PDF ішінде 3 бет: I, II, III орын
            pdfs = []
            for i, pf in enumerate(pages):
                await pg.goto(pf.as_uri()); await pg.evaluate("document.fonts.ready")
                tmp = OUT / "pdf" / f".tmp{i}.pdf"
                await pg.pdf(path=str(tmp), width="297mm", height="210mm", print_background=True)
                pdfs.append(tmp)
            from pypdf import PdfWriter
            w = PdfWriter()
            for t in pdfs: w.append(str(t))
            w.write(str(OUT / "pdf" / f"{n:02d}_{NAMES[n]}.pdf"))
            for t in pdfs: t.unlink()
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
