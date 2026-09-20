# EchoFlight: your final 60-minute mock

Guide a bird through moving gates and collect enough stars before the finish.
Implement `act(observation) -> bool` in `policy.py`.

This is an independent practice exercise, not a claim about the actual exam.
Your assistant may read all public files. Neither of you should read `_staff/`,
private data, or solutions in other practice folders during the attempt.

## What is different?

- A flap command takes effect **one frame later**. The observation tells you
  whether a command is already queued. A queued flap cannot be canceled.
- Gate openings move vertically with time. Their motion parameters are public.
- Two uncollected stars and three uncleared gates are visible at a time.
- Extra stars are optional; some tempt you toward unsafe routes.
- Controls are plain Python booleans. Holding True queues a flap every frame.

Read `RULES.md` and `simulator.py` before implementing your local model.
There is no required algorithm: reactive control, search, and hybrids are allowed.

## Commands

From this folder in PowerShell:

```powershell
.\practice.cmd list
.\practice.cmd test
.\practice.cmd test --case E02
.\practice.cmd replay E02
.\practice.cmd test --all
.\practice.cmd stress --count 30 --seed 1
```

Elsewhere, use `python grade.py` in place of `.\practice.cmd`.
Only Python 3.10+ and the standard library are needed. The Windows launcher also
finds the bundled interpreter on this computer.

Replays are standalone HTML files under `replays/`. They show the state BEFORE
each decision, the command you choose, the previously queued command, and DEBUG.
Use `--submission saved_policy.py` with test, replay, or stress to compare policies.

The suggested decision budget is **20 ms**, advisory rather than enforced.
The grader reports the slowest call. Exit code 1 means some tests failed;
replay generation returns 0 even when the flight fails.

## Cases

| Case | Theme |
|---|---|
| E01 Echo | Static gates, delayed control, no star quota |
| E02 Sweep | Moving openings and star collection |
| E03 Slalom | Closer gates and an initially queued flap |
| E04 Temptation | Optional stars in dangerous positions |
| E05 Narrow | Smaller margins and smaller stars |
| E06 Endurance | A longer course with a larger quota |

There are 6 visible and 12 hidden cases. Hidden results expose only pass/fail.
Every packaged case and generated stress case has a verified successful action
sequence. Feasibility does not mean every mistake remains recoverable.

Start the timer before reading the rules. Keep 10 minutes for testing and
debugging. Save your final policy and record your score, timing, and how much
assistant-generated code you had to correct. Keep changes inside your policy
and its helpers; do not alter the environment, grader, or test cases.
