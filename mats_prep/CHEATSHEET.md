# Cheat sheet — read the morning of the test, not during it

## The frame

```python
def policy(obs):
    ...
    return one_legal_action        # every path. no exceptions, no None.
```

Asked every frame. Ask yourself: **given where I am now, what does the rest of
this episode have to look like?** Not: what feels right this instant.

## The formula

```python
v_allow = math.sqrt(v_end**2 + 2 * a * max(d, 0.0))
```

The fastest you may be going at distance `d` and still arrive at `v_end`.
Reaches `v_end` exactly at `d = 0`, so the endgame needs no special case.
Use `a` = 70–85% of what you actually have; the rest pays for the frame of
lag and for whatever else wants the actuator.

```python
want_v = -copysign(min(v_allow, cruise_cap), position_error)
err    = current_v - want_v
if   err >  dead: thrust one way
elif err < -dead: thrust the other
else:             coast              # dead ≈ one frame's Δv = thrust*dt
```

`sqrt(2ad)` is minimum **time**, which is maximum **cost**. If you have time,
cap the cruise speed at `k · distance / time_available` and save the fuel.

## Duty cycle

```
to hold station        : g / thrust  of frames
left over for anything : 1 - g/thrust
while braking at a     : (a + g)/thrust  of frames are already committed
```

If two jobs share one actuator, do this arithmetic **before** writing either
controller. It tells you whether the plan is possible at all.

## Collision / intercept

```python
r = them_pos - me_pos
w = them_vel - me_vel
den = dot(w, w)
t   = 0.0 if den < 1e-9 else clamp(-dot(r, w) / den, 0.0, HORIZON)
closest = length(r + w * t)          # < safe_radius  ->  act now, not later
```

## Rollout, when you cannot think of a law

```python
best = max(ACTIONS, key=lambda a: simulate(obs, a, HORIZON))
```

Copy the sim's update into your file. Watch the frame budget.

## Traps, in the order they bite

1. **Globals leaking between episodes.** Many episodes, one process, nothing
   resets you. Prefer stateless; otherwise reset on `t == 0` *and* on a
   discontinuity you can detect.
2. **A constant in your code that is also in the observation.** Every one is a
   hidden-test failure waiting. `g`, thrust, limits, arena size, radii — all
   of them come from `obs`.
3. **Tuning to the visible tests.** If you are changing a number to make case 3
   pass, stop and ask what that number *is*.
4. `sqrt` of a negative; divide by zero; normalising a zero-length vector.
5. Returning an illegal action, or raising. Zero for the whole scenario.
6. Sign conventions and units. Read `step()`, not the prose.
7. Planning to arrive exactly on a limit. You are always one frame late.
8. Chattering: bang-bang with no deadband burns the resource doing nothing.
9. The endgame: what happens at distance 0, speed 0, resource 0, already won?
10. Assuming the episode starts at rest, above the goal, and facing forward.

## The hour

```
0-7    read step(). write down state, actions, update, win, lose, score.
7-12   dumbest legal policy. run it. you are now never at zero.
12-20  pick the target quantity. write the profile. one axis.
20-35  run, WATCH, fix. add the second concern.
35-45  edge cases from the spec, not from the failures.
45-55  randomised scenarios. adversarial reread. guards.
55-60  name the constants, one comment per block saying WHY. submit.
```

## Assistant prompts that earn their keep

```
Summarise this simulator: state variables and units, action set, the exact
per-frame update in order, termination conditions, scoring. Flag ambiguities.

Here is the sim and my policy. Give me five starting states where this fails
and explain the mechanism for each. Do not fix anything yet.

Generate 200 randomised scenarios varying every constant, run my policy,
report pass rate broken down by failure type.
```

Never paste in code you cannot explain. You will have to debug it.

## Last five minutes

- [ ] every path returns a legal action
- [ ] no sqrt(negative), no /0, no normalise(0)
- [ ] no physical constant hard-coded that `obs` provides
- [ ] state (if any) resets — tested by running two scenarios back to back
- [ ] sane when starting at the goal / moving wrong / out of resource
- [ ] constants named, each with a reason
- [ ] a comment naming what it does not handle

**Submit whatever you have.** Partial credit is explicit in the brief.
