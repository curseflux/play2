"""Create a standalone HTML replay from recorded decisions."""
import html
import json
from pathlib import Path


def write_replay(path, course, result, frames):
    payload = json.dumps(dict(course=course, result=result, frames=frames)).replace('<', '\\u003c')
    page = TEMPLATE.replace('__NAME__', html.escape(course['mapName'])).replace('__DATA__', payload)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding='utf-8')


TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cosmo flight replay | __NAME__</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101a27;color:#e5edf4;font:15px/1.5 system-ui,sans-serif}main{max-width:1250px;margin:auto;padding:24px}h1{margin:0;font-size:28px}.eyebrow{font:12px monospace;letter-spacing:3px;color:#80d8ef}header{display:flex;justify-content:space-between;align-items:center;gap:20px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 250px;gap:16px;margin-top:18px}canvas{width:100%;background:#1b2d3c;border:1px solid #49677a;border-radius:8px}aside{background:#1b2d3c;border-radius:8px;padding:17px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.7 monospace}.controls{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin:12px 0}button,select{background:#284557;color:#eee;border:1px solid #638397;border-radius:5px;padding:7px 12px;font:inherit;cursor:pointer}input{width:100%;accent-color:#80d8ef}small{color:#a8c1d2}@media(max-width:800px){.layout{grid-template-columns:1fr}header{display:block}}
</style></head><body><main><header><div><div class="eyebrow">COSMO / FLIGHT RECORDER</div><h1 id="title"></h1></div><div id="result"></div></header><div class="layout"><section>
<canvas id="canvas" width="930" height="525" aria-label="Cosmo flight replay"></canvas><div class="controls"><button id="play">Play</button><button id="back">Back</button><button id="next">Next</button><label>Speed <select id="speed"><option value="0.5">0.5x</option><option value="1" selected>1x</option><option value="2">2x</option></select></label><span id="count"></span></div><input type="range" id="scrub" min="0" value="0" aria-label="Replay frame"><small>Blue trail shows recent positions. Orange dog means collision. The dashed line marks the last pipe's end.</small></section><aside><strong>State before decision</strong><pre id="state"></pre><strong>Policy log</strong><pre id="log"></pre><small>Bounce is applied after a safe, unfinished step, changing movement on the next frame.</small></aside></div></main>
<script>
const D=__DATA__,C=D.course,R=D.result,F=D.frames,cv=document.getElementById('canvas'),g=cv.getContext('2d');
const scrub=document.getElementById('scrub'),play=document.getElementById('play');let index=0,playing=false,last=0,elapsed=0;const ground=C.canvasHeight-C.groundHeight;
scrub.max=F.length-1;document.getElementById('title').textContent=C.mapName+' | '+C.challenge.replaceAll('_',' ');document.getElementById('result').textContent=`${R.score}/${R.total} pipes | ${R.reason}`;
function draw(){const f=F[index],scale=(cv.height-45)/C.canvasHeight,origin=Math.max(0,f.x-45),X=x=>24+(x-origin)*scale,Y=y=>20+y*scale;
g.fillStyle='#1b2d3c';g.fillRect(0,0,cv.width,cv.height);g.strokeStyle='#2b4658';for(let y=0;y<=C.canvasHeight;y+=25){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}
g.fillStyle='#48515a';g.fillRect(0,Y(ground),cv.width,C.groundHeight*scale);g.fillStyle='#64899b';
C.pipes.forEach((p,i)=>{const shown=p.position+C.pipeWidth>f.x;g.fillStyle=shown?'#64899b':'#385363';g.fillRect(X(p.position),Y(0),C.pipeWidth*scale,p.topHeight*scale);g.fillRect(X(p.position),Y(p.topHeight+p.gap),C.pipeWidth*scale,(ground-p.topHeight-p.gap)*scale);g.fillStyle='#afc4d2';g.font='12px monospace';g.fillText(String(i+1),X(p.position)+3,Y(ground)-8);});
const finish=Math.max(...C.pipes.map(p=>p.position+C.pipeWidth));g.strokeStyle='#93dfbb';g.setLineDash([6,5]);g.beginPath();g.moveTo(X(finish),Y(0));g.lineTo(X(finish),Y(ground));g.stroke();g.setLineDash([]);
g.strokeStyle='#80d8ef99';g.lineWidth=2;g.beginPath();for(let j=Math.max(0,index-35);j<=index;j++){const q=F[j];if(j===Math.max(0,index-35))g.moveTo(X(q.x+C.cosmo.width/2),Y(q.y+C.cosmo.height/2));else g.lineTo(X(q.x+C.cosmo.width/2),Y(q.y+C.cosmo.height/2));}g.stroke();g.lineWidth=1;
g.fillStyle=index===F.length-1&&R.reason.includes('collision')?'#f39b79':'#d9e9ef';g.fillRect(X(f.x),Y(f.y),C.cosmo.width*scale,C.cosmo.height*scale);if(f.action===true){g.strokeStyle='#f6d97f';g.strokeRect(X(f.x)-3,Y(f.y)-3,C.cosmo.width*scale+6,C.cosmo.height*scale+6);}
let passed=C.pipes.filter(p=>p.position+C.pipeWidth<f.x).length;document.getElementById('state').textContent=`frame     ${f.frame}\nx         ${f.x.toFixed(2)}\ny         ${f.y.toFixed(2)}\nvelocity  ${f.velocity.toFixed(2)}\npassed    ${passed}/${C.pipes.length}\naction    ${f.action===null?'-':f.action}`;document.getElementById('log').textContent=f.log||'No log';document.getElementById('count').textContent=`Frame ${index}/${F.length-1}`;scrub.value=index;}
function pause(){playing=false;elapsed=0;play.textContent='Play';}function toggle(){if(playing){pause();return;}if(index===F.length-1)index=0;playing=true;play.textContent='Pause';draw();}
play.onclick=toggle;document.getElementById('back').onclick=()=>{pause();index=Math.max(0,index-1);draw();};document.getElementById('next').onclick=()=>{pause();index=Math.min(F.length-1,index+1);draw();};scrub.oninput=()=>{pause();index=Number(scrub.value);draw();};document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(e.target.tagName))return;if(e.code==='Space'){e.preventDefault();toggle();}if(e.code==='ArrowRight')document.getElementById('next').click();if(e.code==='ArrowLeft')document.getElementById('back').click();});
function animate(t){if(last&&playing){elapsed+=Math.min(200,t-last)*Number(document.getElementById('speed').value);while(playing&&elapsed>=C.frameTime){elapsed-=C.frameTime;index=Math.min(F.length-1,index+1);if(index===F.length-1)pause();draw();}}last=t;requestAnimationFrame(animate);}draw();requestAnimationFrame(animate);
</script></body></html>'''
