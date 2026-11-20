"""Қазақ оюлы диплом (I, II, III орын). Іске қосу: python3 generate_oyu.py"""
import asyncio
from generate import OUT, PLACES, FONTS, BASE, CHROME, body, medal, async_playwright

TURQ, DARK, GOLD, GREEN = "#0B6E7A", "#06434B", "#D9A928", "#2E8B57"

# Қошқар мүйіз: орталық сабақ, жоғары және төмен қайырылған мүйіздер
def horn(color, sw=6):
    return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M50 62 C50 32 32 14 19 23 C8 31 12 49 25 49 C33 49 35 39 28 36"/>'
            '<path d="M50 62 C50 32 68 14 81 23 C92 31 88 49 75 49 C67 49 65 39 72 36"/>'
            '<path d="M50 62 C40 63 31 70 33 81 C35 90 45 88 43 80"/>'
            '<path d="M50 62 C60 63 69 70 67 81 C65 90 55 88 57 80"/>'
            '<path d="M50 62 L50 96"/></g>'
            f'<path d="M50 6 L58 22 L50 34 L42 22Z" fill="{color}"/>')

def rosette(color, accent):
    # төрт жаққа қараған мүйіздер — тұмар-розетка
    g = "".join(f'<g transform="rotate({a} 50 50) translate(25 0) scale(.5)">{horn(color, 7)}</g>' for a in (0, 90, 180, 270))
    return f'{g}<circle cx="50" cy="50" r="7" fill="{accent}"/><circle cx="50" cy="50" r="3" fill="{color}"/>'

def page_svg(c):
    tile = f'<g transform="scale(.16)">{horn(GOLD, 9)}</g>'
    corner = f'<g>{rosette(GOLD, GREEN)}</g>'
    corners = "".join(f'<g transform="translate({x} {y}) scale(.34)">{corner}</g>'
                      for x, y in ((3, 3), (260, 3), (3, 173), (260, 173)))
    side = lambda x: "".join(f'<g transform="translate({x} {y}) rotate(90 8 8) scale(.16)">{horn(GOLD,9)}</g>' for y in range(42, 160, 16))
    return f'''<svg class="abs" style="inset:0" width="297mm" height="210mm" viewBox="0 0 297 210">
<defs><pattern id="band" width="16" height="16" patternUnits="userSpaceOnUse">
  <rect width="16" height="16" fill="{TURQ}"/>{tile}</pattern>
  <pattern id="band2" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(180 8 8)">
  <rect width="16" height="16" fill="{TURQ}"/>{tile}</pattern></defs>
<rect x="0" y="0" width="297" height="18" fill="url(#band)"/>
<rect x="0" y="192" width="297" height="18" fill="url(#band2)"/>
<rect x="0" y="0" width="18" height="210" fill="{TURQ}"/><rect x="279" y="0" width="18" height="210" fill="{TURQ}"/>
{side(1)}{side(280)}
<rect x="18" y="18" width="261" height="174" fill="none" stroke="{GOLD}" stroke-width="1.4"/>
<rect x="21.5" y="21.5" width="254" height="167" fill="none" stroke="{GOLD}" stroke-width=".4"/>
{corners}
<g opacity=".07" transform="translate(98.5 55) scale(1)">{rosette(TURQ, TURQ)}</g>
<g transform="translate(139.5 23) scale(.18)">{horn(TURQ, 7)}</g>
<g transform="translate(118 160) scale(.15)">{horn(GREEN,8)}</g><g transform="translate(164 160) scale(.15)">{horn(GREEN,8)}</g>
</svg>'''

def theme(p):
    r, c, light, _ = PLACES[p]
    css = f'''body{{background:radial-gradient(circle at 50% 45%,#FFFDF6,#F6ECD2);color:{DARK};font-family:"PT Serif",serif}}
.content{{padding:34mm 48mm 28mm}}
.title{{font-family:"Playfair Display";font-weight:900;font-size:64pt;letter-spacing:6px;color:{TURQ};text-shadow:2px 2px 0 {GOLD}}}
.fest{{color:{GREEN};font-family:"Playfair Display"}} .degree{{color:{c};font-size:22pt}}
.org{{color:{TURQ}}} .mo{{border-color:{TURQ}}}'''
    deco = page_svg(c) + f'<div class="abs" style="left:30mm;top:62mm">{medal(p,92)}</div>' \
           f'<div class="abs" style="right:30mm;top:62mm">{medal(p,92)}</div>'
    return f'''<!doctype html><html lang="kk"><head><meta charset="utf-8"><title>Оюлы диплом — {r} орын</title>
<link rel="stylesheet" href="{FONTS}"><style>{BASE}{css}</style></head><body>{deco}{body(p)}</body></html>'''

async def main():
    from pypdf import PdfWriter
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=CHROME)
        pg = await b.new_page(viewport={"width": 1123, "height": 794}, device_scale_factor=2)
        w, tmps = PdfWriter(), []
        for p in (1, 2, 3):
            f = OUT / "html" / f"11_oyu_{p}-orin.html"
            f.write_text(theme(p), encoding="utf-8")
            await pg.goto(f.as_uri()); await pg.evaluate("document.fonts.ready")
            await pg.screenshot(path=str(OUT / "png" / f"11_Қазақ ою_{p}-орын.png"))
            t = OUT / "pdf" / f".t{p}.pdf"
            await pg.pdf(path=str(t), width="297mm", height="210mm", print_background=True)
            w.append(str(t)); tmps.append(t)
        w.write(str(OUT / "pdf" / "11_Қазақ ою.pdf"))
        for t in tmps: t.unlink()
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
