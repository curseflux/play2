# From your current policy to a practical timed-attempt solution

The worked candidate is `solution_practice.py`. It leaves the three original
files intact and runs through the same engine and grader. All 25 cases are now
public, including the X cases, with geometry in `harness/visible.json`.

## What was wrong with the current approach?

Your physics and collision model already match the engine. The main problem on
these tight maps is the ten-frame horizon. A bounce sets upward velocity that
persists across later frames. Ten safe frames can still leave the bird rising
toward a pipe top with no action that can undo that rise. Once that eventual
collision enters the horizon, it may already be too late.

Your heuristic is reasonable for ordering. It should not need to decide every
difficult maneuver perfectly; search should see far enough to reject bad ones.

## Three changes, in order

1. **Ask whether a complete safe continuation exists.** The recursive function
   returns an action list on success and None on failure. Each call tries bounce
   and coast in heuristic order. It returns immediately when one route survives
   the entire remaining horizon or finishes the course. If none exists, the
   outer policy uses the root action of the deepest safe branch visited.

2. **Remember failed states within this decision.** If the search already
   found no complete safe continuation from a particular depth, y and velocity,
   there is no need to explore that problem again. The failure set is created
   fresh for every real decision. Depth determines horizontal position, so x
   need not appear in its key. Y is rounded to six decimals only in this key
   to merge tiny floating-point differences. This is approximate pruning: it
   could skip an extremely close viable alternative, but cannot turn an
   untested branch into a successful path. Actual motion uses unrounded values.

3. **Precompute the legal vertical range at each depth.** Every branch has the
   same horizontal motion. At a given depth, we therefore already know which
   pipes overlap the bird. Intersect their legal top-left y ranges once. Each
   recursive step then checks two numbers instead of looping through all pipes.

With those changes, a 60-frame horizon becomes practical enough to test. Sixty
is a measured choice for these maps, not a universal value for other engines.

## Read the code in this order

- Constants and the first part of `should_bounce`: physical dimensions and
  the x positions for future frames.
- `bounds`: the legal top-left y interval after each step, including overlapping
  pipes. The bird's height is subtracted from the opening bottom.
- `targets`: the original midpoint heuristic's target at each simulated frame.
- `search`: success, cached failure, exact movement, collision, two choices,
  then cache the state only if both choices fail.
- Final return: first action of the successful path. Only that action executes;
  the next real frame replans from the new observation.

The immediate position update is shared by both choices because this engine
applies the selected bounce AFTER movement and collision checks. A winning
terminal frame need not apply its chosen bounce; the search ends there, so the
candidate's terminal velocity is never used for another prediction.

## Measured results

| Variant | Packaged cases | Worst observed decision |
|---|---:|---:|
| Existing code, horizon 10 | 2/25 | about 8 ms |
| Existing code, horizon 15 | 5/25 | about 225 ms |
| Existing code, horizon 20 | 5/25 | about 3,000 ms |
| Worked candidate, horizon 60 | 25/25 | about 100 ms |

The candidate passed 17/20 fresh stress cases with seed 1, with 93.7% mean pipe
progress and a slowest decision of about 177 ms. Timings vary by machine and load.
The candidate exceeds the harness's advisory 40 ms limit on some decisions;
it is not suitable as-is if an exam enforces that limit strictly. Search still
has difficult worst cases, and a finite horizon can still miss later danger.

## A reasonable 60-minute plan

- Minutes 0-10: read the engine, identify action timing and collision rules.
- Minutes 10-25: implement one exact step and a short recursive survival search.
- Minutes 25-40: inspect failures; add cached failures and a longer horizon.
- Minutes 40-50: precompute pipe overlap ranges if profiling shows the search
  repeatedly scans the same geometry.
- Minutes 50-60: run the suite and fresh cases, save the best version, and
  document known failures. Avoid adding a new algorithm at the last minute.

If decisions must always stay below a strict time limit, that becomes a
different priority: use a bounded search such as a small beam or a node budget
with a retained safe plan. Do not claim that this recursive version provides a
hard time guarantee.

## Run it

From `cosmo_review/harness`:

```powershell
.\practice.cmd test --policy solution_practice.py
.\practice.cmd replay X02 --policy solution_practice.py
.\practice.cmd stress --count 20 --seed 1 --policy solution_practice.py
```

The replay log reports horizon, deepest safe depth, search calls, and the number
of cached failures. These show whether a failure comes with exhausted search,
and where expensive decisions occur.
