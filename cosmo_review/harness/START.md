# Cosmo challenge harness

This extends the three existing files one directory up: `engine.py`,
`solution.py`, and `solution_old.py`. It never edits them. The grader calls the
original `engine.simulate_game()` and swaps in the policy you select for each
run. These are practice maps, not reconstructed assessment maps.

From this folder in PowerShell:

```powershell
.\practice.cmd list
.\practice.cmd test
.\practice.cmd test --all
.\practice.cmd test --case C02
.\practice.cmd replay C02
.\practice.cmd test --all --policy old
.\practice.cmd stress --count 20 --seed 1
.\practice.cmd test --policy solution_practice.py
```

`current` means `../solution.py`; `old` means `../solution_old.py`. Both can be
compared with `--policy`. You may also pass a Python file path. The output
reports pipes passed, pass count, and slowest decision. A 40 ms per-decision
budget is advisory. Exceptions or malformed policy outputs fail the case.

`../solution_practice.py` is a separate worked candidate. Read
`../WALKTHROUGH.md` for the reasoning and measured tradeoffs.

`replay CASE` writes a self-contained HTML file in `replays/`. Open it in any
browser, press Play, or scrub through frames. It shows pipe geometry, the dog,
recent trajectory, selected action, state, and optional `log` text returned
by the policy. The last frame shows the actual terminal state from the engine.

## Cases

| Case | Main pressure |
|---|---|
| C01 | Two ordinary pipes for a baseline |
| C02 | Bouncing upon entering the first gap hits its top |
| C03 | Adjacent pipes with shifted openings |
| C04 | Narrow openings and little vertical margin |
| C05 | A sharper vertical reversal between close pipes |
| C06 | Two pipes so close the dog can overlap both |
| C07 | Safe route approaches the ceiling |
| C08 | Safe route approaches the ground |
| C09 | Five-pipe endurance run |

All **25 courses are visible**. The default test command runs all of them,
and every C or X case supports detailed results and replays. `--all` is an
alias for the default full suite. Stress creates fresh variants from the same families. Each packaged
course has a successful action witness checked against the supplied engine.
For C02, the generator also verifies that adding a bounce on the first
overlap frame makes the otherwise successful path collide shortly afterward.
The close-pipe families verify shifted gap centers and short spacing.

The `_author` folder contains construction code and witnesses. Keep it out
of view when using this as a timed mock. Use visible tests and replays for
debugging. Python 3.10+ and its standard library suffice.
