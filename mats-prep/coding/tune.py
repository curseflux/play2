"""Random search over controller knobs, tuned on a SELF-MADE validation set and
checked once against the held-out hidden set.

Two habits worth keeping:
  * tune on scenarios you generated, never on the visible tests;
  * prefer a config sitting in a broad plateau over the single argmax -- with 120
    scenarios and hundreds of configs, the argmax is partly noise.
"""
import random
import lander
import policies

VAL = lander.validation_scenarios(n=120, seed=4242)


def score(make, **kw):
    s = lander.summarise(lander.evaluate(make(**kw), VAL))
    return s["mean"], s["land_rate"], s["min"]


SPACE_V4 = dict(
    vduty=(0.35, 0.75), hduty=(0.35, 0.70), k_x=(0.25, 0.70),
    k_vx=(14.0, 40.0), floor_base=(3.0, 12.0), commit_alt=(7.0, 16.0),
    margin=(0.06, 0.30), fuel_safety=(1.05, 1.70), vx_cap=(1.4, 3.0),
)
SPACE_V2B = dict(
    vduty=(0.35, 0.75), hduty=(0.35, 0.70), k_x=(0.25, 0.70),
    k_vx=(14.0, 40.0), floor_base=(3.0, 12.0), commit_alt=(7.0, 16.0),
    margin=(0.06, 0.30),
)


def search(make, space, n=250, seed=1):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        kw = {k: rng.uniform(*v) for k, v in space.items()}
        m, l, mn = score(make, **kw)
        rows.append((m, l, mn, kw))
    rows.sort(key=lambda r: -r[0])
    return rows


def plateau(rows, top=25):
    """Centroid of the top configs -- a cheap way to avoid chasing noise."""
    keys = rows[0][3].keys()
    return {k: sum(r[3][k] for r in rows[:top]) / top for k in keys}


if __name__ == "__main__":
    for name, make, space in (("v2b_gated", policies.make_v2b, SPACE_V2B),
                              ("v4_adaptive", policies.make_v4, SPACE_V4)):
        rows = search(make, space)
        cen = plateau(rows)
        m, l, mn = score(make, **cen)
        print(f"{name}: argmax {rows[0][0]:.1f} (land {rows[0][1]:.0%}) | "
              f"top-25 centroid {m:.1f} (land {l:.0%}, min {mn:.1f})")
        print("   ", {k: round(v, 3) for k, v in cen.items()})
