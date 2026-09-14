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

## Do the practice problem

```bash
cd mats_prep
python3 grade.py courier --visible-only      # 4 visible scenarios
python3 grade.py courier                     # visible + 12 hidden
python3 watch.py courier C3_busy             # writes an HTML replay you can scrub
python3 tools/stress.py courier --n 200      # randomised scenarios nobody curated
```

Your file is `practice/courier_policy.py`. The spec is the docstring at the
top of `simlab/courier.py`, and the real spec is the `step()` method below it.

Give yourself **60 minutes on a clock** and treat it like the real thing.
A reference solution is in `spoilers/` — encoded, because reading it before
you have struggled is the one way to get nothing out of this.

## Calibration

These are real numbers from this lab, so you know what a score means:

| policy | courier | lander |
|---|---|---|
| thrust straight at the target | 19% | 0% |
| …plus braking to arrive slowly | 44% | 59% |
| a good 60-minute answer | 100% | 100% |

## The other environment

`lander` is the one solved end to end in `WORKED_EXAMPLE.md`. Run
`python3 grade.py lander` to see the finished policy, and
`solutions/stages/` to see the four versions it went through.
