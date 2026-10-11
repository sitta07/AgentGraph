"""Render a :class:`~neuralmind.recorder.Recording` to a self-contained HTML viewer.

The viewer is a single HTML file with the recording embedded as JSON and a
vanilla-JS/canvas renderer — no external libraries and no network calls, so it
works fully offline. When the recording includes a 3-D layout (see
``recorder.record(..., layout=True)``) it shows a rotatable "brain" network of
neurons that glow with recorded spike activity, plus a connectivity-matrix
heatmap, in the style of digital-twin-brain comparison tools. Otherwise it falls
back to rate traces. Every value displayed is read from the recording, i.e.
actual simulation state.
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
  :root{ --bg:#0b0d12; --panel:#12151c; --ink:#e8ecf3; --muted:#8a93a6;
    --grid:#232a36; --accent:#6d9bff; }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}
  .wrap{max-width:1100px;margin:0 auto;padding:22px 16px}
  h1{font-size:19px;margin:0 0 4px} .sub{color:var(--muted);margin:0 0 16px;font-size:13px}
  .panel{background:var(--panel);border:1px solid var(--grid);border-radius:14px;
    padding:14px;margin-bottom:14px}
  .controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
  button{background:var(--accent);color:#fff;border:0;border-radius:9px;
    padding:8px 14px;font-size:14px;cursor:pointer}
  button.ghost{background:transparent;color:var(--ink);border:1px solid var(--grid)}
  button.ghost.on{border-color:var(--accent);color:var(--accent)}
  input[type=range]{flex:1;min-width:150px;accent-color:var(--accent)}
  canvas{display:block;width:100%;border-radius:10px;touch-action:none}
  #net3d{height:440px} #matrix{height:300px}
  .lbl{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em;margin:0 0 8px}
  .row{display:flex;gap:14px;flex-wrap:wrap}
  .col-net{flex:2;min-width:320px} .col-mx{flex:1;min-width:260px}
  .readout{display:flex;gap:16px;flex-wrap:wrap;font-variant-numeric:tabular-nums;margin-top:10px}
  .readout b{color:var(--muted);font-weight:500}
  .legend{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:12px;margin-top:8px}
  .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:middle}
  .clock{color:var(--muted);font-size:13px;margin-left:auto}
</style>
</head>
<body>
<div class="wrap">
  <h1>__TITLE__</h1>
  <p class="sub">__SUBTITLE__</p>

  <div class="panel">
    <div class="controls">
      <button id="play">&#9654; Play</button>
      <button class="ghost" id="step">Step</button>
      <button class="ghost" id="reset">Reset</button>
      <button class="ghost on" id="rot">Auto-rotate</button>
      <button class="ghost on" id="edgeBtn">Edges</button>
      <span class="clock" id="clock"></span>
    </div>
    <input type="range" id="scrub" min="0" value="0">
    <div class="row" style="margin-top:12px">
      <div class="col-net">
        <p class="lbl">Neural network &mdash; drag to rotate (nodes glow with spikes)</p>
        <canvas id="net3d" height="440"></canvas>
        <div class="legend" id="legend"></div>
      </div>
      <div class="col-mx">
        <p class="lbl">Connectivity matrix (post &times; pre)</p>
        <canvas id="matrix" height="300"></canvas>
        <div class="legend">
          <span><span class="dot" style="background:#6d9bff"></span>excitatory (+)</span>
          <span><span class="dot" style="background:#e0734f"></span>inhibitory (&minus;)</span>
        </div>
      </div>
    </div>
    <div class="readout" id="readout"></div>
  </div>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const REC = JSON.parse(document.getElementById('data').textContent);
const N = REC.n_steps||0, nodes = REC.nodes||[], edges = REC.edges||[], M = REC.matrix||[];
const pops = REC.populations||[];
const PAL = {};
const palette = ['#6d9bff','#bf91f3','#49d6a6','#e0a63b','#e0734f','#3bc4e0'];
pops.forEach((p,i)=>PAL[p]=palette[i%palette.length]);
let cur=0, playing=false, showEdges=true, autoRot=true;
let yaw=0.5, pitch=-0.35, dragging=false, lastX=0, lastY=0, timer=null;

function fit(cv){const r=cv.getBoundingClientRect(),d=window.devicePixelRatio||1;
  const pw=Math.max(1,Math.round(r.width*d)), ph=Math.max(1,Math.round(r.height*d));
  if(cv.width!==pw) cv.width=pw; if(cv.height!==ph) cv.height=ph;
  const x=cv.getContext('2d'); x.setTransform(d,0,0,d,0,0); return {x,w:r.width,h:r.height};}

function project(n,w,h){
  const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
  let x=n.x*cy - n.z*sy, z=n.x*sy + n.z*cy, y=n.y;
  const y2=y*cp - z*sp, z2=y*sp + z*cp;
  const fov=3.0, s=fov/(fov+z2);
  const R=Math.min(w,h)*0.46;
  return {sx:w/2 + x*s*R, sy:h/2 + y2*s*R, s, depth:z2};
}

function drawNet(){
  const cv=document.getElementById('net3d'); const {x,w,h}=fit(cv);
  x.clearRect(0,0,w,h);
  if(!nodes.length){x.fillStyle='#8a93a6';x.font='13px sans-serif';
    x.fillText('No 3-D layout in this recording.',16,28);return;}
  const P=nodes.map(n=>project(n,w,h));
  const act=(REC.activity&&REC.activity[cur])||[];
  if(showEdges){
    for(const e of edges){
      const a=P[e.s],b=P[e.t]; if(!a||!b)continue;
      const glow=Math.max(act[e.s]||0,act[e.t]||0);
      const inh=e.w<0;
      x.strokeStyle = inh ? 'rgba(224,115,79,' : 'rgba(120,150,210,';
      x.globalAlpha=1; x.lineWidth=0.6+glow*1.6;
      x.beginPath();
      x.strokeStyle += (0.05 + 0.28*glow + 0.12*Math.min(1,Math.abs(e.w))) + ')';
      x.moveTo(a.sx,a.sy); x.lineTo(b.sx,b.sy); x.stroke();
    }
  }
  const order=P.map((p,i)=>i).sort((i,j)=>P[i].depth-P[j].depth);
  for(const i of order){
    const p=P[i], n=nodes[i], g=act[i]||0, col=PAL[n.p]||'#6d9bff';
    const rad=(2.2 + 4.8*g)*p.s + 1;
    if(g>0.15){ x.globalAlpha=0.25*g; x.fillStyle=col;
      x.beginPath(); x.arc(p.sx,p.sy,rad*2.4,0,7); x.fill(); }
    x.globalAlpha=0.45+0.55*g; x.fillStyle=col;
    x.beginPath(); x.arc(p.sx,p.sy,rad,0,7); x.fill();
  }
  x.globalAlpha=1;
}

function heat(v,maxAbs){
  const t=Math.min(1,Math.abs(v)/(maxAbs||1));
  const d=[14,20,30];                       // dark base
  const c = v>=0 ? [77,155,255] : [224,115,79];  // blue (+) / orange (-)
  const mix=k=>Math.round(d[k]+(c[k]-d[k])*t);
  return `rgb(${mix(0)},${mix(1)},${mix(2)})`;
}

function drawMatrix(){
  const cv=document.getElementById('matrix'); const {x,w,h}=fit(cv);
  x.clearRect(0,0,w,h); const n=M.length; if(!n)return;
  const side=Math.min(w,h), ox=(w-side)/2, oy=(h-side)/2, c=side/n;
  let maxAbs=0; for(const row of M)for(const v of row)maxAbs=Math.max(maxAbs,Math.abs(v));
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){
    const v=M[i][j]; if(v===0)continue;
    x.fillStyle=heat(v,maxAbs); x.fillRect(ox+j*c, oy+i*c, Math.ceil(c), Math.ceil(c));
  }
  // population separators
  x.strokeStyle='rgba(138,147,166,.35)'; x.lineWidth=1; let off=0;
  for(const p of pops){ off+=REC.sizes[p];
    x.beginPath(); x.moveTo(ox+off*c,oy); x.lineTo(ox+off*c,oy+side); x.stroke();
    x.beginPath(); x.moveTo(ox,oy+off*c); x.lineTo(ox+side,oy+off*c); x.stroke(); }
  x.strokeStyle='rgba(138,147,166,.25)'; x.strokeRect(ox,oy,side,side);
}

function readouts(){
  document.getElementById('clock').textContent =
    N?`step ${cur+1}/${N} · t = ${(cur*REC.dt).toFixed(1)} ms`:'';
  const r=document.getElementById('readout'); r.innerHTML='';
  pops.forEach(p=>{ const v=(REC.rate[p]||[])[cur]??0;
    r.innerHTML+=`<span><span class="dot" style="background:${PAL[p]}"></span>`
      +`<b>${p}</b> ${v.toFixed(1)} Hz</span>`; });
  for(const k of Object.keys(REC.series||{})){ const v=REC.series[k][cur]??0;
    r.innerHTML+=`<span><b>${k}</b> ${v.toFixed(3)}</span>`; }
}

function legend(){
  const l=document.getElementById('legend'); l.innerHTML='';
  pops.forEach(p=>{ l.innerHTML+=`<span><span class="dot" style="background:${PAL[p]}"></span>${p} (${REC.sizes[p]})</span>`; });
}

function frame(){
  if(autoRot && !dragging) yaw+=0.004;
  drawNet();
  requestAnimationFrame(frame);
}
function setStep(i){ cur=Math.max(0,Math.min(N-1,i));
  document.getElementById('scrub').value=cur; readouts(); }
function play(){ playing=!playing;
  document.getElementById('play').innerHTML=playing?'&#10074;&#10074; Pause':'&#9654; Play';
  if(playing) timer=setInterval(()=>{ setStep(cur>=N-1?0:cur+1); },55);
  else clearInterval(timer); }

const net=document.getElementById('net3d');
net.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;lastY=e.clientY;net.setPointerCapture(e.pointerId);});
net.addEventListener('pointermove',e=>{ if(!dragging)return;
  yaw+=(e.clientX-lastX)*0.01; pitch+=(e.clientY-lastY)*0.01;
  pitch=Math.max(-1.4,Math.min(1.4,pitch)); lastX=e.clientX; lastY=e.clientY; });
net.addEventListener('pointerup',()=>dragging=false);
document.getElementById('play').onclick=play;
document.getElementById('step').onclick=()=>setStep(cur+1);
document.getElementById('reset').onclick=()=>{ if(playing)play(); setStep(0); };
document.getElementById('rot').onclick=e=>{autoRot=!autoRot;e.target.classList.toggle('on',autoRot);};
document.getElementById('edgeBtn').onclick=e=>{showEdges=!showEdges;e.target.classList.toggle('on',showEdges);};
const scrub=document.getElementById('scrub'); scrub.max=Math.max(0,N-1);
scrub.oninput=e=>setStep(+e.target.value);
window.addEventListener('resize',()=>{drawMatrix();});
legend(); drawMatrix(); setStep(0); frame();
</script>
</body>
</html>
"""


def render_html(recording: Recording, path: str | Path,
                title: str = "NeuralMind — brain viewer",
                subtitle: str | None = None) -> Path:
    """Write a self-contained HTML viewer for ``recording`` and return its path."""
    data = json.dumps(recording.to_json_dict(), separators=(",", ":"))
    sub = subtitle or (
        f"{len(recording.populations)} populations · "
        f"{len(recording.nodes)} neurons · {len(recording.edges)} synapses · "
        f"{recording.n_steps} steps · all values are recorded simulation state"
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
