# The DEBUG panel

Your policy is called 1200 times. `print()` gives you 1200 lines you will not
read. The `DEBUG` dict gives you the same numbers **lined up with the frame
they belong to**, so you can scrub to the moment it goes wrong and read what
the policy was thinking at that instant.

## Wiring it up — three lines

```python
DEBUG: dict = {}          # module level, next to your imports

def policy(obs):
    ...
    DEBUG.clear()                                   # <- do not skip this
    DEBUG.update(phase=phase, dist=dist, want=speed,
                 speed=math.hypot(vx, vy),
                 can_grab=math.hypot(vx, vy) <= obs["grab_speed"],
                 in_range=dist <= obs["pickup_radius"])
    return action
```

The runner snapshots `DEBUG` straight after each call to `policy`, so one row
of the trace is **one decision**: the state your policy was shown, the action
it chose, and what it was thinking while choosing. Nothing is off by a frame.

`DEBUG.clear()` matters because the dict is a module global. Without it, a key
you set on one branch survives into frames that never took that branch, and
you will debug a number your policy did not compute.

## Reading it — two ways

**In the browser**, scrub through the animation and read the side panel:

```bash
python3 watch.py courier C3_busy --policy practice/courier_policy.py
```

**In the terminal**, when you already know roughly when it breaks:

```bash
python3 watch.py courier C3_busy --dump 120:136
```

```
     t       x       y      vx      vy    act  can_grab   dist  in_range   phase   speed    want
   120   13.38   35.68   -5.54    4.80   idle     False  3.025     False deliver   7.331   7.129
   121   12.89   36.11   -4.98    4.32   idle     False  2.365      True deliver   6.598   6.304
   122   12.44   36.50   -4.49    3.89  right     False  1.772      True deliver   5.938   5.455
   123   12.15   36.85   -2.84    3.50   left     False  1.328      True deliver   4.507   4.723
   124   11.78   37.16   -3.75    3.15  right     False  0.838      True deliver   4.901   3.751
   125   11.56   37.45   -2.18    2.84   down     False  0.496      True deliver   3.577   2.888
   126   11.36   37.58   -1.96    1.35     up      True 23.048     False   fetch   2.382  12.000
```

`in_range=True` and `can_grab=False` for five frames running: the drone is
sitting on top of the dropoff, too fast to trade, wobbling. The score does not
show that. The panel does.

## When the panel is empty

`watch.py` now tells you which of these it is. In order of likelihood:

**1. The DEBUG lines never run.** They are below a `return` that always fires.
The stub ships with `return "idle"` at the bottom of `policy`; if you pasted
the DEBUG lines after it, they are unreachable.

```python
    return "idle"
    DEBUG.clear()          # dead code. python will not warn you.
```

**2. Frame 0 takes an early return.** The viewer opens on frame 0, and a
guard like `if agent["stunned"] > 0: return "idle"` above your DEBUG lines
means the first frames have nothing. Scrub forward and the values appear.
Fix it properly by writing DEBUG *before* the early returns:

```python
def policy(obs):
    DEBUG.clear()
    DEBUG.update(t=obs["t"], stunned=obs["agent"]["stunned"])   # always runs
    if obs["agent"]["stunned"] > 0:
        DEBUG.update(branch="stunned")
        return "idle"
    ...
    DEBUG.update(branch="fetch", dist=dist, want=speed)         # add as you go
```

Updating in stages like this is strictly better anyway: `branch` then tells
you which path each frame took, which is one of the most useful things you
can put in there.

**3. You are looking at a stale file.** `watch.py` overwrites
`traces/<env>_<scenario>.html`, but your browser may serve the cached copy.
Hard-reload (Ctrl-Shift-R / Cmd-Shift-R).

**4. `--policy` points somewhere else.** With no `--policy`, courier defaults
to `practice/courier_policy.py`. If you are editing a different file, say so
on the command line.

**5. `NameError` in the DEBUG line itself.** Referencing a variable that does
not exist yet kills the episode. `grade.py` reports it as
`policy raised NameError: ...` — check there if the score suddenly went to 0.

The fastest check for all of these:

```bash
python3 watch.py courier C1_open_field --dump 0:6
```

If the debug columns are missing or `None`, it is 1 or 2. If they are there,
it was 3.

## What to put in it

Not the state. `x`, `y`, `vx`, `vy` are already in the panel. Put in **what
your policy computed and cannot otherwise see**:

| put this in | catches |
|---|---|
| the target you chose (`tx`, `ty`, or the parcel id) | flipping between two targets every frame |
| your desired speed vs your actual speed | an arrival profile that is too aggressive or too slow |
| which branch fired, as a string (`"fetch"`, `"deliver"`, `"avoid"`) | a branch that never runs, or runs constantly |
| **the win condition, split into booleans** | the single best one — see below |
| the intermediate you are least sure about | the thing you got wrong |

The win-condition trick is worth the whole panel. The rules say you trade when
`in_range AND slow_enough`. Put both in as separate booleans. Now you can see
at a glance whether you are failing because you never arrive, or because you
arrive and cannot stop. Those are completely different bugs and the score
calls them both "0 delivered".

## Scanning instead of scrubbing

Once the values are in the trace you can search them, which beats scrubbing
when you do not know where to look:

```python
res = run_episode(env, mod.policy, record=True, debug_source=mod)
bad = [f for f in res.trace
       if f["debug"].get("in_range") and not f["debug"].get("can_grab")]
print(len(bad), "frames in range but too fast")
```

Run on the example above:

```
buggy  delivered 13   163 frames in range but too fast  (13.6% of the episode)
fixed  delivered 13    96 frames in range but too fast  ( 8.0% of the episode)
```

Identical score on that scenario — and a real defect, worth **44% → 62%**
across the full set once fixed. That is the argument for the panel in one
line: **the score tells you whether you are winning, DEBUG tells you why.**

## On the real assessment

You will not have this. What you will have is `print()`, and the discipline
transfers if you keep it cheap:

```python
if obs["t"] % 20 == 0:                       # every 20th frame, not every frame
    print(f"{obs['t']:4d} d={dist:6.2f} want={speed:5.2f} "
          f"have={math.hypot(vx,vy):5.2f} {phase}")
```

One line per 20 frames is 60 lines for a whole episode — readable. And the
same rule applies to what goes in it: your decision variables and the win
condition split into its parts, not the state you were handed.

---

# Appendix: when the extra machinery is not worth it

The shipped `dog` reference is a ~60-line short-horizon rollout. A reader of
this repo sent in an 8-line policy:

```python
aim = gap_centre - gap_height / 4.5      # aim BELOW the middle of the gap
if stamina and x < pipe.x + pipe.half_w and y < aim:
    return True
return False
```

Measured head to head:

```
                       graded set   400 random courses
  8-line aim point       18/18            83.2%
  60-line rollout        18/18            85.0%

  paired: both pass 324, aim-only 9, rollout-only 16, neither 51
  25 discordant pairs, 16/9 split -> not significant
```

They are the same policy as far as this environment can tell, and the
discordant cases show no pattern in gap width, sight or stamina. The rollout
is four times the code for noise.

**Why the 8-liner works.** The aim point is below the gap centre on purpose.
A bounce sets `vy` upward, so you always arrive at a pipe *rising*: aiming low
means the overshoot lands you in the middle instead of through the top. It is
the offset that does the work, not the threshold — aiming at the exact centre
scores 8/18 and 65%.

**Why write the rollout at all.** It needs no insight into the geometry. Given
a deterministic simulator and a small action set, "simulate both options and
take the one still alive" works before you understand the problem. That is
worth something when you are 15 minutes in and do not yet see the aim point.
It stops being worth it the moment you do.

The honest rule: **rollout buys generality, not accuracy.** Reach for it when
the closed form does not exist — moving targets, several interacting
constraints, a scoring rule you cannot invert. When a one-line aim point
exists, it wins on every axis that matters under a clock: fewer places to be
wrong, faster to debug, and a reviewer can check it by reading.

**The one criticism of the 8-liner.** `4.5` sits at the bottom edge of its safe
range:

```
  divisor      2.5   3.0   3.5   4.0   4.5   5.0   6.0   8.0   12.0   inf
  curated     0/18  3/18  9/18 14/18 18/18 18/18 18/18 18/18 16/18  8/18
  random      5.6% 36.8% 68.0% 77.6% 82.8% 84.0% 84.4% 82.4% 82.4% 65.2%
```

Flat from 4.5 to 8, collapsing below 4. Sitting at the first value that passes
puts you on the cliff edge; 5.5 or 6 is the middle of the plateau and costs
nothing. **When you tune a constant, sweep it and stand in the middle of the
range that works, not at the edge where it started working.**
