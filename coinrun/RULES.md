# Public rules

## Flight and actions

Coordinates increase to the right and UP. Positive `vy` means rising. Lengths
use simulation units, velocities use units/second, and `dt` is seconds/frame.

The dog has a square collision body, centered on `(x, y)`, with half-size
`radius`. The screen runs vertically from 0 to `ceiling`. Horizontal movement
is fixed at `scroll_speed`. There is no resource, cooldown, or action delay.

`act(obs)` must return an actual Python bool. `True` sets vertical velocity to
`bounce_velocity`; it does NOT add to the current velocity. `False` applies
no bounce. Bouncing again while rising resets velocity again and can drive
the dog into a pipe or ceiling.

The exact update in `World.step()` is:

1. If action is True, set `vy = bounce_velocity`.
2. `vy = max(vy - gravity * dt, -max_fall_speed)`.
3. `y += vy * dt`, using NEW velocity.
4. `x += scroll_speed * dt`.
5. Increment frame.
6. Check floor, ceiling, then pipe collisions.
7. If alive, collect overlapping available coins.
8. Mark coins that have been passed as missed; count cleared pipes.
9. If alive and `x >= finish_x`, terminate and check the coin target.
10. Otherwise, if alive and the frame limit is reached, terminate with timeout.

## Observation

`obs` is a fresh, flat dictionary:

| Fields | Meaning |
|---|---|
| `x`, `y`, `vy` | Current position and vertical velocity |
| `frame`, `frames_left`, `dt` | Elapsed frames, remaining frames, seconds per step |
| `gravity`, `bounce_velocity`, `max_fall_speed`, `scroll_speed`, `radius`, `ceiling` | Physics parameters; constant within an episode |
| `finish_x` | Horizontal finish coordinate |
| `coins_collected`, `coin_target` | Current collection count and required count |
| `pipes_cleared`, `pipes_total` | Progress through obstacles |
| `pipes` | At most the next two uncleared pipes, ordered by x |
| `coin` | One coin dictionary, or None |
| `coin_lookahead` | Maximum forward distance at which the nearest coin is exposed |

Each pipe has `id`, `x`, `half_width`, `gap_lo`, `gap_hi`. Its geometry is fixed.
Each visible coin has `id`, `x`, `y`, `radius`. Its position is fixed.
IDs are unique within an episode, not across episodes.

The coin list is deliberately unavailable. Only the nearest still-available
coin is exposed, and only when `coin.x - x <= coin_lookahead`. A coin remains
available until collected or completely passed. A later coin is never exposed
before the nearer one disappears. None means no coin currently visible, not
necessarily that the course contains no more coins.

## Collisions and collection

Ground or ceiling contact is fatal:

```python
y - radius <= 0 or y + radius >= ceiling
```

A pipe overlaps horizontally when:

```python
x + radius > pipe['x'] - pipe['half_width'] and \
x - radius < pipe['x'] + pipe['half_width']
```

While overlapping, the dog's full body must fit in the opening:

```python
y - radius >= pipe['gap_lo'] and y + radius <= pipe['gap_hi']
```

Touching a gap edge exactly is permitted. Touching a screen boundary is not.
All checks use the discrete end-of-frame position, not a swept trajectory.

A coin is collected if the dog is alive and:

```python
(x - coin['x'])**2 + (y - coin['y'])**2 <= (radius + coin['radius'])**2
```

This center-distance pickup rule is intentional even though the pipe collision
body is square. Each coin can be collected only once. Collection is checked
against all remaining coins in the world; visibility restricts information,
not physical pickup. A missed coin disappears once:

```python
x - radius > coin['x'] + coin['radius']
```

The next observation reflects collection or disappearance. Collection on a
frame that also collides is not awarded. A pipe is cleared when its right edge
is strictly behind the dog's left edge.

## Passing and scoring

**Pass:** reach `finish_x` alive with `coins_collected >= coin_target`.
Extra coins are unnecessary for passing.

For coin-target cases, partial score is:

```python
50 * min(x / finish_x, 1) + 50 * min(coins_collected / coin_target, 1)
```

For the zero-target warmup, score is `100 * min(x / finish_x, 1)`.
Pass/fail still requires reaching the finish alive. Score alone is not a pass.
Exceptions and illegal return types fail the case with score zero.

The grader reuses one imported policy module across episodes. Frame zero
signals a new episode. The policy is never called after termination.
`DEBUG` is optional and captured after `act()` returns, alongside the state
before applying its action.
