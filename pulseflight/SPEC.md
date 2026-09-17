# Public specification

## Coordinates and body

The origin is the upper-left. `x` increases rightward; `y` increases DOWNWARD.
Positive `vy` means falling. Distances are pixels, time is seconds, velocity
is pixels/second, and acceleration is pixels/second squared.

The bird is a circle with radius `physics.radius`. It moves right at the
constant `physics.speed` for that episode. You cannot control horizontal speed.
The vertical screen boundaries are `y=0` and `y=course.height`.

## Actions

Return exactly one of the strings `"glide"` or `"pulse"`. Booleans are illegal.

- `glide`: no kick this frame.
- `pulse`: if the current cooldown is zero, subtract `impulse` from `vy` and
  set cooldown to `recharge`. If cooldown is positive, the pulse is ignored.

The pulse ADDS an upward change in velocity; it does not reset velocity to a
fixed value. There is no stamina or fuel. Repeated pulses are limited by the
cooldown and speed caps.

## Telemetry

Every call receives a fresh dictionary with these nested sections:

| Section | Fields |
|---|---|
| `clock` | `tick`: elapsed frames; `limit`: maximum episode frames; `dt`: seconds per frame |
| `bird` | `x`, `y`, `vy`, `cooldown`: number of frames until a kick can be accepted |
| `course` | `height`, `cleared`: gates fully behind the bird; `total`: all gates in the course |
| `physics` | `dt`, `gravity`, `drag`, `impulse`, `recharge`, `rise_cap`, `fall_cap`, `speed`, `radius` |
| `gates` | Up to the next three uncleared gates, sorted from left to right |

All physics values are constant within an episode and may differ between
episodes. `drag` is a linear damping coefficient in inverse seconds. The caps
are positive speed magnitudes; velocity is bounded by `[-rise_cap, fall_cap]`.
`recharge` and `cooldown` are integer frame counts, not seconds.

Each gate dictionary contains:

| Field | Meaning |
|---|---|
| `id` | Zero-based index in the full course |
| `x`, `half_width` | Horizontal center and half-width |
| `centre` | Mean vertical center of its opening |
| `gap` | Full opening height |
| `amplitude` | Vertical oscillation amplitude, possibly zero |
| `period` | Oscillation period in FRAMES |
| `phase` | Phase in radians |
| `top`, `bottom` | Opening edges at the CURRENT tick |

At absolute tick `k`, its opening center is:

```python
centre + amplitude * sin(2 * pi * k / period + phase)
```

Its top and bottom are that value minus/plus `gap/2`. Obstacles beyond sight
are unavailable. Clearing all currently visible gates does not necessarily
finish the course; check the total and cleared counts.

## Exact frame update

The public `Arena.step()` performs these operations, in this order:

1. If action is `pulse` and cooldown is zero, subtract impulse from `vy` and
   set cooldown to recharge.
2. Update velocity: `vy += (gravity - drag * vy) * dt`.
   This uses the velocity AFTER the kick.
3. Clamp velocity into `[-rise_cap, fall_cap]`.
4. Update `y += vy * dt` using the NEW velocity.
5. Update `x += speed * dt`.
6. Increment tick by one.
7. Decrement cooldown by one, clamped at zero.
8. Evaluate shutters at the NEW absolute tick and check collisions.
9. Count fully cleared gates.
10. If alive and every gate is cleared, finish successfully. Otherwise, if
    tick has reached the limit, finish with a timeout.

For example, recharge=4 accepts kicks on ticks 0, 4, 8, ... if pulses are
requested every frame. After the kick on tick 0, the next observation has
tick=1 and cooldown=3.

## Collision rules

Touching the floor or ceiling is a collision: `y-radius <= 0` or
`y+radius >= course.height`.

Each gate consists of two solid rectangles:

- `[x-half_width, x+half_width] × [0, top]`
- `[x-half_width, x+half_width] × [bottom, course.height]`

For each rectangle, clamp the bird's center to the rectangle to get the
nearest point. If the squared distance to that point is at most `radius**2`,
the bird collides. Exact tangency counts as contact. Corners use CIRCULAR
geometry, not a square bounding box. `circle_hits_rect()` implements this.

Collisions are checked at the discrete end-of-frame positions; there is no
continuous swept collision test. A gate is cleared only when its right edge
is strictly left of `bird.x - radius`.

## Scoring and execution

- Pass: finish the entire course alive.
- Score: `100 * cleared / total`, including on collision or timeout.
- Exception or illegal action: score zero and fail that episode.
- Pulses and elapsed time do not directly affect the score.
- Collision takes priority over successful completion on the same frame.
- No policy calls occur after termination.
- All cases in a grading run share one imported policy module. Tick zero is
  the new-episode signal. Keep state between calls only if you reset it.

`DEBUG` is an optional module-level dictionary. Replay frames associate its
contents and the chosen action with the state BEFORE applying that action.
The final frame has no action. Clear DEBUG every call to avoid stale values.
