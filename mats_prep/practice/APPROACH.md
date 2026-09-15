# Courier — what to build, in what order

Measured on this repo. Each row adds one idea to the row above it.

| what the policy knows how to do | curated | mean deliveries (200 unseen) |
|---|---|---|
| thrust at the nearest pickup | 19% | 4.7 |
| …+ slow down on arrival | **62%** | 5.4 |
| …+ avoid hazards | 81% | 6.8 |
| …+ pick parcels by both legs, not one | **100%** | 7.2 |

Read that as: **arrival control is worth ~43 points, hazard avoidance ~19,
and the parcel-choice cost function ~19.** The cost function is one line.

---

## 1. Target selection — this is not a TSP

It looks like routing. It isn't, for three reasons:

- **The tour shape is forced.** You carry at most one parcel, so the route can
  only ever be `pickup → dropoff → pickup → dropoff`. The only freedom you
  have is *which parcel next*. There is no tour to optimise.
- **You never commit.** You are called every frame and may change your mind
  every frame. A route computed at `t=0` is wrong by `t=50` — you got stunned,
  a hazard moved, a parcel was dropped. Re-deciding beats planning.
- **The horizon is short.** ~10 deliveries. Greedy, re-evaluated each frame,
  is within a few percent of optimal, and optimal is not what is being graded.

What actually pays is the **cost function**, not the search:

```python
cost = dist(me, pickup)                      # 19 points worse
cost = dist(me, pickup) + dist(pickup, drop) # this one
```

Because a nearby pickup with a dropoff on the far wall is a bad job. That is
the whole insight, and it is one line.

*If you are ahead of the clock*, a one-step lookahead helps a little: add the
distance from this parcel's dropoff to the nearest *other* pickup. Still not
a solver. Stop there.

**The trap.** Greedy re-evaluated every frame can flip between two
near-equal parcels forever and make no progress. Either commit to a target
until you reach it, or require a new candidate to be meaningfully better:

```python
if new_cost < current_cost * 0.85:   # hysteresis
    switch
```

You will only notice this in `watch.py` — the score just looks mediocre.

---

## 2. Arrival control — the big one

You are right that acceleration plus drag is the interesting part. The maths
is easier than it looks.

```python
v_terminal = obs["thrust"] / obs["drag"]     # both are in the observation
```

You do **not** need the drag-aware stopping distance. Drag only ever helps you
stop, so the drag-free formula is already conservative. Measured in this sim
at `thrust=12, drag=1`: actual braking distance from terminal velocity is
**2.87**, the drag-free formula predicts **6.00**. More than 2× of margin,
free.

And with a velocity setpoint you never compute a stopping distance at all —
the profile *is* the answer:

```python
a_brake = 0.7 * obs["thrust"]                       # 0.7 pays for the frame of lag
reach   = max(0.0, dist - 0.5 * obs["pickup_radius"])
speed   = min(v_terminal,
              math.sqrt((0.55 * obs["grab_speed"])**2 + 2 * a_brake * reach))
want    = (dx/dist * speed, dy/dist * speed)        # guard dist == 0
```

`speed` is `v_terminal` when far away and decays to ~half of `grab_speed` as
you arrive — which is the whole requirement, with no phases and no
if-statements.

Then turn the velocity error into one of five actions:

```python
ex, ey = want_vx - vx, want_vy - vy
if abs(ex) < dead and abs(ey) < dead: return "idle"
return ("right" if ex > 0 else "left") if abs(ex) >= abs(ey) else ("up" if ey > 0 else "down")
```

Serving the larger error each frame is how one-axis-per-frame produces
diagonal motion. `dead ≈ 0.35 * thrust * dt`.

---

## 3. Hazards — react, do not route

Your instinct to route around them is correct in principle and a bad use of
the clock. Hazards **move**. One that is "in the way" now will not be there in
three seconds, so blocked-path penalties are weak signal for a lot of code.
The reference in `spoilers/` never routes around hazards and still scores
100%.

What pays is knowing *when you are about to meet one*:

```python
rx, ry = h["x"] - x,  h["y"] - y      # relative position
ux, uy = h["vx"] - vx, h["vy"] - vy   # relative velocity
uu = ux*ux + uy*uy
t  = 0.0 if uu < 1e-9 else clamp(-(rx*ux + ry*uy) / uu, 0.0, HORIZON)
closest = hypot(rx + ux*t, ry + uy*t)
if closest < h["r"] + obs["agent_radius"] + MARGIN:
    # you are on a collision course. push `want` away from (rx+ux*t, ry+uy*t).
```

Reacting to *current* distance is always too late. Reacting to closest
approach is early enough to matter.

---

## 4. The thing you did not mention, which will bite

```python
if obs["agent"]["stunned"] > 0:
    ...            # thrust is ignored this frame
```

Being hit also **drops your parcel back to its pickup point**. If you cached
"my target is parcel 7's dropoff" in a global, you are now flying to a
dropoff for a parcel you are not carrying, and you will never recover.

Read `obs["carrying"]` fresh every frame and the problem disappears. This is
the concrete reason the guide keeps saying *stay stateless*.

---

## Build in this order and check after each step

```bash
python3 grade.py courier --visible-only     # after each step
python3 watch.py  courier C3_busy           # when the score stops making sense
python3 tools/stress.py courier --n 200     # before you believe any score
```

1. Pick a target (nearest pickup), thrust at it. **Expect ~19%.**
2. Add the arrival profile. **Expect ~60%.** Biggest single jump — do not move
   on until you see it.
3. Add closest-approach avoidance. **Expect ~80%.**
4. Change the cost to `dist(me,pickup) + dist(pickup,dropoff)`. **~100%.**
5. Only now: target hysteresis, one-step lookahead, hazard-aware routing.

If step 2 does not give you the jump, the bug is in the arrival profile, not
in anything downstream. Watch a replay before you add anything else.
