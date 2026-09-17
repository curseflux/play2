"""Pulseflight's public rules. This module is safe to read during the mock.

Coordinates are screen coordinates: y increases DOWNWARD. Pulse SUBTRACTS
velocity, subject to a cooldown. The bird is a CIRCLE. Gate openings oscillate.
See SPEC.md for the observation contract; step() is the authoritative update.
"""
from __future__ import annotations

import math


ACTIONS = ("glide", "pulse")


def opening(gate, tick):
    """Opening at an absolute frame number, not an offset from now."""
    centre = gate["centre"] + gate["amplitude"] * math.sin(
        2 * math.pi * tick / gate["period"] + gate["phase"])
    return centre - gate["gap"] / 2, centre + gate["gap"] / 2


def circle_hits_rect(x, y, radius, left, top, right, bottom):
    """Contact, including exact tangency, counts as a collision."""
    near_x = min(max(x, left), right)
    near_y = min(max(y, top), bottom)
    return (x - near_x) ** 2 + (y - near_y) ** 2 <= radius ** 2


class Arena:
    def __init__(self, case):
        self.case = case
        self.tick = 0
        self.x = 0.0
        self.y = float(case["start"]["y"])
        self.vy = float(case["start"]["vy"])
        self.cooldown = int(case["start"]["cooldown"])
        self.cleared = 0
        self.pulses = 0
        self.finished = False
        self.won = False
        self.reason = "running"

    def observe(self):
        c, p = self.case, self.case["physics"]
        gates = []
        for index, gate in enumerate(c["gates"]):
            if gate["x"] + gate["half_width"] >= self.x - p["radius"]:
                top, bottom = opening(gate, self.tick)
                gates.append({"id": index, **gate, "top": top, "bottom": bottom})
                if len(gates) >= c["sight"]:
                    break
        return {
            "clock": {"tick": self.tick, "limit": c["limit"], "dt": p["dt"]},
            "bird": {"x": self.x, "y": self.y, "vy": self.vy,
                     "cooldown": self.cooldown},
            "course": {"height": c["height"], "cleared": self.cleared,
                       "total": len(c["gates"])},
            "physics": dict(p),
            "gates": gates,
        }

    def step(self, action):
        if self.finished:
            raise RuntimeError("cannot step a finished episode")
        if type(action) is not str or action not in ACTIONS:
            raise ValueError(f"expected one of {ACTIONS}, received {action!r}")
        c, p = self.case, self.case["physics"]

        # Cooldown is checked BEFORE this frame's end-of-frame decrement.
        if action == "pulse" and self.cooldown == 0:
            self.vy -= p["impulse"]       # ADDITIVE kick, never a velocity reset
            self.cooldown = p["recharge"]
            self.pulses += 1

        # Gravity, linear drag, speed caps, then position using NEW velocity.
        self.vy += (p["gravity"] - p["drag"] * self.vy) * p["dt"]
        self.vy = min(p["fall_cap"], max(-p["rise_cap"], self.vy))
        self.y += self.vy * p["dt"]
        self.x += p["speed"] * p["dt"]
        self.tick += 1
        self.cooldown = max(0, self.cooldown - 1)

        # The shutters move to their positions at the NEW absolute tick.
        r = p["radius"]
        if self.y - r <= 0 or self.y + r >= c["height"]:
            self.finished = True
            self.reason = "ceiling" if self.y - r <= 0 else "floor"
        else:
            for index, gate in enumerate(c["gates"]):
                left, right = gate["x"] - gate["half_width"], gate["x"] + gate["half_width"]
                if self.x + r < left or self.x - r > right:
                    continue
                top, bottom = opening(gate, self.tick)
                upper = circle_hits_rect(self.x, self.y, r, left, 0, right, top)
                lower = circle_hits_rect(self.x, self.y, r, left, bottom, right, c["height"])
                if upper or lower:
                    self.finished = True
                    self.reason = f"gate {index + 1}: {'upper' if upper else 'lower'} shutter"
                    break

        self.cleared = sum(g["x"] + g["half_width"] < self.x - r for g in c["gates"])
        if not self.finished:
            if self.cleared == len(c["gates"]):
                self.finished = self.won = True
                self.reason = "complete"
            elif self.tick >= c["limit"]:
                self.finished = True
                self.reason = "timeout"
        return self.observe()

    def snapshot(self):
        return {"tick": self.tick, "x": self.x, "y": self.y, "vy": self.vy,
                "cooldown": self.cooldown, "cleared": self.cleared,
                "finished": self.finished, "reason": self.reason,
                "openings": [opening(g, self.tick) for g in self.case["gates"]]}

    def result(self, error=None):
        return {"name": self.case["name"], "passed": self.won and error is None,
                "score": 0.0 if error else 100.0 * self.cleared / len(self.case["gates"]),
                "cleared": self.cleared, "total": len(self.case["gates"]),
                "frames": self.tick, "pulses": self.pulses,
                "reason": error or self.reason}
