"""Self-contained HTML replay, showing only the currently visible coin by default."""
import html
import json
import pathlib


def write_replay(path, case, result, frames):
    data = json.dumps(dict(case=case, result=result, frames=frames)).replace("<", "\\u003c")
    page = TEMPLATE.replace("__TITLE__", html.escape(case["name"])).replace("__DATA__", data)
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")


TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Coinrun / __TITLE__</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#111821;color:#e8eef4;font:15px/1.5 system-ui,sans-serif}
main{max-width:1280px;padding:24px;margin:auto}header{display:flex;align-items:center;justify-content:space-between;gap:16px}
h1{margin:0;font-size:27px}.eyebrow{color:#b7a6e3;font:12px ui-monospace,monospace;letter-spacing:2px}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:18px;margin-top:18px}canvas{display:block;width:100%;border:1px solid #42515e;border-radius:10px;background:#1c2732}
aside{padding:18px;border:1px solid #42515e;border-radius:10px;background:#1a2631;overflow-wrap:anywhere}.label{color:#a1b0c0;font-size:12px;letter-spacing:1px;text-transform:uppercase}
pre{white-space:pre-wrap;font:13px/1.75 ui-monospace,monospace}.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:12px 0}
button,select{font:inherit;padding:6px 12px;color:#eee;background:#2b3b4a;border:1px solid #617084;border-radius:6px;cursor:pointer}button:hover{background:#425166}
#scrub{width:100%;accent-color:#e6b34e}small{color:#a1b0c0}.gold{color:#f6cc70}@media(max-width:850px){.layout{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column}}
</style></head><body><main>
<header><div><div class="eyebrow">COINRUN / FLIGHT RECORDER</div><h1 id="title"></h1></div><div id="result"></div></header>
<div class="layout"><section><canvas id="view" width="940" height="510" aria-label="Coinrun replay"></canvas>
<div class="controls"><button id="play">Play</button><button id="back">← Back</button><button id="next">Next →</button><label>Speed <select id="speed"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label><span id="counter"></span></div>
<input id="scrub" type="range" min="0" value="0" aria-label="Replay frame">
<label><input id="reveal" type="checkbox"> Reveal future coins (debug only)</label><br>
<small>Space: play/pause · Arrows: step · Gold ring: the one coin visible to your policy</small></section>
<aside><div class="label">Before the decision</div><pre id="state"></pre><div class="label gold">Visible coin</div><pre id="coin"></pre><div class="label">Your DEBUG values</div><pre id="debug"></pre><small>DEBUG and action belong to the state shown. The last frame has no action.</small></aside></div>
</main><script>
const D=__DATA__,C=D.case,P=C.physics,F=D.frames;
const cv=document.getElementById('view'),g=cv.getContext('2d'),slider=document.getElementById('scrub'),play=document.getElementById('play');
let index=0,playing=false,last=0,elapsed=0;slider.max=F.length-1;
document.getElementById('title').textContent=C.name+' · '+C.description;
document.getElementById('result').textContent=`${D.result.coins}/${D.result.target} coins · ${D.result.score.toFixed(1)}/100 · ${D.result.reason}`;
function draw(){const f=F[index],s=(cv.height-50)/P.ceiling,origin=Math.max(0,f.x-35);
 const X=x=>24+(x-origin)*s,Y=y=>cv.height-25-y*s;
 g.fillStyle='#1c2732';g.fillRect(0,0,cv.width,cv.height);g.strokeStyle='#2e3d49';
 for(let y=0;y<=P.ceiling;y+=10){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}
 g.strokeStyle='#869bae';for(const y of [0,P.ceiling]){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}
 let ahead=0;C.pipes.forEach((p,k)=>{const pending=p.x+p.half_width>=f.x-P.radius,visible=pending&&ahead++<C.pipe_sight;
   g.fillStyle=visible?'#517e88':'#344d5c';const x=X(p.x-p.half_width),w=2*p.half_width*s;
   g.fillRect(x,Y(P.ceiling),w,(P.ceiling-p.gap_hi)*s);g.fillRect(x,Y(p.gap_lo),w,p.gap_lo*s);
   g.fillStyle='#d4e4e8';g.font='12px monospace';g.fillText(String(k+1),x,Y(p.gap_hi)-7);
 });
 C.coins.forEach((coin,k)=>{const current=f.visible_coin&&f.visible_coin.id===k;
   if(f.coin_states[k]!=='available'||(!current&&!document.getElementById('reveal').checked))return;
   g.globalAlpha=current?1:0.3;g.beginPath();g.arc(X(coin.x),Y(coin.y),coin.radius*s,0,2*Math.PI);g.fillStyle='#f1c061';g.fill();
   if(current){g.beginPath();g.arc(X(coin.x),Y(coin.y),coin.radius*s+5,0,2*Math.PI);g.strokeStyle='#fbe1a7';g.stroke();}g.globalAlpha=1;
 });
 g.strokeStyle='#bdabd570';g.beginPath();for(let j=Math.max(0,index-22);j<=index;j++){const q=F[j];if(j===Math.max(0,index-22))g.moveTo(X(q.x),Y(q.y));else g.lineTo(X(q.x),Y(q.y));}g.stroke();
 const r=P.radius*s;g.fillStyle=f.done&&f.reason!=='finished'?'#f29191':'#bdb1f0';g.fillRect(X(f.x)-r,Y(f.y)-r,2*r,2*r);
 if(f.action===true){g.strokeStyle='#e3dafa';g.strokeRect(X(f.x)-r-3,Y(f.y)-r-3,2*r+6,2*r+6);}
 g.strokeStyle='#73ccaa';g.setLineDash([6,5]);g.beginPath();g.moveTo(X(C.finish_x),Y(0));g.lineTo(X(C.finish_x),Y(P.ceiling));g.stroke();g.setLineDash([]);
 g.fillStyle='#b1c4d4';g.font='12px monospace';g.fillText('y ↑   x →',12,15);
 document.getElementById('state').textContent=`frame   ${f.frame}\nx       ${f.x.toFixed(2)}\ny       ${f.y.toFixed(2)}\nvy      ${f.vy.toFixed(2)}\ncoins   ${f.coins_collected}/${C.coin_target}\npipes   ${f.pipes_cleared}/${C.pipes.length}\naction  ${f.action===null?'—':f.action?'bounce':'coast'}`;
 document.getElementById('coin').textContent=f.visible_coin?`id      ${f.visible_coin.id}\nx       ${f.visible_coin.x.toFixed(2)}\ny       ${f.visible_coin.y.toFixed(2)}`:'None in sight';
 document.getElementById('debug').textContent=Object.keys(f.debug||{}).length?JSON.stringify(f.debug,null,2):'No debug values';
 document.getElementById('counter').textContent=`Frame ${index}/${F.length-1}`;slider.value=index;
}
function pause(){playing=false;play.textContent='Play';elapsed=0;}
function toggle(){if(playing){pause();return;}if(index===F.length-1)index=0;playing=true;play.textContent='Pause';draw();}
play.onclick=toggle;document.getElementById('back').onclick=()=>{pause();index=Math.max(0,index-1);draw();};document.getElementById('next').onclick=()=>{pause();index=Math.min(F.length-1,index+1);draw();};
slider.oninput=()=>{pause();index=Number(slider.value);draw();};document.getElementById('reveal').onchange=draw;
document.addEventListener('keydown',e=>{if(['INPUT','SELECT'].includes(e.target.tagName))return;if(e.code==='Space'){e.preventDefault();toggle();}if(e.code==='ArrowRight'){e.preventDefault();document.getElementById('next').click();}if(e.code==='ArrowLeft'){e.preventDefault();document.getElementById('back').click();}});
function animate(t){if(last&&playing){elapsed+=Math.min(200,t-last)*Number(document.getElementById('speed').value);while(playing&&elapsed>=P.dt*1000){elapsed-=P.dt*1000;index=Math.min(F.length-1,index+1);if(index===F.length-1)pause();draw();}}last=t;requestAnimationFrame(animate);}
draw();requestAnimationFrame(animate);
</script></body></html>'''
