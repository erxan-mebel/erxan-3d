"""Спальный шкаф 3390 x 2950 x 600 — SketchUp (.rb), COLLADA (.dae) және превью (.png) генераторы.

Барлық өлшем мм. Осьтер: X — ені (солдан оңға), Y — тереңдігі (0 = алдыңғы бет), Z — биіктігі.
Іске қосу: python3 generate.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

T = 16          # ЛДСП қалыңдығы
DVP = 3         # ДВП қалыңдығы
W_TOTAL = 3390
PLANKA = 30
MOD_W = 1110    # бір шкафтың ені
BODY_Y0, BODY_Y1 = 20, 600   # корпус (580) — алдында 4 мм саңылау + 16 мм фасад
SHELF_Y0 = 40                # сөрелер 560 (алдынан 20 мм шегініс)
LEG = 100
LOWER_H = 2290
ANTR_H = 500
CROWN = 60

Z_LOW0 = LEG
Z_LOW1 = LEG + LOWER_H          # 2390
Z_ANT1 = Z_LOW1 + ANTR_H        # 2890
Z_TOP = Z_ANT1 + CROWN          # 2950

MATERIALS = {
    "ЛДСП_корпус": (238, 236, 230),
    "Фасад":       (205, 182, 150),
    "ДВП":         (170, 165, 160),
    "Штанга":      (150, 152, 158),
    "Ножка":       (60, 60, 60),
}

parts = []   # dict(name, group, tag, mat, kind, a, b)


def box(name, group, tag, mat, x0, y0, z0, x1, y1, z1):
    parts.append(dict(name=name, group=group, tag=tag, mat=mat, kind="box",
                      a=(x0, y0, z0), b=(x1, y1, z1)))


def rod(name, group, x0, x1, yc, zc, r=12.5):
    parts.append(dict(name=name, group=group, tag="Штанга", mat="Штанга", kind="rod",
                      a=(x0, yc - r, zc - r), b=(x1, yc + r, zc + r), r=r))


def carcass(g, x0, z0, h, back_name):
    box(f"Бүйір {h}x580", g, "Корпус", "ЛДСП_корпус", x0, BODY_Y0, z0, x0 + T, BODY_Y1, z0 + h)
    box(f"Бүйір {h}x580", g, "Корпус", "ЛДСП_корпус", x0 + MOD_W - T, BODY_Y0, z0, x0 + MOD_W, BODY_Y1, z0 + h)
    box("Түбі 1078x580", g, "Корпус", "ЛДСП_корпус", x0 + T, BODY_Y0, z0, x0 + MOD_W - T, BODY_Y1, z0 + T)
    box("Қақпақ 1078x580", g, "Корпус", "ЛДСП_корпус", x0 + T, BODY_Y0, z0 + h - T, x0 + MOD_W - T, BODY_Y1, z0 + h)
    box(back_name, g, "ДВП", "ДВП", x0 + 2, BODY_Y1, z0 + 2, x0 + MOD_W - 2, BODY_Y1 + DVP, z0 + h - 2)


def door_pair(g, x0, z0, z1, label):
    h = z1 - z0
    box(f"{label} 553x{h:g}", g, "Фасад", "Фасад", x0 + 1.5, 0, z0, x0 + 554.5, T, z1)
    box(f"{label} 553x{h:g}", g, "Фасад", "Фасад", x0 + 555.5, 0, z0, x0 + 1108.5, T, z1)


def legs(g, x0):
    for lx in (x0 + 50, x0 + MOD_W - 90):
        for ly in (70, 520):
            box("Ножка 100", g, "Ножка", "Ножка", lx, ly, 0, lx + 40, ly + 40, LEG)


IN_Z0 = Z_LOW0 + T          # 116
IN_Z1 = Z_LOW1 - T          # 2374
HALF_L = (T, T + 531)       # сол жақ жарты (x0-ге қатысты)
DIV = (T + 531, T + 547)    # ортадағы бөлгіш
HALF_R = (T + 547, MOD_W - T)

for i in range(3):
    x0 = PLANKA + MOD_W * i
    n = i + 1
    g = f"{n}-шкаф"
    ga = f"{n}-антресоль"
    legs(g, x0)
    carcass(g, x0, Z_LOW0, LOWER_H, "Арқасы ДВП 1106x2286")
    carcass(ga, x0, Z_LOW1, ANTR_H, "Арқасы ДВП 1106x496")
    door_pair(ga, x0, Z_LOW1 + 2, Z_ANT1 - 2, "Антресоль есігі (Tip-On)")

    if n == 1:
        box("Бөлгіш 2258x560", g, "Ішкі бөлім", "ЛДСП_корпус",
            x0 + DIV[0], SHELF_Y0, IN_Z0, x0 + DIV[1], BODY_Y1, IN_Z1)
        zs = IN_Z0 + 1100
        for hx in (HALF_L, HALF_R):
            box("Сөре 531x560", g, "Ішкі бөлім", "ЛДСП_корпус",
                x0 + hx[0], SHELF_Y0, zs, x0 + hx[1], BODY_Y1, zs + T)
            for zc in (IN_Z0 + 1050, IN_Z0 + 2200):
                rod("Штанга 529", g, x0 + hx[0] + 1, x0 + hx[1] - 1, 320, zc)
        door_pair(g, x0, Z_LOW0 + 2, Z_LOW1 - 2, "Есік")

    elif n == 2:
        z_sh = Z_LOW0 + 984     # суырмалардың үстіндегі сөре 1084..1100
        box("Сөре (суырма үсті) 1078x580", g, "Ішкі бөлім", "ЛДСП_корпус",
            x0 + T, BODY_Y0, z_sh, x0 + MOD_W - T, BODY_Y1, z_sh + T)
        zd0 = z_sh + T
        box("Бөлгіш 1274x560", g, "Ішкі бөлім", "ЛДСП_корпус",
            x0 + DIV[0], SHELF_Y0, zd0, x0 + DIV[1], BODY_Y1, IN_Z1)
        cell = (IN_Z1 - zd0 - 3 * T) / 4
        for k in range(1, 4):
            zz = zd0 + k * cell + (k - 1) * T
            for hx in (HALF_L, HALF_R):
                box("Сөре 531x560", g, "Ішкі бөлім", "ЛДСП_корпус",
                    x0 + hx[0], SHELF_Y0, zz, x0 + hx[1], BODY_Y1, zz + T)
        for k in range(4):
            fz0 = Z_LOW0 + 2 + 250 * k
            sg = f"{g} / суырма {k + 1}"
            box("Суырма беті 1106x246", sg, "Фасад", "Фасад", x0 + 2, 0, fz0, x0 + 1108, T, fz0 + 246)
            zb = fz0 + 25
            box("Суырма бүйірі 500x180", sg, "Суырма", "ЛДСП_корпус", x0 + 29, 20, zb, x0 + 45, 520, zb + 180)
            box("Суырма бүйірі 500x180", sg, "Суырма", "ЛДСП_корпус", x0 + 1065, 20, zb, x0 + 1081, 520, zb + 180)
            box("Суырма алды 1020x180", sg, "Суырма", "ЛДСП_корпус", x0 + 45, 20, zb, x0 + 1065, 36, zb + 180)
            box("Суырма арты 1020x180", sg, "Суырма", "ЛДСП_корпус", x0 + 45, 504, zb, x0 + 1065, 520, zb + 180)
            box("Суырма түбі ДВП 1052x500", sg, "ДВП", "ДВП", x0 + 29, 20, zb - DVP, x0 + 1081, 520, zb)
        door_pair(g, x0, z_sh + T + 2, Z_LOW1 - 2, "Есік")

    else:
        zs = IN_Z0 + 1000
        box("Сөре 1078x560", g, "Ішкі бөлім", "ЛДСП_корпус",
            x0 + T, SHELF_Y0, zs, x0 + MOD_W - T, BODY_Y1, zs + T)
        door_pair(g, x0, Z_LOW0 + 2, Z_LOW1 - 2, "Есік")

d = "Декор"
half = W_TOTAL / 2
box("Цоколь 1695x100", d, "Декор", "Фасад", 0, BODY_Y0, 0, half, BODY_Y0 + T, LEG)
box("Цоколь 1695x100", d, "Декор", "Фасад", half, BODY_Y0, 0, W_TOTAL, BODY_Y0 + T, LEG)
box("Планка 2790x30", d, "Декор", "Фасад", 0, 0, Z_LOW0, PLANKA, T, Z_ANT1)
box("Планка 2790x30", d, "Декор", "Фасад", W_TOTAL - PLANKA, 0, Z_LOW0, W_TOTAL, T, Z_ANT1)
box("Корона алды 1695x60", d, "Декор", "Фасад", 0, 0, Z_ANT1, half, T, Z_TOP)
box("Корона алды 1695x60", d, "Декор", "Фасад", half, 0, Z_ANT1, W_TOTAL, T, Z_TOP)
box("Корона бүйірі 584x60", d, "Декор", "Фасад", 0, T, Z_ANT1, T, BODY_Y1, Z_TOP)
box("Корона бүйірі 584x60", d, "Декор", "Фасад", W_TOTAL - T, T, Z_ANT1, W_TOTAL, BODY_Y1, Z_TOP)


# ---------------------------------------------------------------- SketchUp Ruby
def fmt(v):
    return f"{v:g}"


def write_rb(path):
    L = []
    L.append("# encoding: UTF-8")
    L.append("# Спальный шкаф 3390 x 2950 x 600 (ЛДСП 16 мм) — SketchUp үшін автоматты сызу.")
    L.append("# Қолдану: Extensions (Расширения) > Developer > Ruby Console ашып, мына жолды жазыңыз:")
    L.append("#   load File.join(Dir.home, 'Downloads', 'shkaf.rb')")
    L.append("# (файл қай қалтада тұрса, 'Downloads' орнына сол қалтаны жазыңыз, мысалы 'Desktop')")
    L.append("")
    L.append("module ErhanShkaf")
    L.append("  def self.pt(x, y, z) Geom::Point3d.new(x.mm, y.mm, z.mm) end")
    L.append("")
    L.append("  def self.box(ents, name, x0, y0, z0, x1, y1, z1, mat, tag)")
    L.append("    g = ents.add_group")
    L.append("    g.name = name")
    L.append("    f = g.entities.add_face(pt(x0, y0, z0), pt(x1, y0, z0), pt(x1, y1, z0), pt(x0, y1, z0))")
    L.append("    f.reverse! if f.normal.z < 0")
    L.append("    f.pushpull((z1 - z0).mm)")
    L.append("    g.material = mat")
    L.append("    g.layer = tag")
    L.append("    g")
    L.append("  end")
    L.append("")
    L.append("  def self.rod(ents, name, x0, x1, yc, zc, r, mat, tag)")
    L.append("    g = ents.add_group")
    L.append("    g.name = name")
    L.append("    edges = g.entities.add_circle(pt(x0, yc, zc), Geom::Vector3d.new(1, 0, 0), r.mm, 24)")
    L.append("    f = g.entities.add_face(edges)")
    L.append("    f.reverse! if f.normal.x < 0")
    L.append("    f.pushpull((x1 - x0).mm)")
    L.append("    g.material = mat")
    L.append("    g.layer = tag")
    L.append("    g")
    L.append("  end")
    L.append("")
    L.append("  def self.build")
    L.append("    model = Sketchup.active_model")
    L.append("    model.start_operation('Спальный шкаф', true)")
    L.append("    mats = {}")
    for k, (r, g_, b) in MATERIALS.items():
        L.append(f"    m = model.materials['{k}'] || model.materials.add('{k}'); m.color = Sketchup::Color.new({r}, {g_}, {b}); mats['{k}'] = m")
    L.append("    tags = {}")
    for t in ["Корпус", "Фасад", "Ішкі бөлім", "Суырма", "Штанга", "ДВП", "Декор", "Ножка"]:
        L.append(f"    tags['{t}'] = model.layers['{t}'] || model.layers.add('{t}')")
    L.append("    root = model.active_entities.add_group")
    L.append("    root.name = 'Спальный шкаф 3390x2950x600'")
    L.append("    grp = {}")
    created = set()
    for p in parts:
        gname = p["group"]
        if gname not in created:   # топ бос қалмауы үшін бірінші бөлшектің алдында ғана жасаймыз
            created.add(gname)
            if " / " in gname:
                parent, child = gname.split(" / ", 1)
                L.append(f"    grp['{gname}'] = grp['{parent}'].entities.add_group; grp['{gname}'].name = '{child}'")
            else:
                L.append(f"    grp['{gname}'] = root.entities.add_group; grp['{gname}'].name = '{gname}'")
        (x0, y0, z0), (x1, y1, z1) = p["a"], p["b"]
        ents = f"grp['{p['group']}'].entities"
        if p["kind"] == "box":
            L.append(f"    box({ents}, '{p['name']}', {fmt(x0)}, {fmt(y0)}, {fmt(z0)}, {fmt(x1)}, {fmt(y1)}, {fmt(z1)}, mats['{p['mat']}'], tags['{p['tag']}'])")
        else:
            r = p["r"]
            L.append(f"    rod({ents}, '{p['name']}', {fmt(x0)}, {fmt(x1)}, {fmt(y0 + r)}, {fmt(z0 + r)}, {fmt(r)}, mats['{p['mat']}'], tags['{p['tag']}'])")
    L.append("    model.commit_operation")
    L.append("    Sketchup.active_model.active_view.zoom_extents")
    L.append(f"    puts 'Дайын: {len(parts)} бөлшек сызылды.'")
    L.append("  end")
    L.append("end")
    L.append("")
    L.append("ErhanShkaf.build")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- COLLADA
def write_dae(path):
    import xml.sax.saxutils as su
    esc = su.escape
    mat_ids = {k: f"mat{i}" for i, k in enumerate(MATERIALS)}
    out = []
    out.append('<?xml version="1.0" encoding="utf-8"?>')
    out.append('<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">')
    out.append('<asset><unit name="millimeter" meter="0.001"/><up_axis>Z_UP</up_axis></asset>')
    out.append('<library_effects>')
    for k, (r, g, b) in MATERIALS.items():
        out.append(f'<effect id="{mat_ids[k]}-fx"><profile_COMMON><technique sid="c"><lambert><diffuse>'
                   f'<color>{r/255:.3f} {g/255:.3f} {b/255:.3f} 1</color></diffuse></lambert></technique></profile_COMMON></effect>')
    out.append('</library_effects><library_materials>')
    for k in MATERIALS:
        out.append(f'<material id="{mat_ids[k]}" name="{esc(k)}"><instance_effect url="#{mat_ids[k]}-fx"/></material>')
    out.append('</library_materials><library_geometries>')
    # quads -> triangles
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    for i, p in enumerate(parts):
        (x0, y0, z0), (x1, y1, z1) = p["a"], p["b"]
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        pos = " ".join(f"{a:g} {b:g} {c:g}" for a, b, c in v)
        idx = " ".join(str(n) for f in faces for n in f)
        out.append(f'<geometry id="g{i}"><mesh><source id="g{i}-p"><float_array id="g{i}-a" count="24">{pos}</float_array>'
                   f'<technique_common><accessor source="#g{i}-a" count="8" stride="3"><param name="X" type="float"/>'
                   f'<param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source>'
                   f'<vertices id="g{i}-v"><input semantic="POSITION" source="#g{i}-p"/></vertices>'
                   f'<triangles material="m" count="12"><input semantic="VERTEX" source="#g{i}-v" offset="0"/><p>{idx}</p></triangles>'
                   f'</mesh></geometry>')
    out.append('</library_geometries><library_visual_scenes><visual_scene id="scene" name="Спальный шкаф">')
    out.append('<node id="root" name="Спальный шкаф 3390x2950x600">')
    for i, p in enumerate(parts):
        out.append(f'<node id="n{i}" name="{esc(p["group"] + " - " + p["name"])}"><instance_geometry url="#g{i}">'
                   f'<bind_material><technique_common><instance_material symbol="m" target="#{mat_ids[p["mat"]]}"/>'
                   f'</technique_common></bind_material></instance_geometry></node>')
    out.append('</node></visual_scene></library_visual_scenes><scene><instance_visual_scene url="#scene"/></scene></COLLADA>')
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


# ---------------------------------------------------------------- превью (алдынан көрініс)
def write_preview(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=110)
    for ax, hide, title in ((axes[0], (), "Есіктері жабық"),
                            (axes[1], ("Фасад",), "Есіктерсіз (іші)")):
        # артынан алдына қарай сызамыз (Y кему ретімен)
        for p in sorted(parts, key=lambda q: -q["a"][1]):
            if p["tag"] in hide:
                continue
            (x0, y0, z0), (x1, y1, z1) = p["a"], p["b"]
            c = [x / 255 for x in MATERIALS[p["mat"]]]
            if p["tag"] == "ДВП" and "Арқасы" in p["name"]:
                c = (0.80, 0.78, 0.75)
            ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=c,
                                   edgecolor=(0.3, 0.3, 0.3), linewidth=0.5))
        ax.set_xlim(-250, 3600); ax.set_ylim(-250, 3150)
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=14)
        kw = dict(fontsize=9, ha="center", va="center")
        ax.annotate("", (0, -120), (3390, -120), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(1695, -190, "3390", **kw)
        ax.annotate("", (-120, 0), (-120, 2950), arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(-190, 1475, "2950", rotation=90, **kw)
        for i in range(3):
            ax.text(PLANKA + MOD_W * i + MOD_W / 2, 3040, f"{i + 1}-шкаф · 1110", **kw)
        ax.text(3480, Z_LOW1 + ANTR_H / 2, "500", rotation=90, **kw)
        ax.text(3480, Z_LOW0 + LOWER_H / 2, "2290", rotation=90, **kw)
        ax.text(3480, Z_ANT1 + 30, "60", **kw)
        ax.text(3480, 50, "100", **kw)
    plt.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    write_rb(os.path.join(HERE, "shkaf.rb"))
    write_dae(os.path.join(HERE, "shkaf.dae"))
    write_preview(os.path.join(HERE, "preview.png"))
    print(len(parts), "бөлшек")
