// Фасадтар: түстер, ағаш текстурасы және есікке салынатын өрнектер (фрезеровка).
// Өрнек «биіктік картасы» ретінде canvas-қа салынады (ақ — бет, қара — ойық),
// содан normal map пен көлеңке картасы шығарылады. Сонда ойықтар 3D сияқты көрінеді.
import * as THREE from 'three';

export const COLORS = [
  { id: '#f1f0ec', name: 'Ақ' },
  { id: '#e6dccb', name: 'Кашемир' },
  { id: '#cdbfa9', name: 'Беж' },
  { id: '#a7aaa6', name: 'Сұр' },
  { id: '#8d9a8a', name: 'Шалфей' },
  { id: '#6f7559', name: 'Зәйтүн' },
  { id: '#3d4a45', name: 'Қою жасыл' },
  { id: '#2f3e56', name: 'Көк' },
  { id: '#7a2e2e', name: 'Шие' },
  { id: '#2e3236', name: 'Антрацит' },
  { id: '#151515', name: 'Қара' },
  { id: 'wood:sonoma', name: 'Емен Сонома' },
  { id: 'wood:craft', name: 'Емен Крафт' },
  { id: 'wood:walnut', name: 'Жаңғақ' },
  { id: 'wood:wenge', name: 'Венге' },
];

const WOODS = {
  sonoma: '#cfae84',
  craft: '#b5844f',
  walnut: '#6b4a33',
  wenge: '#3b2a20',
};

export const PATTERNS = [
  { id: 'flat', name: 'Тегіс' },
  { id: 'frame', name: 'Рамка' },
  { id: 'shaker', name: 'Шейкер' },
  { id: 'classic', name: 'Классика' },
  { id: 'lines-v', name: 'Тік сызық' },
  { id: 'lines-h', name: 'Көлденең' },
  { id: 'rhomb', name: 'Ромб' },
  { id: 'wave', name: 'Толқын' },
  { id: 'oyu', name: 'Қазақ ою' },
  { id: 'glass', name: 'Әйнек' },
  { id: 'image', name: 'Өз суретім' },
];

export function colorName(id) {
  return COLORS.find((c) => c.id === id)?.name || id;
}

// UI үшін түс үлгісінің CSS фоны
export function swatchCss(id) {
  if (id.startsWith('wood:')) {
    const c = WOODS[id.slice(5)] || WOODS.craft;
    return `repeating-linear-gradient(8deg, ${c} 0 5px, color-mix(in srgb, ${c} 80%, #000) 5px 6px, ${c} 6px 11px)`;
  }
  return id;
}

let onAsyncUpdate = () => {};
export function setOnTextureUpdate(fn) { onAsyncUpdate = fn; }

// ---------- ағаш ----------
const woodCache = new Map();
function woodCanvas(id) {
  if (woodCache.has(id)) return woodCache.get(id);
  const base = WOODS[id] || WOODS.craft;
  const c = document.createElement('canvas');
  c.width = c.height = 512;
  const g = c.getContext('2d');
  g.fillStyle = base;
  g.fillRect(0, 0, 512, 512);
  let seed = id.length * 977;
  const r = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 160; i++) {
    const x0 = r() * 512, amp = 2 + r() * 7, dark = r() < 0.65;
    g.strokeStyle = dark ? `rgba(30,18,8,${0.05 + r() * 0.12})` : `rgba(255,235,210,${0.03 + r() * 0.08})`;
    g.lineWidth = 0.5 + r() * 2.2;
    g.beginPath();
    for (let y = 0; y <= 512; y += 16) g.lineTo(x0 + Math.sin(y / 85 + i) * amp, y);
    g.stroke();
  }
  woodCache.set(id, c);
  return c;
}

// ---------- жай материалдар (корпус, фасадтың шеттері) ----------
const plainCache = new Map();
export function plainMaterial(colorId, gloss = false) {
  const key = `${colorId}|${gloss}`;
  if (plainCache.has(key)) return plainCache.get(key);
  const rough = gloss ? 0.12 : 0.6;
  let m;
  if (colorId.startsWith('wood:')) {
    const t = new THREE.CanvasTexture(woodCanvas(colorId.slice(5)));
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    m = new THREE.MeshStandardMaterial({ map: t, roughness: Math.max(rough, 0.45) });
  } else {
    m = new THREE.MeshStandardMaterial({ color: colorId, roughness: rough });
  }
  plainCache.set(key, m);
  return m;
}

// ---------- өрнектің биіктік картасы ----------
// Барлық сызу миллиметрмен: ctx.scale(s, s) қойылған, W×H — есіктің өлшемі.
function groove(ctx, path, width) {
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  ctx.strokeStyle = '#7a7a7a';  // ойықтың жиегі (фаска)
  ctx.lineWidth = width * 2;
  path(); ctx.stroke();
  ctx.strokeStyle = '#000';
  ctx.lineWidth = width;
  path(); ctx.stroke();
}

function rectPath(ctx, x, y, w, h) {
  return () => { ctx.beginPath(); ctx.rect(x, y, w, h); };
}

// Қошқар мүйіз: орталық өзек және төрт жаққа бұралған мүйіздер
function oyuMotif(ctx, size) {
  const k = size / 300;
  const spiral = (cx, cy, x0, y0, turns, dir) => {
    const a0 = Math.atan2(y0 - cy, x0 - cx);
    const r0 = Math.hypot(x0 - cx, y0 - cy);
    const n = 48;
    for (let i = 1; i <= n; i++) {
      const t = i / n;
      const a = a0 + dir * t * turns * Math.PI * 2;
      const rr = r0 * (1 - 0.82 * t);
      ctx.lineTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr);
    }
  };
  const quarter = () => {
    ctx.moveTo(0, -30 * k);
    ctx.bezierCurveTo(8 * k, -95 * k, 85 * k, -118 * k, 108 * k, -68 * k);
    spiral(76 * k, -62 * k, 108 * k, -68 * k, 1.1, -1);
  };
  const side = () => {
    ctx.moveTo(30 * k, 0);
    ctx.bezierCurveTo(70 * k, -4 * k, 110 * k, 20 * k, 128 * k, 0);
    spiral(118 * k, -16 * k, 128 * k, 0, 0.9, -1);
  };
  return () => {
    ctx.beginPath();
    for (const sx of [1, -1]) for (const sy of [1, -1]) {
      ctx.save();
      ctx.scale(sx, sy);
      quarter();
      ctx.restore();
    }
  };
}

// canvas трансформы нүкте қосылған сәтте қолданылады, сондықтан scale(±1) бір жолдың ішінде айна бейне береді.
function drawOyu(ctx, W, H) {
  const m = 45;
  const size = Math.min(W - 2 * m, H - 2 * m) * 0.86;
  const gw = Math.max(4, size / 60);
  groove(ctx, rectPath(ctx, m, m, W - 2 * m, H - 2 * m), 5);
  ctx.save();
  ctx.translate(W / 2, H / 2);
  groove(ctx, () => {
    const p = oyuMotif(ctx, size);
    p();
    const k = size / 300;
    // орталық ромб
    ctx.moveTo(0, -22 * k); ctx.lineTo(22 * k, 0); ctx.lineTo(0, 22 * k); ctx.lineTo(-22 * k, 0); ctx.closePath();
  }, gw);
  ctx.restore();
  // бұрыштардағы шағын мүйіздер
  const cs = Math.min(W, H) * 0.22;
  for (const [cx, cy, sx, sy] of [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]]) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(sx, sy);
    groove(ctx, () => {
      ctx.beginPath();
      ctx.moveTo(cs * 0.12, cs * 0.55);
      ctx.bezierCurveTo(cs * 0.12, cs * 0.2, cs * 0.3, cs * 0.12, cs * 0.55, cs * 0.12);
      ctx.moveTo(cs * 0.22, cs * 0.22);
      ctx.arc(cs * 0.3, cs * 0.3, cs * 0.11, Math.PI * 1.25, Math.PI * 1.25 + Math.PI * 1.6);
    }, Math.max(3, gw * 0.7));
    ctx.restore();
  }
}

function drawHeight(ctx, pattern, W, H) {
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, W, H);
  const minD = Math.min(W, H);
  switch (pattern) {
    case 'frame': {
      const m = Math.min(60, minD * 0.15);
      groove(ctx, rectPath(ctx, m, m, W - 2 * m, H - 2 * m), 6);
      break;
    }
    case 'shaker': {
      const m = Math.min(70, minD * 0.18);
      ctx.fillStyle = '#9c9c9c'; ctx.fillRect(m, m, W - 2 * m, H - 2 * m);
      ctx.fillStyle = '#4a4a4a'; ctx.fillRect(m + 8, m + 8, W - 2 * m - 16, H - 2 * m - 16);
      ctx.fillStyle = '#5c5c5c'; ctx.fillRect(m + 14, m + 14, W - 2 * m - 28, H - 2 * m - 28);
      break;
    }
    case 'classic': {
      const m = Math.min(55, minD * 0.13);
      const m2 = m + Math.min(35, minD * 0.08);
      const a = Math.min(110, (H - 2 * m2) * 0.18);
      const arch = (inset) => () => {
        ctx.beginPath();
        ctx.moveTo(m2 + inset, H - m2 - inset);
        ctx.lineTo(m2 + inset, m2 + a + inset);
        ctx.quadraticCurveTo(W / 2, m2 - a * 0.6 + inset, W - m2 - inset, m2 + a + inset);
        ctx.lineTo(W - m2 - inset, H - m2 - inset);
        ctx.closePath();
      };
      arch(0)(); ctx.fillStyle = '#9c9c9c'; ctx.fill();
      arch(9)(); ctx.fillStyle = '#4e4e4e'; ctx.fill();
      arch(15)(); ctx.fillStyle = '#626262'; ctx.fill();
      groove(ctx, rectPath(ctx, m, m, W - 2 * m, H - 2 * m), 4);
      break;
    }
    case 'lines-v':
    case 'lines-h': {
      const m = 45;
      const vert = pattern === 'lines-v';
      const span = (vert ? W : H) - 2 * m;
      const n = Math.max(2, Math.round(span / 70));
      groove(ctx, () => {
        ctx.beginPath();
        for (let i = 0; i <= n; i++) {
          const t = m + (span * i) / n;
          if (vert) { ctx.moveTo(t, m); ctx.lineTo(t, H - m); } else { ctx.moveTo(m, t); ctx.lineTo(W - m, t); }
        }
      }, 6);
      break;
    }
    case 'rhomb': {
      const m = 45;
      groove(ctx, rectPath(ctx, m, m, W - 2 * m, H - 2 * m), 5);
      ctx.save();
      ctx.beginPath(); ctx.rect(m, m, W - 2 * m, H - 2 * m); ctx.clip();
      const step = 110;
      groove(ctx, () => {
        ctx.beginPath();
        for (let c = -H; c < W + H; c += step) {
          ctx.moveTo(c, m); ctx.lineTo(c + (H - 2 * m) * 0.75, H - m);
          ctx.moveTo(c, H - m); ctx.lineTo(c + (H - 2 * m) * 0.75, m);
        }
      }, 4);
      ctx.restore();
      break;
    }
    case 'wave': {
      const m = 40;
      ctx.save();
      ctx.beginPath(); ctx.rect(m, m, W - 2 * m, H - 2 * m); ctx.clip();
      groove(ctx, () => {
        ctx.beginPath();
        for (let y = m + 25; y < H - m; y += 55) {
          ctx.moveTo(m, y);
          for (let x = m; x <= W - m; x += 8) ctx.lineTo(x, y + Math.sin((x / 170) * Math.PI * 2) * 14);
        }
      }, 6);
      ctx.restore();
      break;
    }
    case 'oyu':
      drawOyu(ctx, W, H);
      break;
    default:
      break;
  }
}

// ---------- текстура жасау ----------
const faceCache = new Map();
const imgCache = new Map();

function loadImage(src) {
  if (imgCache.has(src)) return imgCache.get(src);
  const img = new Image();
  const entry = { img, ready: false, waiters: [] };
  img.onload = () => { entry.ready = true; entry.waiters.forEach((f) => f()); entry.waiters = []; onAsyncUpdate(); };
  img.src = src;
  imgCache.set(src, entry);
  return entry;
}

// Есіктің алдыңғы беті үшін canvas: түс/ағаш × көлеңке + normal map
function frontTextures(colorId, pattern, W, H, imgSrc) {
  const s = Math.min(0.6, 1024 / Math.max(W, H));
  const pw = Math.max(16, Math.round(W * s)), ph = Math.max(16, Math.round(H * s));
  const hc = document.createElement('canvas');
  hc.width = pw; hc.height = ph;
  const hx = hc.getContext('2d');
  hx.scale(pw / W, ph / H);
  drawHeight(hx, pattern === 'image' ? 'flat' : pattern, W, H);
  const hData = hx.getImageData(0, 0, pw, ph).data;

  // normal map (Собель)
  const nc = document.createElement('canvas');
  nc.width = pw; nc.height = ph;
  const nx = nc.getContext('2d');
  const nImg = nx.createImageData(pw, ph);
  const hAt = (x, y) => hData[(Math.min(ph - 1, Math.max(0, y)) * pw + Math.min(pw - 1, Math.max(0, x))) * 4] / 255;
  const strength = 3.2;
  for (let y = 0; y < ph; y++) for (let x = 0; x < pw; x++) {
    const dx = (hAt(x + 1, y) - hAt(x - 1, y)) * strength;
    const dy = (hAt(x, y + 1) - hAt(x, y - 1)) * strength;
    const len = Math.hypot(dx, dy, 1);
    const i = (y * pw + x) * 4;
    nImg.data[i] = ((-dx / len) * 0.5 + 0.5) * 255;
    nImg.data[i + 1] = ((dy / len) * 0.5 + 0.5) * 255;
    nImg.data[i + 2] = ((1 / len) * 0.5 + 0.5) * 255;
    nImg.data[i + 3] = 255;
  }
  nx.putImageData(nImg, 0, 0);

  // түс картасы: ағаш/сурет немесе ақ, ойықтарда қараңғы
  const cc = document.createElement('canvas');
  cc.width = pw; cc.height = ph;
  const cx = cc.getContext('2d');
  const paintColor = () => {
    if (pattern === 'image' && imgSrc) {
      const e = loadImage(imgSrc);
      if (e.ready) {
        const im = e.img;
        const k = Math.max(pw / im.width, ph / im.height);
        cx.drawImage(im, (pw - im.width * k) / 2, (ph - im.height * k) / 2, im.width * k, im.height * k);
      } else {
        cx.fillStyle = '#ddd'; cx.fillRect(0, 0, pw, ph);
      }
    } else if (colorId.startsWith('wood:')) {
      cx.drawImage(woodCanvas(colorId.slice(5)), 0, 0, pw, ph);
    } else {
      cx.fillStyle = '#fff'; cx.fillRect(0, 0, pw, ph);
    }
    const cData = cx.getImageData(0, 0, pw, ph);
    for (let i = 0; i < cData.data.length; i += 4) {
      const f = 0.6 + 0.4 * (hData[i] / 255);
      cData.data[i] *= f; cData.data[i + 1] *= f; cData.data[i + 2] *= f;
    }
    cx.putImageData(cData, 0, 0);
  };
  paintColor();

  const map = new THREE.CanvasTexture(cc);
  map.colorSpace = THREE.SRGBColorSpace;
  map.anisotropy = 4;
  const normalMap = new THREE.CanvasTexture(nc);
  if (pattern === 'image' && imgSrc && !loadImage(imgSrc).ready) {
    loadImage(imgSrc).waiters.push(() => { paintColor(); map.needsUpdate = true; });
  }
  return { map, normalMap };
}

// Есікке арналған материалдар массиві (BoxGeometry ретімен: +x, -x, +y, -y, +z(алды), -z)
export function facadeMaterials(colorId, pattern, gloss, W, H, imgSrc) {
  const side = plainMaterial(colorId, gloss);
  if (!pattern || pattern === 'flat' || pattern === 'glass') return side;
  const key = `${colorId}|${pattern}|${gloss}|${Math.round(W)}|${Math.round(H)}|${pattern === 'image' ? imgSrc : ''}`;
  let front = faceCache.get(key);
  if (!front) {
    const { map, normalMap } = frontTextures(colorId, pattern, W, H, imgSrc);
    const solid = !colorId.startsWith('wood:') && pattern !== 'image';
    front = new THREE.MeshStandardMaterial({
      color: solid ? colorId : '#ffffff',
      map,
      normalMap,
      roughness: gloss ? 0.15 : 0.6,
    });
    faceCache.set(key, front);
  }
  return [side, side, side, side, front, side];
}

export const glassMaterial = new THREE.MeshStandardMaterial({
  color: '#bcd3d6', roughness: 0.05, metalness: 0.1, transparent: true, opacity: 0.32, depthWrite: false,
});

// UI-дағы өрнек белгішесі (кішкентай есік суреті)
const thumbCache = new Map();
export function patternThumb(pattern, colorId, imgSrc) {
  const key = `${pattern}|${colorId}|${pattern === 'image' ? imgSrc?.length : ''}`;
  if (thumbCache.has(key)) return thumbCache.get(key);
  const W = 450, H = 600, s = 0.16;
  const c = document.createElement('canvas');
  c.width = W * s; c.height = H * s;
  const g = c.getContext('2d');
  g.scale(s, s);
  if (pattern === 'glass') {
    g.fillStyle = colorId.startsWith('wood:') ? WOODS[colorId.slice(5)] : colorId;
    g.fillRect(0, 0, W, H);
    g.fillStyle = '#bcd3d6';
    g.fillRect(70, 70, W - 140, H - 140);
    g.strokeStyle = 'rgba(255,255,255,.7)'; g.lineWidth = 14;
    g.beginPath(); g.moveTo(120, 220); g.lineTo(240, 100); g.moveTo(140, 330); g.lineTo(330, 140); g.stroke();
  } else if (pattern === 'image' && !imgSrc) {
    g.fillStyle = '#ddd'; g.fillRect(0, 0, W, H);
    g.strokeStyle = '#777'; g.lineWidth = 16;
    g.beginPath(); g.moveTo(W / 2, 200); g.lineTo(W / 2, 400); g.moveTo(W / 2 - 100, 300); g.lineTo(W / 2 + 100, 300); g.stroke();
  } else {
    const { map } = frontTextures(colorId, pattern, W, H, imgSrc);
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.drawImage(map.image, 0, 0, c.width, c.height);
    if (!colorId.startsWith('wood:') && pattern !== 'image') {
      g.globalCompositeOperation = 'multiply';
      g.fillStyle = colorId;
      g.fillRect(0, 0, c.width, c.height);
    }
  }
  const url = c.toDataURL();
  if (pattern !== 'image' || !imgSrc || loadImage(imgSrc).ready) thumbCache.set(key, url);
  return url;
}
