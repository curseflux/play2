"""Rebuild simlab/_hidden_blob.py. Run from the mats_prep directory."""
from __future__ import annotations

import base64
import json
import pathlib
import zlib

LANDER = [
    dict(_label="rising_start",      y0=70,  vy0=14.0, x0=0,   vx0=0,    fuel=150),
    dict(_label="gusty",             y0=115, vy0=0,    x0=0,   vx0=0,    fuel=190,
         wind_base=0.15, wind_amp=1.05, wind_period=55.0, wind_phase=1.2),
    dict(_label="razor_fuel",        y0=85,  vy0=-2.0, x0=0,   vx0=0,    fuel=58),
    dict(_label="far_offset_wind",   y0=140, vy0=0,    x0=48,  vx0=0,    fuel=200,
         wind_base=-0.35),
    dict(_label="high_altitude",     y0=230, vy0=0,    x0=-12, vx0=0,    fuel=230),
    dict(_label="thrown_sideways",   y0=95,  vy0=-1.0, x0=-20, vx0=-7.0, fuel=265),
    dict(_label="already_on_target", y0=6,   vy0=-0.5, x0=0.5, vx0=0.1,  fuel=40),
    dict(_label="narrow_pad",        y0=100, vy0=0,    x0=14,  vx0=0,    fuel=165,
         pad_half_width=2.5),
    dict(_label="heavy_world",       y0=110, vy0=0,    x0=-9,  vx0=2.0,  fuel=210,
         g=2.6, up_thrust=5.2, side_thrust=2.0),
    dict(_label="feather_world",     y0=95,  vy0=0,    x0=11,  vx0=0,    fuel=150,
         g=0.6, up_thrust=1.5, side_thrust=0.6, max_touchdown_speed=1.5),
    dict(_label="low_ceiling",       y0=150, vy0=-6,   x0=0,   vx0=0,    fuel=190,
         ceiling=175.0),
    dict(_label="slow_gate",         y0=105, vy0=0,    x0=-16, vx0=0,    fuel=190,
         max_touchdown_speed=1.2, max_lateral_speed=0.45),
]

COURIER = [
    dict(_label="calm_big",     seed=101, n_hazards=1, w=150, h=95,  target=10),
    dict(_label="swarm",        seed=113, n_hazards=8, target=7, haz_speed=11.0),
    dict(_label="short_clock",  seed=127, n_hazards=3, max_frames=750, target=5),
    dict(_label="clustered",    seed=131, n_hazards=3, target=10, cluster=True),
    dict(_label="sluggish",     seed=149, n_hazards=3, thrust=6.5, drag=0.8, target=8),
    dict(_label="twitchy",      seed=151, n_hazards=4, thrust=26.0, drag=1.6, target=11),
    dict(_label="cramped",      seed=163, n_hazards=4, w=70, h=50, target=6, haz_r=6.0),
    dict(_label="long_haul",    seed=173, n_hazards=4, w=200, h=120, max_frames=1700, target=10),
    dict(_label="brutal_stun",  seed=181, n_hazards=6, stun_frames=60, target=6),
    dict(_label="few_parcels",  seed=191, n_hazards=2, n_parcels=6, target=5),
    dict(_label="giant_rocks",  seed=197, n_hazards=3, haz_r=11.0, haz_speed=6.0, target=7),
    dict(_label="rerun_of_C2",  seed=23,  n_hazards=2, target=11),
]

DOG = [
    dict(_label="gentle",      seed=201, gap=15.0, max_step=12.0),
    dict(_label="needle",      seed=211, gap=10.5, max_step=14.0, target=10),
    dict(_label="big_steps",   seed=223, gap=13.0, max_step=28.0, target=11),
    dict(_label="tall_room",   seed=227, gap=13.0, ceiling=90.0, max_step=32.0, target=11),
    dict(_label="squeeze",     seed=233, gap=11.0, ceiling=38.0, max_step=9.0, target=11),
    dict(_label="tired_dog",   seed=239, gap=14.0, stamina_max=2, regen_period=8, target=11),
    dict(_label="heavy_dog",   seed=251, gap=13.0, gravity=52.0, bounce_impulse=25.0, target=11),
    dict(_label="floaty_dog",  seed=257, gap=13.0, gravity=13.0, bounce_impulse=12.5, target=11),
    dict(_label="sprinter",    seed=263, gap=14.0, forward_speed=38.0, spacing=72.0, target=11),
    dict(_label="crowded",     seed=269, gap=14.0, spacing=30.0, max_step=10.0, target=11),
    dict(_label="one_eye",     seed=271, gap=13.0, sight=1, max_step=14.0, target=11),
    dict(_label="ragged",      seed=277, gap=14.0, gap_jitter=4.0, max_step=18.0, target=11),
    dict(_label="marathon",    seed=281, gap=13.0, n_pipes=30, max_step=16.0, target=24),
    dict(_label="rerun_of_D2", seed=17,  gap=13.0, max_step=16.0, target=12),
]

if __name__ == "__main__":
    payload = json.dumps({"lander": LANDER, "courier": COURIER, "dog": DOG},
                         separators=(",", ":"))
    blob = base64.b64encode(zlib.compress(payload.encode("utf-8"), 9)).decode("ascii")
    lines = [blob[i:i + 96] for i in range(0, len(blob), 96)]
    body = '"\n    "'.join(lines)
    out = pathlib.Path(__file__).resolve().parents[1] / "simlab" / "_hidden_blob.py"
    out.write_text(
        '"""Hidden scenarios. Opaque on purpose - see simlab/hidden.py."""\n\n'
        f'BLOB = (\n    "{body}"\n)\n'
    )
    print(f"wrote {out} ({len(blob)} chars, "
          f"{len(LANDER)} lander + {len(COURIER)} courier + {len(DOG)} dog)")
