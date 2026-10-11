"use strict";
// NeuralMind Artificial Life Playground — frontend.
// All simulation/learning runs on the backend; this only renders real state.

const API = {
  async post(path, body) {
    const r = await fetch(path, {method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body || {})});
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
    return r.json();
  },
  get: async (p) => (await fetch(p)).json(),
};

const S = {
  session: null, cfg: null, bounds: null, actions: [], nodeOrder: [], sizes: {},
  size: 1, hazards: [], layout: null,
  frame: null, glow: [], queue: [], fetching: false,
  playing: false, learning: true, speed: 10, lastAdvance: 0, deprive: false,
  trail: [], epEnergy: [], epReward: [], learnCurve: [],
  yaw: 0.6, pitch: -0.35, nodeProj: [],
};
window.S = S;  // exposed for inspection/debugging

const PAL = {sensory: "#6d9bff", left: "#bf91f3", forward: "#49d6a6", right: "#e0a63b"};
const $ = (id) => document.getElementById(id);
function toast(msg) { const t = $("toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 2200); }

// ---------- canvas helper (idempotent sizing) ----------
function fit(cv) {
  const r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1;
  const pw = Math.max(1, Math.round(r.width * d)), ph = Math.max(1, Math.round(r.height * d));
  if (cv.width !== pw) cv.width = pw;
  if (cv.height !== ph) cv.height = ph;
  const x = cv.getContext("2d"); x.setTransform(d, 0, 0, d, 0, 0);
  return {x, w: r.width, h: r.height};
}

// ---------- session ----------
async function newWorld() {
  const overrides = gatherControls();
  S.session = await API.post("/api/session", overrides);
  applySession(S.session);
  toast("New world created");
}
function applySession(d) {
  S.cfg = d.config; S.bounds = d.bounds; S.actions = d.actions;
  S.nodeOrder = d.node_order; S.sizes = d.sizes; S.size = d.size;
  S.hazards = d.hazards; S.layout = d.layout;
  S.trail = []; S.epEnergy = []; S.epReward = [];
  S.queue = []; S.frame = d.state; S.glow = d.state.glow || [];
  S.deprive = false;
  $("btnDeprive").classList.remove("on"); $("btnDeprive").textContent = "🚫 Deprive";
  buildControls(d.config, d.bounds);
  buildBrainLegend();
  buildScores(0);
  applyFrame(d.state, true);
  $("worldState").textContent = "ready";
}

// ---------- controls ----------
const ENV_FIELDS = [
  ["n_food", "Food items", 0], ["n_hazard", "Hazards", 0],
  ["sensor_range", "Sensor range", 2], ["speed", "Move speed", 3],
  ["food_energy", "Food energy", 2], ["move_cost", "Move cost", 3],
  ["hazard_cost", "Hazard cost", 3], ["max_ticks", "Max ticks", 0],
  ["seed", "Seed", 0],
];
const NEURO_FIELDS = [
  ["n_action", "Neurons / action", 0], ["sensor_gain", "Sensor gain", 1],
  ["action_noise", "Exploration noise", 1], ["lr", "Learning rate", 2],
  ["w_inhib", "Lateral inhibition", 2], ["r_align", "Align reward", 1],
  ["r_hazard", "Hazard penalty", 1],
];
function sliderRow(key, label, dp, cfg, bounds) {
  const b = bounds[key] || [0, 10];
  const step = dp === 0 ? 1 : Math.pow(10, -dp);
  const val = cfg[key];
  return `<div class="ctl"><label>${label}<span class="val" id="v_${key}">${(+val).toFixed(dp)}</span></label>
    <input type="range" id="c_${key}" min="${b[0]}" max="${b[1]}" step="${step}" value="${val}"></div>`;
}
function buildControls(cfg, bounds) {
  $("envCtls").innerHTML = ENV_FIELDS.map(([k, l, dp]) => sliderRow(k, l, dp, cfg, bounds)).join("");
  $("neuroCtls").innerHTML = NEURO_FIELDS.map(([k, l, dp]) => sliderRow(k, l, dp, cfg, bounds)).join("");
  for (const [k, , dp] of [...ENV_FIELDS, ...NEURO_FIELDS]) {
    const el = $("c_" + k);
    if (el) el.oninput = () => { $("v_" + k).textContent = (+el.value).toFixed(dp); };
  }
}
function gatherControls() {
  const o = {};
  for (const [k] of [...ENV_FIELDS, ...NEURO_FIELDS]) {
    const el = $("c_" + k); if (el) o[k] = +el.value;
  }
  o.learning = S.learning;
  return o;
}

// ---------- apply a frame ----------
function applyFrame(f, instant) {
  S.frame = f; S.glow = f.glow || S.glow;
  S.trail.push(f.agent);
  if (S.trail.length > 240) S.trail.shift();
  S.epEnergy.push(f.energy);
  S.epReward.push(f.reward);
  // inspector
  $("iEnergy").textContent = f.energy.toFixed(3);
  const ep = Math.max(0, Math.min(1, f.energy / (S.cfg.e0 || 1)));
  const bar = $("energyBar"); bar.style.width = (ep * 100).toFixed(0) + "%";
  bar.style.background = ep > 0.5 ? "var(--good)" : ep > 0.2 ? "var(--warn)" : "var(--bad)";
  $("iAge").textContent = f.t;
  $("iFood").textContent = f.food_eaten;
  $("iHaz").textContent = f.hazard_hits;
  $("iAction").textContent = S.actions[f.action] || "–";
  $("iReward").textContent = sum(S.epReward).toFixed(2);
  $("iRpe").textContent = (f.rpe ?? 0).toFixed(3);
  $("iDay").textContent = (f.day ?? 0).toFixed(2);
  const hunger = f.hunger ?? 0;
  $("iHunger").textContent = hunger.toFixed(2);
  $("hungerBar").style.width = (hunger * 100).toFixed(0) + "%";
  $("hungerBar").style.background = hunger > 0.75 ? "var(--bad)" : "var(--warn)";
  drawAffect(f.affect || {});
  const st = !f.alive ? "episode ended" : (f.deprive ? `DEPRIVED · day ${(f.day||0).toFixed(1)}`
    : (S.playing ? "running" : "paused"));
  $("worldState").textContent = st;
  $("worldState").style.color = f.deprive && f.alive ? "var(--bad)" : "";
  buildScores(f.action, f.scores);
}
const sum = (a) => a.reduce((x, y) => x + y, 0);

function buildScores(active, scores) {
  const el = $("scores");
  el.innerHTML = S.actions.map((a, i) =>
    `<div class="score ${i === active ? "on" : ""}">${a}<br><b>${scores ? scores[i] : 0}</b></div>`).join("");
}
function drawAffect(a) {
  const defs = [["valence", -1, 1, "#49d6a6"], ["arousal", 0, 1, "#e0a63b"],
    ["threat", 0, 1, "#e0734f"], ["frustration", 0, 1, "#bf91f3"]];
  $("affectBars").innerHTML = defs.map(([k, lo, hi, col]) => {
    const v = a[k] ?? 0, pct = Math.max(0, Math.min(1, (v - lo) / (hi - lo))) * 100;
    return `<div class="stat" style="border:0;padding:1px 0"><b>${k}</b><span>${v.toFixed(2)}</span></div>
      <div class="bar" style="margin-bottom:4px"><i style="width:${pct}%;background:${col}"></i></div>`;
  }).join("");
}
function buildBrainLegend() {
  $("brainLegend").innerHTML = S.nodeOrder.map(p =>
    `<span><span class="dot" style="background:${PAL[p] || "#888"}"></span>${p} (${S.sizes[p]})</span>`).join("");
}

// ---------- world rendering ----------
function worldGeom() {
  const cv = $("world"); const g = fit(cv);
  g.sz = Math.min(g.w, g.h); g.ox = (g.w - g.sz) / 2; g.oy = (g.h - g.sz) / 2;
  g.sc = g.sz / S.size;
  g.X = (p) => g.ox + p[0] * g.sc;
  g.Y = (p) => g.oy + (S.size - p[1]) * g.sc; // world +y is up; canvas +y is down
  g.cv = cv;
  return g;
}
function drawWorld() {
  const G = worldGeom(); const {x, w, h, sz, ox, oy, sc, X, Y} = G;
  x.clearRect(0, 0, w, h);
  // grass background with a soft vignette + dotted grid
  const grad = x.createRadialGradient(ox + sz / 2, oy + sz / 2, sz * 0.1,
    ox + sz / 2, oy + sz / 2, sz * 0.75);
  grad.addColorStop(0, "#1a2a1f"); grad.addColorStop(1, "#0f1712");
  x.fillStyle = grad; x.fillRect(ox, oy, sz, sz);
  x.fillStyle = "rgba(120,170,130,0.06)";
  const gstep = sz / 24;
  for (let i = 1; i < 24; i++) for (let j = 1; j < 24; j++) {
    x.beginPath(); x.arc(ox + i * gstep, oy + j * gstep, 1, 0, 7); x.fill();
  }
  x.strokeStyle = "#2b3a2f"; x.strokeRect(ox, oy, sz, sz);

  const f = S.frame; const now = performance.now() / 600;
  // hazards — pulsing danger zones
  for (const hz of S.hazards) {
    const r = S.cfg.hazard_radius * sc, cx = X(hz), cy = Y(hz);
    const gl = 0.5 + 0.18 * Math.sin(now + cx);
    const rg = x.createRadialGradient(cx, cy, r * 0.2, cx, cy, r);
    rg.addColorStop(0, `rgba(224,115,79,${0.32 * gl})`);
    rg.addColorStop(1, "rgba(224,115,79,0.02)");
    x.fillStyle = rg; x.beginPath(); x.arc(cx, cy, r, 0, 7); x.fill();
    x.strokeStyle = `rgba(224,115,79,${gl})`; x.lineWidth = 1.5;
    x.beginPath(); x.arc(cx, cy, r, 0, 7); x.stroke();
    // spikes
    x.strokeStyle = `rgba(255,150,110,${gl})`;
    for (let k = 0; k < 10; k++) { const a = k / 10 * 7, rr = r * 0.78;
      x.beginPath(); x.moveTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr);
      x.lineTo(cx + Math.cos(a) * r * 1.12, cy + Math.sin(a) * r * 1.12); x.stroke(); }
  }
  if (!f) return;
  // food — little berries with highlight
  for (const fd of f.food) {
    const cx = X(fd), cy = Y(fd), r = Math.max(4, 0.014 * sc);
    const rg = x.createRadialGradient(cx - r * 0.3, cy - r * 0.3, 1, cx, cy, r);
    rg.addColorStop(0, "#8ff0c8"); rg.addColorStop(1, "#2faa78");
    x.fillStyle = rg; x.beginPath(); x.arc(cx, cy, r, 0, 7); x.fill();
    x.strokeStyle = "#1c6b4c"; x.lineWidth = 1; x.beginPath(); x.moveTo(cx, cy - r); x.lineTo(cx + 2, cy - r - 3); x.stroke();
  }
  // trail
  if (S.trail.length > 1) {
    x.strokeStyle = "rgba(109,155,255,0.30)"; x.lineWidth = 1.5; x.beginPath();
    S.trail.forEach((p, i) => i ? x.lineTo(X(p), Y(p)) : x.moveTo(X(p), Y(p))); x.stroke();
  }
  drawCreature(x, X(f.agent), Y(f.agent), -f.heading, f, sc);
}
function drawCreature(x, ax, ay, hd, f, sc) {
  // sensor ring
  x.strokeStyle = "rgba(109,155,255,0.16)"; x.lineWidth = 1;
  x.beginPath(); x.arc(ax, ay, S.cfg.sensor_range * sc, 0, 7); x.stroke();
  const r = Math.max(9, 0.03 * sc);
  const hungry = (f.hunger ?? 0);
  // body colour fades toward pale grey as it starves
  const base = f.alive ? [109, 155, 255] : [100, 108, 120];
  const col = base.map(c => Math.round(c * (1 - 0.45 * hungry) + 150 * 0.45 * hungry));
  x.save(); x.translate(ax, ay); x.rotate(hd);
  // glow
  x.fillStyle = `rgba(${col.join(",")},0.18)`; x.beginPath(); x.arc(0, 0, r * 1.7, 0, 7); x.fill();
  // body
  x.fillStyle = `rgb(${col.join(",")})`;
  x.beginPath(); x.ellipse(0, 0, r * 1.15, r, 0, 0, 7); x.fill();
  // direction fin
  x.beginPath(); x.moveTo(r * 1.5, 0); x.lineTo(r * 0.5, r * 0.55); x.lineTo(r * 0.5, -r * 0.55); x.closePath(); x.fill();
  // eyes
  x.fillStyle = "#0b0d12";
  x.beginPath(); x.arc(r * 0.5, -r * 0.35, r * 0.17, 0, 7); x.fill();
  x.beginPath(); x.arc(r * 0.5, r * 0.35, r * 0.17, 0, 7); x.fill();
  x.restore();
}

// ---------- brain scanner (3D) ----------
function projNode(n, w, h) {
  const cy = Math.cos(S.yaw), sy = Math.sin(S.yaw), cp = Math.cos(S.pitch), sp = Math.sin(S.pitch);
  let x = n.x * cy - n.z * sy, z = n.x * sy + n.z * cy, y = n.y;
  const y2 = y * cp - z * sp, z2 = y * sp + z * cp;
  const s = 3.0 / (3.0 + z2), R = Math.min(w, h) * 0.46;
  return {sx: w / 2 + x * s * R, sy: h / 2 + y2 * s * R, s, depth: z2};
}
function drawBrain() {
  const cv = $("brain"); const {x, w, h} = fit(cv);
  x.clearRect(0, 0, w, h);
  if (!S.layout) return;
  const nodes = S.layout.nodes, edges = S.layout.edges, glow = S.glow || [];
  const P = nodes.map(n => projNode(n, w, h));
  for (const e of edges) {
    const a = P[e.s], b = P[e.t]; if (!a || !b) continue;
    const g = Math.max(glow[e.s] || 0, glow[e.t] || 0), inh = e.w < 0;
    x.strokeStyle = (inh ? "rgba(224,115,79," : "rgba(120,150,210,") + (0.04 + 0.3 * g) + ")";
    x.lineWidth = 0.5 + g; x.beginPath(); x.moveTo(a.sx, a.sy); x.lineTo(b.sx, b.sy); x.stroke();
  }
  const order = P.map((p, i) => i).sort((i, j) => P[i].depth - P[j].depth);
  for (const i of order) {
    const p = P[i], g = glow[i] || 0, col = PAL[nodes[i].p] || "#6d9bff";
    const rad = (2 + 4.5 * g) * p.s + 1;
    if (g > 0.15) { x.globalAlpha = 0.25 * g; x.fillStyle = col;
      x.beginPath(); x.arc(p.sx, p.sy, rad * 2.3, 0, 7); x.fill(); }
    x.globalAlpha = 0.4 + 0.6 * g; x.fillStyle = col;
    x.beginPath(); x.arc(p.sx, p.sy, rad, 0, 7); x.fill();
  }
  x.globalAlpha = 1;
}

// ---------- charts ----------
function line(cv, series, colors, lo, hi) {
  const {x, w, h} = fit(cv); x.clearRect(0, 0, w, h);
  const all = series.flat(); if (!all.length) return;
  if (lo === undefined) lo = Math.min(...all);
  if (hi === undefined) hi = Math.max(...all);
  if (hi === lo) hi = lo + 1;
  const n = Math.max(...series.map(s => s.length), 2);
  const px = w / (n - 1), Y = v => h - 4 - (v - lo) / (hi - lo) * (h - 10);
  series.forEach((s, k) => {
    if (s.length < 2) return;
    x.strokeStyle = colors[k]; x.lineWidth = 1.6; x.beginPath();
    s.forEach((v, i) => i ? x.lineTo(i * px, Y(v)) : x.moveTo(i * px, Y(v))); x.stroke();
  });
}
function drawCharts() {
  // cumulative reward for readability
  let acc = 0; const cum = S.epReward.map(r => (acc += r));
  line($("chartEp"), [S.epEnergy, cum], ["#49d6a6", "#6d9bff"]);
  if (S.learnCurve.length) line($("chartLearn"), [S.learnCurve], ["#e0a63b"], 0);
  else { const {x, w, h} = fit($("chartLearn")); x.clearRect(0,0,w,h);
    x.fillStyle = "#8a93a6"; x.font = "11px sans-serif";
    x.fillText("Run 'Train 40 episodes' to see the learning curve.", 6, h / 2); }
}

// ---------- loop ----------
async function pump() {
  if (!S.playing || S.fetching || S.queue.length > 10 || !S.session) return;
  S.fetching = true;
  try {
    const d = await API.post("/api/step", {n: 6, learning: S.learning});
    S.queue.push(...d.frames);
    if (!d.alive) { /* let queue drain, then stop */ }
  } catch (e) { toast("step error: " + e.message); S.playing = false; setPlay(); }
  S.fetching = false;
}
function renderLoop(ts) {
  S.yaw += 0.004;
  const interval = 1000 / S.speed;
  if (S.playing && S.queue.length && ts - S.lastAdvance >= interval) {
    applyFrame(S.queue.shift()); S.lastAdvance = ts;
    if (!S.frame.alive && !S.queue.length) { S.playing = false; setPlay(); toast("Episode ended"); }
  }
  drawWorld(); drawBrain(); drawCharts();
  pump();
  requestAnimationFrame(renderLoop);
}

// ---------- controls wiring ----------
function setPlay() { $("btnPlay").textContent = S.playing ? "❚❚ Pause" : "▶ Play"; }
async function togglePlay() {
  if (!S.session) return;
  S.playing = !S.playing; setPlay();
}
async function stepOnce() {
  if (!S.session) return;
  const d = await API.post("/api/step", {n: 1, learning: S.learning});
  if (d.frames.length) applyFrame(d.frames[0]);
}
async function resetWorld(keep) {
  if (!S.session) return;
  S.playing = false; setPlay();
  const d = await API.post("/api/reset", {keep_weights: !!keep});
  S.trail = []; S.epEnergy = []; S.epReward = [];
  S.hazards = d.hazards; S.layout = d.layout; S.frame = d.state; S.glow = d.state.glow || [];
  S.deprive = false; $("btnDeprive").classList.remove("on"); $("btnDeprive").textContent = "🚫 Deprive";
  applyFrame(d.state, true);
  toast(keep ? "Reset (kept learned weights)" : "Reset");
}
async function train() {
  if (!S.session) { toast("Create a world first"); return; }
  S.playing = false; setPlay();
  $("btnTrain").disabled = true; $("btnTrain").textContent = "Training…";
  try {
    const d = await API.post("/api/train", {episodes: 40});
    S.learnCurve = d.curve.map(c => c.food);
    drawCharts();
    toast(`Trained ${d.episodes} episodes. Now Reset (keep weights) or Compare.`);
  } catch (e) { toast("train error: " + e.message); }
  $("btnTrain").disabled = false; $("btnTrain").textContent = "Train 40 episodes";
}
async function compare() {
  if (!S.session) return;
  $("btnCompare").disabled = true;
  try {
    const d = await API.post("/api/compare", {seeds: 16});
    const t = d.trained_mean, u = d.untrained_mean, mx = Math.max(t, u, 1);
    $("compareBox").innerHTML =
      `<div class="seg">Trained vs untrained (10 held-out worlds)</div>
       <div class="row"><span style="width:70px">trained</span>
         <span class="bar" style="flex:1"><i style="width:${t/mx*100}%;background:var(--good)"></i></span>
         <b>${t.toFixed(1)}</b></div>
       <div class="row"><span style="width:70px">untrained</span>
         <span class="bar" style="flex:1"><i style="width:${u/mx*100}%;background:var(--muted)"></i></span>
         <b>${u.toFixed(1)}</b></div>
       <p class="note">mean food eaten / episode. Learning helps when trained &gt; untrained.</p>`;
  } catch (e) { toast("compare error: " + e.message); }
  $("btnCompare").disabled = false;
}
async function save() {
  if (!S.session) return;
  const d = await API.post("/api/save", {note: "ui"});
  $("saveMsg").textContent = "saved run #" + d.id;
}
async function foodAhead() {
  if (!S.session) return;
  const d = await API.post("/api/place_food", {ahead: true});
  if (S.frame) S.frame.food = d.food;
}
async function placeFoodAt(ev) {
  if (!S.session) return;
  const G = worldGeom(); const rect = G.cv.getBoundingClientRect();
  const px = ev.clientX - rect.left, py = ev.clientY - rect.top;
  const wx = (px - G.ox) / G.sc, wy = S.size - (py - G.oy) / G.sc;
  if (wx < 0 || wx > S.size || wy < 0 || wy > S.size) return;
  const d = await API.post("/api/place_food", {x: wx, y: wy});
  if (S.frame) S.frame.food = d.food;
}
async function toggleDeprive() {
  if (!S.session) return;
  S.deprive = !S.deprive;
  await API.post("/api/deprive", {on: S.deprive});
  $("btnDeprive").classList.toggle("on", S.deprive);
  $("btnDeprive").textContent = S.deprive ? "🍃 Feed again" : "🚫 Deprive";
  toast(S.deprive ? "Food deprivation ON — watch energy & affect change" : "Deprivation off");
}

function wire() {
  $("btnNew").onclick = newWorld;
  $("btnPlay").onclick = togglePlay;
  $("btnStep").onclick = stepOnce;
  $("btnReset").onclick = () => resetWorld(true);
  $("btnTrain").onclick = train;
  $("btnCompare").onclick = compare;
  $("btnSave").onclick = save;
  $("btnFood").onclick = foodAhead;
  $("btnDeprive").onclick = toggleDeprive;
  $("world").addEventListener("click", placeFoodAt);
  $("world").style.cursor = "crosshair";
  $("speed").oninput = (e) => { S.speed = +e.target.value; };
  $("learnTgl").onchange = (e) => { S.learning = e.target.checked; };
  // drag to rotate brain
  const b = $("brain"); let drag = false, lx = 0, ly = 0;
  b.addEventListener("pointerdown", e => { drag = true; lx = e.clientX; ly = e.clientY; b.setPointerCapture(e.pointerId); });
  b.addEventListener("pointermove", e => { if (!drag) return;
    S.yaw += (e.clientX - lx) * 0.01; S.pitch = Math.max(-1.4, Math.min(1.4, S.pitch + (e.clientY - ly) * 0.01));
    lx = e.clientX; ly = e.clientY; });
  b.addEventListener("pointerup", () => drag = false);
}

(async function init() {
  wire();
  try { S.session = await API.post("/api/session", {}); applySession(S.session); }
  catch (e) { toast("Could not reach backend: " + e.message); }
  requestAnimationFrame(renderLoop);
})();
