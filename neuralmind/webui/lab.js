"use strict";
// Discovery Lab: renders committed studies and launches replications.
const dlg = $("dlg");
const TESTS_SHOWN = 4;
const L = {studies: [], filter: "all", query: "", expanded: new Set(), polling: null};

// A verdict value is "supported", "not" or null (a non-hypothesis value such as
// "difference detected", a number, or a null-retained flag whose sense is inverted).
function outcome(key, val) {
  if (typeof val === "boolean") return /null_retained/.test(key) ? null : (val ? "supported" : "not");
  if (val === "supported") return "supported";
  if (val === "not supported") return "not";
  return null;
}
function summarise(s) {
  const out = Object.entries(s.verdict).map(([k, v]) => outcome(k, v));
  return {
    supported: out.filter(o => o === "supported").length,
    not: out.filter(o => o === "not").length,
    prereg: !!(s.preregistration && s.preregistration.preregistered),
    text: `${s.title} ${s.question || ""}`.toLowerCase(),
  };
}
const FILTERS = [
  {id: "all", label: "All", test: () => true},
  {id: "some", label: "Some hypothesis supported", test: (m) => m.supported > 0},
  {id: "none", label: "None supported", test: (m) => m.supported === 0 && m.not > 0},
  {id: "noprereg", label: "Not pre-registered", test: (m) => !m.prereg},
];

function badge(key, val) {
  const label = key.replace(/^H(\d+)_?/, "H$1 ").replace(/_/g, " ");
  if (typeof val === "boolean") {
    const nullKey = /null_retained/.test(key);
    const txt = nullKey ? (val ? "null retained" : "null rejected") : (val ? "supported" : "not supported");
    return `<span class="badge ${val ? "yes" : "no"}" title="${esc(key)}">${esc(label.replace(/ (supported|null retained)$/, ""))}: ${txt}</span>`;
  }
  if (typeof val === "string") {
    const cls = val === "supported" ? "yes" : val === "not supported" ? "no" : "val";
    return `<span class="badge ${cls}" title="${esc(key)}">${esc(key)}: ${esc(val)}</span>`;
  }
  return `<span class="badge val" title="${esc(key)}">${esc(label)}: ${typeof val === "number" ? val.toFixed(3) : esc(val)}</span>`;
}

function fmt(v) {
  if (v == null) return "n/a";
  const a = Math.abs(v);
  return a !== 0 && (a < 0.01 || a >= 1000) ? v.toExponential(2) : v.toFixed(a < 1 ? 4 : 2);
}

function ciBar(ci) {
  if (ci.mean == null || ci.lo == null || ci.hi == null)
    return `<div class="num">no data</div>`;
  const m = Math.max(Math.abs(ci.lo), Math.abs(ci.hi), 1e-12) * 1.1;
  const X = (v) => 50 + 50 * v / m;
  const cls = ci.lo > 0 ? "pos" : ci.hi < 0 ? "neg" : "";
  const where = ci.lo > 0 ? "above zero" : ci.hi < 0 ? "below zero" : "crosses zero";
  return `<div><div class="ci ${cls}" role="img" aria-label="mean ${fmt(ci.mean)}, 95% interval ${fmt(ci.lo)} to ${fmt(ci.hi)}, ${where}">
      <div class="zero"></div>
      <div class="bar" style="left:${X(ci.lo)}%;width:${Math.max(0.5, X(ci.hi) - X(ci.lo))}%"></div>
      <div class="dot" style="left:${X(ci.mean)}%"></div></div>
    <div class="num">${fmt(ci.mean)} [${fmt(ci.lo)}, ${fmt(ci.hi)}]${ci.n ? ` · n=${ci.n}` : ""}</div></div>`;
}

function prereg(p, dev) {
  if (!p) return "";
  const link = p.commit ? `<a href="https://github.com/sitta07/NeuralMind/blob/${p.commit}/${p.spec_path}" target="_blank" rel="noopener">${p.commit.slice(0, 7)}</a>` : "none";
  const d = dev && Object.keys(dev).length ? ` · <span style="color:var(--warn)">deviations: ${esc(JSON.stringify(dev))}</span>` : "";
  return `<div class="note" style="margin-bottom:10px">${p.preregistered ? "🔒 pre-registered" : "⚠️ not pre-registered"} · spec ${link}${d}</div>`;
}

function card(s) {
  const entries = Object.entries(s.tests);
  const open = L.expanded.has(s.id);
  const rows = (open ? entries : entries.slice(0, TESTS_SHOWN)).map(([k, ci]) =>
    `<div class="test"><div class="name">${esc(k.replace(/_/g, " "))}</div>${ciBar(ci)}</div>`).join("");
  const more = entries.length > TESTS_SHOWN ? `<button class="ghost more" data-toggle="${esc(s.id)}"
      aria-expanded="${open}">${open ? "Show fewer" : `Show all ${entries.length} tests`}</button>` : "";
  const charts = (s.charts || []).map(c => {
    const src = `/results/${encodeURIComponent(s.folder)}/${encodeURIComponent(c)}`;
    return `<a href="${src}" target="_blank" rel="noopener" aria-label="Open chart ${esc(c)} in a new tab">
      <img src="${src}" alt="Chart: ${esc(c)}" loading="lazy" decoding="async"></a>`;
  }).join("");
  const seeds = s.design && s.design.seeds ? `${s.design.seeds} seeds` : "";
  const ticks = s.design && s.design.ticks ? ` · ${s.design.ticks} ticks` : "";
  return `<article class="panel card">
    <h3>${esc(s.title)}</h3>
    <div class="meta">${esc(s.folder)} · ${seeds}${ticks} · updated ${esc(s.modified)}</div>
    ${s.question ? `<p class="note" style="margin:-2px 0 10px;font-size:13px">${esc(s.question)}</p>` : ""}
    ${prereg(s.preregistration, s.deviations)}
    <div class="badges">${Object.entries(s.verdict).map(([k, v]) => badge(k, v)).join("")}</div>
    ${rows || '<div class="note">No test statistics recorded.</div>'}
    ${more}
    ${charts ? `<div class="charts">${charts}</div>` : ""}
    ${s.has_report ? `<div class="card-foot">
      <button class="ghost" data-report="${esc(s.folder)}" aria-label="Full report: ${esc(s.title)}">Full report</button>
      <a href="https://github.com/sitta07/NeuralMind/tree/main/results/${encodeURIComponent(s.folder)}" target="_blank" rel="noopener">Raw data on GitHub ↗</a></div>` : ""}
  </article>`;
}

function renderSummary() {
  const ms = L.studies.map(s => s.m);
  const tile = (n, label, cls = "") => `<div class="stat-tile ${cls}"><b>${n}</b><span>${label}</span></div>`;
  $("summary").innerHTML = tile(ms.length, "studies") +
    tile(sum(ms, "supported"), "hypotheses supported", "yes") +
    tile(sum(ms, "not"), "hypotheses not supported", "no") +
    tile(ms.filter(m => !m.prereg).length, "not pre-registered");
}
const sum = (arr, k) => arr.reduce((a, m) => a + m[k], 0);

function renderChips() {
  $("chips").innerHTML = FILTERS.map(f => {
    const n = L.studies.filter(s => f.test(s.m)).length;
    return `<button class="chip" data-filter="${f.id}" aria-pressed="${L.filter === f.id}">${esc(f.label)} (${n})</button>`;
  }).join("");
}

function renderStudies() {
  const f = FILTERS.find(f => f.id === L.filter);
  const q = L.query.trim().toLowerCase();
  const shown = L.studies.filter(s => f.test(s.m) && (!q || s.m.text.includes(q)));
  $("count").textContent = `Showing ${shown.length} of ${L.studies.length}`;
  $("studies").innerHTML = shown.length ? shown.map(card).join("")
    : `<div class="empty">${L.studies.length ? "No studies match. Clear the search or pick All." : "No studies yet. Run one below."}</div>`;
}

async function loadStudies() {
  const d = await api("/api/lab/studies", {what: "Loading studies"});
  if (!d) { $("studies").innerHTML = '<div class="empty">Could not load studies. Check that the server is running, then reload.</div>'; return; }
  L.studies = d.studies.map(s => Object.assign(s, {m: summarise(s)}));
  renderSummary(); renderChips(); renderStudies();
}

async function loadSpecs() {
  const d = await api("/api/lab/specs", {what: "Loading registered specs"});
  if (!d) return;
  $("specsSummary").textContent = `Registered study specs (${d.specs.length})`;
  $("specs").innerHTML = d.specs.map(s => s.error ? `<div class="note">${esc(s.file)}: ${esc(s.error)}</div>` : `
    <div class="spec">
      <span class="dotst ${s.has_results ? "done" : ""}" style="margin-top:6px" aria-hidden="true"></span>
      <div><b>${esc(s.title)}</b><br>
        <span class="note">${esc(s.question)}</span><br>
        <span class="note">${s.hypotheses.map(h => `<b>${esc(h.id)}</b> ${esc(h.statement)}`).join(" · ")}</span><br>
        <span class="note">${s.preregistration.preregistered ? "🔒 registered at " + esc(s.preregistration.commit.slice(0, 7)) : "⚠️ not committed yet"} · ${s.seeds} seeds · ${s.ticks} ticks · ${s.has_results ? "results available" : "not run yet"}</span></div>
      <button class="ghost" data-spec="${esc(s.id)}" data-seeds="${s.seeds}" data-ticks="${s.ticks}"
        aria-label="Run ${esc(s.title)} as registered">▶ Run as registered</button>
    </div>`).join("");
}

async function startRun(body) {
  $("runErr").textContent = "";
  const r = await api("/api/lab/run", {body, what: "Starting the run", quiet: true});
  if (!r) { $("runErr").textContent = api.lastError; return; }
  toast(`Started: ${r.title}`);
  loadJobs();
}

async function loadJobs() {
  const d = await api("/api/lab/jobs", {what: "Checking running jobs", quiet: !!L.polling});
  if (!d) return;
  if (!$("kind").options.length)
    $("kind").innerHTML = Object.entries(d.kinds).map(([k, t]) => `<option value="${k}">${esc(t)}</option>`).join("");
  const running = d.jobs.some(j => j.status === "running");
  $("runBtn").disabled = running;
  for (const b of document.querySelectorAll("[data-spec]")) b.disabled = running;
  $("jobs").innerHTML = d.jobs.slice().reverse().map(j => `<div class="job">
    <span class="dotst ${j.status}" aria-hidden="true"></span><b>${esc(j.title)}</b>
    <span class="note">${j.seeds} seeds · ${j.ticks} ticks · started ${j.started}${j.finished ? " · finished " + j.finished : ""}</span>
    <span class="note">${j.status === "error" ? "error: " + esc((j.error || "").split("\n").slice(-2).join(" ")) : j.status}</span></div>`).join("");
  if (!running && L.polling) { clearInterval(L.polling); L.polling = null; loadStudies(); loadSpecs(); }
  if (running && !L.polling) L.polling = setInterval(loadJobs, 3000);
}

function renderEstimate() {
  const seeds = +$("seeds").value || 0, ticks = +$("ticks").value || 0;
  const x = (seeds * ticks) / (3 * 1500);
  $("estimate").textContent = `Rough guide: 3 seeds × 1,500 ticks takes about 1–3 minutes. ` +
    `Time grows with seeds × ticks, so this run is about ${x < 10 ? x.toFixed(1) : Math.round(x)}× that.`;
}

// Minimal Markdown for our auto-generated reports: headings, lists, tables, images, code, bold.
function md(src, folder) {
  const inline = (t) => esc(t)
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, a, u) =>
      `<img alt="${a}" loading="lazy" src="${/^https?:/.test(u) ? u : `/results/${encodeURIComponent(folder)}/${u}`}">`)
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>");
  const lines = src.split("\n"); let out = "", i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (/^\|/.test(l)) {
      const rows = []; while (i < lines.length && /^\|/.test(lines[i])) rows.push(lines[i++]);
      out += "<table>" + rows.filter(r => !/^\|[\s|:-]+\|$/.test(r)).map((r, k) =>
        "<tr>" + r.replace(/\\\|/g, "\u0001").split("|").slice(1, -1).map(c =>
          `<${k ? "td" : "th"}>${inline(c.trim().replace(/\u0001/g, "|"))}</${k ? "td" : "th"}>`).join("") + "</tr>").join("") + "</table>";
      continue;
    }
    if (/^#{1,3} /.test(l)) { const n = l.match(/^#+/)[0].length; out += `<h${n + 1}>${inline(l.slice(n + 1))}</h${n + 1}>`; }
    else if (/^- /.test(l)) { out += "<ul>"; while (i < lines.length && /^- /.test(lines[i])) out += `<li>${inline(lines[i++].slice(2))}</li>`; out += "</ul>"; continue; }
    else if (l.trim()) out += `<p>${inline(l)}</p>`;
    i++;
  }
  return out;
}

async function openReport(folder) {
  const d = await api(`/api/lab/report/${encodeURIComponent(folder)}`, {what: "Opening the report"});
  if (!d) return;
  $("dlgTitle").textContent = folder;
  $("dlgBody").innerHTML = md(d.markdown, folder);
  dlg.showModal();
}

function wire() {
  $("legendBar").innerHTML = ciBar({mean: 0.5, lo: 0.2, hi: 0.8});
  $("search").addEventListener("input", (e) => { L.query = e.target.value; renderStudies(); });
  $("chips").addEventListener("click", (e) => {
    const b = e.target.closest("[data-filter]"); if (!b) return;
    L.filter = b.dataset.filter; renderChips(); renderStudies();
  });
  $("studies").addEventListener("click", (e) => {
    const t = e.target.closest("[data-toggle], [data-report]"); if (!t) return;
    if (t.dataset.report) { openReport(t.dataset.report); return; }
    const id = t.dataset.toggle;
    L.expanded.has(id) ? L.expanded.delete(id) : L.expanded.add(id);
    renderStudies();
    const again = [...document.querySelectorAll("[data-toggle]")].find(b => b.dataset.toggle === id);
    if (again) again.focus();
  });
  $("specs").addEventListener("click", (e) => {
    const b = e.target.closest("[data-spec]"); if (!b) return;
    startRun({kind: "spec", spec: b.dataset.spec, seeds: +b.dataset.seeds, ticks: +b.dataset.ticks});
  });
  $("runBtn").onclick = () => startRun({kind: $("kind").value, seeds: +$("seeds").value, ticks: +$("ticks").value});
  $("seeds").addEventListener("input", renderEstimate);
  $("ticks").addEventListener("input", renderEstimate);
  $("dlgClose").onclick = () => dlg.close();
  renderEstimate();
}

wire();
loadStudies(); loadJobs(); loadSpecs();
