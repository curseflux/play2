# Dog: the harder course set

The default grader now has **9 visible and 16 hidden cases**. D1 is the old
warmup; every other case is new and requires clearing the entire course.
The physics and `policy(obs) -> bool` contract are unchanged.

| Visible case | What it tests |
|---|---|
| D1_warmup | Basic flight and pipe tracking |
| D2_apex | Gaps with less vertical clearance than one bounce's first step; bounce before entry and coast through near the apex |
| D3_stamina_climb | A large climb after a low gate; space bounces to gain height without consuming the reserve too early |
| D4_early_descent | Large downward transitions; start falling before reaching the next pipe |
| D5_slalom | Closely spaced rising gates followed by drops; prepare for subsequent gates while crossing the current one |
| D6_long_tunnel | Several frames of overlap and a low ceiling; stay safe through the trailing edge |
| D7_endurance | 28 narrow gates with just one stamina slot and slow regeneration |
| D8_rising_start | Nonzero upward starting velocity; an immediate bounce can spoil the approach |
| D9_falling_start | Nonzero downward starting velocity; recovery timing matters |

The dog must fit entirely within the opening on the **first overlapping
frame**, and stay there until its trailing edge clears. Its legal centre
height is `[gap_lo + dog_radius, gap_hi - dog_radius]`. It can approach from
below before horizontal overlap begins, but being below the opening at entry
is a collision. Narrow gaps reward arranging the trajectory in advance.

Hidden variants change timestep, gravity, impulse, speed, body size, starting
height, and crossing timing. `sight=4` exposes upcoming gates for planning.
Stress tests cycle through all eight challenge families with new seeded
variants; their results are not comparable to the old broad-gap generator.

```bash
python grade.py dog --visible-only
python grade.py dog
python watch.py dog D2_apex
python watch.py dog D3_stamina_climb
python tools/stress.py dog --n 200 --seed 1
```

## Difficulty calibration

Measured on this revised suite and 200 stress cases with seed 1:

| Policy | Graded | Stress |
|---|---:|---:|
| Bounce below gap centre minus gap height / 4.5 | 1/25 | 0/200 |
| Always bounce | 0/25 | 0/200 |
| Existing short-rollout reference | 13/25 | 100/200 |

The existing reference remains an example, not a complete solution to this
harder suite. Scores in older notes describe the original courses.

## Why these courses are solvable

The authoring generator first simulates a legal sequence of bounces, then
places each opening around the full crossing trajectory with positive
clearance. It uses the actual `DogEnv` engine, including stamina regeneration
and collision geometry. The resulting scenario exposes ordinary pipes and
physics only; the action sequence is never included in observations.

`python tools/validate_dog.py` replays those construction witnesses against
all 24 hard graded cases and 800 generated variants. It also checks that an
inside bounce is fatal in a narrow opening, and that an unnecessary early
bounce exhausts a reserve needed for the climb. Witness replay proves a
feasible path exists; it is not an observation-based solver or a claim that
every possible action history can recover.

Avoid reading the generator and validation witnesses if you want to preserve
the challenge of solving the policies yourself.
