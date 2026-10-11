"""Render a :class:`~neuralmind.recorder.Recording` to a self-contained HTML viewer.

The output is a single HTML file with the recording embedded as JSON and a small
vanilla-JS/canvas viewer (no external libraries, no network calls). It shows a
spike raster, population firing-rate traces, and any extra scalar series, with
play / pause / step / reset / timeline controls. Every value displayed is read
from the embedded recording, i.e. actual simulation state.
"""

from __future__ import annotations

import json
from pathlib import Path

from neuralmind.recorder import Recording

_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root {
    --bg:#f7f8fa; --panel:#ffffff; --ink:#1a1d24; --muted:#5b6472;
    --grid:#e3e7ee; --accent:#3b6fe0; --spike:#e0533b; --line:#2aa37a;
  }
  @media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
    --bg:#11141a; --panel:#1a1f29; --ink:#e8ecf3; --muted:#9aa4b2;
    --grid:#2a313d; --accent:#6d9bff; --spike:#ff7a5c; --line:#49d6a6; } }
  :root[data-theme="dark"]{ --bg:#11141a; --panel:#1a1f29; --ink:#e8ecf3;
    --muted:#9aa4b2; --grid:#2a313d; --accent:#6d9bff; --spike:#ff7a5c; --line:#49d6a6; }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
  .wrap{max-width:1000px;margin:0 auto;padding:24px 16px}
  h1{font-size:19px;margin:0 0 4px} .sub{color:var(--muted);margin:0 0 18px}
  .panel{background:var(--panel);border:1px solid var(--grid);border-radius:12px;
    padding:16px;margin-bottom:16px}
  .controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
  button{background:var(--accent);color:#fff;border:0;border-radius:8px;
    padding:8px 14px;font-size:14px;cursor:pointer}
  button.ghost{background:transparent;color:var(--ink);border:1px solid var(--grid)}
  input[type=range]{flex:1;min-width:160px;accent-color:var(--accent)}
  canvas{width:100%;display:block;border-radius:8px}
  .lbl{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em;margin:0 0 8px}
  .readout{display:flex;gap:18px;flex-wrap:wrap;font-variant-numeric:tabular-nums}
  .readout b{color:var(--muted);font-weight:500}
  .tag{display:inline-block;font-size:12px;color:var(--muted)}
</style>
</head>
<body>
<div class="wrap">
  <h1>__TITLE__</h1>
  <p class="sub">__SUBTITLE__</p>

  <div class="panel">
    <div class="controls">
      <button id="play">▶ Play</button>
      <button class="ghost" id="step">Step ▸</button>
      <button class="ghost" id="reset">⟲ Reset</button>
      <input type="range" id="scrub" min="0" value="0">
      <span class="tag" id="clock"></span>
    </div>
  </div>

  <div class="panel">
    <p class="lbl">Spike raster — neurons (y) vs time (x)</p>
    <canvas id="raster" height="260"></canvas>
  </div>

  <div class="panel">
    <p class="lbl">Population firing rate (Hz)</p>
    <canvas id="rates" height="160"></canvas>
    <div class="readout" id="rateRead"></div>
  </div>

  <div class="panel" id="seriesPanel" hidden>
    <p class="lbl">Model variables</p>
    <canvas id="series" height="160"></canvas>
    <div class="readout" id="seriesRead"></div>
  </div>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const REC = JSON.parse(document.getElementById('data').textContent);
const N = REC.n_steps, pops = REC.populations;
const palette = ['#3b6fe0','#e0533b','#2aa37a','#b05ce0','#e0a63b','#3bc4e0'];
let cur = 0, playing = false, timer = null;

function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
function fit(cv){const r=cv.getBoundingClientRect(),d=window.devicePixelRatio||1;
  cv.width=r.width*d; cv.height=cv.height*d; const x=cv.getContext('2d'); x.scale(d,d);
  return {x, w:r.width, h:cv.height/d};}

function drawRaster(){
  const cv=document.getElementById('raster'); const {x,w,h}=fit(cv);
  x.clearRect(0,0,w,h);
  const totalN = pops.reduce((a,p)=>a+REC.sizes[p],0);
  let yBase=0;
  const px = w / Math.max(1,N);
  pops.forEach((p,pi)=>{
    const sz=REC.sizes[p], col=palette[pi%palette.length];
    const rowH = (h-6) * sz/totalN;
    x.fillStyle=col;
    REC.spikes[p].forEach((idxs,t)=>{
      const xx = t*px;
      idxs.forEach(i=>{ const yy = yBase + (i/Math.max(1,sz))*rowH;
        x.fillRect(xx, yy, Math.max(1,px), Math.max(1.4, rowH/sz)); });
    });
    yBase += rowH + 6;
  });
  // playhead
  x.strokeStyle=css('--ink'); x.globalAlpha=.5; x.beginPath();
  x.moveTo(cur*px,0); x.lineTo(cur*px,h); x.stroke(); x.globalAlpha=1;
}

function drawLines(canvasId, seriesObj, keys){
  const cv=document.getElementById(canvasId); const {x,w,h}=fit(cv);
  x.clearRect(0,0,w,h);
  let lo=Infinity,hi=-Infinity;
  keys.forEach(k=>seriesObj[k].forEach(v=>{lo=Math.min(lo,v);hi=Math.max(hi,v);}));
  if(!isFinite(lo)){lo=0;hi=1;} if(hi===lo){hi=lo+1;}
  const px=w/Math.max(1,N-1||1);
  const Y=v=> h-6 - (v-lo)/(hi-lo)*(h-16);
  x.strokeStyle=css('--grid'); x.beginPath(); x.moveTo(0,Y(lo)); x.lineTo(w,Y(lo)); x.stroke();
  keys.forEach((k,ki)=>{
    x.strokeStyle=palette[ki%palette.length]; x.lineWidth=1.6; x.beginPath();
    seriesObj[k].forEach((v,t)=>{ const xx=t*px, yy=Y(v);
      t?x.lineTo(xx,yy):x.moveTo(xx,yy); }); x.stroke();
  });
  x.strokeStyle=css('--ink'); x.globalAlpha=.5; x.beginPath();
  x.moveTo(cur*px,0); x.lineTo(cur*px,h); x.stroke(); x.globalAlpha=1;
}

function readouts(){
  document.getElementById('clock').textContent =
    `step ${cur+1}/${N}  ·  t = ${(cur*REC.dt).toFixed(1)} ms`;
  const rr=document.getElementById('rateRead'); rr.innerHTML='';
  pops.forEach((p,pi)=>{ const v=REC.rate[p][cur]??0;
    rr.innerHTML+=`<span style="color:${palette[pi%palette.length]}">●</span> `
      +`<b>${p}</b> ${v.toFixed(1)} Hz&nbsp;&nbsp;`; });
  const skeys=Object.keys(REC.series);
  if(skeys.length){ const sr=document.getElementById('seriesRead'); sr.innerHTML='';
    skeys.forEach((k,ki)=>{ const v=REC.series[k][cur]??0;
      sr.innerHTML+=`<span style="color:${palette[ki%palette.length]}">●</span> `
        +`<b>${k}</b> ${v.toFixed(3)}&nbsp;&nbsp;`; }); }
}

function renderAll(){ drawRaster(); drawLines('rates',REC.rate,pops);
  const skeys=Object.keys(REC.series);
  if(skeys.length){ document.getElementById('seriesPanel').hidden=false;
    drawLines('series',REC.series,skeys);} readouts();
  document.getElementById('scrub').value=cur; }

function setStep(i){ cur=Math.max(0,Math.min(N-1,i)); renderAll(); }
function play(){ playing=!playing;
  document.getElementById('play').textContent=playing?'❚❚ Pause':'▶ Play';
  if(playing){ timer=setInterval(()=>{ if(cur>=N-1){setStep(0);} else setStep(cur+1);},60); }
  else clearInterval(timer); }

document.getElementById('play').onclick=play;
document.getElementById('step').onclick=()=>setStep(cur+1);
document.getElementById('reset').onclick=()=>{ if(playing)play(); setStep(0); };
document.getElementById('scrub').max=N-1;
document.getElementById('scrub').oninput=e=>setStep(+e.target.value);
window.addEventListener('resize',renderAll);
setStep(0);
</script>
</body>
</html>
"""


def render_html(recording: Recording, path: str | Path,
                title: str = "NeuralMind — simulation viewer",
                subtitle: str | None = None) -> Path:
    """Write a self-contained HTML viewer for ``recording`` and return its path."""
    data = json.dumps(recording.to_json_dict(), separators=(",", ":"))
    sub = subtitle or (
        f"{len(recording.populations)} populations · {recording.n_steps} steps · "
        f"dt = {recording.dt} ms · all values are recorded simulation state"
    )
    html = (
        _TEMPLATE
        .replace("__TITLE__", _escape(title))
        .replace("__SUBTITLE__", _escape(sub))
        .replace("__DATA__", data)
    )
    out = Path(path)
    out.write_text(html, encoding="utf-8")
    return out


def _escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
