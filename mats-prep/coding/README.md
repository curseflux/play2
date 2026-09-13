# Cargo Lander — practice kit

A stand-in for the MATS AI-Assisted Advanced Coding Assessment: a per-frame
control policy for a simple physics simulation, continuously scored, with visible
and hidden scenario sets.

## Files

| file | what |
|---|---|
| `00-how-to-prepare.md` | How to prepare and how to spend the 60 minutes |
| `01-worked-example.md` | Narrated build of a solution, with measured numbers at each step |
| `02-why-dp-scored-badly.md` | Why a correct DP implementation produces a bad score |
| `lander.py` | Simulator, scoring, and the three scenario sets |
| `policies.py` | Eight policies, in the order you'd write them, including the ones that lost |
| `evaluate.py` | Scoreboard across visible / validation / hidden |
| `tune.py` | Random search over controller constants |
| `visualise.py` | Writes a self-contained `replay.html` you can scrub frame by frame |

## Use it as a drill

```bash
# 1. See the shape of the problem, then DON'T read policies.py yet.
python3 -c "import lander; [print(s) for s in lander.visible_scenarios()]"

# 2. Set a 60-minute timer. Write your own policy in a new file:
#      def my_policy(s) -> str   # returns "none" | "up" | "left" | "right"
#    Score it against the visible set only -- that is all you'd have in the real test.

# 3. Then check yourself honestly against the held-out set:
python3 evaluate.py

# 4. Watch where it goes wrong:
python3 visualise.py final_policy hidden   # -> replay.html
```

The interesting comparison is your visible score against your hidden score. If the
gap is large, the thing to fix is your process, not your controller.

## The measured scoreboard

```
policy                      VISIBLE             VALIDATION              HIDDEN    us/frame
                  mean   land    min    mean  land   min    mean  land    min
v0_baseline       32.9    33%    9.0     6.6    2%   0.0    16.4   10%    1.5        1
v1_pd             34.5    33%    6.9    24.3   23%   0.2    31.1   30%    0.5        1
v2_braking        86.6   100%   83.8    28.0   23%   0.3    41.7   38%    4.7        2
v2b_gated         90.5   100%   88.8    72.4   87%   0.0    84.5  100%   74.2        2
v3_mpc            89.0   100%   87.5    68.4   84%   0.0    79.9   95%   13.9      196
dp_openloop       62.0    67%   13.6     3.6    0%   0.0     7.5    0%    0.6       47
dp_closedloop     84.6   100%   81.6    68.6   87%   0.0    79.8  100%   70.8        3
v4_adaptive       83.8   100%   78.4    70.9   88%   0.0    81.9  100%   68.8        3
final_policy      91.0   100%   89.2    74.2   88%   0.0    85.1  100%   75.8        2
```

Two rows carry the whole lesson. `v2_braking` scores 86.6 visible and 41.7 hidden:
optimising against the visible tests is a trap with a 45-point price. And
`dp_openloop` (7.5) against `dp_closedloop` (79.8) is the *same DP table*, the only
difference being whether it's consulted with the current state or replayed by frame
index.
