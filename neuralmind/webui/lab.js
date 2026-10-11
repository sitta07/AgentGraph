"use strict";
// Discovery Lab: renders committed studies and launches replications.
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const dlg = $("dlg");

function badge(key, val) {
  const label = key.replace(/^H(\d+)_?/, "H$1 ").replace(/_/g, " ");
  if (typeof val === "boolean") {
    const nullKey = /null_retained/.test(key);
    const txt = nullKey ? (val ? "null retained" : "null rejected") : (val ? "supported" : "not supported");
    return `<span class="badge ${val ? "yes" : "no"}" title="${esc(key)}">${esc(label.replace(/ (supported|null retained)$/, ""))}: ${txt}</span>`;
  }
  return `<span class="badge val" title="${esc(key)}">${esc(label)}: ${typeof val === "number" ? val.toFixed(3) : esc(val)}</span>`;
}

function fmt(v) {
  const a = Math.abs(v);
  return a !== 0 && (a < 0.01 || a >= 1000) ? v.toExponential(2) : v.toFixed(a < 1 ? 4 : 2);
}

function ciBar(ci) {
  const m = Math.max(Math.abs(ci.lo), Math.abs(ci.hi), 1e-12) * 1.1;
  const X = (v) => 50 + 50 * v / m;
  const cls = ci.lo > 0 ? "pos" : ci.hi < 0 ? "neg" : "";
  return `<div><div class="ci ${cls}"><div class="zero"></div>
      <div class="bar" style="left:${X(ci.lo)}%;width:${Math.max(0.5, X(ci.hi) - X(ci.lo))}%"></div>
      <div class="dot" style="left:${X(ci.mean)}%"></div></div>
    <div class="num">${fmt(ci.mean)} [${fmt(ci.lo)}, ${fmt(ci.hi)}]${ci.n ? ` · n=${ci.n}` : ""}</div></div>`;
}

function card(s) {
  const tests = Object.entries(s.tests).map(([k, ci]) =>
    `<div class="test"><div class="name">${esc(k.replace(/_/g, " "))}</div>${ciBar(ci)}</div>`).join("");
  const charts = (s.charts || []).map(c =>
    `<img src="/results/${encodeURIComponent(s.folder)}/${encodeURIComponent(c)}" alt="${esc(c)}"
       onclick="window.open(this.src,'_blank')">`).join("");
  const seeds = s.design && s.design.seeds ? `${s.design.seeds} seeds` : "";
  const ticks = s.design && s.design.ticks ? ` · ${s.design.ticks} ticks` : "";
  return `<div class="panel card">
    <h3>${esc(s.title)}</h3>
    <div class="meta">${esc(s.folder)} · ${seeds}${ticks} · updated ${esc(s.modified)}</div>
    <div class="badges">${Object.entries(s.verdict).map(([k, v]) => badge(k, v)).join("")}</div>
    ${tests || '<div class="note">No test statistics recorded.</div>'}
    ${charts ? `<div class="charts">${charts}</div>` : ""}
    ${s.has_report ? `<div class="row" style="margin-top:12px">
      <button class="ghost" onclick="openReport('${esc(s.folder)}')">Full report</button>
      <a class="note" href="https://github.com/sitta07/AgentGraph/tree/main/results/${encodeURIComponent(s.folder)}" target="_blank">raw data on GitHub ↗</a></div>` : ""}
  </div>`;
}

// Minimal Markdown for our auto-generated reports: headings, lists, tables, images, code, bold.
function md(src, folder) {
  const inline = (t) => esc(t)
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, a, u) =>
      `<img alt="${a}" src="${/^https?:/.test(u) ? u : `/results/${encodeURIComponent(folder)}/${u}`}">`)
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
  const r = await fetch(`/api/lab/report/${encodeURIComponent(folder)}`);
  if (!r.ok) return;
  $("dlgTitle").textContent = folder;
  $("dlgBody").innerHTML = md((await r.json()).markdown, folder);
  dlg.showModal();
}
window.openReport = openReport;

async function loadStudies() {
  const d = await (await fetch("/api/lab/studies")).json();
  $("studies").innerHTML = d.studies.length ? d.studies.map(card).join("")
    : '<div class="empty">No studies yet — run one above.</div>';
}

let polling = null;
async function loadJobs() {
  const d = await (await fetch("/api/lab/jobs")).json();
  if (!$("kind").options.length)
    $("kind").innerHTML = Object.entries(d.kinds).map(([k, t]) => `<option value="${k}">${esc(t)}</option>`).join("");
  const running = d.jobs.some(j => j.status === "running");
  $("runBtn").disabled = running;
  $("jobs").innerHTML = d.jobs.slice().reverse().map(j => `<div class="job">
    <span class="dotst ${j.status}"></span><b>${esc(j.title)}</b>
    <span class="note">${j.seeds} seeds · ${j.ticks} ticks · started ${j.started}${j.finished ? " · finished " + j.finished : ""}</span>
    <span class="note">${j.status === "error" ? "error: " + esc((j.error || "").split("\n").slice(-2).join(" ")) : j.status}</span></div>`).join("");
  if (!running && polling) { clearInterval(polling); polling = null; loadStudies(); }
  if (running && !polling) polling = setInterval(loadJobs, 3000);
}

$("runBtn").onclick = async () => {
  const body = {kind: $("kind").value, seeds: +$("seeds").value, ticks: +$("ticks").value};
  const r = await fetch("/api/lab/run", {method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)});
  if (!r.ok) { alert((await r.json()).detail || "could not start"); return; }
  loadJobs();
};

loadStudies(); loadJobs();
