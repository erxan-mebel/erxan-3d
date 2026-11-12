// Бөлме: еден, қабырғалар, өлшем сызықтары.
// Бірлік — миллиметр. Координаттар: X — бөлменің ені (сол қабырғадан оңға),
// Z — тереңдігі (артқы қабырғадан алға), Y — биіктігі (еденнен жоғары).
import * as THREE from 'three';
import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

export const DEFAULT_ROOM = {
  W: 3600, D: 3000, H: 2700,
  walls: { back: true, left: true, right: false },
  wallColor: '#ebe8e1',
  floor: 'oak',
};

const FLOORS = {
  oak: { name: 'Ламинат емен', base: '#c8a57a', plank: true },
  grey: { name: 'Сұр ламинат', base: '#a9a49c', plank: true },
  tile: { name: 'Плитка', base: '#d9d7d2', tile: true },
  concrete: { name: 'Бетон', base: '#9b9d9a' },
};
export const FLOOR_OPTIONS = Object.entries(FLOORS).map(([id, f]) => ({ id, ...f }));
export const WALL_COLORS = ['#ebe8e1', '#f5f5f2', '#d8d3c8', '#c9d1cc', '#c7ced8', '#5a5f63'];

const floorTexCache = {};
function floorTexture(id) {
  if (floorTexCache[id]) return floorTexCache[id];
  const f = FLOORS[id] || FLOORS.oak;
  const c = document.createElement('canvas');
  c.width = c.height = 512;
  const g = c.getContext('2d');
  g.fillStyle = f.base;
  g.fillRect(0, 0, 512, 512);
  let rnd = 7;
  const r = () => ((rnd = (rnd * 16807) % 2147483647) / 2147483647);
  if (f.plank) {
    // 4 тақтай × 128px; текстура 1 метрге = 512px болып созылады
    for (let row = 0; row < 4; row++) {
      const y = row * 128;
      const shift = r() * 512;
      for (let k = 0; k < 2; k++) {
        const tone = (r() - 0.5) * 18;
        g.fillStyle = `rgba(${tone > 0 ? 255 : 0},${tone > 0 ? 240 : 0},${tone > 0 ? 220 : 0},${Math.abs(tone) / 255 * 3})`;
        g.fillRect((shift + k * 256) % 512, y, 256, 128);
      }
      for (let i = 0; i < 26; i++) {
        g.strokeStyle = `rgba(70,45,20,${0.04 + r() * 0.08})`;
        g.lineWidth = 0.6 + r() * 1.6;
        const yy = y + r() * 128;
        g.beginPath();
        for (let x = 0; x <= 512; x += 32) g.lineTo(x, yy + Math.sin(x / 70 + i) * 2.5);
        g.stroke();
      }
      g.fillStyle = 'rgba(40,25,10,.35)';
      g.fillRect(0, y, 512, 2);
      g.fillRect(shift % 512, y, 2, 128);
      g.fillRect((shift + 256) % 512, y, 2, 128);
    }
  } else if (f.tile) {
    g.strokeStyle = 'rgba(0,0,0,.18)';
    g.lineWidth = 3;
    for (let i = 0; i <= 512; i += 256) {
      g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 512); g.stroke();
      g.beginPath(); g.moveTo(0, i); g.lineTo(512, i); g.stroke();
    }
  } else {
    for (let i = 0; i < 4000; i++) {
      g.fillStyle = `rgba(${r() > 0.5 ? 255 : 0},${r() > 0.5 ? 255 : 0},${r() > 0.5 ? 255 : 0},0.05)`;
      g.fillRect(r() * 512, r() * 512, 2, 2);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  floorTexCache[id] = t;
  return t;
}

function label(text, cls) {
  const el = document.createElement('div');
  el.className = 'dim ' + (cls || '');
  el.textContent = text;
  return new CSS2DObject(el);
}

// Өлшем сызығы: екі нүкте арасында сызық, ұштарында белгі, ортасында мәтін.
export function dimensionLine(a, b, text, color, tickDir, cls) {
  const g = new THREE.Group();
  const mat = new THREE.LineBasicMaterial({ color, depthTest: false, transparent: true });
  const t = tickDir.clone().multiplyScalar(60);
  const pts = [a, b, a.clone().sub(t), a.clone().add(t), b.clone().sub(t), b.clone().add(t)];
  const geo = new THREE.BufferGeometry().setFromPoints(pts);
  geo.setIndex([0, 1, 2, 3, 4, 5]);
  const lines = new THREE.LineSegments(geo, mat);
  lines.renderOrder = 10;
  g.add(lines);
  const l = label(text, cls);
  l.position.copy(a).add(b).multiplyScalar(0.5);
  g.add(l);
  return g;
}

export function buildRoom(room, accent) {
  const { W, D, H } = room;
  const g = new THREE.Group();
  g.name = 'room';

  // Еден
  const tex = floorTexture(room.floor).clone();
  tex.needsUpdate = true;
  tex.repeat.set(W / 1000, D / 1000);
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(W, D),
    new THREE.MeshStandardMaterial({ map: tex, roughness: 0.8 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(W / 2, 0, D / 2);
  floor.receiveShadow = true;
  floor.userData.isFloor = true;
  g.add(floor);

  // Қабырғалар: тек ішкі жағы көрінеді (сырттан қарағанда мөлдір), сондықтан камера бөлмені кез келген жақтан көреді.
  const wallMat = new THREE.MeshStandardMaterial({ color: room.wallColor, roughness: 0.95, side: THREE.FrontSide });
  const addWall = (w, h, pos, rotY) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
    m.position.copy(pos);
    m.rotation.y = rotY;
    m.receiveShadow = true;
    g.add(m);
  };
  if (room.walls.back) addWall(W, H, new THREE.Vector3(W / 2, H / 2, 0), 0);
  if (room.walls.left) addWall(D, H, new THREE.Vector3(0, H / 2, D / 2), Math.PI / 2);
  if (room.walls.right) addWall(D, H, new THREE.Vector3(W, H / 2, D / 2), -Math.PI / 2);

  // Бөлменің контуры (еден мен төбе сызықтары) — сызба сияқты көрінуі үшін
  const edge = new THREE.LineBasicMaterial({ color: 0x55605a, transparent: true, opacity: 0.55 });
  const P = (x, y, z) => new THREE.Vector3(x, y, z);
  const segs = [P(0, 0, 0), P(W, 0, 0), P(0, 0, 0), P(0, 0, D), P(W, 0, 0), P(W, 0, D), P(0, 0, D), P(W, 0, D)];
  if (room.walls.back) segs.push(P(0, H, 0), P(W, H, 0));
  if (room.walls.left) segs.push(P(0, H, 0), P(0, H, D), P(0, 0, 0), P(0, H, 0));
  if (room.walls.right) segs.push(P(W, H, 0), P(W, H, D), P(W, 0, 0), P(W, H, 0));
  if (room.walls.back && !room.walls.left) segs.push(P(0, 0, 0), P(0, H, 0));
  if (room.walls.back && !room.walls.right) segs.push(P(W, 0, 0), P(W, H, 0));
  g.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(segs), edge));

  // Еденнің 100 мм торы
  const grid = new THREE.Group();
  const gm = new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.06 });
  const gp = [];
  for (let x = 500; x < W; x += 500) gp.push(P(x, 1, 0), P(x, 1, D));
  for (let z = 500; z < D; z += 500) gp.push(P(0, 1, z), P(W, 1, z));
  grid.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(gp), gm));
  g.add(grid);

  // Бөлме өлшемдері
  const dims = new THREE.Group();
  dims.name = 'roomDims';
  const off = 260;
  dims.add(dimensionLine(P(0, 2, D + off), P(W, 2, D + off), `${W}`, accent, P(0, 0, 1), 'room'));
  dims.add(dimensionLine(P(-off, 2, 0), P(-off, 2, D), `${D}`, accent, P(1, 0, 0), 'room'));
  dims.add(dimensionLine(P(-off, 0, -2), P(-off, H, -2), `${H}`, accent, P(1, 0, 0), 'room'));
  g.add(dims);

  return g;
}
