"""Author-only verification. Do not read during the timed attempt."""
import copy
import math
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulator import World, opening
from grade import courses, run
from _staff.build import build, STYLES
import base64
import json
import zlib


def simple():
    return dict(name='unit', title='unit', start=dict(y=50., vy=0., pending=False),
                physics=dict(dt=0.1, gravity=10., flap_speed=10., fall_limit=20.,
                             speed=10., radius=1., height=100.),
                finish_x=100., limit=200, required=0, gates=[], stars=[])


class Checks(unittest.TestCase):
    def test_delay_and_no_cancellation(self):
        w = World(simple())
        w.step(True)
        self.assertAlmostEqual(w.vy, -1.)
        self.assertAlmostEqual(w.y, 49.9)
        self.assertTrue(w.pending)
        w.step(False)
        self.assertAlmostEqual(w.vy, 9.)
        self.assertAlmostEqual(w.y, 50.8)
        self.assertFalse(w.pending)
        w.step(False)
        self.assertAlmostEqual(w.vy, 8.)

    def test_initial_pending_and_repeated_commands(self):
        c = simple()
        c['start']['pending'] = True
        w = World(c)
        w.step(True)
        w.step(True)
        self.assertAlmostEqual(w.vy, 9.)
        self.assertAlmostEqual(w.y, 51.8)

    def test_gate_uses_new_time(self):
        c = simple()
        c['gates'] = [dict(x=1., half_width=.4, center=49.9, gap=4.,
                           amplitude=10., omega=math.pi / .2, phase=0.)]
        w = World(c)
        self.assertTrue(w.observe()['gates'][0]['gap_lo'] < 50 < w.observe()['gates'][0]['gap_hi'])
        w.step(False)
        self.assertEqual(w.reason, 'gate 1 collision')

    def test_edges(self):
        c = simple()
        c['start']['vy'] = 1.
        c['gates'] = [dict(x=1., half_width=.5, center=50., gap=2.,
                           amplitude=0., omega=0., phase=0.)]
        w = World(c)
        w.step(False)
        self.assertFalse(w.done)  # exact fit is legal
        c['start']['y'] = 1.
        c['gates'] = []
        w = World(c)
        w.step(False)
        self.assertEqual(w.reason, 'floor')

    def test_fatal_frame_never_awards_star(self):
        c = simple()
        c['start']['y'] = 1.1
        c['stars'] = [dict(x=1., y=1., radius=1.)]
        w = World(c)
        w.step(False)
        self.assertTrue(w.done)
        self.assertEqual(w.collected, 0)

    def test_stars_count_once_and_visibility_updates(self):
        c = simple()
        c['stars'] = [dict(x=x, y=49.9, radius=2.) for x in (1., 8., 15.)]
        w = World(c)
        self.assertEqual(len(w.observe()['stars']), 2)
        w.step(False)
        self.assertEqual(w.collected, 1)
        self.assertEqual(w.observe()['stars'][0]['id'], 1)
        w.step(False)
        self.assertEqual(w.collected, 1)

    def test_completion_and_errors(self):
        c = simple()
        c.update(finish_x=1., required=1)
        c['stars'] = [dict(x=1., y=49.9, radius=1.)]
        w = World(c)
        w.step(False)
        self.assertTrue(w.won)
        self.assertEqual(w.result()['score'], 100.)
        result, _ = run(c, types.SimpleNamespace(act=lambda _: 1))
        self.assertEqual(result['score'], 0.)
        self.assertIn('illegal action', result['reason'])
        c['stars'] = []
        w = World(c)
        w.step(False)
        self.assertEqual(w.reason, 'finished below star target')
        c.update(finish_x=100., limit=1)
        w = World(c)
        w.step(False)
        self.assertEqual(w.reason, 'timeout')

    def test_observation_copies_and_debug_alignment(self):
        c = simple()
        w = World(c)
        obs = w.observe()
        obs['physics']['gravity'] = -1000
        self.assertEqual(c['physics']['gravity'], 10.)
        c['limit'] = 3
        module = types.SimpleNamespace(DEBUG={})
        def policy(obs):
            module.DEBUG['seen_tick'] = obs['tick']
            return obs['tick'] == 0
        module.act = policy
        _, frames = run(c, module, record=True)
        self.assertFalse(frames[0]['pending'])
        self.assertTrue(frames[0]['action'])
        self.assertTrue(frames[1]['pending'])
        for f in frames[:-1]:
            self.assertEqual(f['debug']['seen_tick'], f['tick'])

    def test_all_packaged_witnesses(self):
        witnesses = json.loads(zlib.decompress(base64.b64decode(
            (ROOT / '_staff' / 'witnesses.dat').read_text())))
        for c in courses() + courses(True):
            with self.subTest(case=c['name']):
                before = copy.deepcopy(c)
                w = World(c)
                for action in witnesses[c['name']]:
                    w.step(action)
                self.assertTrue(w.won, w.result())
                self.assertEqual(before, c)
                for q in c['gates']:
                    self.assertGreater(q['center'] - q['amplitude'] - q['gap'] / 2, 0)
                    self.assertLess(q['center'] + q['amplitude'] + q['gap'] / 2,
                                    c['physics']['height'])

    def test_generated_courses(self):
        for style in STYLES:
            for seed in range(20):
                c, actions = build('verify', seed * 8191 + 7, style)
                w = World(c)
                for action in actions:
                    w.step(action)
                self.assertTrue(w.won, (style, seed, w.result()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
