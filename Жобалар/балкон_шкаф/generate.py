"""Balcony cabinet generator: drawing, cut list, SketchUp model from a few parameters.

Edit PARAMS and run:  python3 Жобалар/балкон_шкаф/generate.py
Outputs (next to this file, in out/):
  сызба.png / сызба.pdf   drawing sheet with dimensions and cut list
  деталировка.xlsx        cut list + hardware for the workshop
  шкаф.dae                3D model for SketchUp (File > Import)
  шкаф.rb                 SketchUp Pro Ruby Console script (each part a group)
All sizes in millimetres. Coordinates: x = width, y = depth (front 0 -> back), z = height.
"""
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

PARAMS = dict(
    W=800,        # overall width
    H=2200,       # overall height
    D=400,        # carcass depth incl. back panel (doors add 16 mm in front)
    T=16,         # LDSP thickness
    HDF=3,        # back panel thickness
    PLINTH=80,    # plinth height
    SHELVES=5,    # number of fixed shelves
    GAP=2,        # door gap
    COLOR="Ақ",   # LDSP colour
)

HERE = Path(__file__).parent
OUT = HERE / "out"


@dataclass
class Part:
    name: str
    mat: str          # "ЛДСП" | "ХДФ" | "Фасад"
    x: float
    y: float
    z: float
    dx: float
    dy: float
    dz: float
    cut: tuple        # (length, width) as cut from the sheet
    edge: tuple = (0, 0)  # banded edges (long, short)


def build(p: dict) -> list[Part]:
    W, H, D, T, HDF, PL, N, G = (p[k] for k in ("W", "H", "D", "T", "HDF", "PLINTH", "SHELVES", "GAP"))
    Dc = D - HDF                      # LDSP depth
    iw = W - 2 * T                    # inner width
    parts = [
        Part("Бүйір (сол)", "ЛДСП", 0, 0, 0, T, Dc, H, (H, Dc), (1, 0)),
        Part("Бүйір (оң)", "ЛДСП", W - T, 0, 0, T, Dc, H, (H, Dc), (1, 0)),
        Part("Төбе", "ЛДСП", T, 0, H - T, iw, Dc, T, (iw, Dc), (1, 0)),
        Part("Түп", "ЛДСП", T, 0, PL, iw, Dc, T, (iw, Dc), (1, 0)),
        Part("Цоколь алдыңғы", "ЛДСП", T, 20, 0, iw, T, PL, (iw, PL), (1, 0)),
        Part("Цоколь артқы", "ЛДСП", T, Dc - T - 20, 0, iw, T, PL, (iw, PL), (0, 0)),
    ]
    z_lo, z_hi = PL + T, H - T
    cell = (z_hi - z_lo - N * T) / (N + 1)
    sd = Dc - 20
    for i in range(N):
        z = z_lo + (i + 1) * cell + i * T
        parts.append(Part(f"Сөре {i + 1}", "ЛДСП", T, 0, round(z, 1), iw, sd, T, (iw, sd), (1, 0)))
    parts.append(Part("Артқы қабырға", "ХДФ", 1, Dc, 1, W - 2, HDF, H - 2, (H - 2, W - 2)))
    dh = H - PL - 2 * G
    dw = (W - 3 * G) / 2
    parts.append(Part("Есік (сол)", "Фасад", G, -T, PL + G, dw, T, dh, (dh, dw), (2, 2)))
    parts.append(Part("Есік (оң)", "Фасад", 2 * G + dw, -T, PL + G, dw, T, dh, (dh, dw), (2, 2)))
    return parts


def hardware(p: dict, parts: list[Part]) -> list[tuple]:
    dh = p["H"] - p["PLINTH"] - 2 * p["GAP"]
    hinges = 2 if dh <= 900 else 3 if dh <= 1500 else 4 if dh <= 2000 else 5
    shelves = sum(1 for x in parts if x.name.startswith("Сөре"))
    back = next(x for x in parts if x.mat == "ХДФ")
    return [
        ("Петля накладная 110° (доводчикпен)", hinges * 2, "дана", f"{hinges} әр есікке"),
        ("Тұтқа (ручка)", 2, "дана", "128 мм"),
        ("Конфирмат 7×50", 4 + 4 + 8 + shelves * 4, "дана", "төбе, түп, цоколь, сөрелер"),
        ("Шуруп 3,5×16 (ХДФ-ке)", math.ceil(2 * (back.cut[0] + back.cut[1]) / 150) + shelves * 3, "дана", "150 мм сайын"),
        ("Кромка ПВХ 0,4 мм", round(edge_len(parts, "ЛДСП") / 1000 * 1.1, 1), "м", "корпус, +10% қор"),
        ("Кромка ПВХ 2 мм", round(edge_len(parts, "Фасад") / 1000 * 1.1, 1), "м", "есіктер, +10% қор"),
    ]


def edge_len(parts, mat):
    return sum(2 * 0 + x.edge[0] * x.cut[0] + x.edge[1] * x.cut[1] for x in parts if x.mat == mat)


def grouped(parts):
    rows = {}
    for x in parts:
        key = (x.name.split(" (")[0].rstrip("0123456789 ").strip(), x.mat, round(x.cut[0]), round(x.cut[1]), x.edge)
        rows[key] = rows.get(key, 0) + 1
    return [(n, m, l, w, q, e) for (n, m, l, w, e), q in rows.items()]


# ---------------------------------------------------------------- cut list (xlsx)
def write_xlsx(p, parts, hw):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Деталировка"
    ws.append([f"ERXAN MEBEL · Балкон шкаф {p['W']}×{p['H']}×{p['D']} · ЛДСП {p['T']} мм, түсі: {p['COLOR']}"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append([])
    head = ["№", "Деталь", "Материал", "Ұзындығы, мм", "Ені, мм", "Саны", "Кромка ұзын жақ", "Кромка қысқа жақ", "Ауданы, м²"]
    ws.append(head)
    fill = PatternFill("solid", fgColor="D9825B")
    thin = Side(style="thin", color="999999")
    for c in ws[3]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = fill
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    total = {"ЛДСП": 0, "ХДФ": 0, "Фасад": 0}
    for i, (n, m, l, w, q, e) in enumerate(grouped(parts), 1):
        area = l * w * q / 1e6
        total[m] += area
        ws.append([i, n, m if m != "Фасад" else f"ЛДСП {p['T']} (фасад)", l, w, q, e[0], e[1], round(area, 3)])
    ws.append([])
    sheet = 2.75 * 1.83
    for m, a in total.items():
        extra = f" → шамамен {math.ceil(a * 1.15 / sheet * 2) / 2} лист (2750×1830, +15%)" if m != "ХДФ" else ""
        ws.append(["", f"{m} барлығы", "", "", "", "", "", "", round(a, 2)])
        ws.cell(ws.max_row, 2).value += extra
    for row in ws.iter_rows(min_row=3, max_row=ws.max_row):
        for c in row:
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
    for col, wdt in zip("ABCDEFGHI", (5, 22, 18, 14, 10, 8, 14, 14, 12)):
        ws.column_dimensions[col].width = wdt

    hs = wb.create_sheet("Фурнитура")
    hs.append(["Атауы", "Саны", "Өлш.", "Ескерту"])
    for c in hs[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = fill
    for r in hw:
        hs.append(list(r))
    for col, wdt in zip("ABCD", (38, 8, 8, 28)):
        hs.column_dimensions[col].width = wdt
    wb.save(OUT / "деталировка.xlsx")
    return total


# ---------------------------------------------------------------- drawing (svg -> png/pdf)
COP, INK, MUTE, FILL, HDFC = "#D9825B", "#1d1d1f", "#8a8a8e", "#f4efe9", "#c9b49a"


def dim_h(x1, x2, y, label, off=-18):
    yy = y + off
    return (f'<line x1="{x1}" y1="{y}" x2="{x1}" y2="{yy - 4 * (1 if off < 0 else -1)}" class="ext"/>'
            f'<line x1="{x2}" y1="{y}" x2="{x2}" y2="{yy - 4 * (1 if off < 0 else -1)}" class="ext"/>'
            f'<line x1="{x1}" y1="{yy}" x2="{x2}" y2="{yy}" class="dim" marker-start="url(#a)" marker-end="url(#a)"/>'
            f'<text x="{(x1 + x2) / 2}" y="{yy - 5}" class="dt">{label}</text>')


def dim_v(x, y1, y2, label, off=-18):
    xx = x + off
    return (f'<line x1="{x}" y1="{y1}" x2="{xx - 4}" y2="{y1}" class="ext"/>'
            f'<line x1="{x}" y1="{y2}" x2="{xx - 4}" y2="{y2}" class="ext"/>'
            f'<line x1="{xx}" y1="{y1}" x2="{xx}" y2="{y2}" class="dim" marker-start="url(#a)" marker-end="url(#a)"/>'
            f'<text x="{xx - 5}" y="{(y1 + y2) / 2}" class="dt" transform="rotate(-90 {xx - 5} {(y1 + y2) / 2})">{label}</text>')


def front_view(p, parts, k, ox, oy, doors):
    H = p["H"]
    X = lambda v: ox + v * k
    Z = lambda v: oy + (H - v) * k
    s = []
    for x in parts:
        if x.mat == "ХДФ" or x.name == "Цоколь артқы":
            continue
        if doors != (x.mat == "Фасад") and not (doors and x.name.startswith(("Бүйір", "Цоколь"))):
            continue
        fill = FILL if x.mat != "Фасад" else "#ffffff"
        s.append(f'<rect x="{X(x.x)}" y="{Z(x.z + x.dz)}" width="{x.dx * k}" height="{x.dz * k}" fill="{fill}" stroke="{INK}" stroke-width="1"/>')
        if x.mat == "Фасад":
            hx = X(x.x + x.dx - 40) if "сол" in x.name else X(x.x + 40)
            s.append(f'<rect x="{hx - 3}" y="{Z(1200 + 64)}" width="6" height="{128 * k}" rx="3" fill="{INK}"/>')
    W = p["W"]
    s.append(dim_h(X(0), X(W), Z(H), f"{W}"))
    s.append(dim_v(X(0), Z(H), Z(0), f"{H}", off=-28))
    if not doors:
        sh = sorted((x for x in parts if x.name.startswith("Сөре")), key=lambda x: x.z)
        levels = [p["PLINTH"] + p["T"]] + [v for x in sh for v in (x.z, x.z + x.dz)] + [H - p["T"]]
        for a, b in zip(levels[::2], levels[1::2]):
            s.append(dim_v(X(W), Z(a), Z(b), f"{b - a:.0f}", off=26))
        s.append(dim_v(X(W), Z(0), Z(p["PLINTH"]), f"{p['PLINTH']}", off=26))
    return "".join(s)


def side_view(p, parts, k, ox, oy):
    H, D, T = p["H"], p["D"], p["T"]
    Y = lambda v: ox + (v + T) * k
    Z = lambda v: oy + (H - v) * k
    s = []
    for x in parts:
        if x.name == "Бүйір (оң)":
            continue
        col = HDFC if x.mat == "ХДФ" else ("#ffffff" if x.mat == "Фасад" else FILL)
        s.append(f'<rect x="{Y(x.y)}" y="{Z(x.z + x.dz)}" width="{x.dy * k}" height="{x.dz * k}" fill="{col}" stroke="{INK}" stroke-width="1" opacity="{0.35 if x.name == "Бүйір (сол)" else 1}"/>')
    s.append(dim_h(Y(-T), Y(D), Z(H), f"{D + T}"))
    s.append(dim_h(Y(0), Y(D), Z(0), f"{D}", off=22))
    return "".join(s)


def iso_view(p, parts, k, ox, oy):
    c, sn = math.cos(math.radians(30)), 0.5
    P = lambda x, y, z: (ox + (x + y) * c * k, oy + ((x - y) * sn - z) * k)
    order = ["Артқы", "Бүйір (сол)", "Цоколь артқы", "Цоколь алд", "Түп", "Сөре", "Төбе", "Бүйір (оң)", "Есік (сол)"]
    rank = lambda x: next((i for i, o in enumerate(order) if x.name.startswith(o)), 99) * 10000 + x.z
    s = []
    for x in sorted(parts, key=rank):
        if x.name == "Есік (оң)":
            continue
        x0, y0, z0, x1, y1, z1 = x.x, x.y, x.z, x.x + x.dx, x.y + x.dy, x.z + x.dz
        base = {"ХДФ": (201, 180, 154), "Фасад": (250, 250, 250)}.get(x.mat, (244, 239, 233))
        faces = [
            ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], 1.0),   # front
            ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], 0.82),  # right
            ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], 0.92),  # top
        ]
        for pts, sh in faces:
            col = "rgb(%d,%d,%d)" % tuple(int(v * sh) for v in base)
            d = " ".join("%.1f,%.1f" % P(*q) for q in pts)
            s.append(f'<polygon points="{d}" fill="{col}" stroke="{INK}" stroke-width="0.7"/>')
    return "".join(s)


def write_sheet(p, parts, hw, total):
    k = 0.3
    W, H, D = p["W"], p["H"], p["D"]
    fh = H * k
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="{fh + 140}" font-family="Inter, sans-serif">',
        '<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,2 L10,5 L0,8 z" fill="{INK}"/></marker></defs>',
        f'<style>.dim{{stroke:{INK};stroke-width:1}}.ext{{stroke:{MUTE};stroke-width:.6}}'
        f'.dt{{font-size:13px;fill:{INK};text-anchor:middle;font-weight:600}}.cap{{font-size:15px;font-weight:800;fill:{COP};letter-spacing:1px}}</style>',
    ]
    y0 = 70
    views = [
        ("АЛДЫНАН (есіксіз)", 70, lambda ox: front_view(p, parts, k, ox, y0, False)),
        ("АЛДЫНАН (есікпен)", 70 + W * k + 120, lambda ox: front_view(p, parts, k, ox, y0, True)),
        ("БҮЙІРІНЕН (қима)", 70 + 2 * (W * k + 120), lambda ox: side_view(p, parts, k, ox, y0)),
    ]
    for cap, ox, fn in views:
        svg.append(f'<text x="{ox}" y="{y0 - 42}" class="cap">{cap}</text>')
        svg.append(fn(ox))
    ix = 70 + 2 * (W * k + 120) + (D + 16) * k + 120
    svg.append(f'<text x="{ix}" y="{y0 - 42}" class="cap">3D КӨРІНІС</text>')
    svg.append(iso_view(p, parts, 0.26, ix, y0 + H * 0.26 + 10))
    svg.append("</svg>")

    rows = "".join(
        f"<tr><td>{i}</td><td>{n}</td><td>{m}</td><td>{l}</td><td>{w}</td><td><b>{q}</b></td><td>{e[0]}/{e[1]}</td></tr>"
        for i, (n, m, l, w, q, e) in enumerate(grouped(parts), 1)
    )
    hrows = "".join(f"<tr><td>{a}</td><td><b>{b}</b> {c}</td><td>{d}</td></tr>" for a, b, c, d in hw)
    sheet = 2.75 * 1.83
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#fff;font-family:Inter,sans-serif;color:{INK}}}
.wrap{{padding:36px 44px;width:1500px}}
header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid {COP};padding-bottom:12px;margin-bottom:8px}}
.brand{{font-size:30px;font-weight:900;letter-spacing:2px}} .brand span{{color:{COP}}}
.meta{{text-align:right;font-size:14px;color:{MUTE}}} .meta b{{color:{INK};font-size:20px}}
.tables{{display:flex;gap:36px;margin-top:6px}}
table{{border-collapse:collapse;font-size:13px}} th{{background:{COP};color:#fff;padding:6px 8px;text-align:left}}
td{{border-bottom:1px solid #e5e5e5;padding:5px 8px}} h3{{margin:0 0 8px;color:{COP};letter-spacing:1px;font-size:14px}}
.note{{font-size:12px;color:{MUTE};margin-top:8px;max-width:520px}}
</style></head><body><div class="wrap">
<header><div class="brand">ERXAN <span>MEBEL</span></div>
<div class="meta">Балкон шкаф · ЛДСП {p['T']} мм · түсі: {p['COLOR']} · артқы қабырға ХДФ {p['HDF']} мм<br>
<b>{W} × {H} × {D} мм</b> (есікпен тереңдігі {D + p['T']} мм)</div></header>
{''.join(svg)}
<div class="tables"><div><h3>ДЕТАЛИРОВКА</h3><table><tr><th>№</th><th>Деталь</th><th>Материал</th><th>Ұзын</th><th>Ені</th><th>Саны</th><th>Кромка ұз/қыс</th></tr>{rows}</table>
<div class="note">ЛДСП барлығы {total['ЛДСП'] + total['Фасад']:.2f} м² ≈ {math.ceil((total['ЛДСП'] + total['Фасад']) * 1.15 / sheet * 2) / 2} лист 2750×1830 · ХДФ {total['ХДФ']:.2f} м².
Сөрелер артқы қабырғадан 20 мм ішке, цоколь алдынан 20 мм ішке орнатылады.</div></div>
<div><h3>ФУРНИТУРА</h3><table><tr><th>Атауы</th><th>Саны</th><th>Ескерту</th></tr>{hrows}</table></div></div>
</div></body></html>"""
    (OUT / "сызба.html").write_text(html, encoding="utf-8")
    js = f"""const {{chromium}} = require('playwright');
(async () => {{ const b = await chromium.launch(); const pg = await b.newPage({{viewport: {{width: 1590, height: 1000}}, deviceScaleFactor: 2}});
await pg.goto('file://{(OUT / "сызба.html").resolve()}'); await pg.waitForTimeout(300);
await pg.screenshot({{path: '{(OUT / "сызба.png").resolve()}', fullPage: true}});
await pg.pdf({{path: '{(OUT / "сызба.pdf").resolve()}', width: '1590px', height: (await pg.evaluate(() => document.body.scrollHeight + 10)) + 'px', printBackground: true}});
await b.close(); }})();"""
    (OUT / "_render.js").write_text(js)
    subprocess.run(["node", str(OUT / "_render.js")], check=True)
    (OUT / "_render.js").unlink()


# ---------------------------------------------------------------- SketchUp: COLLADA + Ruby
MATS = {"ЛДСП": (0.96, 0.94, 0.91), "ХДФ": (0.79, 0.71, 0.60), "Фасад": (1.0, 1.0, 1.0)}
MAT_ID = {"ЛДСП": "ldsp", "ХДФ": "hdf", "Фасад": "fasad"}


def write_dae(parts):
    tri = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
           (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    geos, nodes = [], []
    for i, x in enumerate(parts):
        x0, y0, z0, x1, y1, z1 = x.x, x.y, x.z, x.x + x.dx, x.y + x.dy, x.z + x.dz
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        pos = " ".join("%g %g %g" % q for q in v)
        idx = " ".join("%d %d %d" % t for t in tri)
        m = MAT_ID[x.mat]
        geos.append(f"""<geometry id="g{i}"><mesh><source id="g{i}p"><float_array id="g{i}pa" count="24">{pos}</float_array>
<technique_common><accessor source="#g{i}pa" count="8" stride="3"><param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source>
<vertices id="g{i}v"><input semantic="POSITION" source="#g{i}p"/></vertices>
<triangles count="12" material="{m}"><input semantic="VERTEX" source="#g{i}v" offset="0"/><p>{idx}</p></triangles></mesh></geometry>""")
        nodes.append(f"""<node id="n{i}" name="{x.name}"><instance_geometry url="#g{i}"><bind_material><technique_common>
<instance_material symbol="{m}" target="#m_{m}"/></technique_common></bind_material></instance_geometry></node>""")
    effects = "".join(
        f'<effect id="e_{MAT_ID[k]}"><profile_COMMON><technique sid="c"><lambert><diffuse><color>{r} {g} {b} 1</color></diffuse></lambert></technique></profile_COMMON></effect>'
        for k, (r, g, b) in MATS.items())
    mats = "".join(f'<material id="m_{MAT_ID[k]}" name="{k}"><instance_effect url="#e_{MAT_ID[k]}"/></material>' for k in MATS)
    dae = f"""<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
<asset><unit name="millimeter" meter="0.001"/><up_axis>Z_UP</up_axis></asset>
<library_effects>{effects}</library_effects><library_materials>{mats}</library_materials>
<library_geometries>{''.join(geos)}</library_geometries>
<library_visual_scenes><visual_scene id="s" name="Балкон шкаф">{''.join(nodes)}</visual_scene></library_visual_scenes>
<scene><instance_visual_scene url="#s"/></scene></COLLADA>"""
    (OUT / "шкаф.dae").write_text(dae, encoding="utf-8")


def write_rb(p, parts):
    lines = [
        "# ERXAN MEBEL · Балкон шкаф — SketchUp Pro: Window > Ruby Console, paste and press Enter.",
        "model = Sketchup.active_model",
        "model.start_operation('Балкон шкаф', true)",
        "mats = {",
        *[f"  '{k}' => model.materials['{k}'] || model.materials.add('{k}')," for k in MATS],
        "}",
        *[f"mats['{k}'].color = Sketchup::Color.new({int(r * 255)}, {int(g * 255)}, {int(b * 255)})" for k, (r, g, b) in MATS.items()],
        f"root = model.active_entities.add_group",
        f"root.name = 'Балкон шкаф {p['W']}x{p['H']}x{p['D']}'",
        "box = lambda do |name, mat, x, y, z, dx, dy, dz|",
        "  g = root.entities.add_group",
        "  f = g.entities.add_face([x.mm, y.mm, z.mm], [(x + dx).mm, y.mm, z.mm], [(x + dx).mm, (y + dy).mm, z.mm], [x.mm, (y + dy).mm, z.mm])",
        "  f.reverse! if f.normal.z < 0",
        "  f.pushpull(dz.mm)",
        "  g.name = name",
        "  g.material = mats[mat]",
        "end",
        *[f"box.call('{x.name}', '{x.mat}', {x.x:g}, {x.y:g}, {x.z:g}, {x.dx:g}, {x.dy:g}, {x.dz:g})" for x in parts],
        "model.commit_operation",
        "Sketchup.active_model.active_view.zoom_extents",
    ]
    (OUT / "шкаф.rb").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    parts = build(PARAMS)
    hw = hardware(PARAMS, parts)
    total = write_xlsx(PARAMS, parts, hw)
    write_dae(parts)
    write_rb(PARAMS, parts)
    write_sheet(PARAMS, parts, hw, total)
    for f in sorted(OUT.iterdir()):
        print(f.name, f"{f.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
