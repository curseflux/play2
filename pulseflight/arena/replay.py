"""Self-contained canvas replay; no server or third-party packages required."""
import html
import json
import pathlib


def write_replay(path, case, result, frames):
    data = json.dumps({"case": case, "result": result, "frames": frames}).replace("<", "\\u003c")
    page = TEMPLATE.replace("__TITLE__", html.escape(case["name"] + " / " + result["reason"]))
    page = page.replace("__DATA__", data)
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")


TEMPLATE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pulseflight — __TITLE__</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#10191d;color:#eaf1f2;font:15px/1.5 system-ui,sans-serif}
main{max-width:1280px;margin:auto;padding:28px}header{display:flex;justify-content:space-between;align-items:center;gap:20px}
h1{font-size:27px;margin:0;letter-spacing:-.5px}.eyebrow{color:#8ebcb7;font:12px ui-monospace,monospace;letter-spacing:2px}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 270px;gap:18px;margin-top:22px}canvas{display:block;width:100%;background:#18252a;border:1px solid #385055;border-radius:12px}
aside{background:#17252a;border:1px solid #385055;border-radius:12px;padding:18px;overflow-wrap:anywhere}.label{color:#8ca7ad;font-size:12px;text-transform:uppercase;letter-spacing:1px}
#status{color:#c6e2dc}#stats{white-space:pre-wrap;font:14px/1.85 ui-monospace,monospace}#debug{white-space:pre-wrap;font:12px/1.6 ui-monospace,monospace}
.controls{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin-top:14px}button,select{font:inherit;background:#243b41;color:#fff;border:1px solid #4e6b70;border-radius:7px;padding:7px 13px;cursor:pointer}
button:hover{background:#345057}#scrub{width:100%;accent-color:#9cdfcc}small{color:#91a9ae}.hint{margin-top:13px;color:#91a9ae;font-size:13px}
@media(max-width:850px){.layout{grid-template-columns:1fr}main{padding:15px}header{align-items:flex-start;flex-direction:column}}
</style></head><body><main>
<header><div><div class="eyebrow">FLIGHT RECORDER / PULSEFLIGHT</div><h1 id="title"></h1></div><div id="status"></div></header>
<div class="layout"><section><canvas id="view" width="940" height="520" aria-label="Flight replay"></canvas>
<div class="controls"><button id="play">Play</button><button id="back">← Back</button><button id="next">Next →</button>
<label>Speed <select id="speed"><option value="0.25">0.25×</option><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label><span id="counter"></span></div>
<input id="scrub" type="range" min="0" value="0" aria-label="Replay frame"><div class="hint">Space: play / pause · Arrow keys: one frame · Dashed outlines: gates currently visible to the agent</div>
</section><aside><div class="label">Decision state</div><div id="stats"></div><hr><div class="label">Your DEBUG values</div><pre id="debug"></pre><small>Action and DEBUG belong to the state shown, before that action is applied.</small></aside></div>
</main><script>
const DATA=__DATA__, c=DATA.case, frames=DATA.frames, p=c.physics;
const canvas=document.getElementById('view'), ctx=canvas.getContext('2d');
const slider=document.getElementById('scrub'), play=document.getElementById('play');
let index=0, playing=false, elapsed=0, last=0;
document.getElementById('title').textContent=c.name+' · '+(c.description||'Replay');
document.getElementById('status').textContent=DATA.result.cleared+'/'+DATA.result.total+' gates · '+DATA.result.reason;
slider.max=frames.length-1;
function render(){
 const f=frames[index], W=canvas.width,H=canvas.height,s=(H-60)/c.height, origin=Math.max(0,f.x-150);
 const X=x=>35+(x-origin)*s, Y=y=>30+y*s;
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#18252a';ctx.fillRect(0,0,W,H);
 ctx.strokeStyle='#263c43';ctx.lineWidth=1;
 for(let y=0;y<=c.height;y+=50){ctx.beginPath();ctx.moveTo(0,Y(y));ctx.lineTo(W,Y(y));ctx.stroke();}
 ctx.strokeStyle='#708c91';for(const y of [0,c.height]){ctx.beginPath();ctx.moveTo(0,Y(y));ctx.lineTo(W,Y(y));ctx.stroke();}
 let visible=0;
 c.gates.forEach((g,k)=>{
   const [top,bottom]=f.openings[k],left=X(g.x-g.half_width),width=2*g.half_width*s;
   const pending=g.x+g.half_width>=f.x-p.radius, shown=pending&&visible++<c.sight;
   ctx.fillStyle=shown?'#4c7a79':'#304b53';ctx.fillRect(left,Y(0),width,top*s);ctx.fillRect(left,Y(bottom),width,(c.height-bottom)*s);
   if(shown){ctx.strokeStyle='#a3d8c9';ctx.setLineDash([4,4]);ctx.strokeRect(left,Y(top),width,(bottom-top)*s);ctx.setLineDash([]);}
   ctx.fillStyle='#d0e3df';ctx.font='12px monospace';ctx.fillText(String(k+1),left,Y(top)-9);
 });
 ctx.strokeStyle='#83b8b080';ctx.beginPath();for(let j=Math.max(0,index-35);j<=index;j++){const q=frames[j];if(j===Math.max(0,index-35))ctx.moveTo(X(q.x),Y(q.y));else ctx.lineTo(X(q.x),Y(q.y));}ctx.stroke();
 const bx=X(f.x),by=Y(f.y);ctx.beginPath();ctx.arc(bx,by,p.radius*s,0,2*Math.PI);ctx.fillStyle=f.finished&&f.reason!=='complete'?'#f29483':'#f0c774';ctx.fill();
 if(f.action==='pulse'){ctx.strokeStyle=f.cooldown===0?'#ffe4a0':'#728991';ctx.beginPath();ctx.arc(bx,by,p.radius*s+6,0,2*Math.PI);ctx.stroke();}
 ctx.fillStyle='#adced0';ctx.font='12px monospace';ctx.fillText('y ↓   x →',12,17);
 document.getElementById('stats').textContent=`tick       ${f.tick}\nx          ${f.x.toFixed(2)}\ny          ${f.y.toFixed(2)}\nvy         ${f.vy.toFixed(2)}\ncooldown   ${f.cooldown}\ncleared    ${f.cleared}/${c.gates.length}\naction     ${f.action||'—'}\ntime       ${(f.tick*p.dt).toFixed(2)} s`;
 document.getElementById('debug').textContent=Object.keys(f.debug||{}).length?JSON.stringify(f.debug,null,2):'No debug values';
 document.getElementById('counter').textContent=`Frame ${index} / ${frames.length-1}`;slider.value=index;
}
function pause(){playing=false;play.textContent='Play';elapsed=0;}
function toggle(){if(playing){pause();return;}if(index===frames.length-1)index=0;playing=true;play.textContent='Pause';render();}
play.onclick=toggle;document.getElementById('back').onclick=()=>{pause();index=Math.max(0,index-1);render();};
document.getElementById('next').onclick=()=>{pause();index=Math.min(frames.length-1,index+1);render();};
slider.oninput=()=>{pause();index=Number(slider.value);render();};
document.addEventListener('keydown',e=>{if(['INPUT','SELECT'].includes(e.target.tagName))return;if(e.code==='Space'){e.preventDefault();toggle();}if(e.code==='ArrowRight'){e.preventDefault();document.getElementById('next').click();}if(e.code==='ArrowLeft'){e.preventDefault();document.getElementById('back').click();}});
function animate(now){if(last&&playing){elapsed+=Math.min(now-last,200)*Number(document.getElementById('speed').value);while(elapsed>=p.dt*1000&&playing){elapsed-=p.dt*1000;index=Math.min(frames.length-1,index+1);if(index===frames.length-1)pause();render();}}last=now;requestAnimationFrame(animate);}
render();requestAnimationFrame(animate);
</script></body></html>'''
