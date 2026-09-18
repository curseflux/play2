"""Public simulator for Coinrun. Read during the mock; no solutions here.

Coordinates: +x right, +y UP. True resets vy to a positive bounce velocity.
There is no cooldown or stamina. Only one coin is exposed per observation.
"""
from __future__ import annotations


class World:
    def __init__(self, case):
        self.case = case
        self.x = 0.0
        self.y, self.vy = float(case["y0"]), float(case["vy0"])
        self.frame = self.coins_collected = self.pipes_cleared = 0
        self.coin_states = ["available"] * len(case["coins"])
        self.done = self.passed = False
        self.reason = "running"

    def observe(self):
        c, p = self.case, self.case["physics"]
        pipes = [{"id": i, **pipe} for i, pipe in enumerate(c["pipes"])
                 if pipe["x"] + pipe["half_width"] >= self.x - p["radius"]]
        coin = None
        for i, item in enumerate(c["coins"]):
            if self.coin_states[i] != "available":
                continue
            if item["x"] - self.x <= c["coin_lookahead"]:
                coin = {"id": i, **item}
            break  # A later coin is never revealed before the nearest one.
        return {**p, "frame": self.frame, "x": self.x, "y": self.y, "vy": self.vy,
                "frames_left": c["max_frames"] - self.frame,
                "finish_x": c["finish_x"], "coin_lookahead": c["coin_lookahead"],
                "coins_collected": self.coins_collected, "coin_target": c["coin_target"],
                "pipes_cleared": self.pipes_cleared, "pipes_total": len(c["pipes"]),
                "pipes": pipes[:c["pipe_sight"]], "coin": coin}

    def step(self, bounce):
        if self.done:
            raise RuntimeError("episode is already finished")
        if type(bounce) is not bool:
            raise ValueError(f"act() must return bool, got {bounce!r}")
        c, p = self.case, self.case["physics"]
        if bounce:
            self.vy = p["bounce_velocity"]
        self.vy = max(self.vy - p["gravity"] * p["dt"], -p["max_fall_speed"])
        self.y += self.vy * p["dt"]
        self.x += p["scroll_speed"] * p["dt"]
        self.frame += 1

        r = p["radius"]
        if self.y - r <= 0:
            self.done, self.reason = True, "fell below screen"
        elif self.y + r >= p["ceiling"]:
            self.done, self.reason = True, "hit ceiling"
        else:
            for i, pipe in enumerate(c["pipes"]):
                overlaps = (self.x + r > pipe["x"] - pipe["half_width"]
                            and self.x - r < pipe["x"] + pipe["half_width"])
                if overlaps and (self.y - r < pipe["gap_lo"] or self.y + r > pipe["gap_hi"]):
                    side = "below" if self.y - r < pipe["gap_lo"] else "above"
                    self.done, self.reason = True, f"pipe {i + 1}: {side} opening"
                    break

        # Collision takes priority: a fatal frame cannot also collect a coin.
        if not self.done:
            for i, coin in enumerate(c["coins"]):
                if self.coin_states[i] == "available":
                    reach = r + coin["radius"]
                    if (coin["x"] - self.x) ** 2 + (coin["y"] - self.y) ** 2 <= reach ** 2:
                        self.coin_states[i] = "collected"
                        self.coins_collected += 1
        for i, coin in enumerate(c["coins"]):
            if self.coin_states[i] == "available" and self.x - r > coin["x"] + coin["radius"]:
                self.coin_states[i] = "missed"
        self.pipes_cleared = sum(g["x"] + g["half_width"] < self.x - r for g in c["pipes"])

        if not self.done:
            if self.x >= c["finish_x"]:
                self.done = True
                self.passed = self.coins_collected >= c["coin_target"]
                self.reason = "finished" if self.passed else "finished below coin target"
            elif self.frame >= c["max_frames"]:
                self.done, self.reason = True, "timeout"
        return self.observe()

    def snapshot(self):
        return {"frame": self.frame, "x": self.x, "y": self.y, "vy": self.vy,
                "coins_collected": self.coins_collected, "pipes_cleared": self.pipes_cleared,
                "coin_states": list(self.coin_states), "visible_coin": self.observe()["coin"],
                "done": self.done, "reason": self.reason}

    def result(self, error=None):
        progress = min(1.0, self.x / self.case["finish_x"])
        target = self.case["coin_target"]
        score = 100 * progress if target == 0 else (
            50 * progress + 50 * min(1.0, self.coins_collected / target))
        return {"name": self.case["name"], "passed": self.passed and error is None,
                "score": 0.0 if error else score, "coins": self.coins_collected,
                "target": target, "progress": progress, "frames": self.frame,
                "reason": error or self.reason}

