"""DOG - a side-scrolling survival course.

A dog runs left to right at a constant speed. Gravity pulls it down. Once per
frame you decide ONE thing: bounce, or do not bounce.

Coordinates
-----------
    x : distance along the course. It advances by forward_speed*dt every frame
        no matter what you do. You cannot slow down, stop or go back.
    y : height. 0 is the ground, `ceiling` is the top of the screen.
        The dog is a square of side 2*dog_radius centred on (x, y).

Actions
-------
    True   bounce - SETS vy to +bounce_impulse (it does not add to it, so
           bouncing while already rising throws away the speed you had).
           Costs 1 stamina. With 0 stamina a bounce does nothing at all.
    False  glide - do nothing this frame.

Per-frame physics (in exactly this order)
-----------------------------------------
    if action and stamina > 0:
        stamina -= 1
        vy = bounce_impulse
    vy -= gravity*dt
    vy  = max(vy, -max_fall_speed)          # terminal velocity
    y  += vy*dt
    x  += forward_speed*dt
    t  += 1
    if t % regen_period == 0:                # stamina trickles back
        stamina = min(stamina_max, stamina + 1)
    then collisions are checked.

Collisions (any of these ends the episode)
------------------------------------------
    y - dog_radius <= 0              fell off the bottom of the screen
    y + dog_radius >= ceiling        hit the top of the screen
    a pipe: a pipe at px with half-width hw blocks everything except the gap
        between gap_lo and gap_hi. You are inside a pipe's column when
            x + dog_radius > px - hw  and  x - dog_radius < px + hw
        and you hit it unless
            y - dog_radius >= gap_lo  and  y + dog_radius <= gap_hi

Observation
-----------
    You are shown the next `sight` pipes only - the ones you have not cleared
    yet, nearest first. When that list is empty the course is finished.

Termination
-----------
    a collision, or all pipes cleared, or t >= max_frames.
    Score = pipes cleared. You pass by clearing `target` of them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .core import Env, EpisodeResult


@dataclass
class Pipe:
    x: float
    half_w: float
    gap_lo: float
    gap_hi: float


@dataclass
class DogScenario:
    name: str = "dog"
    ceiling: float = 60.0
    y0: float = 30.0
    vy0: float = 0.0
    gravity: float = 30.0
    bounce_impulse: float = 19.0
    max_fall_speed: float = 30.0
    forward_speed: float = 22.0
    dt: float = 0.10
    dog_radius: float = 1.5
    stamina_max: int = 5
    regen_period: int = 6
    sight: int = 3
    max_frames: int = 1500
    target: int = 0                     # 0 means "all of them"
    pipes: List[Pipe] = field(default_factory=list)


class DogEnv(Env):
    name = "dog"
    ACTIONS = (True, False)

    def __init__(self, sc: DogScenario):
        self.sc = sc
        self.reset()

    # ---------------------------------------------------------------- state
    def reset(self) -> dict:
        sc = self.sc
        self.name = sc.name
        self.x = 0.0
        self.y = float(sc.y0)
        self.vy = float(sc.vy0)
        self.stamina = int(sc.stamina_max)
        self.t = 0
        self.cleared = 0
        self._done = False
        self._reason = ""
        return self.observe()

    def _pending(self) -> List[Pipe]:
        r = self.sc.dog_radius
        return [p for p in self.sc.pipes if p.x + p.half_w >= self.x - r]

    def observe(self) -> dict:
        sc = self.sc
        ahead = self._pending()[: sc.sight]
        return {
            "t": self.t,
            "frames_left": sc.max_frames - self.t,
            "dt": sc.dt,
            "x": self.x,
            "y": self.y,
            "vy": self.vy,
            "stamina": self.stamina,
            "stamina_max": sc.stamina_max,
            "regen_period": sc.regen_period,
            "gravity": sc.gravity,
            "bounce_impulse": sc.bounce_impulse,
            "max_fall_speed": sc.max_fall_speed,
            "forward_speed": sc.forward_speed,
            "ceiling": sc.ceiling,
            "dog_radius": sc.dog_radius,
            "cleared": self.cleared,
            "pipes_total": len(sc.pipes),
            "pipes": [
                {"x": p.x, "half_w": p.half_w, "gap_lo": p.gap_lo, "gap_hi": p.gap_hi}
                for p in ahead
            ],
        }

    # ---------------------------------------------------------------- step
    def step(self, action) -> dict:
        sc = self.sc
        before = len(self._pending())

        if action and self.stamina > 0:
            self.stamina -= 1
            self.vy = sc.bounce_impulse

        self.vy -= sc.gravity * sc.dt
        if self.vy < -sc.max_fall_speed:
            self.vy = -sc.max_fall_speed
        self.y += self.vy * sc.dt
        self.x += sc.forward_speed * sc.dt
        self.t += 1
        if self.t % sc.regen_period == 0 and self.stamina < sc.stamina_max:
            self.stamina += 1

        r = sc.dog_radius
        if self.y - r <= 0.0:
            self._done, self._reason = True, f"fell off the bottom at x={self.x:.1f}"
        elif self.y + r >= sc.ceiling:
            self._done, self._reason = True, f"hit the ceiling at x={self.x:.1f}"
        else:
            for p in sc.pipes:
                if self.x + r > p.x - p.half_w and self.x - r < p.x + p.half_w:
                    if not (self.y - r >= p.gap_lo and self.y + r <= p.gap_hi):
                        side = "low" if self.y < (p.gap_lo + p.gap_hi) / 2 else "high"
                        self._done = True
                        self._reason = (
                            f"clipped pipe {sc.pipes.index(p) + 1} on the {side} side "
                            f"(y={self.y:.1f}, gap {p.gap_lo:.1f}-{p.gap_hi:.1f})"
                        )
                        break

        self.cleared += before - len(self._pending())

        if not self._done:
            if self.cleared >= len(sc.pipes):
                self._done, self._reason = True, f"cleared the whole course ({self.cleared} pipes)"
            elif self.t >= sc.max_frames:
                self._done, self._reason = True, f"out of time after {self.cleared} pipes"
        return self.observe()

    @property
    def done(self) -> bool:
        return self._done

    # ---------------------------------------------------------------- score
    def result(self, name: str, frames: int, crash: Optional[str] = None) -> EpisodeResult:
        if crash is not None:
            return EpisodeResult(self.sc.name, False, 0.0, crash, frames)
        need = self.sc.target or len(self.sc.pipes)
        passed = self.cleared >= need
        return EpisodeResult(
            self.sc.name, passed, float(self.cleared),
            f"cleared {self.cleared}/{need} needed  ({self._reason})", frames,
            detail={"cleared": self.cleared, "target": need},
        )

    # ---------------------------------------------------------------- render
    def snapshot(self) -> dict:
        return {"t": self.t, "x": self.x, "y": self.y, "vy": self.vy,
                "stamina": self.stamina, "cleared": self.cleared}

    def static(self) -> dict:
        sc = self.sc
        return {
            "env": "dog", "name": sc.name, "ceiling": sc.ceiling,
            "dog_radius": sc.dog_radius, "stamina_max": sc.stamina_max,
            "target": sc.target or len(sc.pipes), "dt": sc.dt,
            "pipes": [[p.x, p.half_w, p.gap_lo, p.gap_hi] for p in sc.pipes],
        }
