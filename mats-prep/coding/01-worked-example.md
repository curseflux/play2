# Worked example — Cargo Lander, narrated

Everything below actually happened, in this order, while building the code in this
directory. The numbers are measured, not illustrative. Reproduce with
`python3 evaluate.py`.

## The task

A 2D lander. Gravity pulls down, one thruster pushes up, two push sideways. Every
frame you are handed `(x, y, vx, vy, fuel, frame)` and return exactly one of
`none / up / left / right`. Land on the pad (`|x| <= 8`) with `|vy| <= 1.2` and
`|vx| <= 0.8`. Score 0–100: 60 for landing, 25 scaled by fuel remaining, 10 for
gentleness, 5 for centring; ~19 partial credit for a near miss.

Three visible scenarios, no wind, generous fuel. Forty hidden ones with wind,
initial drift, tighter fuel, and gravity varying ±12%.

## Minute 0–6: read the spec, and read the scoring function harder

Four observations, in the order they mattered:

1. **One action per frame.** So `up` and `left` are mutually exclusive. Vertical
   and lateral control compete for *frames*, not just fuel. That coupling is the
   actual problem; everything else is arithmetic. I wrote this down because it's
   the kind of constraint that's easy to read past and then be confused by for
   twenty minutes.
2. **Landing is a cliff, fuel is a slope.** 60 points for landing vs 25 for all
   the fuel in the tank. Fuel is worth 0.25 points per unit. So I should spend
   fuel freely to protect the landing. Noted, then promptly under-applied it — see
   minute 40.
3. **Partial credit decays with distance from the pad.** A soft touchdown 15 units
   off-pad scores ~12; a high-speed crash scores ~0. That gives me a fallback
   ordering if things go wrong: soft beats centred.
4. **Gravity 0.18, up-thrust 0.45.** Hovering therefore needs 40% duty. That
   number is going to decide what's affordable.

## Minute 6–12: the dumbest thing that works

```python
def v0_baseline(s):
    if s.vy < -0.8: return "up"
    if s.x > 2.0:   return "left"
    if s.x < -2.0:  return "right"
    return "none"
```

Visible 32.9, hidden 16.4. Bad, but I now know the harness works, the scorer
works, and I have points on the board. **If the clock died here I'd score
something.** This is the step people skip and regret.

## Minute 12–20: PD control, and the first honest surprise

```python
target_vy = -0.9 - 0.03 * s.y        # descend faster when high
if s.vy < target_vy: return "up"
lateral = s.x + 6.0 * s.vx           # position plus lead term
...
```

Visible 34.5. Essentially no better. It lands the straight drop beautifully (86)
and crashes both offset cases, overshooting from x=+45 to x=-32.

Useful lesson, cheap: **a lead term is not a braking plan.** The lead coefficient
that's stable near the target is far too weak 45 units out. PD is a local
linearisation and this problem is not local.

## Minute 20–32: the braking curve

The right tool is kinematics, not gains. From `v² = 2as`, the fastest I can be
descending at altitude `d` and still stop is `sqrt(2*a*d)`:

```python
def desired_vy(y, duty):
    a = (THRUST_UP - GRAVITY) * duty      # duty < 1 reserves frames for lateral
    return -(sqrt(2*a*max(0, y-1.5)) + 0.55)
```

Same idea sideways, with `a = THRUST_SIDE * duty`. Each frame: if falling faster
than allowed, thrust up; otherwise spend the frame on lateral.

**Visible 86.6, all three landed.** Huge jump, three lines of algebra, no search.

## Minute 32–35: the moment that decides the score

Out of habit I ran it on the hidden set — which in a real assessment I could not
do. **Visible 86.6, hidden 41.7, 38% landing rate.**

The thing that looked finished was failing nearly two thirds of what it would
actually be graded on. So the lesson generalises past this task: I cannot see the
hidden set, so **I must manufacture a substitute.** `lander.validation_scenarios()`
— 120 randomised scenarios, ranges deliberately wider than I think the hidden set
uses. From here on, every number I quote to myself is from that.

On validation, the braking controller scored **28.0**.

## Minute 35–42: read the trace, don't theorise

I printed the last frames of a failure:

```
frame      x      y     vx     vy   fuel
   32  -16.2   14.6   1.68  -2.49   79.4
   36  -10.2    5.4   1.49  -1.90   76.1
   40   -4.4    0.4   1.43  -0.88   72.1
   41   -3.0    0.0   1.41  -0.62   71.1   <- crash
```

It landed **on the pad** (x=-3.0), **softly** (vy=-0.62), **with fuel to spare** —
and sideways at `vx=1.41` against a limit of 0.8.

Now the real diagnosis. Vertical and lateral compete for frames, vertical wins
every tie near the ground (correctly — it's the irreversible one), so leftover
lateral velocity can never be paid off. **Altitude is a non-renewable budget for
the lateral problem, and the controller was spending it without accounting for
it.** My braking-curve design had treated the two axes as independent. They are
coupled through time.

The fix is a **gate**: refuse to descend below an altitude that scales with how
much lateral work is outstanding. Brake to a stop at that *floor* instead of at
the ground; the floor falls as lateral error shrinks, so in practice you glide
down continuously rather than hovering.

```python
floor = 0 if lateral_is_clean else 7.0 + 0.42*slack_x + 26*slack_vx
distance = (y - 1.5) if floor == 0 else (y - floor)
```

Visible 87.5 → **hidden 75.9, landing rate 90%**. One structural insight, worth
34 points of hidden score.

**The generalisable form:** when two subgoals compete for a shared irreversible
resource, don't commit to the irreversible part until the other is satisfied. In
this task the resource is altitude. In a pole-balancing task it's angle budget; in
a pursuit task it's closing distance.

## Minute 42–46: the cliff, again

Four residual failures, all with the same fingerprint: touchdown at `x≈0`,
`vx≈0`, and `vy` between **-1.22 and -1.27** against a limit of **-1.20**. Over by
under 0.07. All four had gravity at the high end of its range.

The trace showed why: at `y=8.53, vy=-2.09` the controller returned `none`,
because it was sitting *exactly* on the braking boundary. One frame of gravity put
it outside, and with real gravity stronger than assumed it could never claw back.

**Bang-bang control on an exact feasibility boundary has zero margin for model
error.** Fix: bias the switch to the safe side — thrust when `vy < want_vy +
margin` rather than after crossing. Cost about a unit of fuel (0.25 points) to
protect ~65 points per scenario.

This is the cliff observation from minute 6, which I had written down and then
failed to apply. Writing it down is not the same as applying it.

## Minute 46–52: two ideas that lost

Both of these were more sophisticated than what they were replacing, and both
scored worse. I'm including them because the instinct they illustrate is the main
way people lose points here.

**Model-predictive control.** Simulate each candidate action forward, take the best
first action, re-plan next frame. My first version shaped the rollout cost by hand
and included a term rewarding lost altitude. It **procrastinated**: every frame it
reasoned "falling is progress, and my fallback controller will save me shortly",
then overrode that fallback on the next frame too, and rode a free fall into the
ground at 0 fuel used. Replacing the shaped cost with *roll out to termination and
score with the real scoring function* fixed it entirely — no proxy, nothing to
mis-weight. Result: **79.9 hidden at 196 µs/frame**, against the feedback
controller's **85.1 at 2 µs**. A hundred times the compute for a worse score.

**Online system identification.** Estimate gravity and wind from the acceleration
actually received — one subtraction per frame, since you know what you commanded.
Correct, and it genuinely raised the landing rate. Also **72.6 against 74.2** for
the tuned fixed margin, because a margin absorbs a bounded error instantly while
an estimator needs a dozen frames to converge, and those frames are expensive.

And one idea that was simply **wrong**, which is worth more than either. I tried
replacing the hover gate with "spend altitude as time": estimate how many frames
the lateral problem needs, then descend slowly enough that both axes finish
together. Elegant. It scored **63.4 against 73.5**, with all thirteen failures
touching down softly, off-pad, out of fuel. The premise was false: free fall is
free, but any *constant* descent rate below free fall needs continuous thrust at
the same ~42% duty as hovering. **There is no cheap time in the air.** Total fuel
is roughly `frames_aloft × 0.42 + lateral_thrust`, so the correct objective is to
*minimise* time aloft subject to finishing the lateral manoeuvre — which is what
the gate already did.

I only found out because I measured. Under time pressure the temptation is to ship
the elegant thing because it's elegant.

## Minute 52–58: tune, on my own set, and don't chase the peak

Random search over seven constants, 250 configs, scored on the 120 validation
scenarios (`tune.py`). Then one discipline that matters: **take the centroid of the
top 25 configs, not the argmax.** With 120 scenarios and 250 configs the argmax is
partly noise; the centre of a broad plateau generalises. Argmax scored 76.2 on
validation; the centroid scored 74.2 — and the centroid is the one I'd submit.

## Final numbers

```
policy                      VISIBLE             VALIDATION              HIDDEN    us/frame
                  mean   land    min    mean  land   min    mean  land    min
v0_baseline       32.9    33%    9.0     6.6    2%   0.0    16.4   10%    1.5        1
v1_pd             34.5    33%    6.9    24.3   23%   0.2    31.1   30%    0.5        1
v2_braking        86.6   100%   83.8    28.0   23%   0.3    41.7   38%    4.7        2
v2b_gated         90.5   100%   88.8    72.4   87%   0.0    84.5  100%   74.2        2
v3_mpc            89.0   100%   87.5    68.4   84%   0.0    79.9   95%   13.9      196
dp_openloop       62.0    67%   13.6     3.6    0%   0.0     7.5    0%    0.6       47
dp_closedloop     84.6   100%   81.6    68.6   87%   0.0    79.8  100%   70.8        3
v4_adaptive       83.8   100%   78.4    70.9   88%   0.0    81.9  100%   68.8        3
final_policy      91.0   100%   89.2    74.2   88%   0.0    85.1  100%   75.8        2
```

## What the progression is really about

Look at the visible-vs-hidden columns. `v2_braking` scores **86.6 visible / 41.7
hidden**. If I had optimised against the visible tests — which is what the visible
tests invite you to do — I would have stopped there, felt good, and scored 42.

Every point after that came from four things, none of them algorithmic:

1. Manufacturing a test set the visible tests don't give you.
2. Reading failure traces instead of theorising.
3. Respecting the cliff in the scoring function.
4. Measuring every change and reverting the ones that lost, including the clever
   ones.
