import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { COLORS, PATTERNS, swatchCss, colorName, patternThumb, setOnTextureUpdate } from './facade.js';
import { DEFAULT_ROOM, FLOOR_OPTIONS, WALL_COLORS, buildRoom } from './room.js';
import { CATALOG, GROUPS, TONES, HOBS, TV_SIZES, getDef, newItem, setNextId, takeId, buildItem, halfExtents, footprint, totalHeight } from './cabinet.js';

const $ = (s) => document.querySelector(s);
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const STORE_KEY = 'erxan3d.project.v1';

// ---------- күй ----------
const state = {
  room: structuredClone(DEFAULT_ROOM),
  items: [],
  selected: null,
  showDims: true,
  tab: 'room',
};

// ---------- сахна ----------
const viewport = $('#viewport');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
viewport.prepend(renderer.domElement);

const labelRenderer = new CSS2DRenderer({ element: $('#labels') });

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 20, 60000);

// Жылтыр фасадтарда шағылыс көрінуі үшін жұмсақ орта жарығы
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.45;
scene.add(new THREE.HemisphereLight(0xffffff, 0xb9b2a6, 1.15));
const sun = new THREE.DirectionalLight(0xffffff, 1.7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 2;
scene.add(sun, sun.target);

const roomRoot = new THREE.Group();
const itemsRoot = new THREE.Group();
scene.add(roomRoot, itemsRoot);
const selBox = new THREE.Box3Helper(new THREE.Box3(), 0x2448a8);
selBox.visible = false;
scene.add(selBox);

let needsRender = true;
const invalidate = () => { needsRender = true; };

function applyTheme() {
  scene.background = new THREE.Color(css('--bg') || '#e6e9e4');
  selBox.material.color.set(css('--accent') || '#2448a8');
  rebuildRoom();
}
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

// ---------- камера ----------
// Біздің pointerdown тыңдаушымыз OrbitControls-тан бұрын тіркелуі керек — шкафты сүйрегенде айналдыруды өшіру үшін.
renderer.domElement.addEventListener('pointerdown', onPointerDown);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.12;
controls.maxPolarAngle = Math.PI / 2 - 0.02;
controls.minDistance = 600;
controls.maxDistance = 20000;
controls.screenSpacePanning = true;
controls.addEventListener('change', invalidate);

let tween = null;
function flyTo(pos, target, ms = 450) {
  tween = { p0: camera.position.clone(), t0: controls.target.clone(), p1: pos, t1: target, start: performance.now(), ms };
}
function view(kind, instant) {
  const { W, D, H } = state.room;
  // Тік экранда (телефон) камераны алысырақ қоямыз, бөлме толық сыйсын
  const fit = Math.max(1, 1.25 / Math.max(0.3, camera.aspect));
  const span = Math.max(W, D, H) * fit;
  let pos, tgt;
  if (kind === 'front') {
    tgt = new THREE.Vector3(W / 2, H * 0.45, 0);
    pos = new THREE.Vector3(W / 2, H * 0.5, D + span * 1.15);
  } else if (kind === 'top') {
    tgt = new THREE.Vector3(W / 2, 0, D / 2);
    pos = new THREE.Vector3(W / 2, span * 2.1, D / 2 + 1);
  } else {
    tgt = new THREE.Vector3(W / 2, H * 0.35, D * 0.4);
    pos = new THREE.Vector3(W * 0.95, H * 0.95, D + span * 0.95);
  }
  if (instant) { camera.position.copy(pos); controls.target.copy(tgt); controls.update(); invalidate(); }
  else flyTo(pos, tgt);
  for (const [id, k] of [['#view3d', '3d'], ['#viewFront', 'front'], ['#viewTop', 'top']]) $(id).setAttribute('aria-pressed', String(k === kind));
}

function placeSun() {
  const { W, D, H } = state.room;
  sun.position.set(W * 0.8, H * 1.8, D * 1.6);
  sun.target.position.set(W / 2, 0, D / 2);
  const s = Math.max(W, D) * 0.8;
  Object.assign(sun.shadow.camera, { left: -s, right: s, top: s, bottom: -s, near: 100, far: 20000 });
  sun.shadow.camera.updateProjectionMatrix();
}

// ---------- бөлме ----------
// Ішкі CSS2D белгілерінің DOM элементтерін де өшіру (three.js тек тікелей балаларын өшіреді)
function dropLabels(obj) {
  obj.traverse((o) => { if (o.isCSS2DObject) o.element.remove(); });
}

function rebuildRoom() {
  dropLabels(roomRoot);
  roomRoot.clear();
  const r = buildRoom(state.room, css('--accent') || '#2448a8');
  r.getObjectByName('roomDims').visible = state.showDims;
  roomRoot.add(r);
  placeSun();
  invalidate();
}

// ---------- шкафтар ----------
const views = new Map(); // id -> { outer, label }

function itemTitle(it) {
  return getDef(it.kind).name;
}

function syncItem(it) {
  let v = views.get(it.id);
  if (!v) {
    v = { outer: new THREE.Group() };
    v.outer.userData.itemId = it.id;
    itemsRoot.add(v.outer);
    views.set(it.id, v);
  }
  dropLabels(v.outer);
  v.outer.clear();
  const inner = buildItem(it);
  const fp = footprint(it);
  inner.position.set(-fp.fw / 2, 0, -fp.fd / 2);
  v.outer.add(inner);
  const el = document.createElement('div');
  el.className = 'dim small';
  v.labelEl = el;
  v.label = new CSS2DObject(el);
  v.label.position.set(0, totalHeight(it) + 70, fp.fd / 2);
  v.outer.add(v.label);
  placeItem(it);
  updateLabel(it);
}

function updateLabel(it) {
  const v = views.get(it.id);
  if (!v) return;
  const sel = state.selected === it.id;
  const fp = footprint(it);
  const corner = getDef(it.kind).corner;
  v.labelEl.textContent = sel
    ? (corner ? `${it.w} × ${it.w2} × ${totalHeight(it)}` : `${it.w} × ${totalHeight(it)} × ${it.d}`)
    : (corner ? `${fp.fw} × ${fp.fd}` : `${it.w}`);
  v.labelEl.classList.toggle('room', sel);
  v.label.visible = state.showDims || sel;
}

function placeItem(it) {
  const v = views.get(it.id);
  v.outer.position.set(it.x, it.y, it.z);
  v.outer.rotation.y = (it.rot * Math.PI) / 2;
  invalidate();
}

function removeView(id) {
  const v = views.get(id);
  if (!v) return;
  dropLabels(v.outer);
  v.outer.removeFromParent();
  views.delete(id);
}

function rebuildAll() {
  for (const id of [...views.keys()]) removeView(id);
  state.items.forEach(syncItem);
  select(state.items.some((i) => i.id === state.selected) ? state.selected : null);
}

function getItem(id) { return state.items.find((i) => i.id === id); }

// Жаңа шкафты артқы қабырғаға, басқаларынан кейін бос орынға қою
function addItem(kind) {
  const it = newItem(kind);
  const def = getDef(kind);
  const { hx, hz } = halfExtents(it);
  if (def.corner) {
    // Бұрыштық шкаф: бос бұрышқа (алдымен сол, сосын оң)
    const leftBusy = state.items.some((o) => getDef(o.kind).place === def.place && o.x - halfExtents(o).hx < hx && o.z - halfExtents(o).hz < hz);
    if (leftBusy && state.room.walls.right) { it.rot = 3; const e = halfExtents(it); it.x = state.room.W - e.hx; it.z = e.hz; }
    else { it.x = hx; it.z = hz; }
    state.items.push(it);
    syncItem(it);
    select(it.id);
    commit();
    return;
  }
  const sameRow = state.items.filter((o) => o.rot === 0 && getDef(o.kind).place === def.place && o.z - halfExtents(o).hz < 50);
  const right = sameRow.reduce((m, o) => Math.max(m, o.x + halfExtents(o).hx), 0);
  if (right + 2 * hx <= state.room.W) {
    it.x = right + hx;
    it.z = hz;
  } else {
    // Қабырғада орын жоқ — бөлменің ортасына қоямыз, сосын сүйреп апаруға болады
    it.x = state.room.W / 2;
    it.z = Math.min(state.room.D - hz, state.room.D / 2);
  }
  state.items.push(it);
  syncItem(it);
  select(it.id);
  commit();
}

function select(id) {
  state.selected = id;
  for (const it of state.items) updateLabel(it);
  const it = getItem(id);
  $('#selbar').hidden = !it;
  if (it) $('#hint').hidden = true;
  if (it) $('#selName').textContent = itemTitle(it);
  if (state.tab === 'props' || (it && state.tab === 'catalog')) renderSheet();
  invalidate();
}

// ---------- сүйреу және қабырғаға жабыстыру ----------
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let drag = null;

function setNdc(e) {
  const r = renderer.domElement.getBoundingClientRect();
  ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(ndc, camera);
}

function pickItem(e) {
  setNdc(e);
  const hits = raycaster.intersectObjects(itemsRoot.children, true);
  for (const h of hits) {
    let o = h.object;
    while (o && o.userData.itemId === undefined) o = o.parent;
    if (o) return getItem(o.userData.itemId);
  }
  return null;
}

function planeHit(e, y) {
  setNdc(e);
  const p = new THREE.Vector3();
  return raycaster.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0, 1, 0), -y), p) ? p : null;
}

let downInfo = null;
function onPointerDown(e) {
  if (!e.isPrimary) { if (drag) { drag = null; controls.enabled = true; } return; }
  downInfo = { x: e.clientX, y: e.clientY, moved: false };
  const it = pickItem(e);
  if (it) {
    controls.enabled = false;
    if (state.selected !== it.id) select(it.id);
    const hit = planeHit(e, it.y);
    drag = { it, off: hit ? new THREE.Vector3(it.x - hit.x, 0, it.z - hit.z) : new THREE.Vector3(), before: snapshot() };
    renderer.domElement.setPointerCapture(e.pointerId);
  }
}

renderer.domElement.addEventListener('pointermove', (e) => {
  if (downInfo && Math.hypot(e.clientX - downInfo.x, e.clientY - downInfo.y) > 6) downInfo.moved = true;
  if (!drag || !downInfo?.moved) return;
  const hit = planeHit(e, drag.it.y);
  if (!hit) return;
  moveWithSnap(drag.it, hit.x + drag.off.x, hit.z + drag.off.z);
  $('#hint').hidden = true;
});

renderer.domElement.addEventListener('pointerup', (e) => {
  if (drag) {
    if (downInfo?.moved) { pushHistory(drag.before); save(); }
    drag = null;
    controls.enabled = true;
  } else if (downInfo && !downInfo.moved) {
    select(null); // бос жерді басу — таңдауды алу
  }
  downInfo = null;
});

const SNAP = 60;
function moveWithSnap(it, x, z) {
  const { W, D } = state.room;
  const walls = state.room.walls;
  // Ең жақын қабырғаға қарай автоматты бұру (артын қабырғаға қаратып)
  const cand = [];
  if (walls.back) cand.push({ d: z, rot: 0 });
  if (walls.left) cand.push({ d: x, rot: 1 });
  if (walls.right) cand.push({ d: W - x, rot: 3 });
  cand.sort((a, b) => a.d - b.d);
  if (getDef(it.kind).corner) {
    // Бұрыштық шкаф тек бұрышқа: сол-артқы (0) немесе оң-артқы (3)
    if (z < 700) it.rot = x < W / 2 ? 0 : 3;
  } else if (cand[0] && cand[0].d < 450) it.rot = cand[0].rot;

  const { hx, hz } = halfExtents(it);
  x = Math.min(Math.max(x, hx), Math.max(hx, W - hx));
  z = Math.min(Math.max(z, hz), Math.max(hz, D - hz));
  if (it.rot === 0 && walls.back && z < hz + 300) z = hz;
  if (it.rot === 1 && walls.left && x < hx + 300) x = hx;
  if (it.rot === 3 && walls.right && x > W - hx - 300) x = W - hx;
  if (getDef(it.kind).corner && z < hz + 300) z = hz;

  // Көрші шкафтардың шетіне жабыстыру
  let bestX = SNAP, bestZ = SNAP, dx = 0, dz = 0;
  for (const o of state.items) {
    if (o === it) continue;
    const e = halfExtents(o);
    const ox = [o.x - e.hx, o.x + e.hx], oz = [o.z - e.hz, o.z + e.hz];
    const overlapZ = z + hz > oz[0] - SNAP && z - hz < oz[1] + SNAP;
    const overlapX = x + hx > ox[0] - SNAP && x - hx < ox[1] + SNAP;
    if (overlapZ) for (const a of [x - hx, x + hx]) for (const b of ox) {
      const dd = Math.abs(a - b);
      if (dd < bestX) { bestX = dd; dx = b - a; }
    }
    if (overlapX) for (const a of [z - hz, z + hz]) for (const b of oz) {
      const dd = Math.abs(a - b);
      if (dd < bestZ) { bestZ = dd; dz = b - a; }
    }
  }
  it.x = Math.round(x + dx);
  it.z = Math.round(z + dz);
  placeItem(it);
}

// ---------- тарих (артқа қайтару) және сақтау ----------
const history = [];
function snapshot() { return JSON.stringify({ room: state.room, items: state.items }); }
function pushHistory(s) { history.push(s); if (history.length > 60) history.shift(); }
function commit() { save(); }
function undo() {
  const s = history.pop();
  if (!s) return;
  const data = JSON.parse(s);
  state.room = data.room;
  state.items = data.items;
  rebuildRoom();
  rebuildAll();
  renderSheet();
  save();
}
function save() {
  try { localStorage.setItem(STORE_KEY, snapshot()); } catch { /* жеке терезеде сақталмауы мүмкін */ }
}
function load() {
  try {
    const s = localStorage.getItem(STORE_KEY);
    if (!s) return false;
    const data = JSON.parse(s);
    state.room = { ...structuredClone(DEFAULT_ROOM), ...data.room };
    state.items = data.items || [];
    setNextId(state.items.reduce((m, i) => Math.max(m, i.id + 1), 1));
    return true;
  } catch { return false; }
}

// Алғаш ашқанда көрсетілетін мысал асүй
function sampleKitchen() {
  state.room = structuredClone(DEFAULT_ROOM);
  state.items = [];
  // Артқы қабырға бойымен: x — сол жақ шеті. rot: 1 — сол қабырға бойымен (x орнына z басталуы)
  const put = (kind, x, extra = {}, rot = 0) => {
    const it = newItem(kind, extra);
    it.rot = rot;
    const { hx, hz } = halfExtents(it);
    if (rot === 1) { it.x = hx; it.z = x + hz; } else { it.x = x + hx; it.z = hz; }
    state.items.push(it);
    return it;
  };
  const low = { facade: '#3d4a45', pattern: 'shaker' };
  const up = { facade: '#e6dccb', pattern: 'shaker' };
  put('base-corner', 0, low);
  put('base-sink', 900, low);
  put('dishwasher-builtin', 1700, low);
  put('base-oven', 2300, low);
  put('fridge', 2950, {});
  put('base-drawers', 900, { w: 450, ...low }, 1);
  put('tall-oven', 1350, low, 1);
  put('wall-corner', 0, up);
  put('wall', 600, { w: 500, doors: 1, ...up });
  put('wall', 1100, { w: 600, ...up, pattern: 'glass' });
  put('wall', 1700, { w: 600, ...up });
  put('hood', 2300, {});
  put('wall', 600, { w: 600, ...up }, 1);
}

// ---------- басқару тақтасы ----------
const sheet = $('#sheet');
const body = $('#sheetBody');
const isPhone = () => window.matchMedia('(max-width: 859px)').matches;

document.querySelectorAll('.tabs [role="tab"]').forEach((b) => {
  b.addEventListener('click', () => {
    const t = b.dataset.tab;
    if (isPhone() && t === state.tab) sheet.classList.toggle('collapsed');
    else sheet.classList.remove('collapsed');
    state.tab = t;
    renderSheet();
  });
});

function numField(id, label, value, unit = 'мм') {
  return `<div class="field"><label for="${id}">${label}</label>
    <div class="num"><input id="${id}" type="number" inputmode="numeric" step="10" value="${value}"><span>${unit}</span></div></div>`;
}

function renderSheet() {
  document.querySelectorAll('.tabs [role="tab"]').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.tab === state.tab)));
  if (state.tab === 'room') renderRoomTab();
  else if (state.tab === 'catalog') renderCatalogTab();
  else renderPropsTab();
}

function renderRoomTab() {
  const r = state.room;
  body.innerHTML = `
    <section class="group">
      <h3>Бөлменің өлшемі</h3>
      <div class="row">
        ${numField('roomW', 'Ені', r.W)}
        ${numField('roomD', 'Тереңдігі', r.D)}
        ${numField('roomH', 'Биіктігі', r.H)}
      </div>
      <p class="note">Клиенттің бөлмесін рулеткамен өлшеп, миллиметрмен енгізіңіз.</p>
    </section>
    <section class="group">
      <h3>Қабырғалар</h3>
      <div class="chips">
        <button class="chip" data-wall="left" aria-pressed="${r.walls.left}">Сол жақ</button>
        <button class="chip" data-wall="back" aria-pressed="${r.walls.back}">Артқы</button>
        <button class="chip" data-wall="right" aria-pressed="${r.walls.right}">Оң жақ</button>
      </div>
      <div class="swatches">
        ${WALL_COLORS.map((c) => `<button class="swatch" data-wallcolor="${c}" style="background:${c}" aria-pressed="${r.wallColor === c}" aria-label="Қабырға түсі ${c}"></button>`).join('')}
      </div>
    </section>
    <section class="group">
      <h3>Еден</h3>
      <div class="chips">
        ${FLOOR_OPTIONS.map((f) => `<button class="chip" data-floor="${f.id}" aria-pressed="${r.floor === f.id}">${f.name}</button>`).join('')}
      </div>
    </section>
    <section class="group">
      <h3>Жоба</h3>
      <div class="chips">
        <button class="chip" id="undoBtn">Артқа қайтару</button>
        <button class="chip" id="sampleBtn">Мысал асүй</button>
        <button class="chip" id="clearBtn">Бәрін тазалау</button>
      </div>
    </section>`;
  for (const [id, key] of [['roomW', 'W'], ['roomD', 'D'], ['roomH', 'H']]) {
    $('#' + id).addEventListener('change', (e) => {
      const v = Math.round(Number(e.target.value));
      if (!(v >= 500 && v <= 20000)) { e.target.value = state.room[key]; return; }
      pushHistory(snapshot());
      state.room[key] = v;
      rebuildRoom();
      view('3d');
      commit();
    });
  }
  body.querySelectorAll('[data-wall]').forEach((b) => b.addEventListener('click', () => {
    pushHistory(snapshot());
    state.room.walls[b.dataset.wall] = !state.room.walls[b.dataset.wall];
    rebuildRoom(); renderSheet(); commit();
  }));
  body.querySelectorAll('[data-wallcolor]').forEach((b) => b.addEventListener('click', () => {
    pushHistory(snapshot());
    state.room.wallColor = b.dataset.wallcolor;
    rebuildRoom(); renderSheet(); commit();
  }));
  body.querySelectorAll('[data-floor]').forEach((b) => b.addEventListener('click', () => {
    pushHistory(snapshot());
    state.room.floor = b.dataset.floor;
    rebuildRoom(); renderSheet(); commit();
  }));
  $('#undoBtn').addEventListener('click', undo);
  $('#sampleBtn').addEventListener('click', () => {
    pushHistory(snapshot()); sampleKitchen(); rebuildRoom(); rebuildAll(); renderSheet(); view('3d'); commit();
  });
  $('#clearBtn').addEventListener('click', () => {
    pushHistory(snapshot()); state.items = []; rebuildAll(); commit();
  });
}

// Каталог картасына арналған сызба-белгіше (100×64 сызба)
function icon(def) {
  const k = def.kind;
  const R = (x, y, w, h, extra = '') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="1.5" ${extra}/>`;
  const L = (x1, y1, x2, y2) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
  const C = (cx, cy, r, extra = '') => `<circle cx="${cx}" cy="${cy}" r="${r}" ${extra}/>`;
  const top = (x, w, y) => `<rect x="${x - 3}" y="${y - 4}" width="${w + 6}" height="4" fill="currentColor" opacity=".35" stroke="none"/>`;
  let s = '';
  switch (k) {
    case 'base': s = top(24, 52, 18) + R(24, 18, 52, 44) + L(50, 18, 50, 62); break;
    case 'base-drawers': s = top(28, 44, 18) + R(28, 18, 44, 44) + L(28, 28, 72, 28) + L(28, 45, 72, 45); break;
    case 'base-sink': s = top(18, 64, 18) + R(18, 18, 64, 44) + L(50, 18, 50, 62) + L(44, 14, 44, 4) + L(44, 4, 54, 4) + L(54, 4, 54, 9); break;
    case 'base-oven': s = top(26, 48, 18) + R(26, 18, 48, 44) + R(30, 22, 40, 26) + R(36, 28, 28, 14, 'opacity=".5"') + L(26, 52, 74, 52) + L(30, 14, 46, 14) + L(54, 14, 70, 14); break;
    case 'wall': s = R(22, 10, 56, 38) + L(50, 10, 50, 48); break;
    case 'shelf': s = R(14, 20, 72, 24) + L(14, 32, 86, 32); break;
    case 'base-corner': s = `<path d="M14 58 L14 22 L86 22 L86 40 L40 40 L40 58 Z"/>` + L(14, 22, 40, 40) + L(52, 22, 52, 40); break;
    case 'wall-corner': s = `<path d="M18 50 L18 14 L82 14 L82 32 L42 32 L42 50 Z"/>` + L(18, 14, 42, 32); break;
    case 'tall': s = R(36, 2, 28, 60) + L(36, 24, 64, 24); break;
    case 'tall-oven': s = R(36, 2, 28, 60) + R(39, 30, 22, 14) + R(39, 18, 22, 10) + L(36, 46, 64, 46); break;
    case 'wardrobe': s = R(16, 2, 68, 60) + L(50, 2, 50, 62); break;
    case 'fridge': s = R(34, 2, 32, 60) + L(34, 40, 66, 40) + L(61, 30, 61, 37) + L(61, 43, 61, 50); break;
    case 'fridge-side': s = R(26, 4, 48, 58) + L(48, 4, 48, 62) + L(45, 20, 45, 40) + L(51, 20, 51, 40); break;
    case 'stove': s = R(28, 14, 44, 48) + L(28, 22, 72, 22) + R(33, 27, 34, 22) + C(36, 18, 1.5) + C(44, 18, 1.5) + C(52, 18, 1.5); break;
    case 'hood': s = `<path d="M22 44 L78 44 L70 34 L30 34 Z"/>` + R(42, 4, 16, 30); break;
    case 'dishwasher-builtin': s = top(28, 44, 18) + R(28, 18, 44, 44) + L(42, 24, 58, 24); break;
    case 'dishwasher': s = R(28, 14, 44, 48) + L(28, 24, 72, 24) + L(40, 30, 60, 30); break;
    case 'micro': s = R(18, 22, 64, 34) + R(22, 26, 40, 26) + C(72, 36, 3) + L(14, 56, 86, 56); break;
    case 'micro-builtin': s = R(20, 18, 60, 30) + R(24, 22, 38, 22) + C(70, 33, 3); break;
    case 'washer': s = R(28, 12, 44, 50) + L(28, 22, 72, 22) + C(50, 42, 12) + C(50, 42, 8, 'opacity=".5"'); break;
    case 'tv': s = R(10, 10, 80, 44) + L(44, 58, 56, 58) + L(50, 54, 50, 58); break;
    default: s = R(24, 18, 52, 44);
  }
  return `<svg viewBox="0 0 100 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">${s}</svg>`;
}

function renderCatalogTab() {
  const groups = state.catGroup && GROUPS.some((g) => g.id === state.catGroup) ? state.catGroup : 'base';
  const list = CATALOG.filter((c) => c.group === groups);
  body.innerHTML = `
    <section class="group">
      <div class="chips" role="tablist">
        ${GROUPS.map((g) => `<button class="chip" data-group="${g.id}" aria-pressed="${g.id === groups}">${g.name}</button>`).join('')}
      </div>
      <div class="catalog">
        ${list.map((c) => `<button class="card" data-kind="${c.kind}">${icon(c)}<strong>${c.name}</strong><small>${c.corner ? `${c.w} × ${c.w2}` : `${c.w} × ${c.h} × ${c.d}`}</small></button>`).join('')}
      </div>
      <p class="note">${groups === 'corner'
        ? 'Бұрыштық шкаф бөлменің бос бұрышына қойылады. Оны оң жақ бұрышқа сүйреп апаруға болады.'
        : 'Басқанда артқы қабырғаға қойылады. Сүйреп басқа қабырғаға апарсаңыз, өзі бұрылып қабырғаға тіреледі.'}</p>
    </section>`;
  body.querySelectorAll('[data-group]').forEach((b) => b.addEventListener('click', () => { state.catGroup = b.dataset.group; renderSheet(); }));
  body.querySelectorAll('[data-kind]').forEach((b) => b.addEventListener('click', () => {
    pushHistory(snapshot());
    addItem(b.dataset.kind);
    if (isPhone()) sheet.classList.add('collapsed');
  }));
}

function renderPropsTab() {
  const it = getItem(state.selected);
  if (!it) {
    body.innerHTML = `<section class="group"><h3>Баптау</h3><p class="note">Баптау үшін 3D көріністе шкафты немесе техниканы басыңыз, не «Шкафтар» бөлімінен қосыңыз.</p></section>`;
    return;
  }
  const def = getDef(it.kind);
  const has = (f) => def.fields.includes(f);
  const widths = [300, 400, 450, 500, 600, 800, 900, 1200];
  const chipRow = (attr, items, cur) => `<div class="chips">${items.map((o) => `<button class="chip" data-${attr}="${o.id}" aria-pressed="${String(cur) === String(o.id)}">${o.name}</button>`).join('')}</div>`;
  const second = [
    has('y') ? numField('py', 'Еденнен', it.y) : '',
    has('plinth') ? numField('pp', 'Цоколь', it.plinth) : '',
    has('doors') ? numField('pn', 'Есік саны', it.doors, 'дана') : '',
    has('drawers') ? numField('pn', 'Тартпа', it.drawers, 'дана') : '',
    has('shelves') ? numField('ps', 'Сөре', it.shelves, 'дана') : '',
  ].filter(Boolean).join('');
  const facadeHtml = has('facade') ? `
    <section class="group">
      <h3>Есік түсі</h3>
      <div class="swatches">${COLORS.map((c) => `<button class="swatch" data-fac="${c.id}" style="background:${swatchCss(c.id)}" aria-pressed="${it.facade === c.id}" title="${c.name}" aria-label="${c.name}"></button>`).join('')}
        <label class="swatch picker" title="Басқа түс" style="background:${it.facade.startsWith('#') ? it.facade : '#ffffff'}"><input type="color" id="facPick" value="${it.facade.startsWith('#') ? it.facade : '#ffffff'}" aria-label="Басқа түс"><span>+</span></label>
      </div>
      <div class="chips">
        <span class="note" style="align-self:center">${colorName(it.facade)}</span>
        <button class="chip" id="glossBtn" aria-pressed="${!!it.gloss}">${it.gloss ? 'Жылтыр' : 'Күңгірт'}</button>
      </div>
    </section>
    <section class="group">
      <h3>Есік өрнегі</h3>
      <div class="patterns">${PATTERNS.map((p) => `<button class="pat" data-pat="${p.id}" aria-pressed="${(it.pattern || 'flat') === p.id}"><img alt="" src="${patternThumb(p.id, it.facade, it.patternImg)}"><span>${p.name}</span></button>`).join('')}</div>
      <input type="file" id="imgFile" accept="image/*" hidden>
      ${(it.pattern === 'image') ? `<button class="btn ghost" id="imgBtn">${it.patternImg ? 'Суретті ауыстыру' : 'Сурет таңдау'}</button>` : ''}
    </section>` : '';
  body.innerHTML = `
    <section class="group">
      <h3>${def.name}</h3>
      ${has('tv') ? `<div class="field"><label>Диагоналі</label>${chipRow('tv', TV_SIZES.map((t) => ({ id: t.id, name: t.id + '″' })), (TV_SIZES.find((t) => t.w === it.w) || {}).id)}</div>` : `
      <div class="row ${has('w2') ? 'two' : ''}">
        ${numField('pw', has('w2') ? 'Артқы қанаты' : 'Ені', it.w)}
        ${has('w2') ? numField('pw2', 'Бүйір қанаты', it.w2) : ''}
        ${numField('ph', 'Биіктігі', it.h)}
        ${numField('pd', 'Тереңдігі', it.d)}
      </div>`}
      ${!def.tech && !def.corner ? `<div class="chips">${widths.map((w) => `<button class="chip" data-w="${w}" aria-pressed="${it.w === w}">${w}</button>`).join('')}</div>` : ''}
      ${second ? `<div class="row">${second}</div>` : ''}
      ${has('countertop') ? `<label class="toggle"><input type="checkbox" id="pct" ${it.countertop ? 'checked' : ''}> Столешница</label>` : ''}
      ${has('tone') ? `<div class="field"><label>Түсі</label>${chipRow('tone', TONES, it.tone)}</div>` : ''}
      ${has('hob') ? `<div class="field"><label>Варочная панель</label>${chipRow('hob', HOBS, it.hob)}</div>` : ''}
    </section>
    ${facadeHtml}
    ${has('body') ? `<section class="group">
      <h3>Корпус түсі</h3>
      <div class="swatches">${COLORS.map((c) => `<button class="swatch" data-body="${c.id}" style="background:${swatchCss(c.id)}" aria-pressed="${it.body === c.id}" title="${c.name}" aria-label="${c.name}"></button>`).join('')}</div>
    </section>` : ''}
    ${has('facade') ? `<section class="group">
      <button class="btn" id="applyAll">Бұл есікті барлық шкафқа қолдану</button>
      <p class="note">Түсі, өрнегі және жылтырлығы барлық шкафтың есіктері мен тартпаларына көшеді.</p>
    </section>` : ''}`;

  const upd = (patch) => {
    pushHistory(snapshot());
    Object.assign(it, patch);
    syncItem(it);
    moveWithSnap(it, it.x, it.z);
    commit();
    renderSheet();
  };
  const bindNum = (id, key, min, max) => {
    const el = $('#' + id);
    if (!el) return;
    el.addEventListener('change', () => {
      const v = Math.round(Number(el.value));
      if (!(v >= min && v <= max)) { el.value = it[key]; return; }
      upd({ [key]: v });
    });
  };
  bindNum('pw', 'w', 100, 3000);
  bindNum('pw2', 'w2', 300, 3000);
  body.querySelectorAll('[data-tone]').forEach((b) => b.addEventListener('click', () => upd({ tone: b.dataset.tone })));
  body.querySelectorAll('[data-hob]').forEach((b) => b.addEventListener('click', () => upd({ hob: b.dataset.hob })));
  body.querySelectorAll('[data-tv]').forEach((b) => b.addEventListener('click', () => {
    const t = TV_SIZES.find((x) => String(x.id) === b.dataset.tv);
    upd({ w: t.w, h: t.h });
  }));
  bindNum('ph', 'h', 100, 2800);
  bindNum('pd', 'd', 100, 900);
  bindNum('py', 'y', 0, 2600);
  bindNum('pp', 'plinth', 0, 250);
  bindNum('pn', def.front === 'drawers' ? 'drawers' : 'doors', 1, 6);
  bindNum('ps', 'shelves', 0, 10);
  $('#pct')?.addEventListener('change', (e) => upd({ countertop: e.target.checked }));
  body.querySelectorAll('[data-w]').forEach((b) => b.addEventListener('click', () => upd({ w: Number(b.dataset.w) })));
  body.querySelectorAll('[data-fac]').forEach((b) => b.addEventListener('click', () => upd({ facade: b.dataset.fac })));
  $('#facPick')?.addEventListener('change', (e) => upd({ facade: e.target.value }));
  $('#glossBtn')?.addEventListener('click', () => upd({ gloss: !it.gloss }));
  body.querySelectorAll('[data-pat]').forEach((b) => b.addEventListener('click', () => {
    const p = b.dataset.pat;
    if (p === 'image' && !it.patternImg) { $('#imgFile').click(); return; }
    upd({ pattern: p });
  }));
  $('#imgBtn')?.addEventListener('click', () => $('#imgFile').click());
  $('#imgFile')?.addEventListener('change', async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const url = await shrinkImage(f);
    if (url) upd({ pattern: 'image', patternImg: url });
  });
  $('#applyAll')?.addEventListener('click', () => {
    pushHistory(snapshot());
    for (const o of state.items) if (getDef(o.kind).fields.includes('facade')) Object.assign(o, { facade: it.facade, pattern: it.pattern, gloss: it.gloss, patternImg: it.patternImg });
    state.items.forEach(syncItem);
    commit();
    renderSheet();
  });
  body.querySelectorAll('[data-body]').forEach((b) => b.addEventListener('click', () => upd({ body: b.dataset.body })));
}

// Жүктелген суретті кішірейту (жадқа сыйсын): ең үлкен жағы 640 px, JPEG
function shrinkImage(file) {
  return new Promise((resolve) => {
    const rd = new FileReader();
    rd.onload = () => {
      const img = new Image();
      img.onload = () => {
        const k = Math.min(1, 640 / Math.max(img.width, img.height));
        const c = document.createElement('canvas');
        c.width = Math.round(img.width * k);
        c.height = Math.round(img.height * k);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
        resolve(c.toDataURL('image/jpeg', 0.85));
      };
      img.onerror = () => resolve(null);
      img.src = rd.result;
    };
    rd.onerror = () => resolve(null);
    rd.readAsDataURL(file);
  });
}
setOnTextureUpdate(() => invalidate());

// ---------- жоғарғы батырмалар ----------
$('#view3d').addEventListener('click', () => view('3d'));
$('#viewFront').addEventListener('click', () => view('front'));
$('#viewTop').addEventListener('click', () => view('top'));
$('#dimsBtn').addEventListener('click', () => {
  state.showDims = !state.showDims;
  $('#dimsBtn').setAttribute('aria-pressed', String(state.showDims));
  rebuildRoom();
  state.items.forEach(updateLabel);
});
$('#rotBtn').addEventListener('click', () => {
  const it = getItem(state.selected);
  if (!it) return;
  pushHistory(snapshot());
  it.rot = (it.rot + 1) % 4;
  placeItem(it);
  commit();
});
$('#dupBtn').addEventListener('click', () => {
  const it = getItem(state.selected);
  if (!it) return;
  pushHistory(snapshot());
  const copy = { ...structuredClone(it), id: takeId() };
  const fw = footprint(it).fw;
  copy.x = it.x + (it.rot % 2 === 0 ? fw : 0);
  copy.z = it.z + (it.rot % 2 === 1 ? fw : 0);
  state.items.push(copy);
  syncItem(copy);
  moveWithSnap(copy, copy.x, copy.z);
  select(copy.id);
  commit();
});
$('#delBtn').addEventListener('click', () => {
  if (state.selected == null) return;
  pushHistory(snapshot());
  state.items = state.items.filter((i) => i.id !== state.selected);
  removeView(state.selected);
  select(null);
  commit();
});
window.addEventListener('keydown', (e) => {
  if (e.target.matches('input')) return;
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); undo(); }
  if ((e.key === 'Delete' || e.key === 'Backspace') && state.selected != null) $('#delBtn').click();
  if (e.key.toLowerCase() === 'r' && state.selected != null) $('#rotBtn').click();
});

// ---------- өлшем және цикл ----------
function resize() {
  const w = viewport.clientWidth, h = viewport.clientHeight;
  renderer.setSize(w, h, false);
  labelRenderer.setSize(w, h);
  camera.aspect = w / Math.max(1, h);
  camera.updateProjectionMatrix();
  invalidate();
}
new ResizeObserver(resize).observe(viewport);

function loop(now) {
  requestAnimationFrame(loop);
  if (tween) {
    const k = Math.min(1, (now - tween.start) / tween.ms);
    const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    camera.position.lerpVectors(tween.p0, tween.p1, e);
    controls.target.lerpVectors(tween.t0, tween.t1, e);
    if (k >= 1) tween = null;
    needsRender = true;
  }
  if (controls.update()) needsRender = true;
  if (!needsRender) return;
  needsRender = false;
  const sel = views.get(state.selected);
  selBox.visible = !!sel;
  if (sel) { selBox.box.setFromObject(sel.outer); selBox.box.expandByScalar(8); }
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

// ---------- іске қосу ----------
if (isPhone()) sheet.classList.add('collapsed'); // телефонда алдымен 3D көрініс толық көрінсін
setTimeout(() => { $('#hint').hidden = true; }, 7000);
if (!load()) sampleKitchen();
setNextId(state.items.reduce((m, i) => Math.max(m, i.id + 1), 1));
applyTheme();
rebuildAll();
renderSheet();
resize();
view('3d', true);
requestAnimationFrame(loop);
window.__app = { state, view, addItem, select, camera, controls, THREE };
