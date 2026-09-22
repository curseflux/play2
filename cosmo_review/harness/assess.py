"""Practice grader using the supplied engine.py without modifying it."""
import argparse
import base64
import copy
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
import zlib

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
sys.path.insert(0, str(PROJECT))
import engine
from replay import write_replay


def courses(hidden=False):
    if hidden:
        return json.loads(zlib.decompress(base64.b64decode(
            (ROOT / '_author' / 'hidden.dat').read_text(encoding='ascii'))))
    return json.loads((ROOT / 'visible.json').read_text(encoding='utf-8'))


def load_policy(name):
    options = {'current': PROJECT / 'solution.py',
               'old': PROJECT / 'solution_old.py'}
    path = options.get(name, Path(name))
    if not path.is_absolute() and not path.exists():
        path = PROJECT / path
    spec = importlib.util.spec_from_file_location('candidate_policy', path)
    if spec is None or spec.loader is None:
        raise ValueError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, 'should_bounce', None)):
        raise ValueError(f'{path} has no should_bounce(params)')
    return module


def reason(course, cosmo, lost, won, error):
    if error:
        return error
    if won:
        return 'complete'
    if lost:
        if cosmo['y'] + cosmo['height'] > course['canvasHeight'] - course['groundHeight']:
            return 'ground collision'
        for i, p in enumerate(course['pipes']):
            if engine.check_collision(cosmo, p, course['pipeWidth']):
                edge = 'top' if cosmo['y'] < p['topHeight'] else 'bottom'
                return f'pipe {i + 1} {edge} collision'
        return 'collision'
    return 'frame limit'


def run(course, module, record=False):
    params = copy.deepcopy(course)
    observations = []
    peak = 0.0
    error = None
    def decide(obs):
        nonlocal peak
        before = time.perf_counter()
        result = module.should_bounce(obs)
        peak = max(peak, 1000 * (time.perf_counter() - before))
        if not isinstance(result, dict) or type(result.get('shouldBounce')) is not bool:
            raise ValueError('should_bounce must return a dict with bool shouldBounce')
        if record:
            entry = dict(frame=obs['frameNumber'], x=obs['cosmo']['x'],
                         y=obs['cosmo']['y'], velocity=obs['cosmo']['velocity'],
                         action=result['shouldBounce'])
            if 'log' in result:
                entry['log'] = str(result['log'])[:1000]
            observations.append(entry)
        return result
    saved = engine.should_bounce
    try:
        engine.should_bounce = decide
        _, _, lost, won, score = engine.simulate_game(params)
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'
        lost, won, score = True, False, 0
    finally:
        engine.should_bounce = saved
    total = len(course['pipes'])
    final = params['cosmo']
    status = reason(course, final, lost, won, error)
    result = dict(name=course['mapName'], challenge=course.get('challenge', ''),
                  passed=bool(won and not error), score=score, total=total,
                  progress=score / total, frames=len(observations), reason=status,
                  max_ms=peak)
    if record:
        observations.append(dict(frame=len(observations), x=final['x'],
                                 y=final['y'], velocity=final['velocity'],
                                 action=None, log=status))
    return result, observations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    test = commands.add_parser('test')
    test.add_argument('--all', action='store_true')
    test.add_argument('--case')
    replay = commands.add_parser('replay')
    replay.add_argument('case')
    stress = commands.add_parser('stress')
    stress.add_argument('--count', type=int, default=20)
    stress.add_argument('--seed', type=int, default=1)
    for command in (test, replay, stress):
        command.add_argument('--policy', default='current',
                             help='current, old, or a Python file path')
    args = parser.parse_args(argv)
    visible = courses()
    if args.command == 'list':
        for c in visible:
            print(f"{c['mapName']:<4} {c['challenge']:<12} {len(c['pipes'])} pipes")
        return 0
    if args.command == 'test' and args.case and args.all:
        parser.error('choose --case or --all')
    if args.command == 'stress' and args.count < 1:
        parser.error('--count must be positive')
    try:
        module = load_policy(args.policy)
    except Exception as exc:
        print(f'Cannot load policy: {type(exc).__name__}: {exc}')
        return 2
    if args.command == 'replay' or (args.command == 'test' and args.case):
        selected = [c for c in visible if c['mapName'] == args.case]
        if not selected:
            parser.error('unknown visible case; run list')
    elif args.command == 'stress':
        from _author.build import STYLES, build
        rng = random.Random(args.seed)
        selected = [build(f'R{i+1:03}', rng.randrange(1 << 30),
                          STYLES[1 + i % (len(STYLES)-1)])[0]
                    for i in range(args.count)]
    else:
        selected = list(visible)
        if args.all:
            private = courses(True)
            random.Random(851).shuffle(private)
            selected.extend(private)
    results = []
    for c in selected:
        result, frames = run(c, module, args.command == 'replay')
        results.append(result)
        label = 'PASS' if result['passed'] else 'FAIL'
        if c['mapName'].startswith('X'):
            print(f"{label} {result['name']}", flush=True)
        else:
            print(f"{label} {result['name']} {result['challenge']:<12} "
                  f"{result['score']}/{result['total']} pipes  "
                  f"{result['reason']}", flush=True)
        if args.command == 'replay':
            path = ROOT / 'replays' / f"{c['mapName']}.html"
            write_replay(path, c, result, frames)
            print(f'Replay: {path}')
    count = sum(r['passed'] for r in results)
    average = sum(r['progress'] for r in results) / len(results)
    peak = max(r['max_ms'] for r in results)
    print(f'\nPassed {count}/{len(results)} | mean pipe progress '
          f'{average * 100:.1f}% | slowest decision {peak:.2f} ms')
    if peak > 40:
        print('Advisory: some decisions exceeded the 40 ms practice budget.')
    return 0 if args.command == 'replay' or count == len(results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
