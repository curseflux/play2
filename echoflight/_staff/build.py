"""Author-only course generation; construct and verify feasible trajectories."""
import base64
import json
import math
import pathlib
import random
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulator import World, opening

STYLES = ('echo', 'sweep', 'slalom', 'temptation', 'narrow', 'endurance')
PUBLIC = [(f'E{i + 1:02}', 9713 + 43 * i, s) for i, s in enumerate(STYLES)]
PRIVATE = [(f'X{i + 1:02}', 15091 + 61 * i, STYLES[1 + i % 5]) for i in range(12)]


def build(name, seed, style):
    if style not in STYLES:
        raise ValueError(style)
    for attempt in range(120):
        result = construct(name, seed + 7919 * attempt, style)
        if result:
            return result
    raise RuntimeError(f'could not construct {name}')


def construct(name, seed, style):
    rng = random.Random(seed)
    dt = rng.choice((0.07, 0.09, 0.11))
    scale = rng.uniform(0.9, 1.1)
    p = dict(dt=dt, gravity=24 * scale * (0.1 / dt) ** 2,
             flap_speed=19 * scale * 0.1 / dt,
             fall_limit=34 * scale * 0.1 / dt,
             speed=rng.uniform(21, 28), radius=rng.uniform(1.1, 1.6),
             height=rng.uniform(83, 98))
    count = 8 if style == 'endurance' else 5
    spacing = 34 if style == 'slalom' else 43
    centers = [32 + spacing * i + rng.randint(-2, 2) for i in range(count)]
    end = centers[-1] + 22
    dx = p['speed'] * dt
    c = dict(name=name, title=style.title(), physics=p,
             start=dict(y=p['height'] * rng.uniform(0.4, 0.6), vy=rng.uniform(-3, 3),
                        pending=style in ('slalom', 'endurance')),
             finish_x=(end - 0.25) * dx, limit=end + 5,
             required=0 if style == 'echo' else count - 1, gates=[], stars=[])
    w = World(c)
    phase = rng.uniform(-math.pi, math.pi)
    actions, frames = [], [w.snapshot()]
    for tick in range(end):
        target = p['height'] * (0.5 + 0.16 * math.sin(tick / 19 + phase))
        next_vy = p['flap_speed'] if w.pending else w.vy
        next_vy = max(-p['fall_limit'], next_vy - p['gravity'] * dt)
        next_y = w.y + next_vy * dt
        action = next_y + 0.18 * next_vy < target
        actions.append(action)
        w.step(action)
        if w.done and w.x < c['finish_x']:
            return None
        frames.append(w.snapshot())
    for i, tick in enumerate(centers):
        half_width = rng.uniform(2.5, 4.5)
        x = frames[tick]['x']
        amplitude = 0 if style == 'echo' else rng.uniform(4, 9)
        omega = rng.uniform(0.9, 1.6) * 0.1 / dt
        phase_g = rng.uniform(-math.pi, math.pi)
        crossing = [f for f in frames if abs(f['x'] - x) < half_width + p['radius']]
        relative = [f['y'] - amplitude * math.sin(omega * f['tick'] * dt + phase_g)
                    for f in crossing]
        margin = 2.5 if style == 'narrow' else 5 if style != 'echo' else 7
        gap = max(relative) - min(relative) + 2 * (p['radius'] + margin)
        center = (min(relative) + max(relative)) / 2
        if center - amplitude - gap / 2 < 2 or center + amplitude + gap / 2 > p['height'] - 2:
            return None
        gate = dict(x=x, half_width=half_width, center=center, gap=gap,
                    amplitude=amplitude, omega=omega, phase=phase_g)
        c['gates'].append(gate)
        star_tick = tick - (9 if style == 'temptation' else 3)
        c['stars'].append(dict(x=frames[star_tick]['x'], y=frames[star_tick]['y'],
                               radius=2.2 if style == 'narrow' else 3.2))
        if style == 'temptation':
            # This extra star stays inside solid gate material at all phases.
            decoy_y = center + amplitude + gap / 2 + 4
            if decoy_y + 1 < p['height']:
                c['stars'].append(dict(x=x, y=decoy_y, radius=0.7))
    c['stars'].sort(key=lambda s: s['x'])
    proof = World(c)
    for action in actions:
        proof.step(action)
        if proof.done:
            break
    if not proof.won or proof.collected < count:
        return None
    return c, actions[:proof.tick]


def encode(value):
    return base64.b64encode(zlib.compress(json.dumps(value).encode(), 9)).decode('ascii')


def main():
    visible, hidden, witnesses = [], [], {}
    for output, specs in ((visible, PUBLIC), (hidden, PRIVATE)):
        for name, seed, style in specs:
            course, actions = build(name, seed, style)
            output.append(course)
            witnesses[name] = actions
    (ROOT / 'visible.json').write_text(json.dumps(visible, indent=2) + '\n', encoding='utf-8')
    (ROOT / '_staff' / 'hidden.dat').write_text(encode(hidden), encoding='ascii')
    (ROOT / '_staff' / 'witnesses.dat').write_text(encode(witnesses), encoding='ascii')
    print('Built 6 visible and 12 hidden cases; every witness survives and meets the quota.')


if __name__ == '__main__':
    main()
