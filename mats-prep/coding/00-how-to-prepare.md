# AI-Assisted Advanced Coding Assessment — how to prepare

## Epistemic status

I haven't seen the test. What's solid: the blurb tells you it's a per-frame
control policy for a physics simulation, continuously scored, with hidden
scenarios beyond the visible ones, and that you're expected to lean on the
built-in assistant. Your friend's description ("write an algorithm aspect
solution to play with the game for a single function") is consistent with that.
Everything about the *specific* simulation is inference. The approach below is
robust across the plausible variants, and the practice kit in this directory
instantiates one of them so you can drill against something real.

## What the shape of the task tells you

Four sentences in the blurb are load-bearing:

1. **"a function that is called once per frame and returns a single decision"** —
   this is a closed-loop control problem. You get fresh state every frame. That
   fact is the whole strategic key, and it's the one your friend's approach threw
   away.
2. **"We care about how you reason about a system that unfolds over time"** — the
   difficulty is in the dynamics and the irreversibility, not in the algorithm.
3. **"passing those is not enough for a full score. There are additional
   scenarios your policy is run against"** — the visible tests are a smoke test,
   not the target. Your real competition is the scenarios you can't see.
4. **"Partial progress earns partial credit"** — the score is continuous. Get
   something working early and never be in a state where you'd score zero.

## The single most important idea

**Re-decide every frame from the current state. Never execute a plan you computed
earlier.**

You are handed the true state of the world once per frame, for free. That is a
feedback signal. Any approach that computes a sequence of actions up front and
then replays it is throwing away the most valuable thing the problem gives you,
and it will be destroyed by anything the hidden scenarios vary — a different
starting condition, a disturbance, a physics constant slightly off from what you
assumed.

Measured, on the practice task in this directory, on 40 held-out scenarios:

| approach | visible | **hidden** | hidden success rate |
|---|---|---|---|
| DP solved once, replayed open-loop | 62.0 | **7.5** | **0%** |
| *the same DP table*, re-queried every frame | 84.6 | **79.8** | **100%** |

Same algorithm. Same table. The only difference is when it's consulted. That is
the entire gap between a bad score and a good one.

## How to spend 60 minutes

Pre-commit to this. The clock is the real opponent.

| time | minutes | what |
|---|---|---|
| 0–06 | 6 | Read the whole spec. **Find and read the scoring function.** List the actions, the state fields, the termination conditions, the constraints. |
| 06–12 | 6 | Write the dumbest policy that does something sensible. Run it. Confirm the loop, the score, and the visualiser all work end to end. **Bank partial credit.** |
| 12–20 | 8 | Instrument. Log state across frames and *measure* the physics — gravity, drag, thrust magnitude, what happens at boundaries. Do not take constants from the prose. |
| 20–35 | 15 | Write the real closed-loop controller. Run it on the visible cases. |
| 35–45 | 10 | **Write your own randomised scenario generator.** Make it harder than you think the hidden set is. This is where most of the hidden-test score comes from. |
| 45–55 | 10 | Read failure traces, fix the top failure mode, tune a couple of constants against your generator. |
| 55–60 | 5 | Robustness pass: guard every edge case, wrap the body so it cannot raise, confirm per-frame cost is small, submit. |

Two non-negotiables in that table. **Minute 12: something scoring is submitted.**
**Minute 45: you have your own randomised test set.** Everything else is
negotiable.

## Read the scoring function first, and look for cliffs

The score is continuous but the *constraints* usually aren't. On the practice
task, landing requires `|vy| <= 1.2`; the score for landing is ~85 and for not
landing ~19. Four of my controller's failures touched down at `vy` between -1.22
and -1.27 — over the limit by under 0.07, each costing ~65 points, to save about
one unit of fuel worth 0.25 points.

**Where the objective is a slope and the constraint is a cliff, pay the slope to
stay well off the cliff.** Deliberately aim for 70–80% of any hard limit. This one
habit was worth more on the practice task than every algorithmic improvement
combined.

## Measure the dynamics; don't trust the prose

The spec's constants may be rounded, stale, or overridden per-scenario. Spend
five minutes logging `(state_before, action, state_after)` and back out the real
numbers:

```python
# one frame, no thrust, tells you gravity (and drag, if you do two)
a_observed = v_after / drag - v_before
```

On the practice task, hidden scenarios vary gravity by ±12% and add a wind worth
40% of the side thruster — neither mentioned anywhere. You can *estimate both
online from one subtraction per frame*, because you know what you commanded.

Honest caveat from actually building it: online estimation turned out to score
slightly *worse* than a well-tuned fixed safety margin (72.6 vs 74.2 on 120
validation scenarios), because a margin absorbs a bounded error immediately while
an estimator needs a dozen frames to converge. Measuring is still how you *find
out* the variation exists. Whether you keep the estimator is an empirical
question — answer it by measuring, not by taste.

## The controller patterns worth knowing

You don't need control theory. You need three patterns.

### 1. Proportional-derivative on an error

```python
error = target - current
if error + K * velocity > deadband:  act one way
elif error + K * velocity < -deadband: act the other
else: do nothing
```
Five lines, works on a surprising range of tasks, and a fine 20-minute answer.
Deadband matters: without one a discrete controller chatters.

### 2. The braking curve (this is the one to actually remember)

From `v² = 2as`: the fastest you can be going at distance `d` from a target and
still stop is `v = sqrt(2 * a * d)`, where `a` is the deceleration you can
command. So:

```python
v_allowed = sqrt(2 * a_available * distance_remaining)
if speed > v_allowed - margin:  brake
else:                           coast or accelerate
```

This is the minimum-time *and* near-minimum-fuel solution to "get there and
stop," it's three lines, and it needs no search. On the practice task it took the
score from 34 to 87 on the visible set — a bigger jump than anything else I did.
Use a conservative `a` (assume less authority than you have) and subtract a
margin, for the cliff reason above.

### 3. Re-planned rollout (MPC), only if you have time

Each frame, for each candidate action: simulate forward with your own copy of the
dynamics under a fallback policy, score the outcome, take the best first action,
throw the rest away, repeat next frame.

Two things I learned the hard way building this:

- **Score the rollout with the real objective, not a hand-shaped proxy.** My first
  attempt shaped a cost with a term rewarding progress toward the goal. It
  *procrastinated*: every frame it reasoned "falling is progress and my fallback
  will save me in a moment", then overrode the fallback's correction on the next
  frame too, and rode a free fall into the ground. Rolling out to termination and
  scoring with the actual scoring function removed the whole class of bug.
- **Only deviate from the fallback when clearly better.** Require a margin of
  improvement. Otherwise rollout-model error talks you out of correct actions.

MPC cost 100× the compute per frame (196 µs vs 2 µs) and scored *worse* than the
tuned feedback controller (79.9 vs 85.1). Don't reach for it first. If there is a
per-frame time limit, it's also where you'll hit it.

## Write your own randomised test set — this is the main event

The blurb tells you the visible tests are insufficient. The fix is mechanical:
write a generator that samples initial conditions and physics parameters over
ranges *wider* than you expect, run 50–100 of them, and look at the worst cases.

This is exactly the gap it catches. On the practice task:

| policy | visible | hidden |
|---|---|---|
| before this step | **86.6** | 41.7 |
| after (one structural fix it revealed) | 90.5 | **84.5** |

86.6 on the visible set with 100% success looked finished. It was failing 62% of
hidden scenarios. Nothing but a randomised set of my own would have shown me that.

Vary: starting positions and velocities (including near boundaries), every physics
constant by ±10–20%, any resource budget, any disturbance, episode length, and the
degenerate cases (already at the target; already failing; zero resources).

Ask the assistant to write the generator. It's ideal work to delegate: mechanical,
and you can check it at a glance.

## Read failure traces, don't theorise

Every real improvement I made came from printing the last 15 frames of a failing
episode. Twice I had a confident theory and the trace said otherwise.

The concrete habit: for a failing case, dump `frame, state, action` for the final
frames, find the **first** frame where the decision was wrong, and ask why that
frame looked acceptable to your controller. On the practice task the answer was
once "it coasted for exactly one frame while sitting on the feasibility
boundary" — invisible from the score, obvious from the trace.

## Defensive coding for a graded harness

A crash on one hidden scenario is a zero on that scenario. Costs nothing to avoid:

- Wrap the whole body in `try/except` and return a safe default action.
- Never index a list or dict without a default. State fields you expect may be
  missing on some scenario.
- Clamp every output to the legal action set.
- Guard against division by zero, `sqrt` of a negative, `None`, `NaN`.
- Handle the first frame (no history) and the last (near-termination) explicitly.
- Don't rely on global state surviving between episodes — **detect episode resets**
  (e.g. `frame == 0`, or a frame counter that didn't increment) and reinitialise.
  If the harness runs episodes in parallel or reuses your module, stale state is a
  silent, very confusing failure.
- Keep per-frame cost small and bounded. Never allocate a large table inside the
  per-frame function without caching it.
- No `print` in the hot path at submission time.

## Working with the AI assistant

You're expected to use it heavily and it is not cheating to. But the failure mode
is real: an assistant with access to the visible tests will happily write
something that passes them and fails everything else.

**Delegate freely:** the randomised scenario generator; the parameter sweep
harness; logging and trace-printing utilities; the visualiser; boilerplate;
refactors; "here's my controller, enumerate the edge cases it doesn't handle";
"write me the closed-form braking curve for these dynamics"; translating your
stated intent into clean code.

**Keep for yourself:** the decision about what the controller's *structure* is;
reading the failure traces; judging whether a change actually helped. Those are
what's being assessed, and they're where the assistant is least reliable because
it can't see the scores.

**Prompts that work well here:**

- Paste the spec verbatim, then: *"List every state field, every legal action,
  every termination condition, and the exact scoring formula. Flag anything
  ambiguous."* Catches misreadings in the first five minutes.
- *"Write a function that generates 80 randomised scenarios varying initial
  conditions and every physics constant by ±15%, plus the degenerate edge cases."*
- *"Here is my policy and here are 6 failing episodes with per-frame traces. For
  each, identify the first frame where the decision was wrong and why."*
- *"Sweep these 4 constants over these ranges against my validation set and print
  the top 10 configs by mean score, plus the worst-case score for each."*
- *"Review this for anything that could raise an exception or return an illegal
  action."*

**Discipline that keeps you out of trouble:** after every assistant edit, re-run
your own validation set and compare numbers. Keep the best-scoring version in a
variable or a comment and never lose it. If a change doesn't improve the measured
score, revert it — including your own clever ideas. I discarded two redesigns that
way while building the practice task, and both *felt* better than what they lost to.

## The five-minute pre-submit checklist

- [ ] Cannot raise: whole body wrapped, safe default returned.
- [ ] Returns only legal actions, always.
- [ ] Works from frame 0 with no history; detects episode reset.
- [ ] Per-frame cost is microseconds, not milliseconds.
- [ ] Ran on my own randomised set, not just the visible tests; I know the worst case.
- [ ] Margins on every hard constraint — aiming for ~75% of each limit, not 99%.
- [ ] Re-decides from current state every frame; no replayed plan anywhere.
- [ ] The highest-scoring version I achieved is the one being submitted.
- [ ] No debug printing.
