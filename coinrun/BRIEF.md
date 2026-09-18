# Coinrun — a one-hour control-policy mock

Write `act(obs)` in `solution.py`. Return `True` to bounce or `False` to coast.
The dog runs right automatically. Navigate pipes and collect enough coins to
reach the finish with the displayed target met.

This is an independent practice exercise inspired by a discussion of a dog,
pipes, coins, and limited visibility. It is NOT a reconstruction of the real
test. The exact physics, scoring, and case distribution here are practice
choices. The 21-case count is inspired by the reported score, not evidence
that these cases resemble an actual assessment's cases.

## The attempt

Set a 60-minute timer. Read `RULES.md` and the public simulator `world.py`, then
edit `solution.py`. Use a coding assistant if you want to rehearse that workflow.
Don't read `_private/`: it contains authoring code and solvability witnesses.
No solution policy is supplied in the learner area.

Your policy receives **at most one coin at a time** and the next two pipes.
Coin IDs are stable. A coin disappears after collection or after you pass it;
that disappearance does not always mean you collected it. Check the count.

Some coins are unsafe or impossible to collect. The required target is always
achievable without those coins. You do not need every coin. Reaching the finish
without enough coins is a failed case with partial credit.

## Commands

From this folder on Windows:

```powershell
.\practice.cmd list
.\practice.cmd grade
.\practice.cmd grade --case V03
.\practice.cmd replay V03
.\practice.cmd grade --all
.\practice.cmd stress --count 50 --seed 1
```

On another system with Python 3.10+, use `python run.py` in place of
`.\practice.cmd`. No third-party packages are needed. The Windows launcher
also supports the bundled interpreter on this machine.

Replays are saved as `replays/V03.html`; open them directly in a browser. They
show the visible coin, actions, and your `DEBUG` dictionary aligned with the
pre-action state. The optional reveal checkbox is for diagnosis; your policy
never receives all future coins.

Use `--policy saved_attempt.py` to compare another file. One imported policy
is reused across episodes. Clear persistent state at frame zero if you use it.
The suggested decision budget is 40 ms; timing is reported but no hard timeout
is imposed. Interrupt a hung policy manually.

## Visible cases

| Case | Emphasis |
|---|---|
| V01 Warmup | Survival; coins do not affect passing |
| V02 Harvest | Finishing alone is insufficient; meet the coin target |
| V03 Temptation | Useful coins mixed with unsafe distractions |
| V04 Approach | Coins shortly before pipe crossings |
| V05 Exit | Coins shortly after pipe crossings |
| V06 Sparse | Long stretches without a visible coin |
| V07 Finale | A longer course mixing rewards and unsafe distractions |

There are 7 visible + 14 hidden cases. Hidden results reveal only pass/fail;
the final average includes their partial scores. `grade` exits with code 1
when any case fails; that is an ordinary grading result.

All packaged cases and generated stress cases have a verified action sequence
that finishes AND meets the coin target. This proves feasibility, not that
every decision history can recover or that any one strategy always works.

