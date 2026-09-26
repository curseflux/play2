"""Self-contained HTML canvas replay for Cosmo Coins."""
import html
import json
from pathlib import Path


def write_replay(path, course, result, frames):
    data = json.dumps(dict(course=course, result=result, frames=frames)).replace('<', '\\u003c')
    page = PAGE.replace('__NAME__', html.escape(course['mapName'])).replace('__DATA__', data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding='utf-8')


PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cosmo Coins | __NAME__</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#14202b;color:#e5edf4;font:15px/1.5 system-ui,sans-serif}main{max-width:1250px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;align-items:center;gap:20px}h1{margin:0;font-size:28px}.eyebrow{font:12px monospace;letter-spacing:3px;color:#edc67d}.layout{display:grid;grid-template-columns:minmax(0,1fr) 265px;gap:16px;margin-top:18px}canvas{width:100%;background:#203448;border:1px solid #55778f;border-radius:8px}aside{background:#203448;padding:18px;border-radius:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.7 monospace}.controls{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin:12px 0}button,select{padding:7px 12px;background:#365268;color:#eee;border:1px solid #7a97a9;border-radius:5px;font:inherit;cursor:pointer}input{width:100%;accent-color:#edc67d}small{color:#aec5d3}@media(max-width:850px){.layout{grid-template-columns:1fr}header{display:block}}</style></head>
<body><main><header><div><div class="eyebrow">COSMO COINS / FLIGHT RECORDER</div><h1 id="title"></h1></div><div id="result"></div></header><div class="layout"><section><canvas id="canvas" width="930" height="525" aria-label="Cosmo Coins flight replay"></canvas>
<div class="controls"><button id="play">Play</button><button id="back">Back</button><button id="next">Next</button><label>Speed <select id="speed"><option value="0.5">0.5x</option><option value="1" selected>1x</option><option value="2">2x</option></select></label><span id="count"></span></div>
<input id="scrub" type="range" min="0" value="0" aria-label="Replay frame"><small>Gold: available coins. Green rings: collected. Faded: missed. Space: play/pause. Arrow keys: step.</small></section><aside><strong>Before this decision</strong><pre id="state"></pre><strong>Policy log</strong><pre id="log"></pre><small>Bounce applies after a safe, unfinished step. The selected action changes movement starting on the next frame.</small></aside></div></main>
<script>
const D=__DATA__,C=D.course,R=D.result,F=D.frames,cv=document.getElementById('canvas'),g=cv.getContext('2d');const scrub=document.getElementById('scrub'),play=document.getElementById('play');let index=0,playing=false,last=0,elapsed=0;const ground=C.canvasHeight-C.groundHeight;
scrub.max=F.length-1;document.getElementById('title').textContent=C.mapName+' | '+C.challenge.replaceAll('_',' ');document.getElementById('result').textContent=`${R.coins}/${R.target} coins | ${R.score.toFixed(1)}/100 | ${R.reason}`;
function draw(){const f=F[index],s=(cv.height-45)/C.canvasHeight,origin=Math.max(0,f.x-45),X=x=>24+(x-origin)*s,Y=y=>20+y*s;
g.fillStyle='#203448';g.fillRect(0,0,cv.width,cv.height);g.strokeStyle='#2e4b60';for(let y=0;y<=C.canvasHeight;y+=25){g.beginPath();g.moveTo(0,Y(y));g.lineTo(cv.width,Y(y));g.stroke();}g.fillStyle='#57564f';g.fillRect(0,Y(ground),cv.width,C.groundHeight*s);
C.coins.forEach((q,i)=>{const status=f.coin_states[i];g.globalAlpha=status==='missed'?.2:1;g.beginPath();g.arc(X(q.x),Y(q.y),q.radius*s,0,2*Math.PI);if(status==='collected'){g.strokeStyle='#8fdbb4';g.stroke();}else{g.fillStyle='#efc771';g.fill();}g.globalAlpha=1;});
g.strokeStyle='#91daee88';g.lineWidth=2;g.beginPath();for(let j=Math.max(0,index-35);j<=index;j++){const q=F[j];if(j===Math.max(0,index-35))g.moveTo(X(q.x+q.width/2),Y(q.y+q.height/2));else g.lineTo(X(q.x+q.width/2),Y(q.y+q.height/2));}g.stroke();g.lineWidth=1;
g.fillStyle=f.done&&f.reason==='ground collision'?'#ef9b78':'#dcecf4';g.fillRect(X(f.x),Y(f.y),f.width*s,f.height*s);if(f.action===true){g.strokeStyle='#f9da8f';g.strokeRect(X(f.x)-3,Y(f.y)-3,f.width*s+6,f.height*s+6);}
g.setLineDash([5,5]);g.strokeStyle='#8fdbb4';g.beginPath();g.moveTo(X(C.finishX),Y(0));g.lineTo(X(C.finishX),Y(ground));g.stroke();g.setLineDash([]);
document.getElementById('state').textContent=`frame       ${f.frame}\nx           ${f.x.toFixed(2)}\ny           ${f.y.toFixed(2)}\nvelocity    ${f.velocity.toFixed(2)}\ncollected   ${f.collected}/${C.coinTarget}\nremaining   ${f.coin_states.filter(v=>v==='available').length}\naction      ${f.action===null?'-':f.action}`;document.getElementById('log').textContent=f.log||'No log';document.getElementById('count').textContent=`Frame ${index}/${F.length-1}`;scrub.value=index;}
function pause(){playing=false;elapsed=0;play.textContent='Play';}function toggle(){if(playing){pause();return;}if(index===F.length-1)index=0;playing=true;play.textContent='Pause';draw();}play.onclick=toggle;document.getElementById('back').onclick=()=>{pause();index=Math.max(0,index-1);draw();};document.getElementById('next').onclick=()=>{pause();index=Math.min(F.length-1,index+1);draw();};scrub.oninput=()=>{pause();index=Number(scrub.value);draw();};document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(e.target.tagName))return;if(e.code==='Space'){e.preventDefault();toggle();}if(e.code==='ArrowRight')document.getElementById('next').click();if(e.code==='ArrowLeft')document.getElementById('back').click();});
function animate(t){if(last&&playing){elapsed+=Math.min(200,t-last)*Number(document.getElementById('speed').value);while(playing&&elapsed>=C.frameTime){elapsed-=C.frameTime;index=Math.min(F.length-1,index+1);if(index===F.length-1)pause();draw();}}last=t;requestAnimationFrame(animate);}draw();requestAnimationFrame(animate);
</script></body></html>'''
