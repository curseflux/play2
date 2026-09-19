# Skyparcel — a fresh 60-minute mock

Pilot a bird through gates, pick up parcels, and deliver them to depots.
Implement `choose(view)` in `submission.py`. Return `"press"` or `"release"`.

This is independent practice, not a reconstruction of any actual assessment.
It remains a small-action physics problem, but the controls, state, and reward
rules differ from the previous exercises. Read the new rules before coding.

## Your attempt

Set a 60-minute timer, read `RULES.md` and `engine.py`, then build your policy.
Use `AI_START.md` as a short opening message for your assistant. It establishes
the task boundaries without supplying an algorithm or solution.

Edit `submission.py`. You may create helper modules for your policy, but do
not modify the engine, grader, or cases to improve a score. Do not read `_staff/`
or copy policies from the other practice folders during this mock.

You need to reach the finish alive with enough **deliveries**. Merely picking
up a parcel does not earn delivery credit. Missing a station is allowed, and
some optional pickups should be skipped. Partial progress earns partial credit.

## Commands

From this folder on Windows:

```powershell
.\practice.cmd list
.\practice.cmd test
.\practice.cmd test --case S02
.\practice.cmd replay S02
.\practice.cmd test --all
.\practice.cmd stress --count 30 --seed 1
```

Elsewhere, replace `.\practice.cmd` with `python assess.py`. Python 3.10+ and
its standard library are sufficient. The Windows launcher also finds the
bundled interpreter on this machine.

Replays are self-contained HTML files in `replays/`. Open them in a browser.
Amber lines mark pickup stations; green lines mark depots. The bird shows an
amber parcel while loaded. State, selected action, and your optional module
`DEBUG` dictionary are aligned before each decision.

Use `--submission saved.py` to compare another policy file. The grader reuses
one imported module across episodes. Clear any persistent state at tick zero.
A suggested 40 ms decision budget is reported but not enforced; interrupt a
nonterminating policy manually. Exit code 1 means at least one case failed.

## Cases

| Case | Focus |
|---|---|
| S01 Warmup | Flight control; no required deliveries |
| S02 Handoff | Pickup shortly before an obstacle |
| S03 Heavy | Stronger gravity while carrying a parcel |
| S04 Temptation | Optional unsafe pickup stations |
| S05 Narrow | Tighter station windows and gate openings |
| S06 Longhaul | A longer sequence of pickups and deliveries |

The full grader has 6 visible + 12 hidden cases. Hidden cases reveal only
pass/fail; partial scores contribute to the final average. All packaged courses
and generated stress courses have successful delivery witnesses verified against
the simulator. This proves feasibility, not that every mistake is recoverable.

After the hour, save your answer and note time spent on reading, implementation,
assistant corrections, and debugging. Compare those timings with your solo mock.

