#!/usr/bin/env python3
"""Validate course feasibility and challenge mechanics, without solving the task.

    python tools/validate_dog.py

Witnesses are for the course author only. They demonstrate existence of a
solution, not the performance of a policy that uses only observations.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import unittest
from dataclasses import replace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from simlab.core import run_episode
from simlab.dog import DogEnv
from simlab.dog_challenges import KINDS, VISIBLE_CHALLENGES, build_challenge
from simlab.hidden import dog_hidden
from simlab.scenarios import dog_visible
from tools.make_hidden import DOG


class DogCourseTests(unittest.TestCase):
    def check_witness(self, sc, witness):
        def policy(obs):
            if obs["t"] in witness:
                self.assertGreater(obs["stamina"], 0)
                return True
            return False

        result = run_episode(DogEnv(sc), policy)
        self.assertTrue(result.passed, f"{sc.name}: {result.reason}")
        self.assertIn("cleared the whole course", result.reason)
        self.assertEqual(result.score, len(sc.pipes))
        for pipe in sc.pipes:
            self.assertGreater(pipe.gap_hi - pipe.gap_lo, 2 * sc.dog_radius)
            self.assertGreaterEqual(pipe.gap_lo, 0)
            self.assertLessEqual(pipe.gap_hi, sc.ceiling)

    def test_visible_courses(self):
        actual = {sc.name: sc for sc in dog_visible()}
        for name, seed, kind in VISIBLE_CHALLENGES:
            with self.subTest(name=name):
                sc, witness = build_challenge(name, seed, kind)
                self.assertEqual(sc, actual[name])
                self.check_witness(actual[name], witness)

    def test_hidden_blob_matches_recipes_and_is_solvable(self):
        hidden = dog_hidden()
        self.assertEqual(len(hidden), len(DOG))
        for (_, actual), recipe in zip(hidden, DOG):
            with self.subTest(name=actual.name):
                sc, witness = build_challenge(recipe["_label"], recipe["seed"], recipe["kind"])
                self.assertEqual(sc, actual)
                self.check_witness(actual, witness)

    def test_random_variations(self):
        for kind in KINDS:
            for seed in range(100):
                with self.subTest(kind=kind, seed=seed):
                    sc, witness = build_challenge(f"{kind}/{seed}", seed, kind)
                    self.check_witness(sc, witness)

    def test_narrow_gap_cannot_accommodate_an_inside_bounce(self):
        sc, witness = build_challenge("apex", 301, "apex")
        p = sc.pipes[0]
        usable = p.gap_hi - p.gap_lo - 2 * sc.dog_radius
        bounce_step = (sc.bounce_impulse - sc.gravity * sc.dt) * sc.dt
        # From ANY legal height inside this gap, a bounce rises past its roof
        # on the next frame if the dog is still horizontally overlapping it.
        self.assertLess(usable, bounce_step)
        env = DogEnv(sc)
        while env.x + sc.dog_radius <= p.x - p.half_w:
            env.step(env.t in witness)
            self.assertFalse(env.done)
        self.assertGreater(env.stamina, 0)
        bounce, glide = copy.deepcopy(env), copy.deepcopy(env)
        bounce.step(True)
        glide.step(False)
        self.assertTrue(bounce.done)
        self.assertIn("high side", bounce.result(sc.name, bounce.t).reason)
        self.assertFalse(glide.done)

    def test_wasted_early_bounce_breaks_stamina_climb(self):
        sc, witness = build_challenge("climb", 307, "climb")
        # Remove the low gate to isolate the resource failure from the extra
        # bounce's immediate effect on that gate's crossing height.
        sc = replace(sc, pipes=sc.pipes[1:], target=len(sc.pipes) - 1)
        self.check_witness(sc, witness)
        # One extra bounce during the initial ascent consumes a reserve needed
        # later. Replay through the real engine, with its real regen ordering.
        waste = witness | {1}
        result = run_episode(DogEnv(sc), lambda obs: obs["t"] in waste)
        self.assertFalse(result.passed)
        env = DogEnv(sc)
        for t in range(19):
            self.assertFalse(env.done)
            if t == 18:
                self.assertEqual(env.stamina, 0)
                self.assertIn(t, witness)
            env.step(t in waste)

    def test_height_only_and_spam_do_not_solve_hard_courses(self):
        def height_only(obs):
            p = obs["pipes"][0]
            centre = (p["gap_lo"] + p["gap_hi"]) / 2
            return bool(obs["stamina"] and obs["x"] < p["x"] + p["half_w"]
                        and obs["y"] < centre - (p["gap_hi"] - p["gap_lo"]) / 4.5)

        for name, seed, kind in VISIBLE_CHALLENGES:
            sc, _ = build_challenge(name, seed, kind)
            with self.subTest(name=name):
                self.assertFalse(run_episode(DogEnv(sc), height_only).passed)
                self.assertFalse(run_episode(DogEnv(sc), lambda obs: True).passed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
