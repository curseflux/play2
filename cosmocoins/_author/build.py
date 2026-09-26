"""Author-only generation, with successful trajectories for every case."""
import base64
import json
import math
from pathlib import Path
import random
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import World, touches_coin

STYLES = ('warmup', 'row', 'zigzag', 'clusters', 'forks', 'ground_bait',
          'ceiling', 'fast_scroll', 'longhaul')
SPECS = [(f'K{i+1:02}', 27109 + 113*i, STYLES[i % len(STYLES)]) for i in range(18)]


def build(name, seed, style):
    if style not in STYLES:
        raise ValueError(style)
    for attempt in range(100):
        result = construct(name, seed + attempt * 104729, style)
        if result:
            return result
    raise RuntimeError(f'cannot construct {name}: {style}')


def construct(name, seed, style):
    rng = random.Random(seed)
    n = 205 if style == 'longhaul' else 125
    bird = dict(x=18., y=rng.uniform(100, 130), velocity=rng.uniform(-2, 2),
                gravity=rng.uniform(.5, .75), bouncePower=rng.uniform(-8.5, -6.8),
                width=16., height=16.)
    speed = rng.uniform(4.8, 6.0) if style == 'fast_scroll' else rng.uniform(2.7, 3.5)
    c = dict(mapName=name, challenge=style, cosmo=bird, coins=[],
             scrollSpeed=speed, frameTime=16, canvasHeight=270, canvasWidth=900,
             groundHeight=22, finishX=bird['x'] + (n - .25)*speed,
             maxFrames=n+10, coinTarget=0)
    w = World(c)
    frames, actions = [w.snapshot()], []
    phase = rng.uniform(-math.pi, math.pi)
    period = rng.uniform(24, 33)
    for tick in range(n):
        amplitude = 42 if style in ('zigzag', 'forks') else 22
        target = 120 + amplitude * math.sin(tick / period + phase)
        if style == 'row':
            target = 122
        if style == 'ceiling':
            target -= 65
        if style == 'ground_bait':
            target += 55
        action = w.cosmo['y'] + bird['height']/2 + 2.6*w.cosmo['velocity'] > target + 3
        actions.append(bool(action))
        w.step(bool(action))
        frames.append(w.snapshot())
        if w.done and not w.passed:
            return None
    if not w.passed:
        return None
    ticks = list(range(24, n-10, 19 if style == 'longhaul' else 21))
    for tick in ticks:
        f = frames[tick]
        radius = rng.uniform(2, 3) if style == 'fast_scroll' else rng.uniform(3, 5)
        x = f['x'] + bird['width']/2
        y = f['y'] + bird['height']/2
        c['coins'].append(dict(x=x, y=y, radius=radius))
        if style == 'clusters':
            # Distinct coins can be collected together and must each count once.
            c['coins'].append(dict(x=x+2, y=y+2, radius=radius))
        if style == 'forks':
            other_y = y+95 if y < 130 else y-95
            if 6 < other_y < c['canvasHeight']-c['groundHeight']-6:
                c['coins'].append(dict(x=x, y=other_y, radius=radius))
        if style == 'ground_bait':
            # A visible optional coin entirely inside the ground is unreachable.
            c['coins'].append(dict(x=x-7, y=c['canvasHeight']-c['groundHeight']+5,
                                   radius=2.))
    c['coins'].sort(key=lambda q: q['x'])
    obtainable = len(ticks) * (2 if style == 'clusters' else 1)
    c['coinTarget'] = 0 if style == 'warmup' else max(1, obtainable - (
        2 if style in ('longhaul', 'clusters') else 1))
    proof = World(c)
    for action in actions:
        proof.step(action)
        if proof.done:
            break
    if not proof.passed or proof.collected < obtainable:
        return None
    return c, actions[:proof.frame]


def main():
    courses, witnesses = [], {}
    for name, seed, style in SPECS:
        c, actions = build(name, seed, style)
        courses.append(c)
        witnesses[name] = actions
    (ROOT/'cases.json').write_text(json.dumps(courses, indent=2)+'\n', encoding='utf-8')
    packed = base64.b64encode(zlib.compress(json.dumps(witnesses).encode(), 9)).decode()
    (ROOT/'_author'/'witnesses.dat').write_text(packed, encoding='ascii')
    print('Built 18 visible, verified coin courses. No hidden cases.')


if __name__ == '__main__':
    main()
