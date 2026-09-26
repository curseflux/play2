"""Cosmo Coins practice grader: all cases visible."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import random
import time

from engine import World
from replay import write_replay

ROOT = Path(__file__).resolve().parent


def courses():
    return json.loads((ROOT/'cases.json').read_text(encoding='utf-8'))


def load_policy(filename):
    path = Path(filename)
    if not path.is_absolute():
        path = ROOT/path
    spec = importlib.util.spec_from_file_location('candidate_policy', path)
    if spec is None or spec.loader is None:
        raise ValueError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, 'should_bounce', None)):
        raise ValueError('policy must define should_bounce(params)')
    return module


def run(course, module, record=False):
    world, frames, peak, error = World(course), [], 0.0, None
    while not world.done:
        obs = copy.deepcopy(world.observe())
        before = time.perf_counter()
        try:
            answer = module.should_bounce(obs)
            if not isinstance(answer, dict) or type(answer.get('shouldBounce')) is not bool:
                raise ValueError('return a dict containing bool shouldBounce')
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
            peak = max(peak, 1000*(time.perf_counter()-before))
            break
        peak = max(peak, 1000*(time.perf_counter()-before))
        action = answer['shouldBounce']
        if record:
            f = world.snapshot()
            f.update(action=action, log=str(answer.get('log', ''))[:2000])
            frames.append(f)
        world.step(action)
    result = world.result(error)
    result['max_ms'] = peak
    if record:
        f = world.snapshot()
        f.update(action=None, log=result['reason'])
        frames.append(f)
    return result, frames


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    test = commands.add_parser('test')
    test.add_argument('--case')
    test.add_argument('--all', action='store_true', help='same as default: every public case')
    replay = commands.add_parser('replay')
    replay.add_argument('case')
    stress = commands.add_parser('stress')
    stress.add_argument('--count', type=int, default=20)
    stress.add_argument('--seed', type=int, default=1)
    for command in (test, replay, stress):
        command.add_argument('--policy', default='solution.py')
    args = parser.parse_args(argv)
    visible = courses()
    if args.command == 'list':
        for c in visible:
            print(f"{c['mapName']} {c['challenge']:<12} need {c['coinTarget']}/{len(c['coins'])} coins")
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
            parser.error('unknown case; run list')
    elif args.command == 'stress':
        from _author.build import STYLES, build
        rng = random.Random(args.seed)
        selected = [build(f'R{i+1:03}', rng.randrange(1 << 30),
                          STYLES[1+i%(len(STYLES)-1)])[0]
                    for i in range(args.count)]
    else:
        selected = visible
    results = []
    for c in selected:
        result, frames = run(c, module, args.command == 'replay')
        results.append(result)
        label = 'PASS' if result['passed'] else 'FAIL'
        print(f"{label} {result['name']} {result['challenge']:<12} "
              f"coins {result['coins']}/{result['target']}  "
              f"distance {100*result['progress']:.1f}%  "
              f"score {result['score']:.1f}  {result['reason']}", flush=True)
        if args.command == 'replay':
            path = ROOT/'replays'/f"{c['mapName']}.html"
            write_replay(path, c, result, frames)
            print(f'Replay: {path}')
    passed = sum(r['passed'] for r in results)
    peak = max(r['max_ms'] for r in results)
    print(f'\nPassed {passed}/{len(results)} | mean score '
          f"{sum(r['score'] for r in results)/len(results):.1f}/100 | "
          f'slowest decision {peak:.2f} ms')
    if peak > 40:
        print('Advisory: some decisions exceeded the 40 ms practice budget.')
    return 0 if args.command == 'replay' or passed == len(results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
