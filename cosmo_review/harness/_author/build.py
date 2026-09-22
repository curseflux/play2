"""Construct hard courses around a verified action trajectory.

This is author infrastructure, not a policy for the practice exercise.
"""
from __future__ import annotations

import base64
import json
import math
from pathlib import Path
import random
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import engine

OUT = Path(__file__).resolve().parents[1]
STYLES = ('warmup', 'entry_trap', 'adjacent', 'narrow', 'reversal',
          'overlap', 'ceiling', 'floor', 'long_run')
PUBLIC = [(f'C{i + 1:02}', 7079 + 97 * i, style)
          for i, style in enumerate(STYLES)]
EXTRA = [(f'X{i + 1:02}', 19001 + 83 * i, STYLES[1 + i % 8])
           for i in range(16)]


def clone(obj):
    return json.loads(json.dumps(obj))


def flight(course, actions, stop=None):
    """Use the supplied engine itself; capture exact pre-decision states."""
    frames = []
    def scripted(obs):
        frames.append(dict(x=obs['cosmo']['x'], y=obs['cosmo']['y'],
                           velocity=obs['cosmo']['velocity']))
        i = len(frames) - 1
        return {'shouldBounce': actions[i] if i < len(actions) else False}
    saved = engine.should_bounce
    params = clone(course)
    try:
        engine.should_bounce = scripted
        plan, _, lost, won, score = engine.simulate_game(params)
    finally:
        engine.should_bounce = saved
    return dict(frames=frames, final=params['cosmo'], lost=lost,
                won=won, score=score)


def base(seed, style):
    rng = random.Random(seed)
    speed = rng.choice((2.8, 3.0, 3.2))
    cosmo = dict(x=18., y=rng.uniform(95, 125), velocity=rng.uniform(-2, 2),
                 gravity=rng.uniform(.55, .75), bouncePower=rng.uniform(-8.2, -6.8),
                 width=18., height=18.)
    n = 155 if style == 'long_run' else 105
    course = dict(mapName=style, cosmo=cosmo, pipes=[], pipeSpeed=speed,
                  frameTime=16, canvasHeight=250, canvasWidth=800,
                  groundHeight=20, pipeWidth=14. if style == 'narrow' else 18.)
    # A scripted feedback flight supplies a trajectory. It is kept private and
    # replayed through engine.simulate_game to verify every final course.
    state = clone(cosmo)
    actions = []
    phase = rng.uniform(-math.pi, math.pi)
    for tick in range(n):
        target = (105 + 24 * math.sin(tick / rng.uniform(21, 29) + phase)
                  if style in ('adjacent', 'reversal', 'overlap')
                  else 105 + 18 * math.sin(tick / 28 + phase))
        if style == 'ceiling':
            target -= 42
        if style == 'floor':
            target += 49
        bounce = state['y'] + state['height'] / 2 + 2.8 * state['velocity'] > target + 3
        actions.append(bool(bounce))
        velocity = state['velocity'] + state['gravity']
        state['y'] += velocity
        state['velocity'] = velocity
        if state['y'] + state['height'] > course['canvasHeight'] - course['groundHeight']:
            return None
        if state['y'] < 0:
            state['y'] = 0
            state['velocity'] = 0
        state['x'] += speed
        if bounce:
            state['velocity'] = state['bouncePower']
    course['pipes'] = [dict(position=1e6, topHeight=0, gap=225)]
    proof = flight(course, actions)
    if len(proof['frames']) <= n:
        # The distant sentinel prevents the engine from completing early.
        return None
    course['pipes'] = []
    return course, actions, proof['frames'], rng


def add_pipe(course, frames, tick, margin, width=None):
    width = width or course['pipeWidth']
    x = frames[tick]['x']
    w = course['cosmo']['width']
    crossing = [f['y'] for f in frames
                if f['x'] + w > x and f['x'] < x + width]
    if not crossing:
        return None
    lo = min(crossing) - margin
    hi = max(crossing) + course['cosmo']['height'] + margin
    if lo < 0 or hi > course['canvasHeight'] - course['groundHeight']:
        return None
    return dict(position=x, topHeight=lo, gap=hi-lo)


def candidate(name, seed, style):
    first = base(seed, style)
    if first is None:
        return None
    course, actions, frames, rng = first
    n = len(frames) - 1
    if style == 'warmup':
        ticks = [29, 74]
    elif style == 'long_run':
        ticks = [24, 50, 76, 102, 128]
    elif style in ('adjacent', 'reversal', 'overlap'):
        start = rng.randrange(30, 54)
        ticks = [start, start + (6 if style == 'overlap' else 11), start + 42]
    elif style == 'entry_trap':
        ticks = [rng.randrange(29, 65), 85]
    else:
        ticks = [rng.randrange(30, 53), 77]
    if ticks[-1] + 15 >= n:
        return None
    margin = {'warmup': 10, 'entry_trap': 1.5, 'adjacent': 3.5,
              'narrow': 1.0, 'reversal': 2.5, 'overlap': 4.5,
              'ceiling': 3, 'floor': 3, 'long_run': 4}[style]
    pipes = [add_pipe(course, frames, tick, margin) for tick in ticks]
    if any(p is None for p in pipes):
        return None
    if style == 'warmup':
        # A genuine flight-control baseline with very generous pipe openings.
        pipes = [dict(position=p['position'], topHeight=0.,
                      gap=course['canvasHeight']-course['groundHeight'])
                 for p in pipes]
    course['pipes'] = pipes
    course['mapName'] = name
    final = flight(course, actions)
    if final['lost'] or not final['won'] or final['score'] != len(pipes):
        return None

    tags = []
    if style == 'entry_trap':
        pipe = pipes[0]
        entry = next((i for i, f in enumerate(frames) if
                      f['x'] + course['cosmo']['width'] > pipe['position']
                      and f['x'] < pipe['position'] + course['pipeWidth']), None)
        if entry is None or actions[entry]:
            return None
        altered = actions[:]
        altered[entry] = True
        bad = flight(course, altered)
        if (not bad['lost'] or not (entry < len(bad['frames']) <= entry + 7)
                or bad['final']['y'] >= pipe['topHeight']):
            return None
        tags.append('bounce_at_entry_hits_top')
    if style in ('adjacent', 'reversal', 'overlap'):
        a, b = pipes[:2]
        offset = abs((a['topHeight'] + a['gap']/2) - (b['topHeight'] + b['gap']/2))
        free = b['position'] - (a['position'] + course['pipeWidth'])
        if offset < 10 or free > (3 * course['pipeSpeed'] if style == 'overlap'
                                   else course['cosmo']['width'] + 3 * course['pipeSpeed']):
            return None
        if style == 'overlap' and free >= course['cosmo']['width']:
            return None
        tags.append('close_misaligned_gaps')
    if style == 'narrow' and any(p['gap'] > 45 for p in pipes):
        return None
    if style == 'ceiling' and min(f['y'] for f in final['frames']) > 36:
        return None
    if style == 'floor' and max(f['y'] for f in final['frames']) < 155:
        return None
    if style == 'reversal':
        a, b = pipes[:2]
        if abs((a['topHeight'] + a['gap']/2) - (b['topHeight'] + b['gap']/2)) < 16:
            return None
    course['challenge'] = style
    course['tags'] = tags
    return course, actions[:len(final['frames'])]


def build(name, seed, style):
    if style not in STYLES:
        raise ValueError(style)
    for i in range(500):
        result = candidate(name, seed + 104729 * i, style)
        if result:
            return result
    raise RuntimeError(f'No feasible {style} course for {name}')


def packed(value):
    return base64.b64encode(zlib.compress(json.dumps(value).encode(), 9)).decode('ascii')


def main():
    visible, extra, witnesses = [], [], {}
    for dest, specs in ((visible, PUBLIC), (extra, EXTRA)):
        for name, seed, style in specs:
            course, actions = build(name, seed, style)
            dest.append(course)
            witnesses[name] = actions
            print(name, style, 'pipes', len(course['pipes']), 'gap',
                  [round(p['gap'], 1) for p in course['pipes']], flush=True)
    (OUT / 'visible.json').write_text(json.dumps(visible + extra, indent=2)+'\n', encoding='utf-8')
    (OUT / '_author' / 'witnesses.dat').write_text(packed(witnesses), encoding='ascii')
    print('Verified', len(visible) + len(extra), 'visible courses.')


if __name__ == '__main__':
    main()
