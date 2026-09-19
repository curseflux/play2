"""Standalone browser replay with state, actions, and DEBUG values."""
import html
import json
import pathlib


def write_replay(path, course, result, frames):
    data = json.dumps(dict(course=course, result=result, frames=frames)).replace("<", "\\u003c")
    page = TEMPLATE.replace("__TITLE__", html.escape(course["name"])).replace("__DATA__", data)
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")


TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Skyparcel / __TITLE__</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#121b22;color:#e3edf2;font:15px/1.5 system-ui,sans-serif}
main{max-width:1280px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;align-items:center;gap:20px}h1{margin:0;font-size:28px}
.eyebrow{color:#adc6dc;letter-spacing:2px;font:12px ui-monospace,monospace}.layout{display:grid;grid-template-columns:minmax(0,1fr) 275px;gap:18px;margin-top:20px}
canvas{width:100%;display:block;background:#1c2b36;border:1px solid #476171;border-radius:10px}aside{background:#1b2b36;padding:18px;border:1px solid #476171;border-radius:10px;overflow-wrap:anywhere}
.label{color:#9fb7c7;font-size:12px;text-transform:uppercase;letter-spacing:1px}pre{white-space:pre-wrap;font:13px/1.85 ui-monospace,monospace}
.controls{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:12px 0}button,select{font:inherit;background:#2b4353;color:#eee;border:1px solid #648094;border-radius:6px;padding:6px 12px;cursor:pointer}
#scrub{width:100%;accent-color:#e4b663}small{color:#9fb7c7}@media(max-width:850px){.layout{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column}}
</style></head><body><main><header><div><div class="eyebrow">SKYPARCEL / FLIGHT RECORDER</div><h1 id="title"></h1></div><div id="result"></div></header>
<div class="layout"><section><canvas id="canvas" width="940" height="520" aria-label="Skyparcel flight replay"></canvas>
<div class="controls"><button id="play">Play</button><button id="back">← Back</button><button id="next">Next →</button><label>Speed <select id="speed"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label><span id="count"></span></div>
<input id="scrub" type="range" min="0" value="0" aria-label="Replay frame"><small>Amber: pickup · Green: depot · Faded: beyond observation or already passed<br>Space: play/pause · Arrow keys: one frame</small></section>
<aside><div class="label">Decision state</div><pre id="state"></pre><div class="label">Your DEBUG values</div><pre id="debug"></pre><small>State is shown before the selected action. A press while held produces no flap.</small></aside></div></main>
<script>
const D=__DATA__,C=D.course,P=C.physics,F=D.frames,cv=document.getElementById('canvas'),g=cv.getContext('2d');
const scrub=document.getElementById('scrub'),play=document.getElementById('play');let index=0,playing=false,last=0,elapsed=0;scrub.max=F.length-1;
document.getElementById('title').textContent=C.name+' · '+C.title;document.getElementById('result').textContent=`${D.result.deliveries}/${C.required} delivered · ${D.result.score.toFixed(1)}/100 · ${D.result.reason}`;
function draw(){const f=F[index],scale=(cv.height-50)/P.height,origin=Math.max(0,f.x-35),X=x=>24+(x-origin)*scale,Y=y=>25+y*scale;
g.fillStyle='#1c2b36';g.fillRect(0,0,cv.width,cv.height);g.strokeStyle='#2b4352';for(let y=0;y<=P.height;y+=10){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}
g.strokeStyle='#829cad';for(const y of [0,P.height]){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}
let ahead=0;C.gates.forEach((gate,i)=>{const shown=gate.x+gate.half_width>=f.x-P.radius&&ahead++<2;g.fillStyle=shown?'#588593':'#354f60';const x=X(gate.x-gate.half_width),w=2*gate.half_width*scale;g.fillRect(x,Y(0),w,gate.top*scale);g.fillRect(x,Y(gate.bottom),w,(P.height-gate.bottom)*scale);});
ahead=0;C.stations.forEach((station,i)=>{const pending=f.station_states[i]==='ahead',shown=pending&&ahead++<2;g.globalAlpha=shown?1:.25;g.strokeStyle=station.kind==='pickup'?'#efc16b':'#8ee3b5';g.lineWidth=3;g.beginPath();g.moveTo(X(station.x),Y(station.top));g.lineTo(X(station.x),Y(station.bottom));g.stroke();g.lineWidth=1;g.fillStyle=g.strokeStyle;g.font='12px monospace';g.fillText(station.kind==='pickup'?'P':'D',X(station.x)-4,Y(station.top)-7);g.globalAlpha=1;});
g.strokeStyle='#b1c7dd60';g.beginPath();for(let j=Math.max(0,index-25);j<=index;j++){const q=F[j];if(j===Math.max(0,index-25))g.moveTo(X(q.x),Y(q.y));else g.lineTo(X(q.x),Y(q.y));}g.stroke();
const r=P.radius*scale;g.fillStyle=f.done&&f.reason!=='complete'?'#ec9f8b':'#c5dfef';g.fillRect(X(f.x)-r,Y(f.y)-r,2*r,2*r);if(f.carrying){g.fillStyle='#efc16b';g.fillRect(X(f.x)-r*.5,Y(f.y)-r*.5,r,r);}if(f.action==='press'&&!f.held){g.strokeStyle='#f7e0aa';g.strokeRect(X(f.x)-r-4,Y(f.y)-r-4,2*r+8,2*r+8);}
g.strokeStyle='#91dfba';g.setLineDash([6,5]);g.beginPath();g.moveTo(X(C.finish_x),Y(0));g.lineTo(X(C.finish_x),Y(P.height));g.stroke();g.setLineDash([]);g.fillStyle='#abc6d8';g.font='12px monospace';g.fillText('y ↓   x →',12,15);
document.getElementById('state').textContent=`tick       ${f.tick}\nx          ${f.x.toFixed(2)}\ny          ${f.y.toFixed(2)}\nvy         ${f.vy.toFixed(2)}\nheld       ${f.held}\ncarrying   ${f.carrying}\ndelivered  ${f.delivered}/${C.required}\naction     ${f.action||'—'}`;
document.getElementById('debug').textContent=Object.keys(f.debug||{}).length?JSON.stringify(f.debug,null,2):'No debug values';document.getElementById('count').textContent=`Frame ${index}/${F.length-1}`;scrub.value=index;}
function pause(){playing=false;play.textContent='Play';elapsed=0;}function toggle(){if(playing){pause();return;}if(index===F.length-1)index=0;playing=true;play.textContent='Pause';draw();}
play.onclick=toggle;document.getElementById('back').onclick=()=>{pause();index=Math.max(0,index-1);draw();};document.getElementById('next').onclick=()=>{pause();index=Math.min(F.length-1,index+1);draw();};scrub.oninput=()=>{pause();index=Number(scrub.value);draw();};
document.addEventListener('keydown',e=>{if(['INPUT','SELECT'].includes(e.target.tagName))return;if(e.code==='Space'){e.preventDefault();toggle();}if(e.code==='ArrowRight'){e.preventDefault();document.getElementById('next').click();}if(e.code==='ArrowLeft'){e.preventDefault();document.getElementById('back').click();}});
function animate(t){if(last&&playing){elapsed+=Math.min(200,t-last)*Number(document.getElementById('speed').value);while(playing&&elapsed>=P.dt*1000){elapsed-=P.dt*1000;index=Math.min(F.length-1,index+1);if(index===F.length-1)pause();draw();}}last=t;requestAnimationFrame(animate);}draw();requestAnimationFrame(animate);
</script></body></html>'''

