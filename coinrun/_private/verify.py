"""Author-only mechanics and feasibility checks. No learner solution."""
import base64
import json
import pathlib
import sys
import types
import unittest
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from world import World
from run import load_cases, run_case
from _private.courses import STYLES, build


def fixture(**changes):
    case = dict(name="fixture", description="Unit test", y0=5, vy0=0,
                physics=dict(dt=1, gravity=0, bounce_velocity=3, max_fall_speed=10,
                             scroll_speed=1, radius=0.5, ceiling=10),
                max_frames=10, finish_x=6, coin_target=1, pipe_sight=2,
                coin_lookahead=3, pipes=[], coins=[])
    case.update(changes)
    return case


class Mechanics(unittest.TestCase):
    def test_velocity_reset_then_gravity_and_cap(self):
        case = fixture(vy0=9)
        case["physics"].update(gravity=1)
        world = World(case)
        world.step(True)
        self.assertEqual(world.vy, 2)
        self.assertEqual(world.y, 7)
        world = World(fixture(vy0=-20))
        world.step(False)
        self.assertEqual(world.vy, -10)

    def test_one_coin_at_a_time_and_no_double_credit(self):
        coins = [dict(x=1, y=5, radius=0.25), dict(x=4, y=5, radius=0.25)]
        world = World(fixture(coins=coins))
        self.assertEqual(world.observe()["coin"]["id"], 0)
        world.step(False)
        self.assertEqual(world.coins_collected, 1)
        self.assertEqual(world.observe()["coin"]["id"], 1)
        world.step(False)
        self.assertEqual(world.coins_collected, 1)

    def test_missed_coin_disappears_without_reward_and_no_sight(self):
        coins = [dict(x=1, y=9, radius=0.25), dict(x=4, y=5, radius=0.25)]
        world = World(fixture(coins=coins))
        world.step(False)
        self.assertEqual(world.observe()["coin"]["id"], 0)
        world.step(False)
        self.assertEqual(world.coin_states[0], "missed")
        self.assertEqual(world.coins_collected, 0)
        self.assertEqual(world.observe()["coin"]["id"], 1)
        world = World(fixture(coins=coins[1:], coin_lookahead=1))
        self.assertIsNone(world.observe()["coin"])

    def test_fatal_frame_does_not_collect(self):
        pipe = dict(x=1, half_width=0.25, gap_lo=1, gap_hi=3)
        world = World(fixture(pipes=[pipe], coins=[dict(x=1, y=5, radius=0.25)]))
        world.step(False)
        self.assertTrue(world.done)
        self.assertEqual(world.coins_collected, 0)

    def test_exact_boundaries(self):
        pipe = dict(x=1, half_width=0.25, gap_lo=4.5, gap_hi=5.5)
        world = World(fixture(pipes=[pipe]))
        world.step(False)
        self.assertFalse(world.done)
        world = World(fixture(y0=0.5))
        world.step(False)
        self.assertEqual(world.reason, "fell below screen")
        world = World(fixture(y0=9.5))
        world.step(False)
        self.assertEqual(world.reason, "hit ceiling")

    def test_finish_requires_coins_and_errors_score_zero(self):
        no_coin = fixture(finish_x=3)
        result, _ = run_case(no_coin, types.SimpleNamespace(act=lambda obs: False))
        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 50)
        with_coin = fixture(finish_x=3, coins=[dict(x=1, y=5, radius=0.25)])
        result, _ = run_case(with_coin, types.SimpleNamespace(act=lambda obs: False))
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 100)
        for invalid in (None, 0, 1, "bounce"):
            result, _ = run_case(with_coin, types.SimpleNamespace(act=lambda obs, a=invalid: a))
            self.assertEqual(result["score"], 0)
            self.assertFalse(result["passed"])

    def test_debug_alignment_and_observation_isolation(self):
        policy = types.SimpleNamespace(DEBUG={})
        def act(obs):
            policy.DEBUG["frame"] = obs["frame"]
            obs["y"] = 999
            return False
        policy.act = act
        _, frames = run_case(fixture(), policy, record=True)
        self.assertEqual(frames[0]["y"], 5)
        for frame in frames[:-1]:
            self.assertEqual(frame["debug"]["frame"], frame["frame"])
        self.assertIsNone(frames[-1]["action"])


class Feasibility(unittest.TestCase):
    def check_witness(self, case, actions):
        world = World(case)
        for action in actions:
            self.assertFalse(world.done)
            world.step(action)
        self.assertTrue(world.passed, (case["name"], world.reason))
        self.assertGreaterEqual(world.coins_collected, case["coin_target"])
        self.assertEqual(world.result()["score"], 100)

    def test_all_packaged_cases(self):
        data = (ROOT / "_private" / "witnesses.dat").read_text()
        witnesses = json.loads(zlib.decompress(base64.b64decode(data)))
        for case in load_cases() + load_cases(hidden=True):
            with self.subTest(case=case["name"]):
                self.check_witness(case, witnesses[case["name"]])

    def test_generated_variants(self):
        for style in STYLES:
            for seed in range(20):
                with self.subTest(style=style, seed=seed):
                    case, actions = build("random", seed, style)
                    self.check_witness(case, actions)


if __name__ == "__main__":
    unittest.main(verbosity=2)
