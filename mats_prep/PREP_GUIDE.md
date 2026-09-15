# Preparing for the AI-Assisted Advanced Coding Assessment

They say there is nothing to study. That is half true. There is no syllabus,
but there is a small set of ideas that this genre of problem is built out of,
and there is a way of working that saves fifteen minutes. Both are learnable
in an evening.

---

## 1. What the task actually is

From the brief plus what your friend described, the shape is:

- a physics simulation runs at a fixed timestep
- once per frame it calls **your function** with the current state
- your function returns **one decision**
- there is a visual panel so you can watch it and play it yourself
- automated tests grade it; you see some, and there are more you do not

That is a **control policy**. Not game theory — there is no opponent
optimising against you. Your friend's phrase "algorithm to play the game" is
closer. The adversary is the *dynamics*: momentum, gravity, a resource that
runs out, a deadline.

Their sentence about what they are grading is worth reading twice:

> We care about how you reason about a system that unfolds over time, and
> about your general programming and problem-solving judgment.

"Unfolds over time" is the whole test. A function that only looks at the
current frame is a **reflex**. What they want is a **plan**, recomputed every
frame from the current state. That distinction is the single idea this guide
is about.

---

## 2. The one idea

> Every frame, ask: *given where I am now, what does the rest of this episode
> have to look like for me to win?* Then take the one action that step
> requires.

This is why you almost never need to store state between frames, and why the
answer is usually short. You are not tracking a plan; you are **re-deriving**
it, cheaply, from the observation.

Concretely, that nearly always turns into one of these three shapes:

**(a) A reference profile.** Compute the target value of some quantity as a
function of where you are, then drive the error to zero.

> *"At altitude y, the fastest I can be falling and still stop in time is
> `sqrt(2·a·y)`. Am I above that? Burn. Below it? Coast and save fuel."*

This one formula is the backbone of most of these problems. It converts a
position problem into a velocity problem, and velocity problems have
one-line answers.

**(b) A forward rollout.** You have the physics in front of you. Copy it into
your policy, simulate each candidate action forward for N frames, score the
outcomes, pick the best first action. Brutally effective when the action set
is small, and very fast to write with an AI assistant. Watch the frame budget.

**(c) A time budget.** When one actuator serves two jobs, or a resource has to
last, work in *seconds* and *frames*, not in positions.

> *"The sideways job needs 14 seconds. The descent gives me 9. So the descent
> has to get slower."*

If you can only remember one thing on the day: **compute a target velocity,
not a target position.**

---

## 3. The toolkit

Ten things. Know them well enough that you write them without thinking, so
your 60 minutes goes on the problem and not on the algebra.

### 3.1 Discrete time

Almost every sim of this kind uses semi-implicit Euler:

```python
v += a * dt        # velocity first
x += v * dt        # then position, using the NEW velocity
```

Read the simulator and check the order. It matters at the boundaries, and the
order of the terminal check matters more. Also: **your action takes effect
one frame later than you think.** Leave margin for that lag; never plan to
arrive exactly on a limit.

### 3.2 Stopping distance — `v² = 2·a·d`

The most useful formula in the genre. Rearranged, the three forms you want:

```
d = v² / (2a)                  # distance needed to stop from speed v
v = sqrt(2 a d)                # fastest speed from which you can still stop in d
v = sqrt(v_end² + 2 a d)       # ...ending at v_end instead of 0   <- use this one
```

The third form is the good one. It gives a *profile*: at every distance it
tells you the speed you are allowed to have, and it lands you at `v_end`
exactly at `d = 0`, with no special case at the end.

```python
v_allow = math.sqrt(v_end**2 + 2 * a * max(d, 0.0))   # max(..,0) - never sqrt a negative
```

### 3.3 Velocity setpoint control

```python
want_v = clamp(profile(distance), -v_max, v_max) * direction_to_target
err    = current_v - want_v
if   err >  deadband: thrust one way
elif err < -deadband: thrust the other
else:                 coast
```

Handles arrival, disturbance rejection and overshoot in five lines. The
deadband stops the actuator chattering; one frame's worth of Δv
(`thrust * dt`) is a good starting size.

### 3.4 Bang-bang, chattering, hysteresis

With a discrete on/off actuator you will oscillate around any setpoint. That
is usually fine — it is how you get a duty cycle. It is only a problem when
each toggle costs you something (fuel, a wasted frame). Fix with a deadband,
or with hysteresis (two thresholds) if you are willing to keep state.

### 3.5 Duty cycle

When one actuator serves several jobs, think in **fraction of frames**.

- To hold altitude, the engine must be on `g / thrust` of the time.
- So at most `1 − g/thrust` of frames are available for anything else.
- If you plan a brake that needs 85% of the frames, steering gets 15%,
  and no amount of clever code will give it more.

This turns "can I do both?" into arithmetic you can do in your head. It is
also where most people's policies quietly fail: they write a controller for
each axis, both work in isolation, and neither gets the frames it assumed.

### 3.6 Forward rollout

```python
def rollout(state, action, n):
    s = copy(state)
    apply(s, action)
    for _ in range(n - 1):
        apply(s, coast_or_default)
    return score(s)

best = max(ACTIONS, key=lambda a: rollout(obs, a, HORIZON))
```

Cheap, general, and it handles interactions you have not thought about. The
risks: the frame budget, and scoring a rollout badly (if your score function
is wrong, the search confidently optimises the wrong thing).

### 3.7 Predicting moving things

For a target moving at constant velocity, the time of closest approach is

```python
r = target_pos - my_pos          # relative position
w = target_vel - my_vel          # relative velocity
t_ca = -dot(r, w) / dot(w, w)    # clamp to [0, horizon]; guard dot(w,w) == 0
d_ca = length(r + w * t_ca)      # how close we actually get
```

`d_ca` under a safe radius means you are on a collision course. This is the
whole of obstacle avoidance in most of these problems — and it is far better
than reacting to current distance, which always reacts too late.

### 3.8 Resource budgets

If a resource is spent per frame of actuation, then **slower is more
expensive**. For a lander: over `N` frames with `B` burn frames,

```
v_end − v_start = thrust·dt·B − g·dt·N      →   B = (Δv + g·dt·N) / (thrust·dt)
```

`B` grows with `N`. Hovering is the most expensive thing you can do; the
cheapest descent is the latest possible full-power brake. Every safety
margin you add is bought with fuel. Know which way that trade runs *before*
you start tuning, or you will tune in the wrong direction.

### 3.9 State between episodes — *the classic hidden-test killer*

The harness usually runs many episodes in one process, and **nothing resets
your module globals.** A policy that remembers a plan, a target, a counter or
a "phase" will pass the visible tests and then behave insanely on episode two
because it is still carrying episode one's ideas.

If you keep state, reset it deliberately:

```python
_STATE = {}

def policy(obs):
    if obs["t"] == 0:          # or any other reliable new-episode signal
        _STATE.clear()
```

And watch out: `t == 0` is only reliable if the harness always starts at 0.
A cheap second check is a discontinuity in position, or a change in a
constant that cannot change within an episode (arena size, gravity, the
number of parcels). Belt and braces here is free.

**The safest answer is to keep no state at all.** Most of these problems do
not need it. If you find yourself wanting memory, first ask whether you can
recompute the thing from the observation instead.

### 3.10 Guards

The hidden tests are where the degenerate inputs live.

```python
math.sqrt(max(v, 0.0))          # never sqrt a negative
a / max(b, 1e-9)                # never divide by zero
if dist > 1e-6: ...             # a normalised direction at distance 0 is NaN
```

An exception, an illegal action, or a NaN scores **zero for the entire
scenario** — usually worse than a mediocre policy. Make the function
total: every path returns a legal action.

---

## 4. Spending the 60 minutes

The clock is the real adversary. A plan you decided in advance beats a plan
you improvise while anxious.

| minutes | what | why |
|---|---|---|
| **0–7** | Read the spec twice. Then **read the simulator's update function.** Write down, in a comment block: state variables and units, action set, the exact physics update, the win condition, the score. | Prose is ambiguous; the code is not. Sign conventions and the order of the terminal check have sunk more people than any algorithm. |
| **7–12** | Ship the dumbest legal policy — a constant. Run the tests. | You now have a submittable file and you have proved the harness works. You will never again be at zero. |
| **12–20** | Ask: what does winning require? Write down the target quantity and the profile (§3.2). Implement the one-axis version. | This is where the marks are. Do not skip to code. |
| **20–35** | Run, watch, fix. Handle the second axis / second concern. | Watching beats reading. If there is a visualiser, use it on every iteration. |
| **35–45** | Edge cases from the *spec*, not from the failures: what if it starts already at the goal? moving the wrong way? out of resource? at the boundary? | This is the hidden-test budget. Spend it deliberately. |
| **45–55** | Adversarial pass. Make your own random scenarios and run a hundred. Reread your diff asking "what input breaks this?" | Finds more than another round of tuning. |
| **55–60** | Remove dead code, name the constants, one comment per block explaining *why*. Submit. | Readability is graded. Half your score may be a human reading this. |

Two rules that survive contact with the clock:

**Never be at zero.** Keep a working submittable file at all times. Improve
in small committed steps rather than one big rewrite that might not compile
at minute 58.

**Partial credit is real.** They say so explicitly. A clean policy that
handles the main case well and says, in a comment, what it does not handle,
beats a sprawling one that half-handles everything.

---

## 5. Working with the AI assistant

They expect you to use it. That is a skill with a right and a wrong way, and
they will see the difference in what you produce.

### Delegate these

- **Restating the spec.** "Here is the problem statement and the simulator.
  List the state variables with units, the exact physics update, the
  termination conditions, and anything the prose leaves ambiguous." Catches
  misreadings in 30 seconds. Do this first, every time.
- **Scaffolding.** Debug printing, a rollout loop, a random scenario
  generator, a quick plot of a trajectory.
- **Algebra.** "Solve `v² = v0² + 2a(y − h)` for the altitude where braking
  must start." Fast and reliable, and it frees your attention.
- **Adversarial review.** The highest-value prompt in the whole hour:
  > "Here is the simulator and here is my policy. Give me five specific
  > starting states where this fails, and say why for each."
  Then run them. This is how you find hidden-test failures before the hidden
  tests do.
- **Cleanup.** "Rename these constants to say what they mean and add one
  comment per block explaining why, not what."

### Do not delegate these

- **The control idea.** If you open with "write me a policy for this", you
  will get a plausible reactive heuristic, you will not understand it, and
  you will spend the remaining 50 minutes debugging someone else's model of a
  problem you never built your own model of. Decide the *shape* of the
  solution yourself; ask for help filling it in.
- **Anything you cannot explain.** If a hidden test fails, you have to debug
  it. Code you do not understand is a liability, not progress.
- **Judgment about scope.** The assistant will happily add a Kalman filter.
  You are being graded on knowing you do not need one.

### Prompt patterns worth stealing

```
"Summarise this simulator: state variables and units, action set, exact
 per-frame update in order, termination conditions, and the scoring rule.
 Flag anything the description leaves ambiguous."

"My policy is below. Without changing the approach, list the inputs that
 make it crash, loop forever, or return an illegal action."

"Write a function that generates 200 randomised scenarios for this
 environment, varying every constant, and reports the pass rate by failure
 type."

"This fails when <X>. Do not fix it yet — explain the mechanism first."
```

That last one matters. An assistant asked to fix will patch the symptom. An
assistant asked to explain will often show you that the design is wrong,
which is the fix you actually want.

### If the assistant turns out to be weak

You will not know which model is behind the editor, and it does not change the
plan much — but it does change the failure mode you should fear.

A weaker assistant is **not** mainly a risk of getting no help. It is a risk of
getting *confident, plausible, wrong* help: eighty lines of reasonable-looking
heuristics that you then debug for half an hour, having never built your own
model of the problem. That risk goes **up**, not down, as the model gets
weaker. The correct response is to delegate *less of the thinking*, not to
worry more.

Practical adjustments, in order of value:

1. **Run everything it writes. Never approve by reading.** Plausible code is
   exactly what a weaker model is best at producing. A five-second test run
   settles what ten seconds of reading cannot.
2. **One task per prompt.** "Write this helper" not "write the policy and
   handle the edge cases and add comments". Compound requests are where weaker
   models silently drop a clause.
3. **Paste the code into the prompt.** Do not rely on it having correctly
   picked up the editor context, and do not rely on it remembering what you
   said fifteen minutes ago.
4. **Shift what you delegate toward the mechanical.** Algebra, boilerplate, a
   scenario generator, renaming — these barely degrade. Open-ended design
   critique degrades a lot. Make critique concrete instead: *"list five inputs
   where this returns NaN, raises, or returns None"* is a checklist a weak
   model can run; *"is my design sound?"* is not.
5. **Keep your own check on scope.** A weaker model is more likely to
   enthusiastically agree that you need a Kalman filter.

Two things stay true regardless of the model. First, the single highest-value
prompt — *"summarise this simulator: state variables, units, update order,
termination conditions, ambiguities"* — is a reading-comprehension task on a
short file, which is the easiest thing you will ask all hour. Second, opening
with *"write me a policy for this"* produces a mediocre reactive heuristic from
**any** model, strong or weak, because the prompt does not contain the
insight. The delegation boundary matters more than what is behind it.

---

## 6. What separates a good answer from a bad one

| | weak | strong |
|---|---|---|
| **decisions** | thresholds tuned until the visible tests pass | quantities computed from the observation and the physics |
| **constants** | `if vy < -3.2` | `if vy < -sqrt(2 * a_brake * y)`, with `a_brake` derived from `thrust` and `g` in the observation |
| **spec coverage** | implements the part the visible tests exercise | implements the whole spec, including what is untested |
| **state** | module globals that leak between episodes | stateless, or reset explicitly and defensively |
| **degenerate inputs** | crashes on distance 0, resource 0, already-at-goal | every path returns a legal action |
| **structure** | one 120-line function | named helpers, one concern each |
| **comments** | `# move left` | `# steering only gets the frames hovering doesn't need` |
| **honesty** | silence about what it cannot do | a short comment naming the case it does not handle and why |

The hidden tests exist to catch exactly one thing: **tuning to the visible
cases.** If you find yourself changing a number to make test 3 pass, stop and
ask what that number *is*. If it is not derivable from the observation, you
are overfitting and the hidden tests will find you.

---

## 7. The checklist for the last five minutes

- [ ] Every code path returns a legal action. No exceptions, no `None`.
- [ ] No `sqrt` of a possible negative, no division by a possible zero.
- [ ] No constant in the code that also appears in the observation.
- [ ] If I keep state, it resets on a new episode — and I have tested that by
      running two different scenarios back to back in one process.
- [ ] It behaves sensibly when the episode starts already at the goal, moving
      the wrong way, out of resource, or on a boundary.
- [ ] Constants are named and each has a reason next to it.
- [ ] Anything I know is unhandled is written down in a comment.

---

## 8. How to actually practise

Do the `courier` problem in this repo under a real 60-minute clock. Then:

1. **Read your own transcript.** Where did the time go? Almost everyone
   discovers they spent 15 minutes on something the spec had already
   answered, because they did not read the simulator.
2. **Run `tools/stress.py`.** If your score on randomised scenarios is far
   below your score on the curated ones, you overfit. That gap is the exact
   thing the hidden tests measure.
3. **Then** read `spoilers/courier_reference.py` and compare **structure**,
   not constants.

If you want more reps after that, the same shape covers a lot of ground —
ask an assistant to build the environment and hold yourself to the same
60-minute rule:

| drill | what it forces you to learn |
|---|---|
| Land a rocket with limited fuel | stopping distance, resource budgets |
| Balance a pole on a cart | reacting to a state you must not let diverge |
| Fly through a gap in moving walls | prediction, time of closest approach |
| Catch falling objects with a cart | prioritising under a deadline |
| Steer a car round a track with momentum | speed profiles on a path |
| Pursue an evading target | prediction against something that reacts |
| Ration a battery across a long route | budgeting over the whole episode |
| Dock two bodies with thruster-only control | coupled axes, one actuator |

Three of those, done properly with a clock, is more preparation than anyone
needs. The point is not the problems; it is that by the fourth one you stop
asking "what should I do this frame" and start asking "what does the rest of
this episode have to look like".
