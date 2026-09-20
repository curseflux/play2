# Public rules

## Coordinates and observations

Positive x is right; positive y is UP. The bird is an axis-aligned square with
half-size `radius`. Time units are seconds; `dt` is seconds per frame.

`act(observation)` receives:

- `tick`, `seconds`, `frames_left`: frame count, `tick * dt`, and remaining steps.
- `x`, `y`, `vy`: bird position and vertical speed.
- `pending`: whether a flap is already queued to fire in the upcoming step.
- `collected`, `required`, `finish_x`: mission state.
- `physics`: `dt`, `gravity`, `flap_speed`, `fall_limit`, `speed`, `radius`, `height`.
- `gates`: up to three uncleared gates, ordered by x.
- `stars`: up to two available stars, ordered by x.

Each gate contains `id`, `x`, `half_width`, `center`, `gap`, `amplitude`,
`omega`, `phase`, `gap_lo`, and `gap_hi`. `center` is its mean vertical center;
`gap` is its full opening height. `omega` is radians per second and `phase`
is radians. The last two fields describe the opening at the CURRENT time.

Each star contains `id`, `x`, `y`, `radius`. Star positions are fixed. IDs are
unique within an episode, but repeat across episodes. Objects beyond visibility
are unknown, not nonexistent. Observations contain copies, not live references.

## Exact update order

1. If the OLD `pending` flag is True, set vertical velocity to `flap_speed`.
2. Set `pending` to the newly returned action. It will fire on the NEXT step.
3. Apply gravity: `vy = max(-fall_limit, vy - gravity * dt)`.
4. Move using NEW velocity: `y += vy * dt`; `x += speed * dt`.
5. Increment tick. Evaluate moving gates at `tick * dt`, the NEW time.
6. Check floor, ceiling, and gates.
7. If alive, collect overlapping stars. Mark completely passed stars missed.
8. If alive and `x >= finish_x`, finish and check the quota.
9. Otherwise end with timeout if the frame limit has been reached.

Example: start with pending=False. Returning True now does not flap during this
step; it schedules a flap for the next one. Returning False on that next step
does not cancel the scheduled flap; it simply leaves the subsequent step empty.
There is no stamina, cooldown, or release requirement. Each True queues one flap.
Flaps SET velocity; they do not add to it. Return an actual bool, not 0 or 1.

## Moving gates and collisions

At absolute time `t` seconds:

```python
gap_center = center + amplitude * math.sin(omega * t + phase)
gap_lo = gap_center - gap / 2
gap_hi = gap_center + gap / 2
```

`opening(gate, seconds)` in the simulator implements this formula. Static gates
have amplitude zero. All generated openings remain within the screen.

Floor/ceiling contact is fatal:

```python
y - radius <= 0 or y + radius >= height
```

Horizontal gate overlap is strict:

```python
x + radius > gate_x - half_width and x - radius < gate_x + half_width
```

While overlapping, the full body must fit inside the opening at the NEW time:

```python
y - radius >= gap_lo and y + radius <= gap_hi
```

Touching an opening edge exactly is permitted. All collisions are discrete
end-of-frame checks; there is no swept-path check between frames.

## Stars

An alive bird collects a star when center distance is at most the sum of radii:

```python
(x - star_x)**2 + (y - star_y)**2 <= (radius + star_radius)**2
```

The circle-distance collection rule is intentional despite the square body.
Each star counts once and disappears from subsequent observations. The engine
checks all available stars, even ones outside the observation. A star is missed
when `x - radius > star_x + star_radius`. Collision takes priority over collection.

## Scoring and limits

Pass by reaching the finish alive with `collected >= required`.
For a positive quota, score is:

```python
50 * min(x / finish_x, 1) + 50 * min(collected / required, 1)
```

For quota zero, score is `100 * min(x / finish_x, 1)`. Extra stars bring no extra
score. Exceptions and invalid actions receive zero. A high score need not pass.

The same imported policy module is reused between episodes. Tick zero denotes
a new episode. The grader never calls the policy after termination. `DEBUG` is
an optional dictionary, recorded after the policy returns alongside the state
before its action. Decision time is measured around the policy call, excluding
replay output and environment updates.
