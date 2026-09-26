"""Author verification; keep off limits during a timed attempt."""
import base64
import copy
import json
from pathlib import Path
import sys
import types
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import World, touches_coin
from assess import courses, run
from _author.build import STYLES, build


def simple():
    return dict(mapName='unit', challenge='unit',
                cosmo=dict(x=0., y=30., velocity=0., gravity=1., bouncePower=-8.,
                           width=10., height=10.),
                coins=[], scrollSpeed=2., frameTime=16, canvasHeight=100.,
                canvasWidth=500., groundHeight=10., finishX=100., maxFrames=100,
                coinTarget=0)


class Checks(unittest.TestCase):
    def test_packaged_and_fresh_feasibility(self):
        witnesses = json.loads(zlib.decompress(base64.b64decode(
            (ROOT/'_author'/'witnesses.dat').read_text(encoding='ascii'))))
        maps = courses()
        self.assertEqual(len(maps), 18)
        for c in maps:
            before = copy.deepcopy(c)
            w = World(c)
            for action in witnesses[c['mapName']]:
                w.step(action)
            self.assertTrue(w.passed, w.result())
            self.assertEqual(before, c)
        for style in STYLES:
            for seed in range(10):
                c, actions = build('fresh', 59 + 701*seed, style)
                w = World(c)
                for action in actions:
                    w.step(action)
                self.assertTrue(w.passed, (style, seed, w.result()))

    def test_delayed_bounce_and_terminal_action(self):
        a, b = World(simple()), World(simple())
        a.step(True)
        b.step(False)
        self.assertEqual(a.cosmo['y'], 31.)
        self.assertEqual(a.cosmo['y'], b.cosmo['y'])
        self.assertEqual(a.cosmo['velocity'], -8.)
        a.step(False)
        self.assertEqual(a.cosmo['y'], 24.)
        c = simple()
        c['finishX'] = 2.
        w = World(c)
        w.step(True)
        self.assertTrue(w.passed)
        self.assertEqual(w.cosmo['velocity'], 1.)

    def test_floor_precedes_x_collection_and_bounce(self):
        c = simple()
        c['cosmo']['y'] = 80.
        c['coins'] = [dict(x=7., y=85., radius=2.)]
        w = World(c)
        w.step(True)
        self.assertEqual(w.reason, 'ground collision')
        self.assertEqual(w.cosmo['x'], 0.)
        self.assertEqual(w.collected, 0)
        self.assertEqual(w.cosmo['velocity'], 1.)
        c['cosmo'].update(y=80., velocity=-1.)
        w = World(c)
        w.step(False)
        self.assertFalse(w.done)  # Exact contact with ground is permitted.

    def test_ceiling_clamp(self):
        c = simple()
        c['cosmo'].update(y=0., velocity=-3.)
        w = World(c)
        w.step(False)
        self.assertEqual((w.cosmo['y'], w.cosmo['velocity']), (0., 0.))
        self.assertFalse(w.done)

    def test_circle_rectangle_pickup(self):
        bird = simple()['cosmo']
        self.assertTrue(touches_coin(bird, dict(x=12., y=35., radius=2.)))
        self.assertFalse(touches_coin(bird, dict(x=12., y=42., radius=2.)))
        self.assertTrue(touches_coin(bird, dict(x=5., y=35., radius=.1)))

    def test_multiple_coins_once_and_on_finish(self):
        c = simple()
        c.update(coinTarget=2, finishX=4.)
        c['coins'] = [dict(x=7., y=36., radius=2.), dict(x=8., y=37., radius=2.)]
        w = World(c)
        w.step(False)
        self.assertEqual(w.collected, 2)
        self.assertEqual(w.observe()['coins'], [])
        w.step(False)
        self.assertEqual(w.collected, 2)
        self.assertTrue(w.passed)
        c['finishX'] = 2.
        w = World(c)
        w.step(False)
        self.assertTrue(w.passed)

    def test_ground_bait_really_unreachable(self):
        for c in courses():
            if c['challenge'] != 'ground_bait':
                continue
            ground = c['canvasHeight']-c['groundHeight']
            decoys = [q for q in c['coins'] if q['y'] > ground]
            self.assertTrue(decoys)
            bird = dict(c['cosmo'])
            for coin in decoys:
                bird.update(x=coin['x']-bird['width']/2,
                            y=ground-bird['height'])
                self.assertFalse(touches_coin(bird, coin))

    def test_invalid_policy_and_observation_isolation(self):
        c = simple()
        invalid = types.SimpleNamespace(should_bounce=lambda _: {'shouldBounce':1})
        result, _ = run(c, invalid)
        self.assertEqual(result['score'], 0.)
        w = World(c)
        obs = w.observe()
        obs['cosmo']['gravity'] = 999
        self.assertEqual(w.cosmo['gravity'], 1.)


if __name__ == '__main__':
    unittest.main(verbosity=2)
