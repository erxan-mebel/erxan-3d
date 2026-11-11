// Дайын корпустар мен техника: каталог және 3D модельдер.
// Модельдің жергілікті координаттары: артқы-сол-төменгі бұрыш (0,0,0),
// X — ені, Y — биіктігі, Z — тереңдігі (артқы қабырғадан алға қарай).
import * as THREE from 'three';
import { plainMaterial, facadeMaterials, glassMaterial } from './facade.js';

export const T = 16;     // корпус ЛДСП қалыңдығы
export const FT = 18;    // фасад қалыңдығы
export const BACK = 4;   // артқы ХДФ
export const GAP = 3;    // фасадтар арасындағы саңылау
export const TOP_T = 38; // столешница қалыңдығы

export const GROUPS = [
  { id: 'base', name: 'Төменгі шкафтар' },
  { id: 'wall', name: 'Үстіңгі шкафтар' },
  { id: 'corner', name: 'Бұрыштық шкафтар' },
  { id: 'tall', name: 'Биік шкафтар' },
  { id: 'tech', name: 'Техника' },
];

// fields — «Баптау» бөлімінде көрсетілетін өрістер
const F_BASE = ['w', 'h', 'd', 'plinth', 'shelves', 'countertop', 'facade', 'body'];
const F_WALL = ['w', 'h', 'd', 'y', 'shelves', 'facade', 'body'];

export const CATALOG = [
  // Төменгі
  { kind: 'base', group: 'base', name: 'Есікті шкаф', place: 'floor', w: 600, h: 720, d: 560, plinth: 100, front: 'doors', doors: 2, shelves: 1, countertop: true, fields: [...F_BASE, 'doors'] },
  { kind: 'base-drawers', group: 'base', name: 'Тартпалы шкаф', place: 'floor', w: 500, h: 720, d: 560, plinth: 100, front: 'drawers', drawers: 3, countertop: true, fields: ['w', 'h', 'd', 'plinth', 'drawers', 'countertop', 'facade', 'body'] },
  { kind: 'base-sink', group: 'base', name: 'Жуғыш шкафы', place: 'floor', w: 800, h: 720, d: 560, plinth: 100, front: 'doors', doors: 2, countertop: true, fields: ['w', 'h', 'd', 'plinth', 'doors', 'facade', 'body'] },
  { kind: 'base-oven', group: 'base', name: 'Плита + духовка', place: 'floor', w: 600, h: 720, d: 560, plinth: 100, countertop: true, hob: 'induction', fields: ['w', 'h', 'd', 'plinth', 'hob', 'facade', 'body'] },
  // Үстіңгі
  { kind: 'wall', group: 'wall', name: 'Үстіңгі шкаф', place: 'wall', w: 600, h: 720, d: 320, y: 1450, front: 'doors', doors: 2, shelves: 2, fields: [...F_WALL, 'doors'] },
  { kind: 'shelf', group: 'wall', name: 'Ашық сөре', place: 'wall', w: 800, h: 360, d: 300, y: 1500, front: 'none', fields: ['w', 'h', 'd', 'y', 'shelves', 'body'] },
  // Бұрыштық
  { kind: 'base-corner', group: 'corner', name: 'Бұрыштық төменгі', place: 'floor', corner: true, w: 900, w2: 900, h: 720, d: 560, plinth: 100, shelves: 1, countertop: true, fields: ['w', 'w2', 'h', 'd', 'plinth', 'shelves', 'countertop', 'facade', 'body'] },
  { kind: 'wall-corner', group: 'corner', name: 'Бұрыштық үстіңгі', place: 'wall', corner: true, w: 600, w2: 600, h: 720, d: 320, y: 1450, shelves: 2, fields: ['w', 'w2', 'h', 'd', 'y', 'shelves', 'facade', 'body'] },
  // Биік
  { kind: 'tall', group: 'tall', name: 'Пенал', place: 'floor', w: 600, h: 2100, d: 560, plinth: 100, front: 'tall', doors: 1, shelves: 4, fields: ['w', 'h', 'd', 'plinth', 'doors', 'shelves', 'facade', 'body'] },
  { kind: 'tall-oven', group: 'tall', name: 'Пенал: духовка + микро', place: 'floor', w: 600, h: 2100, d: 560, plinth: 100, fields: ['w', 'h', 'd', 'plinth', 'facade', 'body'] },
  { kind: 'wardrobe', group: 'tall', name: 'Киім шкафы', place: 'floor', w: 1200, h: 2300, d: 600, plinth: 80, front: 'doors', doors: 2, shelves: 1, rod: true, fields: ['w', 'h', 'd', 'plinth', 'doors', 'shelves', 'facade', 'body'] },
  // Техника
  { kind: 'fridge', group: 'tech', name: 'Тоңазытқыш', place: 'floor', tech: true, w: 600, h: 1850, d: 650, tone: 'steel', fields: ['w', 'h', 'd', 'tone'] },
  { kind: 'fridge-side', group: 'tech', name: 'Тоңазытқыш Side-by-Side', place: 'floor', tech: true, w: 910, h: 1780, d: 710, tone: 'steel', fields: ['w', 'h', 'd', 'tone'] },
  { kind: 'stove', group: 'tech', name: 'Плита (бөлек)', place: 'floor', tech: true, w: 600, h: 850, d: 600, tone: 'white', hob: 'gas', fields: ['w', 'h', 'd', 'tone', 'hob'] },
  { kind: 'hood', group: 'tech', name: 'Сорғыш (вытяжка)', place: 'wall', tech: true, w: 600, h: 900, d: 500, y: 1550, tone: 'steel', fields: ['w', 'h', 'd', 'y', 'tone'] },
  { kind: 'dishwasher-builtin', group: 'tech', name: 'Ыдыс жуғыш (кіріктірілген)', place: 'floor', tech: true, w: 600, h: 720, d: 560, plinth: 100, countertop: true, fields: ['w', 'h', 'd', 'plinth', 'countertop', 'facade'] },
  { kind: 'dishwasher', group: 'tech', name: 'Ыдыс жуғыш (бөлек)', place: 'floor', tech: true, w: 600, h: 850, d: 600, tone: 'white', fields: ['w', 'h', 'd', 'tone'] },
  { kind: 'micro', group: 'tech', name: 'Микротолқынды (қарапайым)', place: 'wall', tech: true, w: 480, h: 280, d: 380, y: 858, tone: 'black', fields: ['w', 'h', 'd', 'y', 'tone'] },
  { kind: 'micro-builtin', group: 'tech', name: 'Микротолқынды (кіріктірілген)', place: 'wall', tech: true, w: 595, h: 380, d: 400, y: 1400, tone: 'steel', fields: ['w', 'h', 'd', 'y', 'tone'] },
  { kind: 'washer', group: 'tech', name: 'Кір жуғыш машина', place: 'floor', tech: true, w: 600, h: 850, d: 560, tone: 'white', fields: ['w', 'h', 'd', 'tone'] },
  { kind: 'tv', group: 'tech', name: 'Теледидар', place: 'wall', tech: true, w: 1230, h: 710, d: 60, y: 1000, fields: ['tv', 'y'] },
];

export const TONES = [
  { id: 'steel', name: 'Болат' },
  { id: 'white', name: 'Ақ' },
  { id: 'black', name: 'Қара' },
];
export const HOBS = [
  { id: 'induction', name: 'Индукция' },
  { id: 'gas', name: 'Газ' },
];
// Теледидар өлшемдері (диагональ → ені × биіктігі, мм)
export const TV_SIZES = [
  { id: 43, w: 970, h: 565 },
  { id: 50, w: 1125, h: 650 },
  { id: 55, w: 1230, h: 710 },
  { id: 65, w: 1450, h: 835 },
  { id: 75, w: 1675, h: 960 },
];

export function getDef(kind) {
  return CATALOG.find((c) => c.kind === kind) || CATALOG[0];
}

let nextId = 1;
export function setNextId(n) { nextId = Math.max(nextId, n); }
export function takeId() { return nextId++; }

export function newItem(kind, extra = {}) {
  const def = getDef(kind);
  return {
    id: nextId++,
    kind,
    x: 0, z: 0, rot: 0,
    y: def.y || 0,
    w: def.w, h: def.h, d: def.d,
    w2: def.w2 || 0,
    plinth: def.plinth || 0,
    doors: def.doors || 0,
    drawers: def.drawers || 0,
    shelves: def.shelves || 0,
    countertop: !!def.countertop,
    tone: def.tone || 'steel',
    hob: def.hob || 'induction',
    body: '#f1f0ec',
    facade: '#f1f0ec',
    pattern: 'flat',   // есік өрнегі (facade.js → PATTERNS)
    gloss: false,      // жылтыр фасад
    patternImg: '',    // «Өз суретім» үшін сурет (dataURL)
    ...extra,
  };
}

// Жалпы биіктік (столешницамен бірге)
export function totalHeight(it) {
  return (it.plinth || 0) + it.h + (it.countertop ? TOP_T : 0);
}

// Еденде алатын тікбұрышы (бұрыштық шкаф — екі қанаттың сыртқы өлшемі)
export function footprint(it) {
  return getDef(it.kind).corner ? { fw: it.w, fd: it.w2 || it.w } : { fw: it.w, fd: it.d };
}

export function halfExtents(it) {
  const { fw, fd } = footprint(it);
  return it.rot % 2 === 0 ? { hx: fw / 2, hz: fd / 2 } : { hx: fd / 2, hz: fw / 2 };
}

// ---------- геометрия мен материалдар ----------
const BOX = new THREE.BoxGeometry(1, 1, 1);
BOX.translate(0.5, 0.5, 0.5); // масштабталған қорап min-бұрыштан басталады
const EDGES = new THREE.EdgesGeometry(BOX);
const edgeMat = new THREE.LineBasicMaterial({ color: 0x1b221e, transparent: true, opacity: 0.35 });

const matCache = new Map();
function mat(color, rough = 0.7, metal = 0, extra = {}) {
  const key = `${color}|${rough}|${metal}|${JSON.stringify(extra)}`;
  if (!matCache.has(key)) matCache.set(key, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal, ...extra }));
  return matCache.get(key);
}
const M = {
  back: () => mat('#d9d6cf', 0.9),
  dark: () => mat('#2a2d2b', 0.8),
  steel: () => mat('#c9ccce', 0.28, 0.9),
  chrome: () => mat('#e4e6e8', 0.15, 1),
  top: () => mat('#b98c5c', 0.55),
  glass: () => mat('#0c0d0f', 0.08, 0.3),
  window: () => mat('#26292c', 0.12, 0.2),
  plastic: () => mat('#18191b', 0.5),
  screen: () => mat('#07080a', 0.12, 0.5),
  light: () => mat('#fff6dd', 0.5, 0, { emissive: '#fff1c8', emissiveIntensity: 1.2 }),
};
function toneMat(tone) {
  if (tone === 'white') return mat('#f2f2ef', 0.35, 0.05);
  if (tone === 'black') return mat('#1f2022', 0.32, 0.4);
  return mat('#c3c7ca', 0.3, 0.85);
}

function cyl(parent, r, len, m, x, y, z, axis = 'y', seg = 24) {
  const c = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, seg), m);
  if (axis === 'z') c.rotation.x = Math.PI / 2;
  if (axis === 'x') c.rotation.z = Math.PI / 2;
  c.position.set(x, y, z);
  c.castShadow = true;
  parent.add(c);
  return c;
}

// ---------- құрастырушы ----------
function makeCtx(it) {
  const g = new THREE.Group();
  const box = (parent, sx, sy, sz, x, y, z, m, edges = true) => {
    if (sx <= 0 || sy <= 0 || sz <= 0) return null;
    const mesh = new THREE.Mesh(BOX, m);
    mesh.scale.set(sx, sy, sz);
    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    if (edges) mesh.add(new THREE.LineSegments(EDGES, edgeMat));
    parent.add(mesh);
    return mesh;
  };
  const bodyM = plainMaterial(it.body || '#f1f0ec');

  // Бір есік/тартпа беті (z — фасадтың артқы жазықтығы)
  const facade = (parent, fw, fh, x, y, z) => {
    const pattern = it.pattern || 'flat';
    if (pattern === 'glass' && fw > 200 && fh > 200) {
      const fm = plainMaterial(it.facade, it.gloss);
      const r = 60;
      box(parent, r, fh, FT, x, y, z, fm);
      box(parent, r, fh, FT, x + fw - r, y, z, fm);
      box(parent, fw - 2 * r, r, FT, x + r, y, z, fm);
      box(parent, fw - 2 * r, r, FT, x + r, y + fh - r, z, fm);
      const gl = box(parent, fw - 2 * r, fh - 2 * r, 4, x + r, y + r, z + FT / 2 - 2, glassMaterial, false);
      if (gl) gl.castShadow = false;
      return;
    }
    const p = pattern === 'glass' ? 'frame' : pattern;
    box(parent, fw, fh, FT, x, y, z, facadeMaterials(it.facade, p, it.gloss, fw, fh, it.patternImg));
  };

  // Хром тұтқа (z — фасадтың алдыңғы беті)
  const handle = (parent, x, y, z, vertical, len = 128) => {
    if (vertical) box(parent, 12, len, 14, x - 6, y - len / 2, z, M.steel(), false);
    else box(parent, len, 12, 14, x - len / 2, y - 6, z, M.steel(), false);
  };

  // Тікбұрышты корпус (бүйірлер, түбі, қақпағы/планкалары, артқы ХДФ, сөрелер)
  const carcass = (parent, w, h, d, y0, { shelves = 0, rails = false, x0 = 0 } = {}) => {
    box(parent, T, h, d - BACK, x0, y0, BACK, bodyM);
    box(parent, T, h, d - BACK, x0 + w - T, y0, BACK, bodyM);
    box(parent, w - 2 * T, T, d - BACK, x0 + T, y0, BACK, bodyM);
    if (rails) {
      box(parent, w - 2 * T, T, 100, x0 + T, y0 + h - T, BACK, bodyM);
      box(parent, w - 2 * T, T, 100, x0 + T, y0 + h - T, d - 100, bodyM);
    } else {
      box(parent, w - 2 * T, T, d - BACK, x0 + T, y0 + h - T, BACK, bodyM);
    }
    box(parent, w, h, BACK, x0, y0, 0, M.back(), false);
    for (let i = 1; i <= shelves; i++) {
      const sy = y0 + T + ((h - 2 * T) * i) / (shelves + 1) - T / 2;
      box(parent, w - 2 * T, T, d - BACK - 20, x0 + T, sy, BACK, bodyM);
    }
  };

  // Есіктер қатары
  const doorsRow = (parent, w, d, count, yb, hh, at, x0 = 0) => {
    const dw = (w - GAP * count) / count;
    for (let i = 0; i < count; i++) {
      const x = x0 + GAP / 2 + i * (dw + GAP);
      facade(parent, dw, hh - GAP, x, yb + GAP / 2, d);
      const hingeLeft = count === 1 ? true : i % 2 === 0;
      const hx = hingeLeft ? x + dw - 40 : x + 40;
      const hy = at === 'top' ? yb + hh - 110 : at === 'bottom' ? yb + 110 : yb + hh / 2;
      handle(parent, hx, hy, d + FT, true);
    }
  };

  // Тартпалар (биіктіктері төменнен жоғары)
  const drawers = (parent, w, d, y0, heights) => {
    let y = y0;
    for (const hh of heights) {
      facade(parent, w - GAP, hh - GAP, GAP / 2, y + GAP / 2, d);
      handle(parent, w / 2, y + hh - 50, d + FT, false);
      y += hh;
    }
  };

  const plinthStrip = (parent, w, d, x0 = 0) => {
    if (it.plinth > 0) box(parent, w, it.plinth, T, x0, 0, d - 60, M.dark());
  };
  const countertop = (parent, w, d, y) => box(parent, w, TOP_T, d + 30, 0, y, 0, M.top());

  return { g, box, facade, handle, carcass, doorsRow, drawers, plinthStrip, countertop, bodyM };
}

// ---------- техника бөлшектері ----------

// Кіріктірілген духовка беті: x,y — сол-төменгі бұрыш, z — алдыңғы жазықтық
function ovenFace(c, parent, x, y, fw, fh, z) {
  c.box(parent, fw, fh, 20, x, y, z - 20, M.steel(), false);
  c.box(parent, fw - 16, fh - 110, 8, x + 8, y + 8, z, M.glass(), false);
  c.box(parent, fw - 130, fh - 250, 2, x + 65, y + 50, z + 8, M.window(), false);
  c.box(parent, fw - 16, 86, 8, x + 8, y + fh - 94, z, M.plastic(), false);
  for (const kx of [x + 70, x + fw - 70]) cyl(parent, 17, 22, M.chrome(), kx, y + fh - 51, z + 18, 'z');
  c.box(parent, 90, 26, 2, x + fw / 2 - 45, y + fh - 64, z + 8, M.light(), false);
  c.box(parent, fw - 150, 14, 16, x + 75, y + fh - 135, z + 24, M.chrome(), false);
  for (const sx of [x + 85, x + fw - 95]) c.box(parent, 10, 10, 16, sx, y + fh - 133, z + 8, M.chrome(), false);
}

// Кіріктірілген микротолқынды пеш беті
function microFace(c, parent, x, y, fw, fh, z, tone = 'steel') {
  c.box(parent, fw, fh, 20, x, y, z - 20, toneMat(tone), false);
  const dw = (fw - 24) * 0.72;
  c.box(parent, dw, fh - 24, 8, x + 12, y + 12, z, M.glass(), false);
  c.box(parent, dw - 80, fh - 110, 2, x + 52, y + 55, z + 8, M.window(), false);
  c.box(parent, fw - 36 - dw, fh - 24, 8, x + 24 + dw, y + 12, z, M.plastic(), false);
  const px = x + 24 + dw + (fw - 36 - dw) / 2;
  c.box(parent, 70, 22, 2, px - 35, y + fh - 60, z + 8, M.light(), false);
  cyl(parent, 18, 16, M.chrome(), px, y + fh * 0.45, z + 14, 'z');
}

// Варочная панель столешницаның үстінде: x0 — сол жақ, y — столешница беті
function hob(c, parent, type, x0, w, y, d) {
  const hw = Math.min(580, w - 20), hd = Math.min(510, d - 40);
  const hx = x0 + (w - hw) / 2, hz = 30;
  if (type === 'gas') {
    c.box(parent, hw, 6, hd, hx, y, hz, M.steel(), false);
    const pos = [[0.27, 0.3], [0.73, 0.3], [0.27, 0.72], [0.73, 0.72]];
    for (const [fx, fz] of pos) {
      const bx = hx + hw * fx, bz = hz + hd * fz;
      cyl(parent, 42, 10, M.plastic(), bx, y + 11, bz);
      cyl(parent, 26, 8, M.dark(), bx, y + 18, bz);
      c.box(parent, 190, 8, 10, bx - 95, y + 24, bz - 5, M.plastic(), false);
      c.box(parent, 10, 8, 190, bx - 5, y + 24, bz - 95, M.plastic(), false);
    }
  } else {
    c.box(parent, hw, 5, hd, hx, y, hz, M.glass(), false);
    const ringM = mat('#5b5f63', 0.4, 0.3);
    const pos = [[0.27, 0.3, 95], [0.73, 0.3, 75], [0.27, 0.72, 75], [0.73, 0.72, 105]];
    for (const [fx, fz, r] of pos) {
      const ring = new THREE.Mesh(new THREE.RingGeometry(r - 4, r, 48), ringM);
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(hx + hw * fx, y + 5.5, hz + hd * fz);
      parent.add(ring);
    }
  }
}

// Жуғыш және кран: столешница бетінде
function sink(c, parent, x0, w, y) {
  const sw = Math.min(w - 120, 600), sd = 440, sx = x0 + (w - sw) / 2, sz = 70;
  c.box(parent, sw, 3, sd, sx, y, sz, M.steel(), false);
  c.box(parent, sw - 50, 2, sd - 50, sx + 25, y + 2.5, sz + 25, mat('#8e9396', 0.35, 0.8), false);
  cyl(parent, 18, 6, mat('#5a5e61', 0.4, 0.8), sx + sw / 2, y + 5, sz + sd / 2, 'y');
  // кран
  const fx = sx + sw / 2, fz = sz - 25;
  cyl(parent, 22, 40, M.chrome(), fx, y + 20, fz);
  cyl(parent, 12, 260, M.chrome(), fx, y + 170, fz);
  const arc = new THREE.Mesh(new THREE.TorusGeometry(90, 12, 12, 24, Math.PI), M.chrome());
  arc.rotation.y = -Math.PI / 2;
  arc.position.set(fx, y + 300, fz + 90);
  parent.add(arc);
  cyl(parent, 12, 70, M.chrome(), fx, y + 265, fz + 180);
  c.box(parent, 12, 12, 70, fx + 18, y + 200, fz - 6, M.chrome(), false);
}

// ---------- әр түрдің моделі ----------
const BUILD = {
  standard(c, it) {
    const def = getDef(it.kind);
    const { w, h, d } = it;
    const y0 = it.plinth;
    c.carcass(c.g, w, h, d, y0, { shelves: it.shelves, rails: it.kind === 'base-sink' });
    if (def.rod) cyl(c.g, 12, w - 2 * T, M.steel(), w / 2, y0 + h - 380, d / 2, 'x');
    c.plinthStrip(c.g, w, d);
    if (it.countertop) c.countertop(c.g, w, d, y0 + h);
    const n = Math.max(1, it.doors);
    if (def.front === 'doors') {
      const at = def.place === 'wall' ? 'bottom' : it.kind === 'wardrobe' ? 'mid' : 'top';
      c.doorsRow(c.g, w, d, n, y0, h, at);
    } else if (def.front === 'tall') {
      const low = Math.min(h - 400, Math.round(h * 0.62));
      c.doorsRow(c.g, w, d, n, y0, low, 'top');
      c.doorsRow(c.g, w, d, n, y0 + low, h - low, 'bottom');
    } else if (def.front === 'drawers') {
      const m = Math.max(1, it.drawers);
      const topH = m >= 3 ? Math.round(h * 0.2) : h / m;
      const restH = m >= 3 ? (h - topH) / (m - 1) : h / m;
      c.drawers(c.g, w, d, y0, Array.from({ length: m }, (_, i) => (i === m - 1 ? topH : restH)));
    }
    if (it.kind === 'base-sink' && it.countertop) sink(c, c.g, 0, w, y0 + h + TOP_T);
  },

  'base-oven'(c, it) {
    const { w, h, d } = it;
    const y0 = it.plinth;
    c.carcass(c.g, w, h, d, y0, { rails: true });
    c.plinthStrip(c.g, w, d);
    c.countertop(c.g, w, d, y0 + h);
    const dh = 150;
    c.drawers(c.g, w, d, y0, [dh]);
    ovenFace(c, c.g, GAP / 2, y0 + dh + GAP / 2, w - GAP, h - dh - GAP, d + FT);
    hob(c, c.g, it.hob, 0, w, y0 + h + TOP_T, d);
  },

  'tall-oven'(c, it) {
    const { w, h, d } = it;
    const y0 = it.plinth;
    c.carcass(c.g, w, h, d, y0, { shelves: 0 });
    c.plinthStrip(c.g, w, d);
    const low = 720, oven = 595, micro = 380;
    const top = Math.max(150, h - low - oven - micro);
    c.doorsRow(c.g, w, d, 1, y0, low, 'top');
    ovenFace(c, c.g, GAP / 2, y0 + low + GAP / 2, w - GAP, oven - GAP, d + FT);
    microFace(c, c.g, GAP / 2, y0 + low + oven + GAP / 2, w - GAP, micro - GAP, d + FT);
    c.doorsRow(c.g, w, d, 1, y0 + low + oven + micro, top, 'bottom');
  },

  // L-тәрізді бұрыштық шкаф: артқы қанат X бойымен (w), бүйір қанат Z бойымен (w2), бұрышы (0,0)
  corner(c, it) {
    const { w, h, d } = it;
    const w2 = it.w2 || w;
    const y0 = it.plinth;
    const g = c.g;
    const bodyM = c.bodyM;
    // Артқы қанат
    c.box(g, T, h, d - BACK, w - T, y0, BACK, bodyM);
    c.box(g, w - T - BACK, T, d - BACK, BACK, y0, BACK, bodyM);
    c.box(g, w - T - BACK, T, d - BACK, BACK, y0 + h - T, BACK, bodyM);
    c.box(g, w, h, BACK, 0, y0, 0, M.back(), false);
    // Бүйір қанат
    c.box(g, d - BACK, h, T, BACK, y0, w2 - T, bodyM);
    c.box(g, d - BACK, T, w2 - d - T, BACK, y0, d, bodyM);
    c.box(g, d - BACK, T, w2 - d - T, BACK, y0 + h - T, d, bodyM);
    c.box(g, BACK, h, w2 - BACK, 0, y0, BACK, M.back(), false);
    for (let i = 1; i <= it.shelves; i++) {
      const sy = y0 + T + ((h - 2 * T) * i) / (it.shelves + 1) - T / 2;
      c.box(g, w - T - BACK, T, d - BACK - 20, BACK, sy, BACK, bodyM);
      c.box(g, d - BACK - 20, T, w2 - d - T, BACK, sy, d, bodyM);
    }
    const at = getDef(it.kind).place === 'wall' ? 'bottom' : 'top';
    const hy = at === 'top' ? y0 + h - 110 : y0 + 110;
    // Есік 1: артқы қанаттың алдында (x: d..w)
    const fw1 = w - d - FT - GAP;
    c.facade(g, fw1, h - GAP, d + FT + GAP / 2, y0 + GAP / 2, d);
    c.handle(g, d + 40, hy, d + FT, true);
    // Есік 2: бүйір қанаттың алдында, +X жаққа қарайды
    const side = new THREE.Group();
    side.rotation.y = Math.PI / 2; // жергілікті X → әлемдік −Z, жергілікті Z → әлемдік +X
    side.position.set(0, 0, w2);
    g.add(side);
    const fw2 = w2 - d - GAP;
    c.facade(side, fw2, h - GAP, GAP / 2, y0 + GAP / 2, d);
    c.handle(side, fw2 - 40, hy, d + FT, true);
    // Цоколь мен столешница
    if (it.plinth > 0) {
      c.box(g, w - d + 60, it.plinth, T, d - 60, 0, d - 60, M.dark());
      c.box(g, T, it.plinth, w2 - d + 60, d - 60, 0, d - 60, M.dark());
    }
    if (it.countertop) {
      c.box(g, w, TOP_T, d + 30, 0, y0 + h, 0, M.top());
      c.box(g, d + 30, TOP_T, w2 - d - 30, 0, y0 + h, d + 30, M.top());
    }
  },

  fridge(c, it) {
    const { w, h, d } = it;
    const tm = toneMat(it.tone);
    const dd = 50;
    c.box(c.g, w, h - 20, d - dd, 0, 20, 0, tm);
    c.box(c.g, w - 40, 20, d - 80, 20, 0, 20, M.plastic(), false);
    const low = Math.round(h * 0.36);
    c.box(c.g, w, low - 22, dd, 0, 20, d - dd, tm);
    c.box(c.g, w, h - low - 4, dd, 0, low + 2, d - dd, tm);
    c.box(c.g, 16, 320, 22, w - 40, low - 360, d, M.chrome(), false);
    c.box(c.g, 16, 420, 22, w - 40, low + 30, d, M.chrome(), false);
  },

  'fridge-side'(c, it) {
    const { w, h, d } = it;
    const tm = toneMat(it.tone);
    const dd = 55;
    c.box(c.g, w, h - 20, d - dd, 0, 20, 0, tm);
    c.box(c.g, w - 40, 20, d - 80, 20, 0, 20, M.plastic(), false);
    const lw = Math.round(w * 0.45);
    c.box(c.g, lw - 2, h - 22, dd, 0, 20, d - dd, tm);
    c.box(c.g, w - lw - 2, h - 22, dd, lw + 2, 20, d - dd, tm);
    c.box(c.g, 16, 900, 22, lw - 40, h * 0.3, d, M.chrome(), false);
    c.box(c.g, 16, 900, 22, lw + 24, h * 0.3, d, M.chrome(), false);
    c.box(c.g, 150, 260, 2, lw / 2 - 75, h * 0.58, d, M.glass(), false);
    c.box(c.g, 60, 120, 2, lw / 2 - 30, h * 0.62, d + 2, mat('#2d3238', 0.2, 0.3), false);
  },

  stove(c, it) {
    const { w, h, d } = it;
    const tm = toneMat(it.tone);
    c.box(c.g, w, h - 20, d - 20, 0, 20, 0, tm);
    c.box(c.g, w - 40, 20, d - 60, 20, 0, 20, M.plastic(), false);
    // басқару панелі
    c.box(c.g, w, 90, 20, 0, h - 110, d - 20, tm, false);
    for (let i = 0; i < 5; i++) cyl(c.g, 18, 22, M.plastic(), 70 + i * ((w - 140) / 4), h - 65, d + 10, 'z');
    // духовка есігі
    c.box(c.g, w - 20, h - 300, 16, 10, 170, d - 20, M.glass(), false);
    c.box(c.g, w - 140, h - 460, 2, 70, 230, d - 4, M.window(), false);
    c.box(c.g, w - 120, 14, 18, 60, h - 160, d - 4, M.chrome(), false);
    // төменгі тартпа
    c.box(c.g, w - 20, 130, 16, 10, 30, d - 20, tm);
    hob(c, c.g, it.hob, 0, w, h - 20, d);
    if (it.hob === 'gas') c.box(c.g, w, 20, 20, 0, h - 20, 0, tm, false);
  },

  hood(c, it) {
    const { w, h, d } = it;
    const tm = toneMat(it.tone);
    const canopy = 80;
    c.box(c.g, w, canopy, d, 0, 0, 0, tm);
    c.box(c.g, w - 40, 4, d - 60, 20, -2, 20, mat('#6d7275', 0.5, 0.6), false);
    for (const lx of [w * 0.25, w * 0.75]) cyl(c.g, 22, 4, M.light(), lx, -3, d - 70);
    const cw = Math.min(280, w * 0.5);
    c.box(c.g, cw, h - canopy, 260, (w - cw) / 2, canopy, 0, tm);
    c.box(c.g, 90, 18, 4, w / 2 - 45, 30, d, M.plastic(), false);
  },

  'dishwasher-builtin'(c, it) {
    const { w, h, d } = it;
    const y0 = it.plinth;
    c.box(c.g, w - 6, h - 20, d - 30, 3, y0 + 10, 0, M.steel());
    c.plinthStrip(c.g, w, d);
    if (it.countertop) c.countertop(c.g, w, d, y0 + h);
    c.facade(c.g, w - GAP, h - GAP, GAP / 2, y0 + GAP / 2, d);
    c.handle(c.g, w / 2, y0 + h - 60, d + FT, false);
  },

  dishwasher(c, it) {
    const { w, h, d } = it;
    const tm = toneMat(it.tone);
    c.box(c.g, w, h - 20, d - 20, 0, 20, 0, tm);
    c.box(c.g, w - 40, 20, d - 60, 20, 0, 20, M.plastic(), false);
    c.box(c.g, w - 10, h - 140, 16, 5, 30, d - 20, tm);
    c.box(c.g, w - 10, 90, 16, 5, h - 105, d - 20, M.plastic(), false);
    c.box(c.g, 80, 22, 2, w - 140, h - 72, d - 4, M.light(), false);
    for (let i = 0; i < 4; i++) cyl(c.g, 7, 6, M.chrome(), 50 + i * 40, h - 60, d - 2, 'z', 12);
    c.box(c.g, w - 160, 14, 18, 80, h - 160, d - 4, M.chrome(), false);
  },

  micro(c, it) {
    const { w, h, d } = it;
    const tm = toneMat(it.tone);
    c.box(c.g, w, h - 10, d - 20, 0, 10, 0, tm);
    for (const fx of [30, w - 50]) c.box(c.g, 20, 10, 20, fx, 0, d - 60, M.plastic(), false);
    microFace(c, c.g, 0, 10, w, h - 10, d, it.tone);
  },

  'micro-builtin'(c, it) {
    const { w, h, d } = it;
    c.box(c.g, w - 30, h - 20, d - 30, 15, 10, 0, M.dark(), false);
    microFace(c, c.g, 0, 0, w, h, d, it.tone);
  },

  washer(c, it) {
    const { w, h, d } = it;
    const tm = toneMat(it.tone);
    c.box(c.g, w, h - 15, d, 0, 15, 0, tm);
    c.box(c.g, w - 40, 15, d - 60, 20, 0, 20, M.plastic(), false);
    c.box(c.g, w, 4, d, 0, h, 0, mat('#e1e2df', 0.5), false);
    // басқару панелі
    c.box(c.g, w - 20, 100, 3, 10, h - 115, d, M.plastic(), false);
    c.box(c.g, 140, 70, 6, 20, h - 100, d, tm, false);
    cyl(c.g, 30, 24, M.chrome(), w - 90, h - 65, d + 12, 'z');
    c.box(c.g, 110, 28, 2, w / 2 - 40, h - 78, d + 3, M.light(), false);
    // есік: сақина және әйнек
    const cy = (h - 115) * 0.5 + 20, r = Math.min(w, h) * 0.3;
    const ring = new THREE.Mesh(new THREE.TorusGeometry(r, 22, 16, 48), mat('#d9dbdd', 0.25, 0.7));
    ring.position.set(w / 2, cy, d + 18);
    ring.castShadow = true;
    c.g.add(ring);
    const glassDisc = new THREE.Mesh(new THREE.CircleGeometry(r - 12, 48), mat('#2a3138', 0.05, 0.3, { transparent: true, opacity: 0.9 }));
    glassDisc.position.set(w / 2, cy, d + 16);
    c.g.add(glassDisc);
    c.box(c.g, 26, 70, 20, w / 2 + r - 5, cy - 35, d + 10, M.plastic(), false);
  },

  tv(c, it) {
    const { w, h } = it;
    c.box(c.g, w * 0.5, h * 0.5, 40, w * 0.25, h * 0.25, 0, M.plastic(), false);
    c.box(c.g, w, h, 22, 0, 0, 40, mat('#141518', 0.4, 0.3));
    c.box(c.g, w - 14, h - 14, 2, 7, 7, 62, M.screen(), false);
  },
};

export function buildItem(it) {
  const c = makeCtx(it);
  const def = getDef(it.kind);
  const fn = def.corner ? BUILD.corner : BUILD[it.kind] || BUILD.standard;
  fn(c, it);
  return c.g;
}
