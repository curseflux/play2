# Pulseflight — a 60-minute practice assessment

Fly a small bird through a sequence of shutter gates. Write one function:

```python
def decide(telemetry):
    return "glide"  # or "pulse"
```

Your function is called once per simulation frame. The starter in `answer.py`
is intentionally unfinished. Your objective is to clear as many gates as you
can across different courses. A full pass requires completing a course alive.
Partial progress earns credit.

## Start the clock here

1. Give yourself 60 uninterrupted minutes.
2. Read `SPEC.md` and `arena/engine.py`. These are the public rules.
3. Implement your policy in `answer.py`. You may use a coding assistant.
4. Run visible tests and inspect replays as you work.
5. Run the full grader before stopping. Save your best working submission.

This is a new setup. Read the rules instead of assuming the dog experiment's
actions, coordinates, update order, resources, or collisions still apply.

## Commands

On this Windows machine, open a terminal in this folder:

```powershell
.\run.cmd list
.\run.cmd test
.\run.cmd test --case A03
.\run.cmd watch A03
.\run.cmd test --all
.\run.cmd stress --count 50 --seed 1
```

The launcher finds Python or uses the locally bundled interpreter. On another
machine with Python 3.10+, replace `.\run.cmd` with `python exam.py`.
There are no third-party dependencies.

`watch` writes `replays/A03.html`. Open it in a browser. It has playback,
frame stepping, scrubbing, and your `DEBUG` dictionary beside each decision.
Add debug values before returning an action:

```python
DEBUG.clear()
DEBUG.update(y=telemetry["bird"]["y"], note="my current decision")
```

Use `--agent attempt2.py` with `test`, `watch`, or `stress` to compare a saved
version. Paths are relative to this folder. One imported agent is reused across
all cases in a run; globals are not reset for you.

## Assessment layout

| File | Purpose |
|---|---|
| `answer.py` | Your submission |
| `SPEC.md` | Observation contract and mechanics |
| `arena/engine.py` | Authoritative public simulator |
| `cases/visible.json` | Five visible courses |
| `exam.py` | Runner and scoring |
| `arena/replay.py` | Replay rendering |
| `_exam/` | Private cases, authoring tools, and solvability checks; do not read during the mock |

The full grader runs 5 visible and 10 hidden cases. Hidden cases show only
pass/fail. The final average score includes partial progress on every case.
Exceptions and illegal actions score zero for that case. Exit code 1 from
`test` or `stress` means at least one case failed; it is not a broken command.

Aim for decisions under 40 ms on this machine. Timing is reported, and the
budget is advisory: no hard runtime cutoff is imposed. A policy that loops
forever must be interrupted manually.

Every packaged course and generated stress course has a successful flight
verified against the final simulator. A poor score does not mean the course
requires an impossible maneuver. The one-hour goal is useful progress, not
necessarily a perfect solution.

