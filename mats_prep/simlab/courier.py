"""COURIER - the environment for the *practice problem* (hidden tests live here).

You fly a small delivery drone around a rectangular arena. Once per frame you
choose ONE action. Deliver as many parcels as you can before the clock runs out.

Coordinates
-----------
    Origin is the bottom-left corner of the arena. +x right, +y up.
    The arena is arena.w by arena.h. The drone is a disc of radius agent_radius.

Actions
-------
    "idle", "up", "down", "left", "right"
    A thrust action adds an acceleration of magnitude `thrust` along that axis.
    "idle" applies no thrust. There is no fuel cost - time is the only currency.

Per-frame physics (semi-implicit Euler, in exactly this order)
--------------------------------------------------------------
    ax, ay = thrust vector from the action (0,0 for "idle" or while stunned)
    ax -= drag * vx ;  ay -= drag * vy         # linear drag
    vx += ax*dt     ;  vy += ay*dt
    x  += vx*dt     ;  y  += vy*dt
    walls: position is clamped into the arena and the velocity component
           normal to that wall is set to 0.
    hazards move, then bounce off the arena walls.
    then: hazard contact is checked, then pickup/delivery is checked.

Terminal velocity under continuous thrust is thrust/drag.

Parcels
-------
    Every parcel has a `pickup` point and a `dropoff` point. You can carry at
    most one at a time.
    A parcel is PICKED UP when, on a frame where you are not carrying anything
    and not stunned, your centre is within `pickup_radius` of its pickup point
    AND your speed is at most `grab_speed`. If several qualify, the nearest is
    taken.
    A parcel is DELIVERED when you are carrying it, not stunned, within
    `pickup_radius` of its dropoff point, and your speed is at most
    `grab_speed`.
    You must therefore SLOW DOWN to trade. Flying past at full speed does
    nothing.

Hazards
-------
    Discs that drift and bounce off the arena walls forever. If the distance
    between centres drops to `agent_radius + hazard.r` or less you are hit:
        * your velocity is zeroed
        * you are stunned for `stun_frames` frames (thrust is ignored)
        * any carried parcel is dropped and returns to its pickup point
    After a hit you are immune for `stun_frames + 5` frames total, so you
    cannot be chain-stunned inside one hazard.

Termination
-----------
    t >= max_frames. There is no other way for the episode to end.
    Score = number of parcels delivered. You pass a scenario by reaching its
    target.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .core import Env, EpisodeResult, clamp


@dataclass
class Hazard:
    x: float
    y: float
    vx: float
    vy: float
    r: float


@dataclass
class Parcel:
    px: float
    py: float
    dx: float
    dy: float


@dataclass
class CourierScenario:
    name: str = "courier"
    w: float = 120.0
    h: float = 80.0
    x0: float = 60.0
    y0: float = 40.0
    thrust: float = 12.0
    drag: float = 1.0
    dt: float = 0.10
    agent_radius: float = 1.5
    pickup_radius: float = 3.0
    grab_speed: float = 2.5
    stun_frames: int = 25
    max_frames: int = 1200
    target: int = 8
    parcels: List[Parcel] = field(default_factory=list)
    hazards: List[Hazard] = field(default_factory=list)


class CourierEnv(Env):
    name = "courier"
    ACTIONS = ("idle", "up", "down", "left", "right")
    _THRUST_VEC = {
        "idle": (0.0, 0.0),
        "up": (0.0, 1.0),
        "down": (0.0, -1.0),
        "left": (-1.0, 0.0),
        "right": (1.0, 0.0),
    }

    def __init__(self, sc: CourierScenario):
        self.sc = sc
        self.reset()

    # ---------------------------------------------------------------- state
    def reset(self) -> dict:
        sc = self.sc
        self.name = sc.name
        self.x, self.y = float(sc.x0), float(sc.y0)
        self.vx = self.vy = 0.0
        self.t = 0
        self.stun = 0
        self.immune = 0
        self.hits = 0
        self.carrying: Optional[int] = None
        self.delivered = 0
        self.states = ["waiting"] * len(sc.parcels)
        self.haz = [Hazard(h.x, h.y, h.vx, h.vy, h.r) for h in sc.hazards]
        self._done = False
        return self.observe()

    def observe(self) -> dict:
        sc = self.sc
        return {
            "t": self.t,
            "frames_left": sc.max_frames - self.t,
            "dt": sc.dt,
            "arena": {"w": sc.w, "h": sc.h},
            "agent": {"x": self.x, "y": self.y, "vx": self.vx, "vy": self.vy,
                      "stunned": self.stun},
            "thrust": sc.thrust,
            "drag": sc.drag,
            "agent_radius": sc.agent_radius,
            "pickup_radius": sc.pickup_radius,
            "grab_speed": sc.grab_speed,
            "stun_frames": sc.stun_frames,
            "carrying": self.carrying,
            "delivered": self.delivered,
            "parcels": [
                {"id": i, "pickup": [p.px, p.py], "dropoff": [p.dx, p.dy],
                 "state": self.states[i]}
                for i, p in enumerate(sc.parcels)
            ],
            "hazards": [{"x": h.x, "y": h.y, "vx": h.vx, "vy": h.vy, "r": h.r}
                        for h in self.haz],
        }

    # ---------------------------------------------------------------- step
    def step(self, action: str) -> dict:
        sc = self.sc
        ux, uy = self._THRUST_VEC[action]
        if self.stun > 0:
            ux = uy = 0.0
            self.stun -= 1
        if self.immune > 0:
            self.immune -= 1

        ax = ux * sc.thrust - sc.drag * self.vx
        ay = uy * sc.thrust - sc.drag * self.vy
        self.vx += ax * sc.dt
        self.vy += ay * sc.dt
        self.x += self.vx * sc.dt
        self.y += self.vy * sc.dt

        lo, hix, hiy = sc.agent_radius, sc.w - sc.agent_radius, sc.h - sc.agent_radius
        if self.x < lo:
            self.x, self.vx = lo, 0.0
        elif self.x > hix:
            self.x, self.vx = hix, 0.0
        if self.y < lo:
            self.y, self.vy = lo, 0.0
        elif self.y > hiy:
            self.y, self.vy = hiy, 0.0

        for h in self.haz:
            h.x += h.vx * sc.dt
            h.y += h.vy * sc.dt
            if h.x < h.r:
                h.x, h.vx = h.r, -h.vx
            elif h.x > sc.w - h.r:
                h.x, h.vx = sc.w - h.r, -h.vx
            if h.y < h.r:
                h.y, h.vy = h.r, -h.vy
            elif h.y > sc.h - h.r:
                h.y, h.vy = sc.h - h.r, -h.vy

        hit_now = False
        if self.immune == 0:
            for h in self.haz:
                rr = (h.r + sc.agent_radius) ** 2
                if (h.x - self.x) ** 2 + (h.y - self.y) ** 2 <= rr:
                    hit_now = True
                    break
        if hit_now:
            self.hits += 1
            self.vx = self.vy = 0.0
            self.stun = sc.stun_frames
            self.immune = sc.stun_frames + 5
            if self.carrying is not None:
                self.states[self.carrying] = "waiting"
                self.carrying = None

        if not hit_now and self.stun == 0:
            speed = math.hypot(self.vx, self.vy)
            if speed <= sc.grab_speed:
                rr = sc.pickup_radius ** 2
                if self.carrying is None:
                    best, bestd = None, rr
                    for i, p in enumerate(sc.parcels):
                        if self.states[i] != "waiting":
                            continue
                        d = (p.px - self.x) ** 2 + (p.py - self.y) ** 2
                        if d <= bestd:
                            best, bestd = i, d
                    if best is not None:
                        self.carrying = best
                        self.states[best] = "carried"
                else:
                    p = sc.parcels[self.carrying]
                    if (p.dx - self.x) ** 2 + (p.dy - self.y) ** 2 <= rr:
                        self.states[self.carrying] = "delivered"
                        self.carrying = None
                        self.delivered += 1

        self.t += 1
        if self.t >= sc.max_frames:
            self._done = True
        return self.observe()

    @property
    def done(self) -> bool:
        return self._done

    # ---------------------------------------------------------------- score
    def result(self, name: str, frames: int, crash: Optional[str] = None) -> EpisodeResult:
        if crash is not None:
            return EpisodeResult(self.sc.name, False, 0.0, crash, frames)
        passed = self.delivered >= self.sc.target
        reason = (f"delivered {self.delivered}/{self.sc.target} needed, "
                  f"hits={self.hits}")
        return EpisodeResult(
            self.sc.name, passed, float(self.delivered), reason, frames,
            detail={"delivered": self.delivered, "target": self.sc.target,
                    "hits": self.hits},
        )

    # ---------------------------------------------------------------- render
    def snapshot(self) -> dict:
        return {
            "t": self.t, "x": self.x, "y": self.y, "vx": self.vx, "vy": self.vy,
            "stun": self.stun, "carrying": self.carrying,
            "delivered": self.delivered,
            "states": list(self.states),
            "hazards": [[h.x, h.y, h.r] for h in self.haz],
        }

    def static(self) -> dict:
        sc = self.sc
        return {
            "env": "courier", "name": sc.name, "w": sc.w, "h": sc.h,
            "agent_radius": sc.agent_radius, "pickup_radius": sc.pickup_radius,
            "target": sc.target, "max_frames": sc.max_frames, "dt": sc.dt,
            "parcels": [[p.px, p.py, p.dx, p.dy] for p in sc.parcels],
        }
