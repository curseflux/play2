# The courier, one rung at a time

You have the decomposition right. Three of your four instincts are correct.
One is a trap, and it happens to be the one that looks hardest — which is the
whole lesson.

---

## Your plan, corrected

> *"first i get the x, y coordinates"*

Yes — and also `vx, vy`. **The velocities are the important half.** Position
tells you where you are; velocity tells you where you are about to be, and
that is what you are actually controlling.

> *"check if i have a package, if yes move to destination, if no pick a good
> one and go to its pickup"*

Exactly right. `obs["carrying"]` is `None` or an index. That is a four-line
`if`, and it is the correct top-level structure.

> *"i am guessing i have to implement some Traveling Salesman algorithm here"*

**No.** This is the trap. See below — I measured it.

> *"i don't have a fixed velocity, instead a fixed acceleration with some drag"*

Yes, and **this is the actual hard part**, not the routing. It is where the
marks are.

> *"on top of everything i need to somehow factor in the moving hazards"*

Yes, and it is ~10 lines, not the monster it looks like. Their velocities are
in the observation, so where they will be is arithmetic, not prediction.

---

## Why not TSP

I built five versions and ran them against all 16 scenarios:

| version | score |
|---|---|
| thrust straight at the nearest pickup | **19%** |
| + arrive slowly enough to actually trade | **44%** |
| + choose the parcel by `both legs`, not nearest pickup | **81%** |
| + steer around hazards | **100%** |
| | |
| the route-planning idea, tuned well (`+0.2 · next_leg`) | 88% |
| the same idea, tuned slightly wrong (`+0.6 · next_leg`) | **62%** |

Read those last two rows carefully. The step *towards* TSP-style reasoning —
one move of lookahead — buys 7 points when you tune its weight correctly and
**costs you 19** when you don't. Meanwhile the thing you were not worried
about (arriving slowly) buys 25, and one line of parcel-selection buys 37.

Four reasons routing is the wrong place to spend your hour:

1. **You carry one parcel at a time.** There is no route to optimise, only a
   "which next" decision. That is a sort, not a search.
2. **You re-decide every frame.** A plan that is recomputed 1200 times per
   episode does not need to be optimal; it needs to be sane. Greedy re-run
   constantly beats optimal computed once.
3. **Hazards randomise your travel times anyway.** Optimising a route against
   distances you cannot actually achieve is optimising the wrong objective.
4. **It is a tuned constant.** The weight on lookahead is not derivable from
   the observation, so it is exactly the kind of number the hidden tests
   punish. Note how badly it degrades at `0.6`.

If you finish early, a one-step lookahead is a legitimate *last* improvement.
It is never the first.

**The general lesson, which is what they are grading:** the combinatorial part
of a problem looks hard and is usually worth little; the continuous control
part looks fiddly and is usually worth everything. Spend accordingly.

---

## The four rungs

Aim to be on rung 2 by minute 25. Rungs 3 and 4 are the back half.

### Rung 1 — get on the board (5 minutes, ~19%)

No control theory. Just pick a target and lean at it.

```python
import math

def policy(obs):
    a = obs["agent"]
    x, y = a["x"], a["y"]

    if obs["carrying"] is not None:
        tx, ty = obs["parcels"][obs["carrying"]]["dropoff"]
    else:
        best = None
        for p in obs["parcels"]:
            if p["state"] != "waiting":
                continue
            d = math.hypot(p["pickup"][0] - x, p["pickup"][1] - y)
            if best is None or d < best[0]:
                best = (d, p["pickup"])
        if best is None:
            return "idle"
        tx, ty = best[1]

    dx, dy = tx - x, ty - y
    if abs(dx) >= abs(dy):
        return "right" if dx > 0 else "left"
    return "up" if dy > 0 else "down"
```

Run it. You now have a file that works and a number that is not zero. **Never
go back below this line.**

### Rung 2 — arrive slowly enough to trade (~44%)

Rung 1 flies past every target at terminal velocity and can never pick
anything up except by accident. You need a target *speed*, not just a target
direction.

```python
speed = min(v_terminal,
            sqrt(arrival_speed**2 + 2 * a_brake * max(0.0, dist - margin)))
want_vx, want_vy = (dx / dist) * speed, (dy / dist) * speed
```

Then act on the **velocity error**, not the position error:

```python
ex, ey = want_vx - vx, want_vy - vy
if abs(ex) >= abs(ey):  return "right" if ex > 0 else "left"
else:                   return "up"    if ey > 0 else "down"
```

You only get one axis per frame, so serving whichever is further off is the
natural allocation. It produces a staircase path. That is fine — a staircase
that arrives is better than a straight line that overshoots.

**About the drag.** You do not need the exact integral. Two facts are enough:

- Terminal velocity is `thrust / drag`. Both are in `obs`. Never hard-code it.
- Drag *helps* you when braking and *fights* you when accelerating. So the
  drag-free formula `sqrt(2·a·d)` overestimates the distance you need — with
  this environment's numbers, by about 2×. You brake early and lose a little
  time. That is the right side to be wrong on. Use `a_brake ≈ 0.7 · thrust`
  and move on.

**Gotcha:** you must be within `pickup_radius` **and** at or below
`grab_speed` on the *same frame*. Both numbers are in `obs`. Aim for about
half of `grab_speed`, so a frame of lag does not cost you the pickup.

### Rung 3 — choose the parcel properly (~81%)

One line, the biggest single jump in the table. Nearest *pickup* is the wrong
metric, because you then have to fly the delivery leg too:

```python
cost = dist(me, pickup) + dist(pickup, dropoff)
```

You are minimising time per delivery, and both legs are time.

### Rung 4 — steer around the hazards (~100%)

Measured: without avoidance, **7.4 hits per episode**. With it, **2.2**. Each
hit is 25 frozen frames *plus* your parcel returns to its pickup point, so
you fly that leg again. It is worth roughly 1.5 deliveries per episode.

Do not react to current distance — you will always react too late. Compute
where you and the hazard *will be*:

```python
rx, ry = h["x"] - x,  h["y"] - y          # relative position
ux, uy = h["vx"] - vx, h["vy"] - vy       # relative velocity
den = ux*ux + uy*uy
t = 0.0 if den < 1e-9 else max(0.0, min(HORIZON, -(rx*ux + ry*uy) / den))
cx, cy = rx + ux*t, ry + uy*t             # separation at closest approach
if math.hypot(cx, cy) < h["r"] + obs["agent_radius"] + MARGIN:
    # on a collision course: add a push away from (cx, cy) to your desired velocity
```

Blend it into the *desired velocity* you already computed in rung 2, then
re-clamp to terminal velocity. Do not make it a separate mode — a policy with
an "avoiding" mode and a "delivering" mode will oscillate between them.

**Gotcha:** hazards bounce off the walls. Straight-line prediction is wrong
across a bounce. With a short horizon (1–2 seconds) it does not matter, which
is a good reason to keep the horizon short.

---

## Before you call it done

```bash
python3 grade.py courier                  # visible + hidden
python3 tools/stress.py courier --n 200   # scenarios nobody curated
python3 watch.py courier C3_busy          # WATCH it. do this at every rung.
```

Watch one full episode at every rung. Every bug I have described above is
obvious in three seconds of animation and invisible in the score.
