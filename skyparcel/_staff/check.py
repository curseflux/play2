"""Author-only validation, including hidden delivery witnesses."""
import base64
import json
import pathlib
import sys
import types
import unittest
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import Flight
from assess import courses, run
from _staff.build import STYLES, build


def fixture(**changes):
    case = dict(name="unit", title="Test", start=dict(y=50, vy=0, held=False, carrying=False),
                physics=dict(dt=1, gravity_empty=1, gravity_loaded=3, flap_speed=4,
                             fall_limit=10, speed=2, radius=1, height=100),
                gates=[], stations=[], finish_x=20, limit=20, required=1)
    case.update(changes)
    return case


class Mechanics(unittest.TestCase):
    def test_press_requires_release_before_retrigger(self):
        f = Flight(fixture())
        f.step("press")
        self.assertEqual((f.vy, f.held), (-3, True))
        f.step("press")
        self.assertEqual(f.vy, -2)
        f.step("release")
        self.assertEqual((f.vy, f.held), (-1, False))
        f.step("press")
        self.assertEqual(f.vy, -3)

    def test_cargo_gravity_changes_next_frame(self):
        stations = [dict(x=1, top=0, bottom=100, kind="pickup"),
                    dict(x=3, top=0, bottom=100, kind="depot")]
        f = Flight(fixture(stations=stations))
        f.step("release")
        self.assertEqual((f.vy, f.y, f.carrying), (1, 51, True))
        f.step("release")
        self.assertEqual((f.vy, f.y, f.carrying, f.delivered), (4, 55, False, 1))
        f.step("release")
        self.assertEqual((f.vy, f.delivered), (5, 1))

    def test_crossing_window_and_visibility(self):
        stations = [dict(x=1, top=50, bottom=52, kind="pickup"),
                    dict(x=3, top=0, bottom=1, kind="depot"),
                    dict(x=5, top=0, bottom=100, kind="depot")]
        f = Flight(fixture(stations=stations))
        self.assertEqual(len(f.observe()["stations"]), 2)
        f.step("release")
        self.assertTrue(f.carrying)  # Exact window edges are allowed.
        self.assertEqual(f.observe()["stations"][0]["id"], 1)
        f.step("release")
        self.assertEqual((f.carrying, f.delivered, f.station_states[1]), (True, 0, "missed"))
        f.step("release")
        self.assertEqual(f.delivered, 1)

    def test_collision_precedes_pickup(self):
        f = Flight(fixture(gates=[dict(x=2, half_width=1, top=10, bottom=20)],
                           stations=[dict(x=1, top=0, bottom=100, kind="pickup")]))
        f.step("release")
        self.assertTrue(f.done)
        self.assertFalse(f.carrying)

    def test_start_held_and_loaded(self):
        f = Flight(fixture(start=dict(y=50, vy=0, held=True, carrying=True)))
        f.step("press")
        self.assertEqual(f.vy, 3)

    def test_no_credit_for_pickup_alone(self):
        c = fixture(finish_x=4, stations=[dict(x=1, top=0, bottom=100, kind="pickup")])
        r, _ = run(c, types.SimpleNamespace(choose=lambda view: "release"))
        self.assertFalse(r["passed"])
        self.assertEqual(r["score"], 40)
        for action in (True, 0, None, "flap"):
            r, _ = run(c, types.SimpleNamespace(choose=lambda view, a=action: a))
            self.assertEqual(r["score"], 0)

    def test_observation_isolation_and_debug(self):
        m = types.SimpleNamespace(DEBUG={})
        def choose(view):
            m.DEBUG["tick"] = view["tick"]
            view["bird"]["y"] = -999
            return "release"
        m.choose = choose
        _, frames = run(fixture(), m, record=True)
        self.assertEqual(frames[0]["y"], 50)
        for f in frames[:-1]:
            self.assertEqual(f["debug"]["tick"], f["tick"])
        self.assertIsNone(frames[-1]["action"])


class Feasibility(unittest.TestCase):
    def check_flight(self, course, actions):
        f = Flight(course)
        for action in actions:
            self.assertFalse(f.done)
            f.step(action)
        self.assertTrue(f.won, (course["name"], f.reason))
        self.assertGreaterEqual(f.delivered, course["required"])
        self.assertEqual(f.result()["score"], 100)

    def test_all_packaged_courses(self):
        data = (ROOT / "_staff" / "witnesses.dat").read_text()
        witnesses = json.loads(zlib.decompress(base64.b64decode(data)))
        for course in courses() + courses(True):
            with self.subTest(course=course["name"]):
                self.check_flight(course, witnesses[course["name"]])

    def test_random_variations(self):
        for style in STYLES:
            for seed in range(20):
                with self.subTest(style=style, seed=seed):
                    course, actions = build("random", seed, style)
                    self.check_flight(course, actions)


if __name__ == "__main__":
    unittest.main(verbosity=2)
