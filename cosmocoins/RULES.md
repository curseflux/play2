# Public rules

## Observation and actions

`should_bounce(params)` returns a dictionary with a Python bool `shouldBounce`.
An optional string `log` is captured for replays. Integers 0/1 are invalid.

Fields in `params`:

- `cosmo`: x, y, velocity, gravity, bouncePower, width, height.
- `coins`: every currently available coin, ordered by x; each has id, x, y, radius.
- `currentCoin`: the first coin in that list, or None. It is a convenience field,
  not a recommended target. It can be an optional unreachable coin.
- `coinsCollected`, `coinTarget`, `coinsTotal`: count, required count, total count.
- `scrollSpeed`: horizontal units per frame.
- `frameTime`: milliseconds per frame, used for replay playback ONLY.
- `frameNumber`, `framesLeft`: elapsed and remaining steps.
- `canvasHeight`, `canvasWidth`, `groundHeight`: screen geometry.
- `finishX`, `mapName`: finish coordinate and course ID.

Positive y points DOWN; positive velocity is falling. The bird's x/y are its
TOP-LEFT corner. Its body is an axis-aligned rectangle. Bounce power is negative
and SETS velocity rather than adding an impulse. Physics values are per frame:
do not multiply by frameTime or a dt. There is no stamina, cooldown or terminal
fall speed. Coins do not change physics. IDs are unique within an episode.

## Exact update order

1. `velocity += gravity`.
2. `y += velocity`; increment frame.
3. If `y + height > canvasHeight - groundHeight`, die immediately. No horizontal
   movement, collection, or bounce occurs on that fatal frame.
4. If `y < 0`, clamp y and velocity to zero. Ceiling contact is not fatal.
5. `x += scrollSpeed`.
6. Collect ALL available overlapping coins and remove them from later observations.
7. Mark a remaining coin missed if its rightmost edge is behind the bird's left
   edge: `x > coin.x + coin.radius`. Equality is not yet missed.
8. If `x >= finishX`, terminate and check the quota. If it is not reached, fail.
9. Otherwise, terminate with timeout when the frame limit is reached.
10. Only if the flight is still unfinished, apply the chosen action:
    if shouldBounce is True, set `velocity = bouncePower`.

Returning True cannot prevent a collision or change a coin pickup on the current
frame: it changes movement beginning on the NEXT frame. Holding True applies a
bounce each safe unfinished frame. The engine never calls your policy after
termination. Exact ground contact is permitted; going below it is fatal.

## Coin overlap

A coin is a circle; the bird is a rectangle. Clamp the coin's center to the
rectangle to find its nearest point, then compare distance with coin radius:

```python
nearest_x = max(x, min(coin_x, x + width))
nearest_y = max(y, min(coin_y, y + height))
touches = (coin_x - nearest_x)**2 + (coin_y - nearest_y)**2 <= coin_radius**2
```

Touching counts. A coin whose center is inside the bird counts. Distinct
overlapping coins can all be collected on one frame, but each ID counts once.
`touches_coin(cosmo, coin)` in engine.py implements the rule. Some optional coins
are inside the ground and cannot be collected alive. All remaining coins are
observed; the engine has no hidden future coin list.

## Pass and score

Pass by reaching finishX alive with `coinsCollected >= coinTarget`. Missing
coins is allowed. Collecting the quota early does not end the flight.

Distance progress is `(x - initial_x) / (finishX - initial_x)`, capped at 1.
For a positive quota, partial score is:

```python
50 * distance_progress + 50 * min(collected / target, 1)
```

For a zero quota, score is 100 times distance progress. No credit beyond the
quota. Exceptions and invalid actions give score zero. A high score is not
necessarily a pass. Collection on the finish frame counts; collection on a
fatal ground frame does not.
