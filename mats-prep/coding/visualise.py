"""Write a self-contained HTML replay of a policy on a set of scenarios.

    python3 visualise.py final_policy hidden  ->  replay.html
"""
import json
import sys
import lander
import policies

SETS = {"visible": lambda: lander.visible_scenarios(),
        "validation": lambda: lander.validation_scenarios(n=12, seed=4242),
        "hidden": lambda: lander.hidden_scenarios(n=12, seed=7)}

HTML = """<title>Cargo Lander replay</title>
<style>
 :root{--bg:#f7f7f5;--fg:#1a1a1a;--mut:#6b6b6b;--ok:#1d7a4c;--bad:#b3261e;--line:#d8d8d4;--pad:#2b6cb0}
 @media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#16171a;--fg:#e8e8e6;--mut:#9a9a96;--line:#2e3034;--ok:#4ade80;--bad:#f87171;--pad:#60a5fa}}
 :root[data-theme=dark]{--bg:#16171a;--fg:#e8e8e6;--mut:#9a9a96;--line:#2e3034;--ok:#4ade80;--bad:#f87171;--pad:#60a5fa}
 body{background:var(--bg);color:var(--fg);font:14px/1.5 ui-sans-serif,system-ui,sans-serif;padding-block:20px;padding-left:16px;padding-right:16px;max-width:880px;margin:0 auto}
 h1{font-size:17px;margin:0 0 2px}p.sub{color:var(--mut);margin:0 0 16px}
 canvas{width:100%;height:auto;border:1px solid var(--line);border-radius:8px;display:block;background:transparent}
 .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:12px 0}
 select,button{font:inherit;padding:5px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
 button{cursor:pointer}
 table{border-collapse:collapse;width:100%;margin-top:8px;font-variant-numeric:tabular-nums}
 td,th{padding:4px 8px;border-bottom:1px solid var(--line);text-align:right}
 th:first-child,td:first-child{text-align:left}
 .ok{color:var(--ok)}.bad{color:var(--bad)}
</style>
<h1>Cargo Lander &mdash; __POL__ on __SET__</h1>
<p class="sub">Scrub a run to see exactly where it goes wrong. Reading failure traces beats theorising.</p>
<div class="row">
  <select id=pick></select>
  <button id=play>play</button>
  <input id=scrub type=range min=0 value=0 style="flex:1;min-width:140px">
  <span id=stat class=sub></span>
</div>
<canvas id=c width=860 height=420></canvas>
<table id=tbl><thead><tr><th>run<th>score<th>outcome<th>vy<th>vx<th>x<th>fuel left</tr></thead><tbody></tbody></table>
<script>
const RUNS=__DATA__;
const c=document.getElementById('c'),g=c.getContext('2d');
const pick=document.getElementById('pick'),scrub=document.getElementById('scrub'),stat=document.getElementById('stat');
RUNS.forEach((r,i)=>pick.add(new Option(r.name+'  ('+r.score.toFixed(1)+')',i)));
document.querySelector('tbody').innerHTML=RUNS.map(r=>
 `<tr><td>${r.name}<td>${r.score.toFixed(1)}<td class="${r.landed?'ok':'bad'}">${r.reason}
  <td>${r.vy.toFixed(2)}<td>${r.vx.toFixed(2)}<td>${r.x.toFixed(1)}<td>${r.fuel.toFixed(1)}</tr>`).join('');
let run=RUNS[0],f=0,playing=false;
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
function draw(){
 const W=c.width,H=c.height,maxY=Math.max(...run.t.map(p=>p[1]))*1.15+10;
 const sx=v=>W/2+v*(W/2)/210, sy=v=>H-18-v*(H-34)/maxY;
 g.clearRect(0,0,W,H);
 g.strokeStyle=css('--line');g.lineWidth=1;g.beginPath();g.moveTo(0,sy(0));g.lineTo(W,sy(0));g.stroke();
 g.strokeStyle=css('--pad');g.lineWidth=4;g.beginPath();g.moveTo(sx(-8),sy(0));g.lineTo(sx(8),sy(0));g.stroke();
 g.strokeStyle=css('--mut');g.lineWidth=1.2;g.globalAlpha=.45;g.beginPath();
 run.t.forEach((p,i)=>i?g.lineTo(sx(p[0]),sy(p[1])):g.moveTo(sx(p[0]),sy(p[1])));g.stroke();g.globalAlpha=1;
 const p=run.t[Math.min(f,run.t.length-1)];
 g.fillStyle=run.landed?css('--ok'):css('--bad');
 g.beginPath();g.arc(sx(p[0]),sy(p[1]),5,0,7);g.fill();
 stat.textContent=`frame ${f}  x=${p[0].toFixed(1)} y=${p[1].toFixed(1)} vx=${p[2].toFixed(2)} vy=${p[3].toFixed(2)} fuel=${p[4].toFixed(1)}`;
}
function load(i){run=RUNS[i];f=0;scrub.max=run.t.length-1;scrub.value=0;draw();}
pick.onchange=e=>load(+e.target.value);
scrub.oninput=e=>{f=+e.target.value;draw();};
document.getElementById('play').onclick=function(){playing=!playing;this.textContent=playing?'pause':'play';};
setInterval(()=>{if(playing){f=(f+1)%run.t.length;scrub.value=f;draw();}},33);
load(0);
</script>"""

if __name__ == "__main__":
    pol_name = sys.argv[1] if len(sys.argv) > 1 else "final_policy"
    set_name = sys.argv[2] if len(sys.argv) > 2 else "hidden"
    pol = policies.ALL[pol_name]
    runs = []
    for i, s in enumerate(SETS[set_name]()):
        r = lander.run(pol, s, record=True, seed=i)
        runs.append({"name": s.name, "score": r.score, "landed": r.landed,
                     "reason": r.reason, "vy": r.touchdown_vy, "vx": r.touchdown_vx,
                     "x": r.touchdown_x, "fuel": r.fuel_left, "t": r.trajectory})
    out = (HTML.replace("__DATA__", json.dumps(runs))
               .replace("__POL__", pol_name).replace("__SET__", set_name))
    with open("replay.html", "w") as fh:
        fh.write(out)
    print(f"wrote replay.html  ({len(runs)} runs, "
          f"mean {sum(r['score'] for r in runs)/len(runs):.1f})")
