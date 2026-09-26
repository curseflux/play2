# Cosmo Coins: a 60-minute practice problem

Fly to the finish and collect enough coins. There are **no pipes** and
**no hidden cases**. Implement `should_bounce(params)` in `solution.py`.
Return `{'shouldBounce': True or False, 'log': optional_text}`.

The movement rules match the important parts of cosmo_review: y points down,
position is the bird's top-left corner, ceiling contact clamps, and the selected
bounce is applied AFTER this frame's movement. Coins use circle-versus-rectangle
overlap. Read RULES.md and engine.py for the exact order and observations.

## Try it

From this folder in PowerShell:

```powershell
.\practice.cmd list
.\practice.cmd test
.\practice.cmd test --case K03
.\practice.cmd replay K03
.\practice.cmd stress --count 20 --seed 1
```

Use `python assess.py` elsewhere. Only Python 3.10+ and the standard library
are needed. Use `--policy saved.py` to compare saved policies. `test --all`
is an alias for `test`; both run every public case. Replays are self-contained
HTML files in `replays/`, with playback, scrubbing, state, actions and your log.
The module is reused across cases; reset any persistent state at frame zero.

Set a 60-minute timer before reading the rules. Keep the final 10 minutes for
testing and inspecting failures. The suggested decision budget is 40 ms,
reported but not enforced. Exit code 1 means at least one tested case failed.

## Public cases

Each family has two cases. All 18 maps, including their initial states,
geometry, quotas and physics, are in `cases.json`.

| Cases | Challenge |
|---|---|
| K01, K10 | Flight warmup; quota zero |
| K02, K11 | Coins arranged around a horizontal row |
| K03, K12 | Changing coin heights |
| K04, K13 | Coin clusters: each distinct coin counts once |
| K05, K14 | Widely separated alternatives at the same x |
| K06, K15 | Reachable low coins plus optional coins inside the ground |
| K07, K16 | Coins near the ceiling |
| K08, K17 | Faster scrolling and shorter collection windows |
| K09, K18 | A longer route and larger quota |

The observation exposes **all available coins**, so future target choices are
possible. You are not required to collect every coin. Meeting the quota and
surviving to the finish is the goal; additional coins do not increase score.
There is no required algorithm. Build the simplest policy that performs well.

All packaged and generated courses have successful collection routes verified
against engine.py. The `_author` folder stores construction code and witnesses;
keep it off limits to yourself and the assistant during the timed attempt.
Edit only your policy and policy helpers, not the engine, grader or cases.
