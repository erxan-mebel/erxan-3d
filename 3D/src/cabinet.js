// Дайын корпустар: каталог және 3D модельді ЛДСП панельдерінен құру.
// Модельдің жергілікті координаттары: артқы-сол-төменгі бұрыш (0,0,0),
// X — ені, Y — биіктігі, Z — тереңдігі (артқы қабырғадан фасадқа қарай).
import * as THREE from 'three';
import { plainMaterial, facadeMaterials, glassMaterial } from './facade.js';

export const T = 16;    // корпус ЛДСП қалыңдығы
export const FT = 18;   // фасад қалыңдығы
export const BACK = 4;  // артқы ХДФ
export const GAP = 3;   // фасадтар арасындағы саңылау
export const TOP_T = 38; // столешница қалыңдығы

export const CATALOG = [
  { kind: 'base', name: 'Төменгі шкаф', place: 'floor', w: 600, h: 720, d: 560, plinth: 100, front: 'doors', doors: 2, shelves: 1, countertop: true },
  { kind: 'base-drawers', name: 'Тартпалы шкаф', place: 'floor', w: 500, h: 720, d: 560, plinth: 100, front: 'drawers', drawers: 3, shelves: 0, countertop: true },
  { kind: 'wall', name: 'Үстіңгі шкаф', place: 'wall', w: 600, h: 720, d: 320, y: 1450, front: 'doors', doors: 2, shelves: 2 },
  { kind: 'tall', name: 'Пенал', place: 'floor', w: 600, h: 2100, d: 560, plinth: 100, front: 'tall', doors: 1, shelves: 4 },
  { kind: 'wardrobe', name: 'Киім шкафы', place: 'floor', w: 1200, h: 2300, d: 600, plinth: 80, front: 'doors', doors: 2, shelves: 1, rod: true },
  { kind: 'shelf', name: 'Ашық сөре', place: 'wall', w: 800, h: 360, d: 300, y: 1500, front: 'none', shelves: 0 },
];

export function getDef(kind) {
  return CATALOG.find((c) => c.kind === kind) || CATALOG[0];
}

let nextId = 1;
export function setNextId(n) { nextId = Math.max(nextId, n); }
export function takeId() { return nextId++; }

export function newItem(kind, extra = {}) {
  const def = getDef(kind);
  const it = {
    id: nextId++,
    kind,
    x: 0, z: 0, rot: 0,
    y: def.y || 0,
    w: def.w, h: def.h, d: def.d,
    plinth: def.plinth || 0,
    doors: def.doors || 0,
    drawers: def.drawers || 0,
    shelves: def.shelves || 0,
    countertop: !!def.countertop,
    body: '#f1f0ec',
    facade: '#f1f0ec',
    pattern: 'flat',   // есік өрнегі (facade.js → PATTERNS)
    gloss: false,      // жылтыр фасад
    patternImg: '',    // «Өз суретім» үшін сурет (dataURL)
    ...extra,
  };
  return it;
}

// Жалпы биіктік (столешницамен бірге)
export function totalHeight(it) {
  return it.plinth + it.h + (it.countertop ? TOP_T : 0);
}

// Еденнен төмен түспейтін, бөлмеде көлденең алатын жері (жартылай өлшемдер)
export function halfExtents(it) {
  return it.rot % 2 === 0 ? { hx: it.w / 2, hz: it.d / 2 } : { hx: it.d / 2, hz: it.w / 2 };
}

const BOX = new THREE.BoxGeometry(1, 1, 1);
BOX.translate(0.5, 0.5, 0.5); // масштабталған қорап min-бұрыштан басталады
const EDGES = new THREE.EdgesGeometry(BOX);
const edgeMat = new THREE.LineBasicMaterial({ color: 0x1b221e, transparent: true, opacity: 0.35 });

const matCache = new Map();
function mat(color, rough = 0.7, metal = 0) {
  const key = `${color}|${rough}|${metal}`;
  if (!matCache.has(key)) matCache.set(key, new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal }));
  return matCache.get(key);
}

export function buildItem(it) {
  const g = new THREE.Group();
  const def = getDef(it.kind);
  const bodyM = plainMaterial(it.body || '#f1f0ec');
  const backM = mat('#d9d6cf', 0.9);
  const darkM = mat('#2a2d2b', 0.8);
  const steelM = mat('#c9ccce', 0.3, 0.9);
  const topM = mat('#b98c5c', 0.55);

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

  const { w, h, d } = it;
  const y0 = it.plinth;

  // Бір есік/тартпа беті: өрнекпен немесе әйнекті рамка
  const facade = (fw, fh, x, y) => {
    const pattern = it.pattern || 'flat';
    if (pattern === 'glass' && fw > 200 && fh > 200) {
      const fm = plainMaterial(it.facade, it.gloss);
      const r = 60;
      box(g, r, fh, FT, x, y, d, fm);
      box(g, r, fh, FT, x + fw - r, y, d, fm);
      box(g, fw - 2 * r, r, FT, x + r, y, d, fm);
      box(g, fw - 2 * r, r, FT, x + r, y + fh - r, d, fm);
      const glass = box(g, fw - 2 * r, fh - 2 * r, 4, x + r, y + r, d + FT / 2 - 2, glassMaterial, false);
      if (glass) glass.castShadow = false;
      return;
    }
    const p = pattern === 'glass' ? 'frame' : pattern;
    box(g, fw, fh, FT, x, y, d, facadeMaterials(it.facade, p, it.gloss, fw, fh, it.patternImg));
  };

  // Корпус
  box(g, T, h, d - BACK, 0, y0, BACK, bodyM);           // сол бүйір
  box(g, T, h, d - BACK, w - T, y0, BACK, bodyM);       // оң бүйір
  box(g, w - 2 * T, T, d - BACK, T, y0, BACK, bodyM);   // түбі
  box(g, w - 2 * T, T, d - BACK, T, y0 + h - T, BACK, bodyM); // қақпағы
  box(g, w, h, BACK, 0, y0, 0, backM, false);           // артқы ХДФ
  const n = it.shelves;
  for (let i = 1; i <= n; i++) {
    const sy = y0 + T + ((h - 2 * T) * i) / (n + 1) - T / 2;
    box(g, w - 2 * T, T, d - BACK - 20, T, sy, BACK, bodyM);
  }
  if (def.rod) {
    const rod = new THREE.Mesh(new THREE.CylinderGeometry(12, 12, w - 2 * T, 16), steelM);
    rod.rotation.z = Math.PI / 2;
    rod.position.set(w / 2, y0 + h - 380, d / 2);
    g.add(rod);
  }

  // Цоколь
  if (it.plinth > 0) box(g, w, it.plinth, T, 0, 0, d - 60, darkM);

  // Столешница
  if (it.countertop) box(g, w, TOP_T, d + 30, 0, y0 + h, 0, topM);

  // Тұтқа: тік немесе көлденең хром планка
  const handle = (x, y, vertical) => {
    const len = 128;
    if (vertical) box(g, 12, len, 14, x - 6, y - len / 2, d + FT, steelM, false);
    else box(g, len, 12, 14, x - len / 2, y - 6, d + FT, steelM, false);
  };

  const doorsRow = (count, yb, hh, handleAt) => {
    const dw = (w - GAP * count) / count;
    for (let i = 0; i < count; i++) {
      const x = GAP / 2 + i * (dw + GAP);
      facade(dw, hh - GAP, x, yb + GAP / 2);
      const hingeLeft = count === 1 ? true : i % 2 === 0;
      const hx = hingeLeft ? x + dw - 40 : x + 40;
      const hy = handleAt === 'top' ? yb + hh - 110 : handleAt === 'bottom' ? yb + 110 : yb + hh / 2;
      handle(hx, hy, true);
    }
  };

  if (def.front === 'doors') {
    const at = def.place === 'wall' ? 'bottom' : it.kind === 'wardrobe' ? 'mid' : 'top';
    doorsRow(Math.max(1, it.doors), y0, h, at);
  } else if (def.front === 'tall') {
    const low = Math.min(h - 400, Math.round(h * 0.62));
    doorsRow(Math.max(1, it.doors), y0, low, 'top');
    doorsRow(Math.max(1, it.doors), y0 + low, h - low, 'bottom');
  } else if (def.front === 'drawers') {
    const m = Math.max(1, it.drawers);
    const topH = m >= 3 ? Math.round(h * 0.2) : h / m;
    const restH = m >= 3 ? (h - topH) / (m - 1) : h / m;
    let y = y0;
    for (let i = 0; i < m; i++) {
      const hh = i === m - 1 ? topH : restH;
      facade(w - GAP, hh - GAP, GAP / 2, y + GAP / 2);
      handle(w / 2, y + hh - 50, false);
      y += hh;
    }
  }

  return g;
}
