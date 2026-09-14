"""LANDER - the environment used for the *worked example*.

You control a lander descending toward a pad. Once per frame you choose ONE
action. You cannot burn vertically and laterally on the same frame - that
single-action budget is the whole game.

Coordinates
-----------
    x : horizontal offset from the centre of the pad (metres). +x is right.
    y : altitude above the pad surface (metres). +y is up. Touchdown is y <= 0.
    vx, vy : velocities in m/s, same sign conventions.

Actions
-------
    "off"   : no burn, no fuel spent
    "up"    : main engine, adds +up_thrust to vertical acceleration, 1 fuel
    "left"  : RCS, adds -side_thrust to horizontal acceleration, 1 fuel
    "right" : RCS, adds +side_thrust to horizontal acceleration, 1 fuel

With zero fuel every action behaves like "off".

Per-frame physics (semi-implicit Euler, in exactly this order)
--------------------------------------------------------------
    ax = wind(t)                       # horizontal acceleration from wind
    ay = -g
    if action != "off" and fuel > 0:
        fuel -= 1
        ay += up_thrust                 if action == "up"
        ax -= side_thrust               if action == "left"
        ax += side_thrust               if action == "right"
    vx += ax*dt ; vy += ay*dt
    x  += vx*dt ; y  += vy*dt
    t  += 1

Termination
-----------
    y <= 0                -> touchdown, evaluated against the landing gates
    |x| > arena_half      -> drifted out of bounds, failure
    y > ceiling           -> flew away, failure
    t >= max_frames       -> ran out of time, failure

Landing gates (all must hold at touchdown)
------------------------------------------
    vy >= -max_touchdown_speed      (not falling too fast)
    |vx| <= max_lateral_speed       (not sliding)
    |x|  <= pad_half_width          (on the pad)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .core import Env, EpisodeResult


@dataclass
class LanderScenario:
    name: str = "lander"
    y0: float = 100.0
    vy0: float = 0.0
    x0: float = 0.0
    vx0: float = 0.0
    fuel: int = 120
    g: float = 1.60
    up_thrust: float = 4.00
    side_thrust: float = 1.50
    dt: float = 0.10
    max_touchdown_speed: float = 2.50
    max_lateral_speed: float = 1.00
    pad_half_width: float = 6.00
    arena_half: float = 140.0
    ceiling: float = 260.0
    max_frames: int = 1400
    # wind:  ax = wind_base + wind_amp * sin(2*pi*t/wind_period + wind_phase)
    wind_base: float = 0.0
    wind_amp: float = 0.0
    wind_period: float = 200.0
    wind_phase: float = 0.0


class LanderEnv(Env):
    name = "lander"
    ACTIONS = ("off", "up", "left", "right")

    def __init__(self, sc: LanderScenario):
        self.sc = sc
        self.reset()

    # ---------------------------------------------------------------- state
    def reset(self) -> dict:
        sc = self.sc
        self.name = sc.name
        self.x = float(sc.x0)
        self.y = float(sc.y0)
        self.vx = float(sc.vx0)
        self.vy = float(sc.vy0)
        self.fuel = int(sc.fuel)
        self.t = 0
        self._done = False
        self._reason = ""
        self._passed = False
        return self.observe()

    def wind(self, t: int) -> float:
        sc = self.sc
        if sc.wind_amp == 0.0 and sc.wind_base == 0.0:
            return 0.0
        return sc.wind_base + sc.wind_amp * math.sin(
            2.0 * math.pi * t / sc.wind_period + sc.wind_phase
        )

    def observe(self) -> dict:
        sc = self.sc
        return {
            "t": self.t,
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "fuel": self.fuel,
            "wind": self.wind(self.t),          # wind acting on THIS frame
            "dt": sc.dt,
            "g": sc.g,
            "up_thrust": sc.up_thrust,
            "side_thrust": sc.side_thrust,
            "max_touchdown_speed": sc.max_touchdown_speed,
            "max_lateral_speed": sc.max_lateral_speed,
            "pad_half_width": sc.pad_half_width,
            "arena_half": sc.arena_half,
            "ceiling": sc.ceiling,
            "frames_left": sc.max_frames - self.t,
        }

    # ---------------------------------------------------------------- step
    def step(self, action: str) -> dict:
        sc = self.sc
        ax = self.wind(self.t)
        ay = -sc.g

        if action != "off" and self.fuel > 0:
            self.fuel -= 1
            if action == "up":
                ay += sc.up_thrust
            elif action == "left":
                ax -= sc.side_thrust
            elif action == "right":
                ax += sc.side_thrust

        self.vx += ax * sc.dt
        self.vy += ay * sc.dt
        self.x += self.vx * sc.dt
        self.y += self.vy * sc.dt
        self.t += 1

        if self.y <= 0.0:
            self.y = 0.0
            self._done = True
            ok_speed = self.vy >= -sc.max_touchdown_speed
            ok_slide = abs(self.vx) <= sc.max_lateral_speed
            ok_pad = abs(self.x) <= sc.pad_half_width
            self._passed = ok_speed and ok_slide and ok_pad
            if self._passed:
                self._reason = (
                    f"landed  vy={self.vy:+.2f} vx={self.vx:+.2f} x={self.x:+.2f} fuel={self.fuel}"
                )
            else:
                bad = []
                if not ok_speed:
                    bad.append(f"impact vy={self.vy:.2f} (limit {-sc.max_touchdown_speed:.2f})")
                if not ok_slide:
                    bad.append(f"slide vx={self.vx:+.2f} (limit {sc.max_lateral_speed:.2f})")
                if not ok_pad:
                    bad.append(f"off pad x={self.x:+.2f} (limit {sc.pad_half_width:.2f})")
                self._reason = "crash: " + "; ".join(bad)
        elif abs(self.x) > sc.arena_half:
            self._done = True
            self._reason = f"out of bounds x={self.x:+.1f}"
        elif self.y > sc.ceiling:
            self._done = True
            self._reason = f"escaped, y={self.y:.1f}"
        elif self.t >= sc.max_frames:
            self._done = True
            self._reason = f"timeout at y={self.y:.1f}"

        return self.observe()

    @property
    def done(self) -> bool:
        return self._done

    # ---------------------------------------------------------------- score
    def result(self, name: str, frames: int, crash: Optional[str] = None) -> EpisodeResult:
        if crash is not None:
            return EpisodeResult(self.sc.name, False, 0.0, crash, frames)
        score = 0.0
        if self._passed:
            # 100 for landing, plus fuel economy, plus accuracy, plus softness
            score = 100.0
            score += 0.25 * self.fuel
            score += 10.0 * max(0.0, 1.0 - abs(self.x) / self.sc.pad_half_width)
            score += 10.0 * max(0.0, 1.0 - abs(self.vy) / self.sc.max_touchdown_speed)
        return EpisodeResult(
            self.sc.name, self._passed, score, self._reason, frames,
            detail={"x": self.x, "vx": self.vx, "vy": self.vy, "fuel": self.fuel},
        )

    # ---------------------------------------------------------------- render
    def snapshot(self) -> dict:
        return {
            "t": self.t, "x": self.x, "y": self.y, "vx": self.vx, "vy": self.vy,
            "fuel": self.fuel, "wind": self.wind(self.t),
        }

    def static(self) -> dict:
        sc = self.sc
        return {
            "env": "lander", "name": sc.name,
            "pad_half_width": sc.pad_half_width, "arena_half": sc.arena_half,
            "ceiling": sc.ceiling, "y0": sc.y0, "dt": sc.dt,
            "max_touchdown_speed": sc.max_touchdown_speed,
            "max_lateral_speed": sc.max_lateral_speed,
        }
