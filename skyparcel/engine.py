"""Public Skyparcel simulator. Positive y points DOWNWARD.

Press triggers a flap only after release. Cargo changes gravity. Stations
are evaluated once, when the bird's center crosses their horizontal position.
"""
from __future__ import annotations


class Flight:
    def __init__(self, course):
        self.course = course
        self.tick = 0
        self.x = 0.0
        self.y = float(course["start"]["y"])
        self.vy = float(course["start"]["vy"])
        self.held = bool(course["start"]["held"])
        self.carrying = bool(course["start"]["carrying"])
        self.delivered = 0
        self.station_states = ["ahead"] * len(course["stations"])
        self.done = self.won = False
        self.reason = "flying"

    def observe(self):
        c, p = self.course, self.course["physics"]
        gates = [{"id": i, **g} for i, g in enumerate(c["gates"])
                 if g["x"] + g["half_width"] >= self.x - p["radius"]]
        stations = [{"id": i, **s} for i, s in enumerate(c["stations"])
                    if self.station_states[i] == "ahead"]
        return {"tick": self.tick, "frames_left": c["limit"] - self.tick,
                "bird": {"x": self.x, "y": self.y, "vy": self.vy,
                         "held": self.held, "carrying": self.carrying},
                "mission": {"delivered": self.delivered, "required": c["required"],
                            "finish_x": c["finish_x"]},
                "physics": dict(p), "gates": gates[:2], "stations": stations[:2]}

    def step(self, action):
        if self.done:
            raise RuntimeError("cannot step after termination")
        if type(action) is not str or action not in ("press", "release"):
            raise ValueError("choose() must return 'press' or 'release'")
        c, p = self.course, self.course["physics"]
        previous_x = self.x
        pressed = action == "press"
        # Only a RELEASED -> PRESSED transition produces a flap.
        if pressed and not self.held:
            self.vy = -p["flap_speed"]
        self.held = pressed

        gravity = p["gravity_loaded"] if self.carrying else p["gravity_empty"]
        self.vy = min(p["fall_limit"], self.vy + gravity * p["dt"])
        self.y += self.vy * p["dt"]
        self.x += p["speed"] * p["dt"]
        self.tick += 1

        r = p["radius"]
        if self.y - r <= 0:
            self.done, self.reason = True, "ceiling"
        elif self.y + r >= p["height"]:
            self.done, self.reason = True, "floor"
        else:
            for i, gate in enumerate(c["gates"]):
                overlap = (self.x + r > gate["x"] - gate["half_width"]
                           and self.x - r < gate["x"] + gate["half_width"])
                if overlap and (self.y - r < gate["top"] or self.y + r > gate["bottom"]):
                    self.done, self.reason = True, f"gate {i + 1} collision"
                    break

        # Cargo changes AFTER flight physics, and only on a nonfatal frame.
        for i, station in enumerate(c["stations"]):
            if self.station_states[i] != "ahead":
                continue
            if previous_x < station["x"] <= self.x:
                fits = self.y - r >= station["top"] and self.y + r <= station["bottom"]
                can_use = self.carrying if station["kind"] == "depot" else not self.carrying
                if not self.done and fits and can_use:
                    self.carrying = station["kind"] == "pickup"
                    if station["kind"] == "depot":
                        self.delivered += 1
                    self.station_states[i] = "used"
                else:
                    self.station_states[i] = "missed"

        if not self.done:
            if self.x >= c["finish_x"]:
                self.done = True
                self.won = self.delivered >= c["required"]
                self.reason = "complete" if self.won else "finished below delivery target"
            elif self.tick >= c["limit"]:
                self.done, self.reason = True, "timeout"
        return self.observe()

    def snapshot(self):
        return {"tick": self.tick, "x": self.x, "y": self.y, "vy": self.vy,
                "held": self.held, "carrying": self.carrying, "delivered": self.delivered,
                "station_states": list(self.station_states), "done": self.done,
                "reason": self.reason}

    def result(self, error=None):
        c = self.course
        progress = min(1.0, self.x / c["finish_x"])
        reward = min(1.0, self.delivered / c["required"]) if c["required"] else 1.0
        score = 100 * progress if not c["required"] else 40 * progress + 60 * reward
        return {"name": c["name"], "passed": self.won and error is None,
                "progress": progress, "deliveries": self.delivered,
                "required": c["required"], "score": 0.0 if error else score,
                "ticks": self.tick, "reason": error or self.reason}

