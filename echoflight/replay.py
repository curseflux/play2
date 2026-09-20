"""Self-contained HTML replay writer; no third-party dependencies."""
import html
import json
from pathlib import Path


def write_replay(path, course, result, frames):
    data = json.dumps(dict(course=course, result=result, frames=frames)).replace('<', '\\u003c')
    page = PAGE.replace('__TITLE__', html.escape(course['name'])).replace('__DATA__', data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding='utf-8')


PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EchoFlight | __TITLE__</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101b26;color:#e4edf4;font:15px/1.5 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:24px}h1{margin:0}header{display:flex;justify-content:space-between;gap:20px;align-items:center}.eyebrow{letter-spacing:3px;color:#7be1d2;font:12px monospace}.layout{display:grid;grid-template-columns:minmax(0,1fr) 265px;gap:16px;margin-top:20px}canvas{width:100%;background:#192c3b;border:1px solid #476174;border-radius:8px}aside{background:#192c3b;padding:16px;border-radius:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.7 monospace}small{color:#afc0cc}.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:12px 0}button,select{padding:7px 12px;background:#284455;color:#fff;border:1px solid #648393;border-radius:5px;font:inherit}input{width:100%;accent-color:#7be1d2}@media(max-width:850px){.layout{grid-template-columns:1fr}header{display:block}}
</style><main><header><div><div class="eyebrow">ECHOFLIGHT / FLIGHT RECORDER</div><h1 id="title"></h1></div><div id="result"></div></header>
<div class="layout"><section><canvas id="canvas" width="920" height="520" aria-label="Flight replay"></canvas>
<div class="controls"><button id="play">Play</button><button id="back">Back</button><button id="next">Next</button><label>Speed <select id="speed"><option value="0.5">0.5x</option><option value="1" selected>1x</option><option value="2">2x</option></select></label><span id="count"></span></div>
<input id="scrub" type="range" min="0" value="0" aria-label="Replay frame"><small>Yellow: stars. Teal outline: a queued flap fires this step. Faded objects are outside the current observation or already passed.</small></section>
<aside><strong>Before this decision</strong><pre id="state"></pre><strong>Your DEBUG values</strong><pre id="debug"></pre><small>Space: play/pause. Arrow keys: step. Current action is queued for the following step.</small></aside></div></main>
<script>
const D=__DATA__,C=D.course,P=C.physics,F=D.frames,cv=document.getElementById('canvas'),g=cv.getContext('2d');
const scrub=document.getElementById('scrub'),play=document.getElementById('play');let index=0,playing=false,last=0,elapsed=0;
scrub.max=F.length-1;document.getElementById('title').textContent=C.name+' | '+C.title;
document.getElementById('result').textContent=`${D.result.collected}/${C.required} stars | ${D.result.score.toFixed(1)}/100 | ${D.result.reason}`;
function draw(){const f=F[index],s=(cv.height-50)/P.height,origin=Math.max(0,f.x-30),X=x=>24+(x-origin)*s,Y=y=>cv.height-25-y*s;
g.fillStyle='#192c3b';g.fillRect(0,0,cv.width,cv.height);g.strokeStyle='#2e4657';for(let y=0;y<=P.height;y+=10){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}
g.strokeStyle='#91a5b2';for(const y of [0,P.height]){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}
let ahead=0;C.gates.forEach(q=>{const visible=q.x+q.half_width>=f.x-P.radius&&ahead++<3;const center=q.center+q.amplitude*Math.sin(q.omega*f.tick*P.dt+q.phase),lo=center-q.gap/2,hi=center+q.gap/2;g.fillStyle=visible?'#598b9a':'#304959';g.fillRect(X(q.x-q.half_width),Y(lo),2*q.half_width*s,lo*s);g.fillRect(X(q.x-q.half_width),Y(P.height),2*q.half_width*s,(P.height-hi)*s);});
ahead=0;C.stars.forEach((q,i)=>{if(f.star_states[i]==='collected')return;const shown=f.star_states[i]==='ahead'&&ahead++<2;g.globalAlpha=shown?1:.2;g.fillStyle='#f2c56d';g.beginPath();g.arc(X(q.x),Y(q.y),q.radius*s,0,Math.PI*2);g.fill();g.globalAlpha=1;});
g.strokeStyle='#bad7e166';g.beginPath();for(let j=Math.max(0,index-25);j<=index;j++){const q=F[j];if(j===Math.max(0,index-25))g.moveTo(X(q.x),Y(q.y));else g.lineTo(X(q.x),Y(q.y));}g.stroke();
const r=P.radius*s;g.fillStyle=f.done&&f.reason!=='complete'?'#ef9b86':'#dceef5';g.fillRect(X(f.x)-r,Y(f.y)-r,2*r,2*r);if(f.pending){g.strokeStyle='#7be1d2';g.strokeRect(X(f.x)-r-4,Y(f.y)-r-4,2*r+8,2*r+8);}
g.strokeStyle='#7be1d2';g.setLineDash([5,5]);g.beginPath();g.moveTo(X(C.finish_x),Y(0));g.lineTo(X(C.finish_x),Y(P.height));g.stroke();g.setLineDash([]);
document.getElementById('state').textContent=`tick       ${f.tick}\nseconds    ${(f.tick*P.dt).toFixed(2)}\nx          ${f.x.toFixed(2)}\ny          ${f.y.toFixed(2)}\nvy         ${f.vy.toFixed(2)}\npending    ${f.pending}\ncollected  ${f.collected}/${C.required}\nqueue now  ${f.action===null?'-':f.action}`;
document.getElementById('debug').textContent=Object.keys(f.debug||{}).length?JSON.stringify(f.debug,null,2):'No debug values';document.getElementById('count').textContent=`Frame ${index}/${F.length-1}`;scrub.value=index;}
function pause(){playing=false;elapsed=0;play.textContent='Play';}function toggle(){if(playing){pause();return;}if(index===F.length-1)index=0;playing=true;play.textContent='Pause';draw();}
play.onclick=toggle;document.getElementById('back').onclick=()=>{pause();index=Math.max(0,index-1);draw();};document.getElementById('next').onclick=()=>{pause();index=Math.min(F.length-1,index+1);draw();};scrub.oninput=()=>{pause();index=Number(scrub.value);draw();};
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(e.target.tagName))return;if(e.code==='Space'){e.preventDefault();toggle();}if(e.code==='ArrowRight')document.getElementById('next').click();if(e.code==='ArrowLeft')document.getElementById('back').click();});
function animate(t){if(last&&playing){elapsed+=Math.min(200,t-last)*Number(document.getElementById('speed').value);while(playing&&elapsed>=P.dt*1000){elapsed-=P.dt*1000;index=Math.min(F.length-1,index+1);if(index===F.length-1)pause();draw();}}last=t;requestAnimationFrame(animate);}draw();requestAnimationFrame(animate);
</script></html>'''
