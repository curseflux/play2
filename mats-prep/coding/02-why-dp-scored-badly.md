# Why your friend's dynamic programming scored badly

> *"I applied dynamic programming and thought it should be correct but eventually
> only solve to a bad score."*

Dynamic programming was almost certainly not the wrong *choice*. It's a reasonable
tool for this problem class. But there are four specific ways a correct DP
implementation produces a bad score on a per-frame control task, and I hit three
of them by accident while building the practice kit — so these aren't
hypotheticals.

Ranked by how likely I think each one is to be what happened, with the caveat that
I'm reasoning from one sentence of secondhand description.

---

## 1. Open-loop execution — most likely, and by far the most costly

**The failure.** Solve the DP on frame 0, extract the optimal action sequence,
then return `plan[frame]` each frame. This is a completely correct solution to a
different problem: the one where the world does exactly what your model said.

**Why it collapses.** The moment reality diverges — a different initial condition,
a disturbance, a physics constant slightly off, a rounding difference — your state
is no longer the state your plan assumed, and the error compounds every frame with
nothing correcting it. You are flying a 200-frame trajectory with your eyes shut.

**Measured on the practice task**, 40 held-out scenarios:

| | visible | hidden | hidden success |
|---|---|---|---|
| DP solved once, replayed open-loop | 62.0 | **7.5** | **0%** |
| *identical DP table*, re-queried each frame | 84.6 | **79.8** | **100%** |

Same algorithm, same table, same everything. The only change is consulting it with
the current state instead of the frame index. Note also that the open-loop version
scores a *plausible-looking* 62 on the visible scenarios — clean, no disturbances,
matching its assumptions — which is exactly how you end up submitting it.

**What "correct but bad score" feels like from the inside:** the logic is right,
the visible tests look acceptable, and the hidden score is terrible. That matches
your friend's description closely enough that I'd put most of my probability here.

**The fix is one line of structure.** A DP table is a *policy* — a map from state to
action. Query it with the state you're in, every frame. Never index it by time.

---

## 2. Discretisation artifacts — I hit two distinct ones

DP needs a grid, and the grid is where the difficulty secretly lives. Both of
these produced a table that was *silently all-infeasible*, which manifests as a
policy that never fires the thruster at all.

**(a) Self-transitions.** One frame at low speed moved my lander 0.18 units. My
altitude cells were 3.0 units. So `next_cell == current_cell`, and a backward sweep
ordered by altitude had no valid topological order. My sweep forbade same-cell
transitions, concluded every state was unreachable, and returned "do nothing"
everywhere. I lost real time to this before printing the transition:

```
action=none  dy=-0.179  grid step=3.0  iy=40 -> jy=40  (needs jy<iy)
action=up    dy=+0.269  grid step=3.0  iy=40 -> jy=40  (needs jy<iy)
```

**(b) An unreachable goal.** Soft touchdown required `|vy| <= 1.2`, i.e. descending
at most ~1 unit per frame. My bottom altitude cell was 2 units tall. You
*physically cannot* cross that cell in one frame while staying under the speed
limit — so the terminal state was unreachable from anywhere and the table was
all-infeasible again, for an entirely different reason.

**Fixes:** cells small relative to one frame of motion; solve with value iteration
or Dijkstra rather than a single ordered sweep, so self-transitions are handled;
and **sanity-check the table before trusting it** — e.g. "how many states does my
policy thrust in?" If the answer is 0 or all of them, you have a bug, not a policy.

---

## 3. Model mismatch

Your DP optimises against *your* model of the dynamics. If the simulator's gravity,
drag, integration order, or collision handling differs even slightly, your plan is
optimal for the wrong world.

On the practice task the hidden scenarios vary gravity by ±12% and add a wind
nobody mentions. A plan computed with textbook gravity is wrong by exactly the
amount that matters. Closed-loop execution largely absorbs this (you keep
re-deciding from where you actually are); open-loop execution amplifies it every
frame.

**Fix:** measure the dynamics empirically (log `state_before, action, state_after`
and back out the constants), and leave margin on every hard constraint.

---

## 4. Objective mismatch

A DP minimising the obvious thing — time, or control effort — may not be
maximising the *score*. If the scoring function weights gentleness, or resource
remaining, or a centring bonus, and your cost function doesn't, you get a
beautifully optimal trajectory that scores mid.

Related and nastier: **a hard constraint that the score treats as a cliff.** My
controller's residual failures touched down at `vy = -1.22` against a limit of
-1.20 — optimal by the fuel objective, catastrophic by the score. A DP that treats
the constraint as a hard boundary will happily plan trajectories that sit exactly
on it, which is the one place you must not be when your model is imperfect.

**Fix:** make the DP's cost function the actual scoring function where you can, and
tighten every constraint to ~75–80% of its stated limit.

---

## 5. Two more worth checking

- **Per-frame compute.** If the table is built inside the per-frame function rather
  than cached, you'll blow any time limit. Build once, memoise, and know your
  per-frame cost. (Mine: 2 µs for the feedback controller, 196 µs for MPC.)
- **Stale state across episodes.** An open-loop plan stored in a module global, with
  the harness running several episodes, gives episode 2 episode 1's plan. Detect
  resets (`frame == 0`, or a frame counter that didn't increment) and reinitialise.

---

## What to tell him, and what to do yourself

DP wasn't the mistake. **Executing a plan instead of a policy was** — probably,
given the description. The one-sentence version:

> Any method that produces a *policy* (state → action, consulted every frame) is
> fine. Any method that produces a *plan* (a sequence, replayed) will be destroyed
> by the hidden scenarios.

And the practical ordering for the 60 minutes, which is what I'd actually optimise:

1. A closed-loop feedback controller, derived from kinematics (`v = sqrt(2as)`),
   gets you most of the score in a fraction of the time. On the practice task it
   beat both the DP and the MPC versions, ran 100× faster than MPC, and fit in
   about 30 lines.
2. If you want search, use it as **re-planned rollout** — simulate forward each
   frame, take the first action, discard the rest, repeat. Score rollouts with the
   real objective, not a hand-shaped proxy.
3. Either way: **the score comes from your own randomised test set, not from the
   algorithm.** On the practice task, the gap between "aces the visible tests" and
   "works" was 43 points of hidden score, and no amount of algorithmic
   sophistication would have found it.
