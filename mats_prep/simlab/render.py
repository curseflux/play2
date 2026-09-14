"""Writes a self-contained HTML replay of a recorded episode."""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List

_TEMPLATE = """<!doctype html>
<meta charset="utf-8"><title>__TITLE__</title>
<style>
 :root{color-scheme:dark}
 body{margin:0;background:#0f1216;color:#d7dde5;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
 header{padding:10px 14px;border-bottom:1px solid #222a33;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
 h1{font-size:14px;margin:0;font-weight:600;color:#8fd4ff}
 button{background:#1b232c;color:#d7dde5;border:1px solid #2c3742;border-radius:5px;padding:4px 11px;cursor:pointer;font:inherit}
 button:hover{background:#25303b}
 input[type=range]{width:min(420px,45vw);vertical-align:middle}
 #wrap{display:flex;gap:14px;padding:14px;flex-wrap:wrap}
 canvas{background:#12171d;border:1px solid #222a33;border-radius:6px;max-width:100%}
 #hud{min-width:230px;white-space:pre;color:#9fb3c8}
 .k{color:#5f7c96}
 b{color:#ffd479}
</style>
<header>
 <h1>__TITLE__</h1>
 <button id=play>play</button><button id=step>step</button><button id=back>back</button>
 <input id=scrub type=range min=0 value=0><span id=tlabel></span>
 <span class=k>speed</span><input id=spd type=range min=1 max=8 value=3 style="width:90px">
</header>
<div id=wrap><canvas id=cv width=880 height=520></canvas><div id=hud></div></div>
<script>
const DATA = __DATA__;
const S = DATA.static, F = DATA.frames;
const cv = document.getElementById('cv'), g = cv.getContext('2d');
const scrub = document.getElementById('scrub'), hud = document.getElementById('hud');
const tlabel = document.getElementById('tlabel'), spd = document.getElementById('spd');
let i = 0, playing = false;
scrub.max = F.length - 1;

function ring(x, y, r, fill, stroke){
  g.beginPath(); g.arc(x, y, r, 0, 6.2832);
  if(fill){ g.fillStyle = fill; g.fill(); }
  if(stroke){ g.strokeStyle = stroke; g.lineWidth = 1.5; g.stroke(); }
}

function drawLander(f){
  const half = S.arena_half, top = Math.max(S.ceiling * 0.55, S.y0 * 1.25);
  const sx = cv.width / (2 * half), sy = (cv.height - 40) / top;
  const X = x => cv.width / 2 + x * sx, Y = y => cv.height - 30 - y * sy;
  g.strokeStyle = '#2a3440'; g.fillStyle = '#1a2129';
  g.fillRect(0, Y(0), cv.width, 30);
  g.strokeStyle = '#3d4b59'; g.beginPath(); g.moveTo(0, Y(0)); g.lineTo(cv.width, Y(0)); g.stroke();
  g.fillStyle = '#4ea3ff';
  g.fillRect(X(-S.pad_half_width), Y(0) - 3, (2 * S.pad_half_width) * sx, 5);
  g.strokeStyle = '#243040'; g.beginPath(); g.moveTo(X(0), 0); g.lineTo(X(0), Y(0)); g.stroke();
  // past trajectory
  g.strokeStyle = '#33506b'; g.lineWidth = 1; g.beginPath();
  for(let k = 0; k <= i; k++){ const p = F[k]; k ? g.lineTo(X(p.x), Y(p.y)) : g.moveTo(X(p.x), Y(p.y)); }
  g.stroke();
  const px = X(f.x), py = Y(f.y);
  if(f.action === 'up'){ g.fillStyle = '#ff9d3c'; g.beginPath();
    g.moveTo(px - 5, py + 6); g.lineTo(px + 5, py + 6); g.lineTo(px, py + 22); g.closePath(); g.fill(); }
  if(f.action === 'left'){ g.fillStyle = '#ff9d3c'; g.fillRect(px + 6, py - 2, 13, 4); }
  if(f.action === 'right'){ g.fillStyle = '#ff9d3c'; g.fillRect(px - 19, py - 2, 13, 4); }
  ring(px, py, 7, '#e8eef5', '#9fb3c8');
  g.strokeStyle = '#7fe08a'; g.lineWidth = 2; g.beginPath();
  g.moveTo(px, py); g.lineTo(px + f.vx * 3, py - f.vy * 3); g.stroke();
}

function drawCourier(f){
  const pad = 16, sc = Math.min((cv.width - 2 * pad) / S.w, (cv.height - 2 * pad) / S.h);
  const X = x => pad + x * sc, Y = y => cv.height - pad - y * sc;
  g.strokeStyle = '#2c3742'; g.lineWidth = 1;
  g.strokeRect(X(0), Y(S.h), S.w * sc, S.h * sc);
  S.parcels.forEach((p, k) => {
    const st = f.states[k];
    if(st === 'delivered') return;
    if(st === 'waiting'){
      g.fillStyle = '#4ea3ff'; g.fillRect(X(p[0]) - 4, Y(p[1]) - 4, 8, 8);
      g.strokeStyle = '#26415c'; g.setLineDash([3, 3]); g.beginPath();
      g.moveTo(X(p[0]), Y(p[1])); g.lineTo(X(p[2]), Y(p[3])); g.stroke(); g.setLineDash([]);
    } else {
      g.strokeStyle = '#ffd479'; g.setLineDash([4, 3]); g.beginPath();
      g.moveTo(X(f.x), Y(f.y)); g.lineTo(X(p[2]), Y(p[3])); g.stroke(); g.setLineDash([]);
    }
    g.fillStyle = st === 'carried' ? '#ffd479' : '#2f6d4f';
    g.beginPath(); g.moveTo(X(p[2]), Y(p[3]) - 6); g.lineTo(X(p[2]) + 6, Y(p[3]) + 5);
    g.lineTo(X(p[2]) - 6, Y(p[3]) + 5); g.closePath(); g.fill();
  });
  f.hazards.forEach(h => ring(X(h[0]), Y(h[1]), h[2] * sc, '#43202a', '#c4506a'));
  g.strokeStyle = '#33506b'; g.lineWidth = 1; g.beginPath();
  for(let k = Math.max(0, i - 160); k <= i; k++){ const p = F[k];
    k === Math.max(0, i - 160) ? g.moveTo(X(p.x), Y(p.y)) : g.lineTo(X(p.x), Y(p.y)); }
  g.stroke();
  ring(X(f.x), Y(f.y), Math.max(4, S.agent_radius * sc),
       f.stun > 0 ? '#c4506a' : (f.carrying !== null ? '#ffd479' : '#e8eef5'), '#9fb3c8');
  g.strokeStyle = '#7fe08a'; g.lineWidth = 2; g.beginPath();
  g.moveTo(X(f.x), Y(f.y)); g.lineTo(X(f.x) + f.vx * sc * 0.5, Y(f.y) - f.vy * sc * 0.5); g.stroke();
}

function draw(){
  const f = F[i];
  g.clearRect(0, 0, cv.width, cv.height);
  (S.env === 'lander' ? drawLander : drawCourier)(f);
  let t = `frame  ${String(f.t).padStart(5)}\\naction ${String(f.action)}\\n\\n`;
  for(const k of Object.keys(f)){
    if(['t','action','debug','states','hazards'].includes(k)) continue;
    const v = f[k];
    t += k.padEnd(9) + (typeof v === 'number' ? v.toFixed(2).padStart(9) : String(v)) + '\\n';
  }
  if(f.debug){ t += '\\n-- DEBUG --\\n';
    for(const k of Object.keys(f.debug)){ const v = f.debug[k];
      t += k.padEnd(9) + (typeof v === 'number' ? v.toFixed(3).padStart(9) : String(v)) + '\\n'; } }
  hud.textContent = t;
  tlabel.textContent = `${i} / ${F.length - 1}`;
  scrub.value = i;
}
document.getElementById('play').onclick = e => { playing = !playing; e.target.textContent = playing ? 'pause' : 'play'; };
document.getElementById('step').onclick = () => { i = Math.min(F.length - 1, i + 1); draw(); };
document.getElementById('back').onclick = () => { i = Math.max(0, i - 1); draw(); };
scrub.oninput = () => { i = +scrub.value; draw(); };
document.onkeydown = e => {
  if(e.key === ' '){ playing = !playing; e.preventDefault(); }
  if(e.key === 'ArrowRight'){ i = Math.min(F.length - 1, i + 1); draw(); }
  if(e.key === 'ArrowLeft'){ i = Math.max(0, i - 1); draw(); }
};
let acc = 0;
setInterval(() => {
  if(!playing) return;
  acc += +spd.value;
  while(acc >= 4){ acc -= 4; i++; }
  if(i >= F.length){ i = F.length - 1; playing = false;
    document.getElementById('play').textContent = 'play'; }
  draw();
}, 33);
draw();
</script>
"""


def write_html(path: pathlib.Path, title: str, static: Dict[str, Any],
               frames: List[dict]) -> pathlib.Path:
    payload = json.dumps({"static": static, "frames": frames}, separators=(",", ":"))
    html = _TEMPLATE.replace("__TITLE__", title).replace("__DATA__", payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path
