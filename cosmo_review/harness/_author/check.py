"""Author verification of courses, counterfactuals, and grader behavior."""
import base64
import copy
import json
import pathlib
import sys
import unittest
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from assess import courses, run, reason
from _author.build import STYLES, build, flight


def witnesses():
    return json.loads(zlib.decompress(base64.b64decode(
        (ROOT / '_author' / 'witnesses.dat').read_text(encoding='ascii'))))


class CheckCourses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_courses = courses() + courses(True)
        cls.actions = witnesses()

    def test_all_25_packaged_routes(self):
        self.assertEqual(len(self.all_courses), 25)
        for c in self.all_courses:
            with self.subTest(c['mapName']):
                before = copy.deepcopy(c)
                result = flight(c, self.actions[c['mapName']])
                self.assertFalse(result['lost'])
                self.assertTrue(result['won'])
                self.assertEqual(result['score'], len(c['pipes']))
                self.assertEqual(before, c)

    def test_entry_trap_is_really_a_top_collision(self):
        traps = [c for c in self.all_courses if c['challenge'] == 'entry_trap']
        self.assertGreaterEqual(len(traps), 3)
        for c in traps:
            with self.subTest(c['mapName']):
                actions = self.actions[c['mapName']][:]
                pipe = c['pipes'][0]
                frames = flight(c, actions)['frames']
                entry = next(i for i, f in enumerate(frames)
                             if f['x'] + c['cosmo']['width'] > pipe['position']
                             and f['x'] < pipe['position'] + c['pipeWidth'])
                self.assertFalse(actions[entry])
                actions[entry] = True
                bad = flight(c, actions)
                self.assertTrue(bad['lost'])
                self.assertFalse(bad['won'])
                self.assertLessEqual(len(bad['frames']), entry + 7)
                self.assertLess(bad['final']['y'], pipe['topHeight'])

    def test_visible_entry_route_dips_below_gap_then_rises(self):
        c = next(c for c in courses() if c['mapName'] == 'C02')
        actions = self.actions['C02']
        frames = flight(c, actions)['frames']
        pipe = c['pipes'][0]
        entry = next(i for i, f in enumerate(frames)
                     if f['x'] + c['cosmo']['width'] > pipe['position']
                     and f['x'] < pipe['position'] + c['pipeWidth'])
        safe_bottom_y = pipe['topHeight'] + pipe['gap'] - c['cosmo']['height']
        self.assertGreater(frames[entry - 1]['y'], safe_bottom_y)
        self.assertTrue(actions[entry - 2])
        self.assertFalse(actions[entry])
        self.assertLessEqual(frames[entry]['y'], safe_bottom_y)

    def test_close_misaligned_and_simultaneous_overlap(self):
        near = [c for c in self.all_courses
                if c['challenge'] in ('adjacent', 'reversal', 'overlap')]
        for c in near:
            with self.subTest(c['mapName']):
                a, b = c['pipes'][:2]
                centers = [p['topHeight'] + p['gap']/2 for p in (a, b)]
                self.assertGreaterEqual(abs(centers[0] - centers[1]), 10)
                free = b['position'] - a['position'] - c['pipeWidth']
                self.assertLessEqual(free, c['cosmo']['width'] + 3*c['pipeSpeed'])
                if c['challenge'] == 'overlap':
                    frames = flight(c, self.actions[c['mapName']])['frames']
                    self.assertTrue(any(
                        f['x'] + c['cosmo']['width'] > a['position']
                        and f['x'] < a['position'] + c['pipeWidth']
                        and f['x'] + c['cosmo']['width'] > b['position']
                        and f['x'] < b['position'] + c['pipeWidth']
                        for f in frames))

    def test_narrow_close_to_bird_height(self):
        for c in self.all_courses:
            if c['challenge'] == 'narrow':
                with self.subTest(c['mapName']):
                    self.assertTrue(all(18 < p['gap'] <= 45 for p in c['pipes']))

    def test_80_fresh_verified_variants(self):
        for style in STYLES[1:]:
            for seed in range(10):
                with self.subTest(style=style, seed=seed):
                    c, actions = build('fresh', 431 + seed*9713, style)
                    r = flight(c, actions)
                    self.assertTrue(r['won'])
                    self.assertEqual(r['score'], len(c['pipes']))

    def test_grader_uses_selected_policy_and_copies_course(self):
        course = courses()[0]
        before = copy.deepcopy(course)
        class NoBounce:
            @staticmethod
            def should_bounce(_):
                return {'shouldBounce': False, 'log': 'observed'}
        result, frames = run(course, NoBounce(), record=True)
        self.assertFalse(result['passed'])
        self.assertEqual(len(frames), result['frames']+1)
        self.assertEqual(frames[0]['log'], 'observed')
        self.assertEqual(before, course)
        class Invalid:
            @staticmethod
            def should_bounce(_):
                return {'shouldBounce': 1}
        invalid, _ = run(course, Invalid())
        self.assertFalse(invalid['passed'])
        self.assertIn('ValueError', invalid['reason'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
