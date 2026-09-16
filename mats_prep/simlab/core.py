"""Shared scaffolding for the practice environments.

Design notes (read these - they mirror how a real assessment harness behaves):

* Time is discrete. Every environment advances with a FIXED timestep `dt` using
  semi-implicit Euler:  v += a*dt   then   x += v*dt.
* Your policy is a plain function `policy(obs) -> action`, called exactly once
  per frame. It gets a deep copy of the observation, so you cannot smuggle a
  live reference to internal state.
* The runner does NOT reset your module-level globals between episodes.
  Many episodes run inside one process. If you keep state across frames you are
  responsible for detecting a new episode and clearing it. This is the single
  most common way a policy passes visible tests and fails hidden ones.
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------
# results
# --------------------------------------------------------------------------
@dataclass
class EpisodeResult:
    name: str
    passed: bool
    score: float           # environment specific quality score, higher = better
    reason: str            # human readable outcome
    frames: int
    detail: Dict[str, Any] = field(default_factory=dict)
    trace: Optional[List[dict]] = None
    wall_ms: float = 0.0

    def line(self) -> str:
        mark = "PASS" if self.passed else "FAIL"
        return f"[{mark}] {self.name:<28} score={self.score:8.2f}  frames={self.frames:<4}  {self.reason}"


# --------------------------------------------------------------------------
# base environment
# --------------------------------------------------------------------------
class Env:
    """Minimal environment contract."""

    name = "env"
    ACTIONS: Tuple[str, ...] = ()

    def reset(self) -> dict:
        raise NotImplementedError

    def step(self, action: str) -> dict:
        raise NotImplementedError

    @property
    def done(self) -> bool:
        raise NotImplementedError

    def result(self, name: str, frames: int, crash: Optional[str] = None) -> EpisodeResult:
        raise NotImplementedError

    def snapshot(self) -> dict:
        """Render-friendly dump of the full internal state."""
        raise NotImplementedError


# --------------------------------------------------------------------------
# episode runner
# --------------------------------------------------------------------------
def run_episode(
    env: Env,
    policy_fn: Callable[[dict], str],
    record: bool = False,
    debug_source: Any = None,
) -> EpisodeResult:
    """Run one episode to termination.

    `debug_source` may be the policy module. If it exposes a dict attribute
    named DEBUG, a shallow copy is captured every frame and stored in the trace
    so the HTML viewer can overlay your own numbers on top of the animation.
    """
    t0 = time.perf_counter()
    obs = env.reset()
    frames = 0
    trace: List[dict] = []

    while not env.done:
        try:
            action = policy_fn(copy.deepcopy(obs))
        except Exception as exc:  # noqa: BLE001 - a raising policy is a failing policy
            res = env.result(env.name, frames, crash=f"policy raised {type(exc).__name__}: {exc}")
            res.trace = trace if record else None
            res.wall_ms = (time.perf_counter() - t0) * 1000.0
            return res

        if action not in env.ACTIONS:
            res = env.result(
                env.name, frames,
                crash=f"illegal action {action!r} (legal: {list(env.ACTIONS)})",
            )
            res.trace = trace if record else None
            res.wall_ms = (time.perf_counter() - t0) * 1000.0
            return res

        # Recorded BEFORE stepping, so one row of the trace is one decision:
        # the state the policy was shown, the action it chose, and whatever it
        # put in DEBUG while choosing. Recording after the step would pair your
        # debug values with the state they produced, which is off by one frame
        # and very confusing to read.
        if record:
            trace.append(_frame_snapshot(env, action, debug_source))

        obs = env.step(action)
        frames += 1

    if record:
        trace.append(_frame_snapshot(env, None, None))     # terminal state

    res = env.result(env.name, frames)
    res.trace = trace if record else None
    res.wall_ms = (time.perf_counter() - t0) * 1000.0
    return res


def _frame_snapshot(env: Env, action: Optional[str], debug_source: Any) -> dict:
    snap = env.snapshot()
    snap["action"] = action
    dbg = getattr(debug_source, "DEBUG", None) if debug_source is not None else None
    if isinstance(dbg, dict):
        snap["debug"] = {k: _jsonable(v) for k, v in dbg.items()}
    return snap


def _jsonable(v: Any) -> Any:
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    return repr(v)


# --------------------------------------------------------------------------
# small math helpers shared by the environments
# --------------------------------------------------------------------------
def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v
