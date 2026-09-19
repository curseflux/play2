# Public rules

## Coordinates and controls

Screen coordinates: x increases RIGHT, y increases DOWN. Positive vy means
falling. Lengths use simulation units, velocities use units/second, and dt is
seconds/frame. The bird is a square with half-size `radius`. Horizontal speed
is constant within each course.

Return the string `"press"` or `"release"`. A flap occurs only when `press` is
chosen while `bird.held` was False. It sets `vy = -flap_speed`. Choosing press
again while held produces NO new flap. Release sets held to False and produces
no flap. There is no stamina, fuel, or additional cooldown.

The current held state is in the observation; you do not need module globals
to remember it. A course may begin with held=True.

## Observation contract

`choose(view)` receives a fresh nested dictionary:

| Field | Meaning |
|---|---|
| `tick`, `frames_left` | Elapsed and remaining frame counts |
| `bird` | `x`, `y`, `vy`, `held` (bool), `carrying` (bool) |
| `mission` | `delivered`, `required`, `finish_x` |
| `physics` | `dt`, `gravity_empty`, `gravity_loaded`, `flap_speed`, `fall_limit`, `speed`, `radius`, `height` |
| `gates` | Up to two uncleared gates, ordered by x |
| `stations` | Up to two unpassed stations, ordered by x |

Physics values are fixed within an episode and vary between episodes.
Gate dictionaries contain `id`, `x`, `half_width`, `top`, `bottom`.
The opening extends from top to bottom; positions never move.

Station dictionaries contain `id`, `x`, `kind`, `top`, `bottom`. Kind is
`"pickup"` or `"depot"`. A station is a vertical crossing line with an active
window from top to bottom. Stations do not physically block the bird.

IDs are unique within each list for an episode, not globally across episodes.
Future stations and gates beyond the visible lists are unknown. Exhausting
either visible list does not imply the course has finished.

## Exact update order

1. If action is press and held is False, set vy to `-flap_speed`.
2. Set held according to the action: press=True, release=False.
3. Choose gravity from the cargo state at the START of the frame.
4. `vy = min(fall_limit, vy + gravity * dt)`.
5. Update y using the NEW vy, then x using speed: `y += vy*dt`, `x += speed*dt`.
6. Increment tick.
7. Check screen and gate collisions.
8. Process station lines crossed this frame, in horizontal order. A fatal
   frame cannot pick up or deliver anything.
9. If alive and x has reached finish_x, end and check the delivery target.
10. Otherwise, if alive and the frame limit is reached, end with a timeout.

Picking up or dropping cargo changes gravity beginning with the NEXT frame.
It does not directly change velocity. Carrying a parcel increases gravity.

## Collisions

Screen boundary contact is fatal: `y-radius <= 0` or `y+radius >= height`.
A gate overlaps horizontally when:

```python
x + radius > gate['x'] - gate['half_width'] and \
x - radius < gate['x'] + gate['half_width']
```

While overlapping, the body must fit entirely inside the opening:

```python
y - radius >= gate['top'] and y + radius <= gate['bottom']
```

Exact opening-edge contact is allowed. Collisions use discrete end-of-frame
positions, not swept geometry. A gate is cleared once its right edge is
strictly behind the bird's left edge.

## Pickups and deliveries

A station is processed exactly once, when the center crosses its x coordinate:

```python
previous_x < station['x'] <= new_x
```

At that frame's NEW y, the whole body must fit inside its vertical window:

```python
new_y - radius >= station['top'] and new_y + radius <= station['bottom']
```

- At a pickup while empty: set carrying=True.
- At a depot while carrying: increment delivered and set carrying=False.
- At a pickup while carrying, or a depot while empty: nothing happens.
- Outside the window: nothing happens.

Every crossed station disappears from future observations, regardless of
whether it was used. Use carrying/delivered to determine what happened.
You carry at most one parcel. Any parcel can be delivered at any depot.
There is no penalty for missing a station. Some optional pickups are unsafe;
the delivery target never requires collecting those parcels.

## Passing and partial score

Pass requires reaching finish_x alive with `delivered >= required`.
Picking up a parcel alone earns no delivery credit. Additional deliveries
beyond the target earn no additional score.

For a positive delivery target, score is:

```python
40 * min(x / finish_x, 1) + 60 * min(delivered / required, 1)
```

The zero-target warmup uses `100 * min(x / finish_x, 1)`. A collision or timeout
keeps partial progress. An exception or illegal action scores zero. Score alone
does not establish a pass. Collision takes precedence over finish or delivery.

The grader reuses one imported module across episodes and never calls the
policy after termination. Tick zero is the new-episode signal. Replay DEBUG
values are captured after choose() returns and paired with its pre-action state.
