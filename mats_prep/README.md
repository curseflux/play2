# MATS AI-Assisted Advanced Coding — practice lab

A working replica of the kind of problem the assessment describes: write one
function, called once per frame, that returns one decision, and get graded by
tests you cannot see.

## Read in this order

| file | what it is | when |
|---|---|---|
| `PREP_GUIDE.md` | how to prepare and how to spend the 60 minutes | first, once, slowly |
| `WORKED_EXAMPLE.md` | a full solve with the reasoning written down as it happened | second |
| `CHEATSHEET.md` | one page of formulas and traps | skim the morning of the test |
| `DEBUGGING.md` | how to see what your policy is thinking | the first time a score stops making sense |

## Two practice problems

`courier` — a delivery drone with momentum, hazards and a routing choice.
`dog` — a side-scrolling course with exactly two actions per frame. Different
skill: `courier` rewards a good control law, `dog` rewards searching a short
horizon. Do `courier` first.

Dog now has **9 visible + 16 hidden cases** covering narrow apex crossings,
stamina-limited climbs, early descents, slaloms, tunnels, and nonzero starting
velocity. See [practice/DOG_CHALLENGES.md](practice/DOG_CHALLENGES.md) for the
new suite, commands, and difficulty measurements.

## Do the practice problem

```bash
cd mats_prep
python3 grade.py courier --visible-only      # 4 visible scenarios
python3 grade.py courier                     # visible + 12 hidden
python3 watch.py courier C3_busy             # writes an HTML replay you can scrub
python3 tools/stress.py courier --n 200      # randomised scenarios nobody curated
```

Same four commands work for `dog` and `lander`. Your files are
`practice/courier_policy.py` and `practice/dog_policy.py`.

Your file is `practice/courier_policy.py`; `practice/LADDER.md` breaks it into
four rungs if you want a way in. The spec is the docstring at the
top of `simlab/courier.py`, and the real spec is the `step()` method below it.

Give yourself **60 minutes on a clock** and treat it like the real thing.
A reference solution is in `spoilers/` — encoded, because reading it before
you have struggled is the one way to get nothing out of this.

## Calibration

These are historical numbers from the original lab. The dog column predates
the harder course set; use DOG_CHALLENGES.md for current dog measurements.

| policy | courier | lander | dog |
|---|---|---|---|
| the obvious reactive thing | 19% | 0% | 0% |
| …plus the one idea it is missing | 44% | 59% | 50% |
| …plus a second idea | — | 94% | 72% |
| a good 60-minute answer | 100% | 100% | 100% |

These old `dog` scores are on the original graded set. On its randomised courses the same four
policies get 0% / 64% / 70% / 87%.

## The other environment

`lander` is the one solved end to end in `WORKED_EXAMPLE.md`. Run
`python3 grade.py lander` to see the finished policy, and
`solutions/stages/` to see the four versions it went through.
