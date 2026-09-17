"""Author-only verification. Reads witnesses; do not open during the mock."""
import base64
import json
import math
import pathlib
import sys
import tempfile
import types
import unittest
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from arena.engine import Arena, circle_hits_rect
from arena.replay import write_replay
from exam import hidden_cases, run_case, visible_cases
from _exam.factory import FAMILIES, build


def empty_course(**physics):
    p = dict(dt=0.05, gravity=300, drag=0, impulse=100, recharge=4,
             rise_cap=200, fall_cap=200, speed=100, radius=8)
    p.update(physics)
    return dict(name="unit", height=400, start=dict(y=200, vy=40, cooldown=0),
                physics=p, limit=100, sight=3,
                gates=[dict(x=10000, half_width=10, centre=200, gap=200,
                            amplitude=0, period=100, phase=0)])


class EngineTests(unittest.TestCase):
    def test_additive_kick_and_cooldown_order(self):
        env = Arena(empty_course())
        env.step("pulse")
        self.assertAlmostEqual(env.vy, -45)
        self.assertAlmostEqual(env.y, 197.75)
        self.assertEqual((env.tick, env.cooldown, env.pulses), (1, 3, 1))
        for _ in range(3):
            env.step("pulse")
        self.assertEqual((env.cooldown, env.pulses), (0, 1))
        env.step("pulse")
        self.assertEqual(env.pulses, 2)

    def test_drag_and_caps(self):
        env = Arena(empty_course(drag=2))
        env.step("pulse")
        self.assertAlmostEqual(env.vy, -39)
        env = Arena(empty_course(rise_cap=20))
        env.step("pulse")
        self.assertEqual(env.vy, -20)
        env = Arena(empty_course(fall_cap=45))
        env.step("glide")
        self.assertEqual(env.vy, 45)

    def test_circle_corner_and_tangency(self):
        self.assertFalse(circle_hits_rect(2.1, 17.9, 8, 10, 0, 20, 10))
        self.assertTrue(circle_hits_rect(2, 5, 8, 10, 0, 20, 10))
        self.assertFalse(circle_hits_rect(1.99, 5, 8, 10, 0, 20, 10))

    def test_shutter_uses_new_tick(self):
        case = empty_course(dt=1, gravity=0, speed=1, radius=1)
        case["start"].update(y=5, vy=0)
        case["gates"] = [dict(x=1, half_width=0.5, centre=5, gap=4,
                              amplitude=2, period=4, phase=0)]
        env = Arena(case)
        self.assertEqual(env.observe()["gates"][0]["top"], 3)
        env.step("glide")
        self.assertTrue(env.finished)
        self.assertIn("upper shutter", env.reason)

    def test_known_success_is_terminal_and_partial_progress_is_retained(self):
        case = empty_course(dt=0.1, gravity=0, speed=100, radius=1)
        case["start"].update(y=200, vy=0)
        case["gates"] = [dict(x=10, half_width=1, centre=200, gap=100,
                              amplitude=0, period=100, phase=0)]
        env = Arena(case)
        env.step("glide")
        env.step("glide")
        self.assertTrue(env.won)
        self.assertEqual(env.result()["score"], 100)
        with self.assertRaises(RuntimeError):
            env.step("glide")
        case["gates"].append(dict(x=30, half_width=1, centre=50, gap=20,
                                  amplitude=0, period=100, phase=0))
        env = Arena(case)
        while not env.finished:
            env.step("glide")
        self.assertFalse(env.won)
        self.assertEqual(env.result()["score"], 50)

    def test_submission_errors_and_snapshot_alignment(self):
        for action in (True, None, "jump", []):
            agent = types.SimpleNamespace(decide=lambda obs, a=action: a)
            result, _ = run_case(empty_course(), agent)
            self.assertFalse(result["passed"])
            self.assertEqual(result["score"], 0)
            self.assertIn("illegal action", result["reason"])
        def broken(obs):
            raise ValueError("example")
        result, _ = run_case(empty_course(), types.SimpleNamespace(decide=broken))
        self.assertIn("ValueError", result["reason"])
        agent = types.SimpleNamespace(DEBUG={})
        def decide(obs):
            agent.DEBUG["tick"] = obs["clock"]["tick"]
            obs["bird"]["y"] = -9999
            return "glide"
        agent.decide = decide
        result, trace = run_case(empty_course(), agent, record=True)
        self.assertEqual(trace[0]["y"], 200)
        for frame in trace[:-1]:
            self.assertEqual(frame["tick"], frame["debug"]["tick"])
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "replay.html"
            write_replay(path, empty_course(), result, trace)
            page = path.read_text(encoding="utf-8")
            self.assertNotIn("__DATA__", page)
            self.assertIn('"openings"', page)


class CourseTests(unittest.TestCase):
    def check_flight(self, case, actions):
        self.assertTrue(case["gates"])
        self.assertEqual(sorted(g["x"] for g in case["gates"]), [g["x"] for g in case["gates"]])
        for g in case["gates"]:
            self.assertGreater(g["gap"], 2 * case["physics"]["radius"])
            self.assertGreater(g["centre"] - g["amplitude"] - g["gap"] / 2, 0)
            self.assertLess(g["centre"] + g["amplitude"] + g["gap"] / 2, case["height"])
        env = Arena(case)
        for action in actions:
            self.assertFalse(env.finished)
            if action == "pulse":
                self.assertEqual(env.cooldown, 0)
            env.step(action)
        self.assertTrue(env.won, (case["name"], env.reason))

    def test_packaged_witnesses(self):
        encoded = (ROOT / "_exam" / "witnesses.dat").read_text()
        witnesses = json.loads(zlib.decompress(base64.b64decode(encoded)))
        for case in visible_cases() + hidden_cases():
            with self.subTest(name=case["name"]):
                self.check_flight(case, witnesses[case["name"]])

    def test_generated_variants(self):
        for family in FAMILIES:
            for seed in range(20):
                with self.subTest(family=family, seed=seed):
                    case, actions = build("random", seed, family)
                    self.check_flight(case, actions)


if __name__ == "__main__":
    unittest.main(verbosity=2)
