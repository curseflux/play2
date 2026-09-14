"""Visible scenarios + the scenario generators.

These are the cases you can see and iterate against. The graded set also
contains hidden scenarios built with the same generators but different
parameters. Tuning constants until the visible list goes green is exactly the
failure mode the hidden set is designed to catch.
"""

from __future__ import annotations

import math
import random
from typing import List

from .courier import CourierScenario, Hazard, Parcel
from .lander import LanderScenario


# --------------------------------------------------------------------------
# generators
# --------------------------------------------------------------------------
def make_courier(name: str, seed: int, *, n_parcels: int = 14, n_hazards: int = 3,
                 w: float = 120.0, h: float = 80.0, max_frames: int = 1200,
                 target: int = 8, haz_speed: float = 9.0, haz_r: float = 5.0,
                 thrust: float = 12.0, drag: float = 1.0,
                 stun_frames: int = 25, cluster: bool = False) -> CourierScenario:
    rng = random.Random(seed)
    m = 8.0

    def pt():
        return (rng.uniform(m, w - m), rng.uniform(m, h - m))

    parcels: List[Parcel] = []
    for _ in range(n_parcels):
        if cluster:
            cx, cy = (w * 0.2, h * 0.5) if rng.random() < 0.5 else (w * 0.8, h * 0.5)
            px = min(max(rng.gauss(cx, w * 0.08), m), w - m)
            py = min(max(rng.gauss(cy, h * 0.15), m), h - m)
        else:
            px, py = pt()
        dx, dy = pt()
        parcels.append(Parcel(px, py, dx, dy))

    hazards: List[Hazard] = []
    for _ in range(n_hazards):
        hx, hy = pt()
        ang = rng.uniform(0, 6.283185)
        sp = haz_speed * rng.uniform(0.7, 1.3)
        r = haz_r * rng.uniform(0.8, 1.3)
        hazards.append(Hazard(hx, hy, sp * math.cos(ang), sp * math.sin(ang), r))

    return CourierScenario(name=name, w=w, h=h, x0=w / 2, y0=h / 2,
                           thrust=thrust, drag=drag, stun_frames=stun_frames,
                           max_frames=max_frames, target=target,
                           parcels=parcels, hazards=hazards)


# --------------------------------------------------------------------------
# visible sets
# --------------------------------------------------------------------------
def lander_visible() -> List[LanderScenario]:
    return [
        LanderScenario(name="L1_straight_drop", y0=100, vy0=0, x0=0, vx0=0, fuel=120),
        LanderScenario(name="L2_offset_left", y0=110, vy0=0, x0=-34, vx0=0, fuel=140),
        LanderScenario(name="L3_tight_fuel", y0=90, vy0=-4, x0=8, vx0=0, fuel=80),
        LanderScenario(name="L4_crosswind", y0=120, vy0=0, x0=0, vx0=0, fuel=175,
                       wind_base=0.45),
        LanderScenario(name="L5_low_and_fast", y0=32, vy0=-11, x0=-5, vx0=1.5, fuel=110),
    ]


def courier_visible() -> List[CourierScenario]:
    return [
        make_courier("C1_open_field", seed=11, n_hazards=0, target=12),
        make_courier("C2_two_hazards", seed=23, n_hazards=2, target=11),
        make_courier("C3_busy", seed=37, n_hazards=5, target=9),
        make_courier("C4_wide_arena", seed=41, n_hazards=3, w=170, h=70, target=10),
    ]
