# A worked example, with the thinking left in

This is the `lander` environment in this repo, solved end to end. Every number
below is real — you can reproduce all of it. The point is not the final code;
it is the sequence of wrong ideas that led to it, because that sequence is
what you will be doing on the day.

> **Honesty about the clock.** This took me longer than 60 minutes, and it
> includes one dead end I would not have had time to explore in a test. I have
> marked the parts that are realistic in 60 minutes and the parts that are
> "only if you are ahead". The *reasoning* is the transferable bit.

Run along:

```bash
python3 grade.py lander --policy solutions/stages/stage2.py --reveal
python3 watch.py  lander L4_crosswind --policy solutions/stages/stage3.py
```

---

## The problem

A lander descends toward a pad. Once per frame you return **one** of
`"off" | "up" | "left" | "right"`. `"up"` fires the main engine; `"left"`/
`"right"` fire side thrusters; each costs one unit of fuel. You land
successfully if, when altitude reaches zero, you are slow enough, not sliding
sideways, and over the pad.

---

## Minutes 0–7 — read, and write down what you read

I did not look at the prose twice. I read `step()`. Here is what I wrote in a
comment block before touching anything:

```
state:   x (offset from pad, +right), y (altitude, +up), vx, vy, fuel, t
         also given: g, up_thrust, side_thrust, dt, and the three landing gates
actions: off / up / left / right   -- ONE per frame, each non-off costs 1 fuel
update:  ax = wind(t); ay = -g
         if action != off and fuel > 0:  fuel -= 1; ay += up_thrust  (or ax ± side)
         vx += ax*dt; vy += ay*dt;  x += vx*dt; y += vy*dt;  t += 1
win:     at y <= 0:  vy >= -2.5  AND  |vx| <= 1.0  AND  |x| <= 6
lose:    too fast / off pad / |x| > arena / y > ceiling / out of time
```

Five things jumped out of that, and four of them mattered later:

1. **One action per frame.** You cannot brake and steer on the same frame.
   That is not a detail, that is the problem. The two jobs compete for the
   same scarce thing: frames.
2. **Fuel is per frame of thrust, not per unit of impulse.** So the cost of a
   manoeuvre is how many frames it takes, which means *slow is expensive*.
   I flagged this but did not yet believe how much it mattered.
3. **Semi-implicit Euler** — velocity updates before position, so my action
   affects position on the same frame it affects velocity, but I only observe
   the result on the next call. One frame of lag. Leave margin.
4. `wind` is in the observation, so the disturbance is **observable**, not
   something I have to estimate.
5. `g`, `up_thrust`, `side_thrust` and all three gates are in the observation.
   **So no constant in my code may be a physical quantity.** If I ever write
   `2.5` I have made a mistake, because the hidden tests will change it.

That last one is free marks and most people miss it. I checked afterwards:
four of the twelve hidden scenarios change gravity, thrust, or a gate.

---

## Minutes 7–12 — ship something that runs

```python
def policy(obs):
    return "off"
```

`0/17`. Obviously. But the harness works, my file imports, and I have
something submittable. From here I am never at zero.

---

## The first real idea — and why the obvious one is wrong

The reflex version, which is what I would have written at 22:

```python
def policy(obs):
    if obs["vy"] < -3.0:      return "up"     # falling too fast? burn
    if obs["x"] >  2.0 and obs["vx"] > -2.0: return "left"
    if obs["x"] < -2.0 and obs["vx"] <  2.0: return "right"
    return "off"
```

**`0/17`. 1% on random scenarios.** Worth understanding *why*, because the
reason generalises.

It does not crash into the ground. It runs out of fuel. Descending at a held
3 m/s from 100 m takes 33 seconds; over `N` frames with `B` burn frames,

```
v_end − v_start = up_thrust·dt·B − g·dt·N      →     B = (Δv + g·dt·N) / (up_thrust·dt)
```

`B` grows with `N`. **A slow descent costs more fuel than a fast one**, because
you are paying to fight gravity for longer. The intuition that "gentle is
safe" is exactly backwards here. The cheapest descent is free-fall followed by
the latest possible full-power brake.

I did not know that when I started. I got it by staring at the failure reason
(`impact vy=-5.92` after 337 frames — far too many frames) and asking where
the fuel had gone. **Read the failure text, not the pass count.** It is trying
to tell you something.

---

## Stage 2 — stop picking a speed, compute one

The fix is to replace the constant `3.0` with the *fastest speed I could have
at this altitude and still stop in time*:

```
v² = v_end² + 2·a·d      →      v_allow(y) = sqrt(v_touch² + 2·a_brake·y)
```

At `y = 0` this equals `v_touch` exactly, so there is no special case near the
ground — which is where special cases go wrong.

```python
touch  = 0.45 * obs["max_touchdown_speed"]     # aim at 45% of the limit, not 100%
a_br   = 0.80 * (up - g)                       # plan on 80% of what we have
v_allow = -math.sqrt(touch**2 + 2 * a_br * max(y, 0.0))
if vy < v_allow:  return "up"
```

Two deliberate margins. `touch` at 45% of the gate means a late frame is a
soft landing rather than a crash. `a_br` at 80% of available deceleration is
the budget that pays for the one-frame lag *and* for frames stolen by
steering. Both are named, both have a reason, neither is tuned.

The same profile idea handles sideways: `want_vx = −sign(x)·sqrt(2·a_lat·|x|)`,
then thrust to close the gap between `vx` and `want_vx`.

**`10/17`, 25% on random scenarios.** A real jump. And notice the shape of
what it now gets right *for free*, without any special-casing:

- starts moving upward → `vy > v_allow` → coast, let gravity do the work
- starts low and fast → already past the profile → burn immediately
- almost no fuel → burns as late as possible, which is the optimal thing

That is the payoff of a profile over a threshold. **One expression replaced
four cases I would otherwise have had to think of.**

---

## Reading the failure, not the score

Every stage-2 failure looked like this:

```
L4_crosswind   crash: slide vx=+3.10 (limit 1.00); off pad x=+10.87
L2_offset_left crash: slide vx=+1.80 (limit 1.00); off pad x=+10.90
```

All sideways. Never vertical. So the vertical controller is fine and something
systematically starves the sideways one. I printed the actions frame by frame
(30 seconds of work, and I should have done it sooner):

```
t=  96 y=46.10 vy=-13.36 x= 0.43 vx=0.27 -> up
t= 108 y=31.38 vy=-11.28 x= 1.11 vx=0.81 -> up
t= 120 y=19.72 vy= -8.40 x= 2.43 vx=1.35 -> up
t= 132 y=11.51 vy= -5.52 x= 4.40 vx=1.89 -> up
```

There it is. During the entire braking phase the answer is `up`, every frame,
and `x` walks away unopposed. **Obvious in the trace, invisible in the score.**

And now the duty-cycle arithmetic from §3.5 of the guide explains it exactly.
While braking, the fraction of frames the engine must be on is

```
f = (a_brake + g) / up_thrust  =  (1.92 + 1.6) / 4.0  =  88%
```

leaving 12% for steering. The crosswind needs `0.45 / 1.5 = 30%` just to hold
position. **12% < 30%: the sideways controller cannot win, and no tuning of it
will help.** The bug is not in the steering code. The bug is that the vertical
plan did not leave room for it.

This is the moment the problem stopped being two controllers and became one
allocation problem. If I take one thing from this exercise, it is that:
**when two jobs share an actuator, the sizing of one is a constraint on the
other, and you have to do that arithmetic explicitly.**

---

## Stage 3 — couple the axes through time

If the sideways job needs more clock than the descent gives it, then the
descent has to be slower. So: estimate both, compare, and cap the descent
speed when sideways is on the critical path.

```python
t_ground = (v_prof - touch) / a_br + max(0.0, (v_prof + vy) / g)   # seconds to land
t_lat    = 2 * sqrt(d / a_lat) + abs(vx) / a_lat                   # bang-bang estimate

if t_lat > CRIT * t_ground:
    t_want = STRETCH * t_lat
    v_cap  = max(touch, y / t_want)        # descend no faster than this
v_allow = -min(profile, v_cap)
```

`v_cap = y / t_want` reads directly: *"do not reach the ground for at least
`t_want` seconds"*.

I also stopped the sideways controller flying the *minimum-time* approach.
`sqrt(2·a·|x|)` gets there as fast as possible, which is the most expensive
way — and pointless if I have 20 seconds of descent anyway. So cap the cruise
speed at what the available clock actually requires:

```python
want_vx = -sign(x) * min(sqrt(2*a_lat*abs(x)),          # never faster than we can stop
                         CRUISE_K * abs(x) / t_use)     # nor faster than we need
```

**`16/17`, 79% on random scenarios.** Same two ideas — a profile, and a time
budget — applied twice.

*In a real 60 minutes, this is where I would have stopped and spent the
remaining time on guards and comments. 94% with clean reasoning is a good
submission.*

---

## The dead end (worth more than the fix)

I was not happy that `L4_crosswind` still failed, so I rebuilt the
arbitration. The idea sounded better: instead of "vertical first, steering
gets leftovers", serve **whichever axis is further behind**, with a safety
veto that checks whether skipping a vertical frame is still recoverable.

```python
vert_frames = max(0, deficit) / (net * dt)     # frames of burn owed
lat_frames  = abs(err) / (side * dt)           # frames of steering owed
if lat and recoverable and lat_frames >= vert_frames:
    return lat
```

It looks more principled. It scored **53%** — far worse than the thing it
replaced.

The trace showed why, and it is a good lesson. The vertical error is *small in
magnitude and fatal in consequence*; the sideways error is *large in magnitude
and survivable*. Comparing their magnitudes treats them as commensurable, and
they are not. The policy spent every frame steering, rode the recoverability
limit all the way down, and arrived at the ground having never braked.

Worse, an earlier version had a genuine feedback loop: drift made `t_lat`
larger, which stretched the descent, which lowered the cruise speed cap, which
slowed the correction, which increased the drift. **A control law whose own
error makes its response weaker will fail, and it will fail slowly enough that
the first few seconds look fine.** Watch for the sign of that loop in anything
that feeds an error estimate back into a planning horizon.

The lesson I actually took: **a hard constraint is not a priority.** Vertical
is not "more important" than sideways — it is a *constraint*, and constraints
do not get traded off against objectives. The right structure is:

> Vertical always wins. Steering gets every frame vertical does not need.
> All the intelligence goes into choosing a descent profile that leaves
> enough of them.

which is both simpler and correct, and is what the final version does.

---

## The overfitting trap, caught by a tool I should have built sooner

A later version hit **17/17**. Curated tests, visible and hidden, all green.

Then I generated 400 randomised scenarios — random gravity, thrust, gate
widths, starting states, wind — and ran it: **54%.**

Seventeen out of seventeen, and it fails half of everything else.

I had tuned six constants against seventeen scenarios and the constants had
absorbed the scenarios. The fix was not better constants; it was noticing that
one of them should never have been a constant at all:

```python
# WRONG: "the steering channel gets about half of the side thrust"
a_lat = 0.5 * side_thrust

# RIGHT: it gets the frames hovering doesn't need, and that is computable
share = max(0.05, 1.0 - g / up_thrust)      # fraction of frames left over
a_lat = LAT_MARGIN * share * side_thrust    # LAT_MARGIN is the only free number
```

In the default world `1 − g/up = 0.60`. In the `feather_world` hidden case it
is `0.60` too, but in `heavy_world` it is `0.50` — and in a randomised world it
can be `0.15`. A constant cannot know that. The observation does.

**Random stress went 54% → 92% from that one change**, and the curated set
stayed at 17/17. That is the signature of a real fix rather than a tuned one:
it helps most where you were not looking.

If you take one *practical* habit from this document, take this one:

> Before you believe a score, generate scenarios nobody curated and run a
> hundred of them. It costs ten minutes and it is the closest thing you have
> to seeing the hidden tests.

`tools/stress.py` in this repo is that, and writing it is a fine use of the
assistant.

---

## Where it ended up

```
stage 0   always "off"                         0/17     0% random
stage 1   reactive thresholds                  0/17     1% random
stage 2   velocity reference profile          10/17    25% random
stage 3   + coupled through a time budget     16/17    79% random
final     + sizing derived from observation   17/17    92% random
```

The final policy is ~60 lines in `solutions/lander_reference.py`. The whole of
it is:

1. `share = 1 − g/up` — how many frames steering can ever have.
2. `a_lat` sized from that, not guessed.
3. `a_brake` reduced when there is wind to hold against.
4. A descent profile; stretched when the sideways job needs the clock;
   the stretch capped by what the fuel can pay for.
5. A sideways velocity setpoint: never faster than we can stop, never faster
   than we need.
6. Arbitration in three lines: vertical if below profile, else steer, else off.

Every constant that remains is a *margin* (`0.80`, `0.45`, `1.20`) rather than
a physical quantity, and each has a sentence next to it saying what it buys.

## What it still gets wrong

8% of randomised scenarios. Mostly worlds with very weak side thrust and a
large initial offset, where the honest answer is that the scenario may not be
survivable at all. I know this because I re-ran them with eight times the fuel
and the failure rate barely moved — so it is not a fuel problem, and where it
is not a fuel problem it is a scenario that cannot be flown.

Writing that paragraph is part of the answer. On the day, a comment saying
*"this does not handle X, because Y, and here is what I would do with more
time"* is worth more than silence, and much more than a hack that makes X pass
by accident.

---

## The rubric, restated from this example

What made the difference, in order of how much it was worth:

1. **Reading `step()` instead of the prose.** Told me about the one-action
   constraint and the per-frame fuel cost, which are the whole problem.
2. **Replacing a threshold with a profile.** `0/17 → 10/17`.
3. **Reading a trace when the score plateaued.** Turned "sideways is broken"
   into "88% of frames are already committed", which is a different and
   solvable problem.
4. **Doing the duty-cycle arithmetic explicitly.** Proved that no amount of
   work on the steering code could fix it.
5. **Randomised stress testing.** Caught an overfit that every curated test
   said was fine.
6. **Deriving constants from the observation.** `54% → 92%`.

What was worth nothing:

- Tuning constants against the visible cases. Every hour I spent there bought
  a percent or two and hid a structural bug.
- The "more principled" arbitration. Being clever about priority when the
  right answer was that one of them is a constraint.
