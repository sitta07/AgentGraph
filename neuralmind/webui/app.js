"use strict";
// NeuralMind Artificial Life Playground frontend.
// All simulation and learning runs on the backend; this only renders real state.

const S = {
  session: null, cfg: null, defaults: null, applied: {}, bounds: null, actions: [], nodeOrder: [], sizes: {},
  size: 1, hazards: [], layout: null,
  frame: null, glow: [], queue: [], fetching: false,
  playing: false, learning: true, speed: 10, lastAdvance: 0, deprive: false,
  trail: [], epEnergy: [], epReward: [], learnCurve: [],
  selId: 0, brainId: -1, brainAge: 0, trails: {}, timeline: [], fx: [], popSeries: [], genSeries: [],
  yaw: 0.6, pitch: -0.35, nodeProj: [],
};
window.S = S;  // read by tools/make_media.py and handy for debugging

const PAL = {sensory: "#6d9bff", left: "#bf91f3", forward: "#49d6a6", right: "#e0a63b",
  attack: "#ff5a4f", share: "#5fe08a", signal: "#ffd84a"};

function fit(cv) {
  const r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1;
  const pw = Math.max(1, Math.round(r.width * d)), ph = Math.max(1, Math.round(r.height * d));
  if (cv.width !== pw) cv.width = pw;
  if (cv.height !== ph) cv.height = ph;
  const x = cv.getContext("2d"); x.setTransform(d, 0, 0, d, 0, 0);
  return {x, w: r.width, h: r.height};
}

// ---------- settings: one registry drives build, gather and dirty-check ----------
const LOCO = ["left", "forward", "right"];
const GROUPS = ["World", "Brain & learning", "Research switches (ablations)"];
const CONTROLS = [
  {key: "n_agents", label: "People", help: "How many creatures the world starts with.", tier: "basic", kind: "range", dp: 0},
  {key: "n_food", label: "Food", help: "How many food items are on the ground at once.", tier: "basic", kind: "range", dp: 0},
  {key: "n_hazard", label: "Hazards", help: "Fire pits that drain energy from anyone standing in them.", tier: "basic", kind: "range", dp: 0},
  {key: "seed", label: "Seed", help: "Fixes the random layout and brains, so the same seed gives the same world.", tier: "basic", kind: "range", dp: 0},

  {key: "social", label: "Social life", help: "Creatures see each other and can attack, share food and signal.", tier: "advanced", group: "World", kind: "toggle"},
  {key: "evolve", label: "Evolution", help: "Creatures reproduce, offspring mutate, and old or starving ones die. Turns on social life.", tier: "advanced", group: "World", kind: "toggle"},
  {key: "viscous", label: "Born near parent", help: "Newborns appear next to their parent instead of anywhere.", tier: "advanced", group: "World", kind: "toggle"},
  {key: "sensor_range", label: "Sight range", help: "How far a creature can sense food, hazards and others.", tier: "advanced", group: "World", kind: "range", dp: 2},
  {key: "speed", label: "Walk speed", help: "Distance moved per step.", tier: "advanced", group: "World", kind: "range", dp: 3},
  {key: "food_energy", label: "Food energy", help: "Energy gained from one food item.", tier: "advanced", group: "World", kind: "range", dp: 2},
  {key: "move_cost", label: "Moving cost", help: "Energy spent on every step.", tier: "advanced", group: "World", kind: "range", dp: 3},
  {key: "hazard_cost", label: "Hazard damage", help: "Energy lost per step inside a hazard.", tier: "advanced", group: "World", kind: "range", dp: 3},
  {key: "max_ticks", label: "Episode length", help: "Steps before an episode ends on its own.", tier: "advanced", group: "World", kind: "range", dp: 0},
  {key: "ticks_per_day", label: "Day length", help: "Steps that make up one simulated day.", tier: "advanced", group: "World", kind: "range", dp: 0},

  {key: "substeps", label: "Decision time (ms)", help: "Simulated milliseconds the brain runs before each move. 32 lets senses reach the action groups (Exp. W).", tier: "advanced", group: "Brain & learning", kind: "range", dp: 0},
  {key: "n_action", label: "Neurons per action", help: "Size of each group of neurons that votes for one action.", tier: "advanced", group: "Brain & learning", kind: "range", dp: 0},
  {key: "sensor_gain", label: "Sense strength", help: "How strongly sensing drives the sensory neurons.", tier: "advanced", group: "Brain & learning", kind: "range", dp: 1},
  {key: "action_noise", label: "Exploration", help: "Random input that makes creatures try different actions.", tier: "advanced", group: "Brain & learning", kind: "range", dp: 1},
  {key: "lr", label: "Learning rate", help: "How much one reward changes the connections.", tier: "advanced", group: "Brain & learning", kind: "range", dp: 2},
  {key: "w_inhib", label: "Action competition", help: "How strongly the action groups suppress each other.", tier: "advanced", group: "Brain & learning", kind: "range", dp: 2},
  {key: "r_align", label: "Reward for facing food", help: "Learning reward for turning towards nearby food.", tier: "advanced", group: "Brain & learning", kind: "range", dp: 1},
  {key: "r_hazard", label: "Hazard penalty", help: "Learning penalty for touching a hazard.", tier: "advanced", group: "Brain & learning", kind: "range", dp: 1},

  {key: "credit_chosen_only", exp: "I", label: "Reward chosen action only", help: "Reward changes only the connections of the action actually taken.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "frozen_inputs", exp: "J", label: "Freeze movement learning", help: "The left, ahead and right action groups never learn.", tier: "advanced", group: "Research switches (ablations)", kind: "loco"},
  {key: "normalized_inputs", exp: "K", label: "Fixed movement drive", help: "Total input to each movement neuron is held at its starting value.", tier: "advanced", group: "Research switches (ablations)", kind: "loco"},
  {key: "deaf", exp: "M", label: "No hearing", help: "Nobody can hear signals.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "positive_rpe_only", exp: "P", label: "Learn from good surprises only", help: "Rewards worse than expected change nothing.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "born_near_stranger", exp: "Q", label: "Born beside a stranger", help: "Newborns are placed next to a non-relative. Needs Born near parent off.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "no_filial_gain", exp: "Q3", label: "No gain from attacking offspring", help: "Attacking your own offspring drains it but gives you no energy.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "critic", exp: "R", label: "Expectation per situation", help: "Keep a separate reward expectation for each sensed situation.", tier: "advanced", group: "Research switches (ablations)", kind: "critic"},
  {key: "directional_hearing", exp: "S", label: "Hear direction of calls", help: "Creatures hear which side a signal comes from.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "scramble_senses", exp: "V", label: "Scrambled senses", help: "Food and hazard readings are shuffled every step, so they carry no direction.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "reset_each_decision", exp: "W", label: "Fresh start each decision", help: "Neuron state is cleared before every move, so the last winner does not keep winning.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "normalize", exp: "W", label: "Balanced learning", help: "Each action neuron's total input weight stays fixed, so one pathway cannot run away.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
  {key: "lamarckian", label: "Inherit learned brains", help: "Offspring inherit the parent's learned connections, not its inborn ones.", tier: "advanced", group: "Research switches (ablations)", kind: "toggle"},
];
// UI value <-> config value. Every non-range control shows as one checkbox.
const CODEC = {
  range: {decode: v => +v, encode: v => v},
  toggle: {decode: v => !!v, encode: v => v},
  loco: {decode: v => (v || []).length > 0, encode: on => on ? LOCO : []},
  critic: {decode: v => v === "state", encode: on => on ? "state" : "scalar"},
};
const elOf = (c) => $((c.kind === "range" ? "c_" : "t_") + c.key);
const readCtl = (c) => { const el = elOf(c); return el ? (c.kind === "range" ? +el.value : el.checked) : undefined; };
function writeCtl(c, v) {
  const el = elOf(c); if (!el) return;
  if (c.kind === "range") { el.value = v; $("v_" + c.key).textContent = (+el.value).toFixed(c.dp); }
  else el.checked = !!v;
}

const SCENARIOS = [
  {id: "lone", name: "Lone forager", blurb: "One creature learns to find food and avoid hazards.",
   overrides: {n_agents: 1}},
  {id: "learner", name: "Learning that works", blurb: "One creature with the fixed brain dynamics from Exp. W. Train it and it learns to steer to food.",
   overrides: {n_agents: 1, substeps: 32, reset_each_decision: true, normalize: true}},
  {id: "social", name: "Social group", blurb: "Six creatures that can attack, share food and signal.",
   overrides: {n_agents: 6, social: true}},
  {id: "evolve", name: "Evolving population", blurb: "Creatures reproduce and mutate. Watch the family tree.",
   overrides: {n_agents: 8, n_food: 22, social: true, evolve: true}},
];
const CUSTOM = {id: "custom", name: "Custom", blurb: "Your own mix. Pick a scenario above to start again."};

// Seed is left out so a scenario keeps the seed the user chose.
function scenarioValues(sc) {
  const out = {};
  for (const c of CONTROLS) if (c.key !== "seed")
    out[c.key] = c.key in sc.overrides ? sc.overrides[c.key] : CODEC[c.kind].decode(S.defaults[c.key]);
  return out;
}
const same = (a, b) => typeof a === "number" ? Math.abs(a - b) < 1e-9 : a === b;
function activeScenario() {
  if (!S.defaults) return CUSTOM;
  return SCENARIOS.find(sc => Object.entries(scenarioValues(sc)).every(([k, v]) =>
    same(readCtl(CONTROLS.find(c => c.key === k)), v))) || CUSTOM;
}
const pendingCount = () => CONTROLS.filter(c => !same(readCtl(c), S.applied[c.key])).length;

function controlHtml(c, cfg, bounds) {
  const help = `<button type="button" class="help" aria-expanded="false" aria-controls="h_${c.key}"
      aria-label="What is ${esc(c.label)}?">?</button>`;
  const exp = c.exp ? `<span class="exp" title="Experiment ${c.exp} in results/">Exp ${c.exp}</span>` : "";
  const value = CODEC[c.kind].decode(cfg[c.key]);
  if (c.kind === "range") {
    const [lo, hi] = bounds[c.key] || [0, 10];
    const step = c.dp === 0 ? 1 : Math.pow(10, -c.dp);
    return `<div class="ctl"><div class="ctl-head"><label for="c_${c.key}">${esc(c.label)}</label>
        <span class="val" id="v_${c.key}">${value.toFixed(c.dp)}</span>${help}</div>
      <input type="range" id="c_${c.key}" min="${lo}" max="${hi}" step="${step}" value="${value}">
      <p class="note help-text" id="h_${c.key}" hidden>${esc(c.help)}</p></div>`;
  }
  const research = !!c.exp || c.group === GROUPS[2];
  return `<div class="ctl"><div class="ctl-head"><label><input type="checkbox" id="t_${c.key}" ${value ? "checked" : ""}>
      ${esc(c.label)}</label>${exp}${research ? "" : help}</div>
    <p class="note help-text" id="h_${c.key}" ${research ? "" : "hidden"}>${esc(c.help)}</p></div>`;
}
function buildControls(cfg, bounds) {
  const html = (list) => list.map(c => controlHtml(c, cfg, bounds)).join("");
  $("basicCtls").innerHTML = html(CONTROLS.filter(c => c.tier === "basic"));
  $("advCtls").innerHTML = GROUPS.map(g => `<div class="group-title">${esc(g)}</div>` +
    html(CONTROLS.filter(c => c.tier === "advanced" && c.group === g))).join("");
  S.applied = Object.fromEntries(CONTROLS.map(c => [c.key, readCtl(c)]));
  refreshSetup();
}
function buildScenarios() {
  $("scenarios").innerHTML = `<legend>Scenario</legend>` + [...SCENARIOS, CUSTOM].map(sc =>
    `<label class="scard"><input type="radio" name="scenario" value="${sc.id}">
      <div><b>${esc(sc.name)}</b><span>${esc(sc.blurb)}</span></div></label>`).join("");
}
function chooseScenario(id) {
  const sc = SCENARIOS.find(s => s.id === id);
  if (!sc || !S.defaults) return;
  for (const [k, v] of Object.entries(scenarioValues(sc))) writeCtl(CONTROLS.find(c => c.key === k), v);
  refreshSetup();
}
function refreshSetup() {
  const active = activeScenario();
  for (const r of document.querySelectorAll("input[name=scenario]")) {
    r.checked = r.value === active.id;
    if (r.value === CUSTOM.id) r.disabled = active.id !== CUSTOM.id;
  }
  const n = pendingCount();
  $("pending").textContent = n ? `${n} ${n === 1 ? "change" : "changes"} not applied yet` : "";
  const btn = $("btnNew");
  btn.classList.toggle("ghost", !n);
  btn.textContent = n ? "Create world with these settings" : "New world";
}
function gatherControls() {
  const o = {};
  for (const c of CONTROLS) { const v = readCtl(c); if (v !== undefined) o[c.key] = CODEC[c.kind].encode(v); }
  if (o.evolve) o.social = true;   // evolution experiments run with the social layer
  o.learning = S.learning;
  return o;
}

// ---------- session ----------
async function newWorld() {
  const d = await api("/api/session", {body: gatherControls(), what: "Creating the world"});
  if (!d) return;
  S.session = d; applySession(d);
  toast("New world created");
}
function applySession(d) {
  S.cfg = d.config; S.bounds = d.bounds; S.actions = d.actions;
  S.nodeOrder = d.node_order; S.sizes = d.sizes; S.size = d.size;
  S.hazards = d.hazards; S.layout = d.layout;
  S.trail = []; S.epEnergy = []; S.epReward = []; S.trails = {}; S.timeline = []; S.selId = (d.state.agents && d.state.agents[0]) ? d.state.agents[0].id : 0;
  S.brainId = -1; S.fx = []; S.popSeries = []; S.genSeries = [];
  renderTimeline();
  S.queue = []; S.frame = d.state; S.glow = d.state.glow || [];
  setDeprive(false);
  buildControls(d.config, d.bounds);
  buildBrainLegend();
  buildScores(0);
  applyFrame(d.state, true);
  setStatus("ready", "ready");
}

// ---------- inspector ----------
const INSPECTOR = [
  {id: "iEnergy", label: "Energy", help: "Stored energy. Food adds it; moving and hazards use it. At zero the creature dies.", bar: "energyBar"},
  {id: "iHunger", label: "Hunger", help: "Time since the creature last ate, from 0 (just ate) to 1 (starving).", bar: "hungerBar"},
  {id: "iDay", label: "Day", help: "Simulated days since the episode started."},
  {id: "iAge", label: "Time alive (ticks)", help: "Simulation steps survived this episode."},
  {id: "iFood", label: "Food eaten", help: "Food items eaten this episode."},
  {id: "iHaz", label: "Hazard hits", help: "Steps spent inside a hazard."},
  {id: "iAction", label: "Current action", help: "The action group that fired most on the last step."},
  {id: "iReward", label: "Reward this episode", help: "Sum of the learning signal so far."},
  {id: "iRpe", label: "Surprise (reward prediction error)", help: "How much better or worse the last reward was than expected. This is what drives learning."},
];
const AFFECT = [
  {key: "valence", label: "Mood (valence)", lo: -1, hi: 1, col: "#49d6a6", help: "Good or bad overall, from -1 to 1."},
  {key: "arousal", label: "Arousal", lo: 0, hi: 1, col: "#e0a63b", help: "How activated the creature is."},
  {key: "threat", label: "Threat", lo: 0, hi: 1, col: "#e0734f", help: "Sensed danger, mostly from nearby hazards or attackers."},
  {key: "frustration", label: "Frustration", lo: 0, hi: 1, col: "#bf91f3", help: "Builds when rewards stay below expectation. Feeds the urge to attack."},
];
function buildInspector() {
  $("inspector").innerHTML = INSPECTOR.map(r =>
    `<div class="stat" title="${esc(r.help)}"><b>${esc(r.label)}</b><span id="${r.id}">0</span></div>` +
    (r.bar ? `<div class="bar" style="margin-bottom:6px"><i id="${r.bar}" style="width:0%"></i></div>` : "")).join("");
  $("inspectorHelp").innerHTML = [...INSPECTOR, ...AFFECT].map(r =>
    `<dt>${esc(r.label)}</dt><dd>${esc(r.help)}</dd>`).join("");
}

// ---------- apply a frame ----------
function applyFrame(frame, instant) {
  S.frame = frame;
  const agents = frame.agents || [frame];
  let selAg = agents.find(a => a.id === S.selId);
  if (!selAg || (!selAg.alive && agents.some(a => a.alive))) {
    selAg = selAg && selAg.alive ? selAg : (agents.find(a => a.alive) || agents[0]);
    S.selId = selAg.id;
  }
  queueEffects(frame);
  if (frame.evolve) { S.popSeries.push(frame.population);
    const live = agents.filter(a => a.alive);
    S.genSeries.push(live.length ? live.reduce((s, a) => s + a.generation, 0) / live.length : 0);
    if (S.popSeries.length > 600) { S.popSeries.shift(); S.genSeries.shift(); } }
  for (const ag of agents) { const k = ag.id ?? 0;
    (S.trails[k] = S.trails[k] || []).push(ag.agent);
    if (S.trails[k].length > 240) S.trails[k].shift(); }
  // the inspector, brain scanner and charts follow the SELECTED agent
  const f = Object.assign({}, frame, selAg);
  if (S.brainId !== S.selId || ++S.brainAge > 60) loadBrain(S.selId);
  S.glow = f.glow || S.glow;
  S.epEnergy.push(f.energy);
  S.epReward.push(f.reward);
  const nAlive = agents.filter(a => a.alive).length;
  $("selName").textContent = "P" + (S.selId + 1) + (agents.length > 1 ? ` · ${nAlive} alive` : "");
  $("brainWho").textContent = "P" + (S.selId + 1);
  $("iEnergy").textContent = f.energy.toFixed(3);
  const ep = Math.max(0, Math.min(1, f.energy / (S.cfg.e0 || 1)));
  const bar = $("energyBar"); bar.style.width = (ep * 100).toFixed(0) + "%";
  bar.style.background = ep > 0.5 ? "var(--good)" : ep > 0.2 ? "var(--warn)" : "var(--bad)";
  $("iAge").textContent = f.t;
  $("iFood").textContent = f.food_eaten;
  $("iHaz").textContent = f.hazard_hits;
  $("iAction").textContent = f.action_name || S.actions[f.action] || "–";
  renderSocial(f);
  $("iReward").textContent = sum(S.epReward).toFixed(2);
  $("iRpe").textContent = (f.rpe ?? 0).toFixed(3);
  $("iDay").textContent = (f.day ?? 0).toFixed(2);
  const hunger = f.hunger ?? 0;
  $("iHunger").textContent = hunger.toFixed(2);
  $("hungerBar").style.width = (hunger * 100).toFixed(0) + "%";
  $("hungerBar").style.background = hunger > 0.75 ? "var(--bad)" : "var(--warn)";
  drawAffect(f.affect || {});
  if (!f.alive) setStatus("ended", "episode ended");
  else if (f.deprive) setStatus("deprived", `deprived · day ${(f.day || 0).toFixed(1)}`);
  else setStatus(S.playing ? "running" : "paused", S.playing ? "running" : "paused");
  buildScores(f.action, f.scores);
}
function setStatus(state, text) {
  const el = $("worldState");
  if (el.dataset.state !== state || el.textContent !== text) { el.dataset.state = state; el.textContent = text; }
}
const sum = (a) => a.reduce((x, y) => x + y, 0);

function buildScores(active, scores) {
  const el = $("scores");
  el.innerHTML = S.actions.map((a, i) =>
    `<div class="score ${i === active ? "on" : ""}">${a}<br><b>${scores ? scores[i] : 0}</b></div>`).join("");
}
function drawAffect(a) {
  $("affectBars").innerHTML = AFFECT.map(({key, label, lo, hi, col}) => {
    const v = a[key] ?? 0, pct = Math.max(0, Math.min(1, (v - lo) / (hi - lo))) * 100;
    return `<div class="stat" style="border:0;padding:1px 0"><b>${label}</b><span>${v.toFixed(2)}</span></div>
      <div class="bar" style="margin-bottom:4px"><i style="width:${pct}%;background:${col}"></i></div>`;
  }).join("");
}
function renderSocial(f) {
  const el = $("socialStats"); if (!el) return;
  const rows = [];
  if (f.attacks !== undefined) rows.push(
    ["Attacks made / received", `${f.attacks} / ${f.attacked}`],
    ["Shares given / received", `${f.shares_given} / ${f.shares_received}`],
    ["Signals sent", f.signals],
    ["Urge to attack (nA)", (f.aggression_drive ?? 0).toFixed(2)]);
  if (f.generation !== undefined) rows.push(
    ["Generation · family line", `${f.generation} · L${f.lineage}`],
    ["Age (ticks)", f.age], ["Aggression gene", (f.aggr_gain ?? 0).toFixed(2)]);
  el.innerHTML = rows.length ? `<div class="seg">Social life and evolution</div>` + rows.map(([k, v]) =>
    `<div class="stat"><b>${k}</b><span>${v}</span></div>`).join("") : "";
}
async function loadBrain(id) {
  S.brainId = id; S.brainAge = 0;
  // quiet: the selected creature may have just died; the last brain stays on screen
  const b = await api("/api/brain/" + id, {quiet: true});
  if (b && b.layout && S.selId === id) { S.layout = b.layout; S.nodeOrder = b.node_order;
    S.sizes = b.sizes; S.actions = b.actions; buildBrainLegend(); }
}
function queueEffects(frame) {
  const byId = {}; for (const a of frame.agents || []) byId[a.id] = a;
  const now = performance.now();
  for (const e of frame.events || []) {
    const src = byId[e.src], dst = e.dst !== undefined ? byId[e.dst] : null;
    if (!src && !dst) continue;
    S.fx.push({type: e.type, a: src ? src.agent : null, b: dst ? dst.agent : null, t0: now});
  }
  if (S.fx.length > 200) S.fx.splice(0, S.fx.length - 200);
}
function drawEffects(x, G) {
  const now = performance.now(), {X, Y, ts} = G, life = 900;
  S.fx = S.fx.filter(f => now - f.t0 < life);
  x.font = `${Math.max(12, ts * 0.7)}px sans-serif`; x.textAlign = "center";
  for (const f of S.fx) {
    const k = 1 - (now - f.t0) / life; x.globalAlpha = k;
    const A = f.a && [X(f.a), Y(f.a)], B = f.b && [X(f.b), Y(f.b)];
    if (f.type === "attack" && A && B) {
      x.strokeStyle = "#ff5a4f"; x.lineWidth = 3; x.beginPath(); x.moveTo(...A);
      const mx = (A[0] + B[0]) / 2 + 4, my = (A[1] + B[1]) / 2 - 4; x.lineTo(mx, my); x.lineTo(...B); x.stroke();
      x.fillText("💢", A[0], A[1] - ts * 1.3);
    } else if (f.type === "share" && A && B) {
      x.strokeStyle = "#5fe08a"; x.lineWidth = 2.5; x.setLineDash([4, 3]);
      x.beginPath(); x.moveTo(...A); x.lineTo(...B); x.stroke(); x.setLineDash([]);
      x.fillText("💚", B[0], B[1] - ts * 1.3);
    } else if (f.type === "signal" && A) {
      x.strokeStyle = "#ffd84a"; x.lineWidth = 2;
      x.beginPath(); x.arc(A[0], A[1], ts * (0.6 + 2.5 * (1 - k)), 0, 7); x.stroke();
      x.fillText("📢", A[0], A[1] - ts * 1.3);
    } else if (f.type === "birth" && B) { x.fillText("✨", B[0], B[1] - ts);
    } else if (f.type === "death" && B) { x.fillText("💀", B[0], B[1] - ts);
    } else if (f.type === "attack_miss" && A) { x.fillText("💨", A[0] + ts * 0.6, A[1] - ts); }
  }
  x.globalAlpha = 1; x.textAlign = "start";
}
function mood(ag) {
  if ((ag.aggression_drive ?? 0) > 0.5) return "😠";
  if ((ag.hunger ?? 0) > 0.7) return "😫";
  if (ag.signaling) return "📢";
  if ((ag.affect && ag.affect.valence) > 0.3) return "🙂";
  return "";
}
function buildBrainLegend() {
  $("brainLegend").innerHTML = S.nodeOrder.map(p =>
    `<span><span class="dot" style="background:${PAL[p] || "#888"}"></span>${p} (${S.sizes[p]})</span>`).join("");
}

// ---------- world rendering ----------
// ---------- pixel-art world (Kenney CC0 tiles) ----------
const TOWN = new Image(); TOWN.src = "static/assets/kenney/tiny_town.png";
const DUN = new Image(); DUN.src = "static/assets/kenney/tiny_dungeon.png";
const SPRITES = [85, 99, 86, 88, 87, 100, 97, 111];   // tiny_dungeon character tiles
const T = {grass: 0, grass2: 1, flower: 2, trees: [4, 16, 28, 5], food: 29};
const D = {fire: 29, spikes: 41, grave: 65};
const GRID = 18;                                       // walkable tiles across

function tile(x, img, idx, dx, dy, size, flip) {
  if (!img.complete || !img.naturalWidth) return;
  const sx = (idx % 12) * 16, sy = Math.floor(idx / 12) * 16;
  if (flip) { x.save(); x.translate(dx + size, dy); x.scale(-1, 1);
    x.drawImage(img, sx, sy, 16, 16, 0, 0, size, size); x.restore(); }
  else x.drawImage(img, sx, sy, 16, 16, dx, dy, size, size);
}
const hash = (i, j) => { let h = (i * 374761393 + j * 668265263) ^ 0x5bd1e995;
  h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };

function worldGeom() {
  const cv = $("world"); const g = fit(cv);
  const total = GRID + 2;                               // +1 tree border each side
  g.ts = Math.max(8, Math.floor(Math.min(g.w, g.h) / total));
  g.sz = g.ts * total; g.ox = Math.floor((g.w - g.sz) / 2); g.oy = Math.floor((g.h - g.sz) / 2);
  g.ax = g.ox + g.ts; g.ay = g.oy + g.ts; g.as = g.ts * GRID;   // arena origin/size in px
  g.X = (p) => g.ax + p[0] / S.size * g.as;
  g.Y = (p) => g.ay + (1 - p[1] / S.size) * g.as;              // world +y up
  g.cv = cv;
  return g;
}
function drawWorld() {
  const G = worldGeom(); const {x, w, h, ts, ox, oy, ax, ay, as, X, Y} = G;
  x.imageSmoothingEnabled = false;
  x.clearRect(0, 0, w, h);
  // ground + decorative tree border (decoration only: the border lies OUTSIDE
  // the simulated arena, so it never misrepresents an obstacle)
  for (let i = 0; i < GRID + 2; i++) for (let j = 0; j < GRID + 2; j++) {
    const r = hash(i, j), dx = ox + i * ts, dy = oy + j * ts;
    tile(x, TOWN, r < 0.85 ? T.grass : T.grass2, dx, dy, ts);  // no flowers: they look like food
    const border = i === 0 || j === 0 || i === GRID + 1 || j === GRID + 1;
    if (border) tile(x, TOWN, T.trees[Math.floor(r * 4)], dx, dy, ts);
  }
  const f = S.frame; const pulse = 0.55 + 0.25 * Math.sin(performance.now() / 300);
  // hazards: danger zone + spike traps on covered tiles + fire in the centre
  for (const hz of S.hazards) {
    const cx = X(hz), cy = Y(hz), r = S.cfg.hazard_radius / S.size * as;
    x.fillStyle = `rgba(224,90,60,${0.18 * pulse})`;
    x.beginPath(); x.arc(cx, cy, r, 0, 7); x.fill();
    x.strokeStyle = `rgba(255,120,80,${0.7 * pulse})`; x.setLineDash([4, 3]);
    x.beginPath(); x.arc(cx, cy, r, 0, 7); x.stroke(); x.setLineDash([]);
    const n = Math.ceil(r / ts);
    for (let di = -n; di <= n; di++) for (let dj = -n; dj <= n; dj++) {
      const tx = cx + di * ts, ty = cy + dj * ts;
      if (Math.hypot(tx - cx, ty - cy) < r - ts * 0.3 && (di || dj))
        tile(x, DUN, D.spikes, tx - ts / 2, ty - ts / 2, ts);
    }
    tile(x, DUN, D.fire, cx - ts * 0.6, cy - ts * 0.6, ts * 1.2);
  }
  if (!f) return;
  // food: forageable mushrooms
  for (const fd of f.food) tile(x, TOWN, T.food, X(fd) - ts * 0.45, Y(fd) - ts * 0.45, ts * 0.9);
  const agents = f.agents || [f];
  const sel = agents.find(a => a.id === S.selId) || agents[0];
  // selected agent: sensor range + trail
  const tr = S.trails[sel.id ?? 0] || [];
  if (tr.length > 1) { x.strokeStyle = "rgba(255,255,255,0.35)"; x.lineWidth = 1.5;
    x.beginPath(); tr.forEach((p, i) => i ? x.lineTo(X(p), Y(p)) : x.moveTo(X(p), Y(p))); x.stroke(); }
  x.strokeStyle = "rgba(255,255,255,0.22)"; x.lineWidth = 1;
  x.beginPath(); x.arc(X(sel.agent), Y(sel.agent), S.cfg.sensor_range / S.size * as, 0, 7); x.stroke();
  for (const ag of agents) drawPerson(x, G, ag, ag === sel);
  drawEffects(x, G);
}
function drawPerson(x, G, ag, selected) {
  const {ts, X, Y} = G, cx = X(ag.agent), cy = Y(ag.agent), s = ts * 1.25;
  if (!ag.alive) { tile(x, DUN, D.grave, cx - ts / 2, cy - ts / 2, ts); return; }
  if (selected) { x.fillStyle = "rgba(109,155,255,0.30)";
    x.beginPath(); x.ellipse(cx, cy + s * 0.42, s * 0.55, s * 0.2, 0, 0, 7); x.fill(); }
  // faded sprite as the agent starves
  x.globalAlpha = 1 - 0.45 * (ag.hunger ?? 0);
  // in evolution mode relatives share a sprite (lineage); otherwise one per person
  const look = ag.lineage !== undefined ? ag.lineage : (ag.id ?? 0);
  tile(x, DUN, SPRITES[look % SPRITES.length], cx - s / 2, cy - s / 2, s,
       Math.cos(ag.heading) < 0);
  x.globalAlpha = 1;
  // heading arrow (world +y up -> canvas -y)
  const hx = Math.cos(ag.heading), hy = -Math.sin(ag.heading);
  x.strokeStyle = "#ffffff"; x.lineWidth = 2; x.beginPath();
  x.moveTo(cx + hx * s * 0.45, cy + hy * s * 0.45); x.lineTo(cx + hx * s * 0.8, cy + hy * s * 0.8); x.stroke();
  // energy bar + name tag
  const e = Math.max(0, Math.min(1, ag.energy / (S.cfg.e0 || 1))), bw = s;
  x.fillStyle = "rgba(0,0,0,0.55)"; x.fillRect(cx - bw / 2, cy - s * 0.78, bw, 4);
  x.fillStyle = e > 0.5 ? "#49d6a6" : e > 0.2 ? "#e0a63b" : "#e0734f";
  x.fillRect(cx - bw / 2, cy - s * 0.78, bw * e, 4);
  x.font = `bold ${Math.max(9, ts * 0.42)}px sans-serif`; x.textAlign = "center";
  x.fillStyle = "rgba(0,0,0,0.6)"; x.fillText("P" + ((ag.id ?? 0) + 1), cx + 1, cy - s * 0.86 + 1);
  x.fillStyle = selected ? "#ffffff" : "#d8deea"; x.fillText("P" + ((ag.id ?? 0) + 1), cx, cy - s * 0.86);
  const m = mood(ag);
  if (m) { x.font = `${Math.max(10, ts * 0.55)}px sans-serif`; x.fillText(m, cx + s * 0.55, cy - s * 0.45); }
  x.textAlign = "start";
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
  const pc = $("chartPop");
  if (pc) { pc.parentElement.style.display = S.popSeries.length ? "" : "none";
    if (S.popSeries.length > 1) line(pc, [S.popSeries, S.genSeries.map(g => g * 2)], ["#6d9bff", "#e0a63b"], 0); }
  if (S.learnCurve.length) line($("chartLearn"), [S.learnCurve], ["#e0a63b"], 0);
  else { const {x, w, h} = fit($("chartLearn")); x.clearRect(0,0,w,h);
    x.fillStyle = "#9aa3b5"; x.font = "12px sans-serif";
    x.fillText("Run 'Train 40 episodes' to see the learning curve.", 6, h / 2); }
}


// ---------- loop ----------
async function pump() {
  if (!S.playing || S.fetching || S.queue.length > 10 || !S.session) return;
  S.fetching = true;
  const d = await api("/api/step", {body: {n: 6, learning: S.learning}, what: "Running the world"});
  if (d) S.queue.push(...d.frames);
  else { S.playing = false; setPlay(); }
  S.fetching = false;
}
function renderLoop(ts) {
  S.yaw += 0.004;
  const interval = 1000 / S.speed;
  if (S.playing && S.queue.length && ts - S.lastAdvance >= interval) {
    applyFrame(S.queue.shift()); S.lastAdvance = ts;
    const anyAlive = (S.frame.agents || [S.frame]).some(a => a.alive);
    if (!anyAlive && !S.queue.length) { S.playing = false; setPlay();
      toast(S.frame.evolve ? "The population died out. Press New world to start again."
        : "Episode ended. Press Restart to run it again with what was learned."); }
  }
  drawWorld(); drawBrain(); drawCharts();
  pump();
  requestAnimationFrame(renderLoop);
}

// ---------- actions ----------
function setPlay() {
  $("btnPlay").textContent = S.playing ? "❚❚ Pause" : "▶ Play";
  $("btnPlay").setAttribute("aria-pressed", S.playing ? "true" : "false");
  if (["running", "paused", "ready"].includes($("worldState").dataset.state))
    setStatus(S.playing ? "running" : "paused", S.playing ? "running" : "paused");
}
function togglePlay() {
  if (!S.session) return;
  S.playing = !S.playing; setPlay();
  if (S.playing) dismissHint();
}
async function stepOnce() {
  if (!S.session) return;
  S.playing = false; setPlay();
  // frames prefetched while playing are older than the backend's state now
  S.queue = [];
  const d = await api("/api/step", {body: {n: 1, learning: S.learning}, what: "Stepping"});
  if (d && d.frames.length) applyFrame(d.frames[0]);
}
async function resetWorld(keep) {
  if (!S.session) return;
  S.playing = false; setPlay();
  const d = await api("/api/reset", {body: {keep_weights: !!keep}, what: "Restarting"});
  if (!d) return;
  S.trail = []; S.epEnergy = []; S.epReward = []; S.queue = [];
  S.hazards = d.hazards; S.layout = d.layout; S.frame = d.state; S.glow = d.state.glow || [];
  setDeprive(false);
  applyFrame(d.state, true);
  toast(keep ? "Episode restarted. The brains kept what they learned." : "Episode restarted");
}
async function busy(btn, label, work) {
  const idle = btn.textContent;
  btn.disabled = true; btn.setAttribute("aria-busy", "true"); btn.textContent = label;
  try { return await work(); }
  finally { btn.disabled = false; btn.removeAttribute("aria-busy"); btn.textContent = idle; }
}
async function train() {
  if (!S.session) { toast("Create a world first"); return; }
  S.playing = false; setPlay();
  const d = await busy($("btnTrain"), "Training…", () =>
    api("/api/train", {body: {episodes: 40}, what: "Training"}));
  if (!d) return;
  S.learnCurve = d.curve.map(c => c.food);
  drawCharts();
  toast(`Trained ${d.episodes} episodes. Press Restart to watch, or Compare.`);
}
async function compare() {
  if (!S.session) return;
  const d = await busy($("btnCompare"), "Comparing…", () =>
    api("/api/compare", {body: {seeds: 16}, what: "Comparing"}));
  if (!d) return;
  const t = d.trained_mean, u = d.untrained_mean, mx = Math.max(t, u, 1);
  $("compareBox").innerHTML =
    `<div class="seg">Trained vs untrained (${d.seeds.length} unseen worlds)</div>
     <div class="row"><span style="width:76px">trained</span>
       <span class="bar" style="flex:1"><i style="width:${t / mx * 100}%;background:var(--good)"></i></span>
       <b>${t.toFixed(1)}</b></div>
     <div class="row"><span style="width:76px">untrained</span>
       <span class="bar" style="flex:1"><i style="width:${u / mx * 100}%;background:var(--muted)"></i></span>
       <b>${u.toFixed(1)}</b></div>
     <p class="note">Mean food eaten per episode. Learning helped if trained is higher than untrained.</p>`;
}
async function save() {
  if (!S.session) return;
  const d = await api("/api/save", {body: {note: "ui"}, what: "Saving the episode"});
  if (!d) return;
  if (d.download) { downloadJson(d.download, "neuralmind-episode.json");
    $("saveMsg").textContent = "Downloaded as JSON (the browser version keeps no run history)"; }
  else $("saveMsg").textContent = "Saved as run #" + d.id;
}
function downloadJson(data, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: "application/json"}));
  a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
async function foodAhead() {
  if (!S.session) return;
  const d = await api("/api/place_food", {body: {ahead: true}, what: "Dropping food"});
  if (d && S.frame) S.frame.food = d.food;
}
async function placeFoodAt(ev) {
  if (!S.session) return;
  const G = worldGeom(); const rect = G.cv.getBoundingClientRect();
  const px = ev.clientX - rect.left, py = ev.clientY - rect.top;
  // click near a person -> select it; otherwise drop food on the grass
  const agents = (S.frame && S.frame.agents) || [];
  let best = -1, bd = G.ts * 1.0;
  agents.forEach((ag, i) => { const d = Math.hypot(G.X(ag.agent) - px, G.Y(ag.agent) - py);
    if (d < bd) { bd = d; best = i; } });
  if (best >= 0) { S.selId = agents[best].id; S.epEnergy = []; S.epReward = [];
    applyFrame(S.frame, true); loadBrain(S.selId);
    toast("Inspecting P" + (S.selId + 1) + ". The brain scanner now shows this creature."); return; }
  const wx = (px - G.ax) / G.as * S.size, wy = (1 - (py - G.ay) / G.as) * S.size;
  if (wx < 0 || wx > S.size || wy < 0 || wy > S.size) return;
  const d = await api("/api/place_food", {body: {x: wx, y: wy}, what: "Dropping food"});
  if (d && S.frame) S.frame.food = d.food;
}
async function advanceDays(days) {
  if (!S.session) return;
  S.playing = false; setPlay(); S.queue = [];
  const btn = $(days === 1 ? "btnDay1" : "btnDay3");
  const d = await busy(btn, "Running…", () => api("/api/advance",
    {body: {days, agent: S.selId, learning: S.learning}, what: "Skipping ahead"}));
  if (!d) return;
  S.timeline.push(...d.snapshots); renderTimeline();
  if (d.frame) applyFrame(d.frame, true);
  toast(`Skipped ${days} day${days > 1 ? "s" : ""}` + (d.alive ? "" : ". Everyone has died."));
}
function renderTimeline() {
  const el = $("timeline"); if (!el) return;
  if (!S.timeline.length) { el.textContent = "Press Skip 1 day to log how the selected creature's body, " +
    "feelings model and neuron firing change from day to day. Try Deprive first."; return; }
  const pct = (v) => (v * 100).toFixed(0) + "%";
  el.innerHTML = `<div class="tl-wrap"><table class="tl"><tr><th>day</th><th>energy</th><th>hunger</th><th>mood</th>
    <th>arousal</th><th>threat</th><th>senses</th><th>left</th><th>ahead</th><th>right</th></tr>` +
    S.timeline.slice(-12).map(r => `<tr style="${r.alive ? "" : "color:var(--bad)"}">
      <td>${r.day.toFixed(1)}${r.alive ? "" : " †"}</td><td>${r.energy.toFixed(2)}</td><td>${pct(r.hunger)}</td>
      <td>${r.affect.valence.toFixed(2)}</td><td>${r.affect.arousal.toFixed(2)}</td><td>${r.affect.threat.toFixed(2)}</td>
      <td>${pct(r.firing.sensory)}</td><td>${pct(r.firing.left)}</td><td>${pct(r.firing.forward)}</td><td>${pct(r.firing.right)}</td></tr>`).join("") +
    `</table></div><p class="note">End-of-day snapshot for P${S.selId + 1}. The last four columns are the
     share of steps in which that neuron group fired (senses, then the left, ahead and right action groups).</p>`;
}
function setDeprive(on) {
  S.deprive = on;
  const b = $("btnDeprive");
  b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false");
  b.textContent = on ? "Feed again" : "Deprive";
}
async function toggleDeprive() {
  if (!S.session) return;
  const d = await api("/api/deprive", {body: {on: !S.deprive}, what: "Changing food supply"});
  if (!d) return;
  setDeprive(d.deprive);
  toast(S.deprive ? "Food stopped. Watch energy and the feelings model change." : "Food is back");
}

// ---------- first-run hint ----------
const HINT_KEY = "neuralmind.hintDismissed";
function storageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function storageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode: hint shows again next visit */ } }
function dismissHint() { if ($("hint").hidden) return; $("hint").hidden = true; storageSet(HINT_KEY, "1"); }

// ---------- evolution observatory (phylogeny) ----------
const TREE = {timer: null, rows: [], geom: null};
function geneColor(g) {
  // 0..1 blue->yellow, 1..3 yellow->red
  const lerp = (a, b, t) => Math.round(a + (b - a) * Math.max(0, Math.min(1, t)));
  const [c0, c1, c2] = [[77, 124, 255], [232, 212, 77], [255, 79, 79]];
  const [a, b, t] = g <= 1 ? [c0, c1, g] : [c1, c2, (g - 1) / 2];
  return `rgb(${lerp(a[0], b[0], t)},${lerp(a[1], b[1], t)},${lerp(a[2], b[2], t)})`;
}
async function drawTree() {
  const d = await api("/api/lineage", {what: "Loading the family tree"});
  if (!d) return;
  const cv = $("treeCv"); const {x, w, h} = fit(cv);
  x.clearRect(0, 0, w, h);
  if (!d.evolve || !d.records.length) {
    x.fillStyle = "#8a93a6"; x.font = "13px sans-serif";
    x.fillText("Pick Evolving population in Set up a world, create the world, then press Play.", 16, 28);
    $("treeStats").textContent = ""; return;
  }
  const recs = d.records, byId = {}, kids = {};
  for (const r of recs) { byId[r.id] = r; kids[r.id] = []; }
  const roots = [];
  for (const r of recs) (r.parent !== null && byId[r.parent] ? kids[r.parent] : roots).push(r);
  const order = [];
  const visit = (r) => { order.push(r); kids[r.id].sort((a, b) => a.born - b.born).forEach(visit); };
  roots.sort((a, b) => a.id - b.id).forEach(visit);
  const alive = new Set(d.alive), T = Math.max(1, d.t);
  const L = 40, R = 12, top = 8, bot = 22;
  const rowH = (h - top - bot) / Math.max(1, order.length);
  const X = (t) => L + (w - L - R) * t / T, Y = (i) => top + (i + 0.5) * rowH;
  const row = {}; order.forEach((r, i) => row[r.id] = i);
  x.strokeStyle = "#232a36"; x.fillStyle = "#8a93a6"; x.font = "10px sans-serif";
  for (let k = 0; k <= 4; k++) { const t = Math.round(T * k / 4);
    x.beginPath(); x.moveTo(X(t), top); x.lineTo(X(t), h - bot); x.stroke();
    x.fillText("t=" + t, X(t) - 10, h - 6); }
  const lw = Math.max(0.6, Math.min(3, rowH * 0.7));
  for (const r of order) {                     // connectors first
    if (r.parent === null || row[r.parent] === undefined) continue;
    x.strokeStyle = "rgba(138,147,166,0.35)"; x.lineWidth = 0.6;
    x.beginPath(); x.moveTo(X(r.born), Y(row[r.parent])); x.lineTo(X(r.born), Y(row[r.id])); x.stroke();
  }
  for (const r of order) {
    const end = r.died === null ? T : r.died;
    x.strokeStyle = geneColor(r.aggr_gain); x.lineWidth = lw;
    x.beginPath(); x.moveTo(X(r.born), Y(row[r.id])); x.lineTo(X(Math.max(end, r.born + 1)), Y(row[r.id])); x.stroke();
    if (alive.has(r.id)) { x.fillStyle = "#ffffff";
      x.beginPath(); x.arc(X(T), Y(row[r.id]), Math.max(1.5, lw), 0, 7); x.fill(); }
  }
  TREE.rows = order; TREE.geom = {top, rowH};
  const liveRecs = recs.filter(r => alive.has(r.id));
  const lineages = new Set(liveRecs.map(r => r.lineage));
  const maxGen = Math.max(...recs.map(r => r.generation));
  const meanGene = liveRecs.length ? liveRecs.reduce((s, r) => s + r.aggr_gain, 0) / liveRecs.length : 0;
  $("treeStats").textContent = `· ${recs.length} individuals ever lived · ${liveRecs.length} alive · ` +
    `${lineages.size} founder lineage(s) surviving · max generation ${maxGen} · mean aggression gene ${meanGene.toFixed(2)}`;
}
function openTree() {
  $("treeDlg").showModal(); drawTree();
  TREE.timer = setInterval(() => { if (S.playing) drawTree(); }, 1500);
}
function closeTree() { clearInterval(TREE.timer); TREE.timer = null; $("treeDlg").close(); }

function openHelp() { $("helpDlg").showModal(); }
const isTyping = (t) => t.closest("input, select, textarea, [contenteditable=true], dialog");
// Space already activates a focused button or summary; handling it too would toggle twice.
const ownsSpace = (t) => t.closest("button, summary, a");

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
  $("btnDay1").onclick = () => advanceDays(1);
  $("btnDay3").onclick = () => advanceDays(3);
  $("btnTree").onclick = openTree;
  $("treeClose").onclick = closeTree;
  $("btnHelp").onclick = openHelp;
  $("helpClose").onclick = () => $("helpDlg").close();
  $("hintClose").onclick = dismissHint;
  $("treeDlg").addEventListener("close", () => { clearInterval(TREE.timer); TREE.timer = null; });
  $("treeCv").addEventListener("mousemove", (ev) => {
    if (!TREE.geom || !TREE.rows.length) return;
    const r = $("treeCv").getBoundingClientRect();
    const i = Math.floor((ev.clientY - r.top - TREE.geom.top) / TREE.geom.rowH);
    const rec = TREE.rows[i]; if (!rec) return;
    $("treeHover").textContent = `P${rec.id + 1} · generation ${rec.generation} · family line L${rec.lineage} · ` +
      `born t=${rec.born}${rec.died !== null ? " · died t=" + rec.died : " · alive"} · aggression gene ${rec.aggr_gain}`;
  });
  $("world").addEventListener("click", placeFoodAt);
  $("speed").oninput = (e) => { S.speed = +e.target.value; };
  $("learnTgl").onchange = (e) => { S.learning = e.target.checked; };

  const setup = $("setup");
  setup.addEventListener("input", (e) => {
    const t = e.target;
    if (t.name === "scenario") { chooseScenario(t.value); return; }
    const c = CONTROLS.find(c => elOf(c) === t);
    if (c && c.kind === "range") $("v_" + c.key).textContent = (+t.value).toFixed(c.dp);
    refreshSetup();
  });
  setup.addEventListener("click", (e) => {
    const b = e.target.closest("button.help"); if (!b) return;
    const open = b.getAttribute("aria-expanded") !== "true";
    b.setAttribute("aria-expanded", String(open));
    $(b.getAttribute("aria-controls")).hidden = !open;
  });

  document.addEventListener("keydown", (e) => {
    if (e.altKey || e.ctrlKey || e.metaKey || isTyping(e.target)) return;
    if (e.key === " ") { if (ownsSpace(e.target)) return; e.preventDefault(); togglePlay(); }
    else if (e.key === "ArrowRight") { e.preventDefault(); stepOnce(); }
  });

  // drag to rotate brain
  const b = $("brain"); let drag = false, lx = 0, ly = 0;
  b.addEventListener("pointerdown", e => { drag = true; lx = e.clientX; ly = e.clientY; b.setPointerCapture(e.pointerId); });
  b.addEventListener("pointermove", e => { if (!drag) return;
    S.yaw += (e.clientX - lx) * 0.01; S.pitch = Math.max(-1.4, Math.min(1.4, S.pitch + (e.clientY - ly) * 0.01));
    lx = e.clientX; ly = e.clientY; });
  b.addEventListener("pointerup", () => drag = false);
}

(async function init() {
  buildInspector();
  buildScenarios();
  renderTimeline();
  $("hint").hidden = storageGet(HINT_KEY) === "1";
  wire();
  const d = await api("/api/session", {body: {}, what: "Creating the first world"});
  if (d) { S.session = d; S.defaults = d.config; applySession(d); }
  requestAnimationFrame(renderLoop);
})();
