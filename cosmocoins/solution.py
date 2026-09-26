"""Implement should_bounce(params). Read START.md and engine.py first."""

# def should_bounce(params):

#     return {'shouldBounce': False, 'log': ''}

import math

HORIZON = 40
BEAM_WIDTH = 32


def should_bounce(params):
    bird = params['cosmo']
    x, y, velocity = bird['x'], bird['y'], bird['velocity']
    gravity, bounce = bird['gravity'], bird['bouncePower']
    width, height = bird['width'], bird['height']
    speed = params['scrollSpeed']
    max_y = params['canvasHeight'] - params['groundHeight'] - height
    coins_needed = max(0, params['coinTarget'] - params['coinsCollected'])
    horizon = min(HORIZON, params['framesLeft'],
                  max(1, math.ceil((params['finishX'] - x) / speed)))

    # Coins wholly inside the ground cannot be collected alive.
    coins = [c for c in params['coins']
             if c['y'] - c['radius'] <= max_y + height]

    # At each future x, turn circle/rectangle contact into a legal y interval.
    # This geometry is shared by every candidate flight at that depth.
    pickup_ranges = []
    for step in range(1, horizon + 1):
        future_x = x + speed * step
        intervals = []
        for coin in coins:
            horizontal_distance = max(future_x - coin['x'], coin['x'] - future_x - width, 0)
            if horizontal_distance <= coin['radius']:
                reach = math.sqrt(max(0, coin['radius'] ** 2 - horizontal_distance ** 2))
                intervals.append((coin['id'], coin['y'] - reach - height,
                                  coin['y'] + reach))
        pickup_ranges.append(intervals)

    def rank(y, velocity, collected, future_x):
        count = min(coins_needed, len(collected))
        target_y = max_y / 2
        lookahead = 4.0
        if count < coins_needed:
            for coin in coins:
                if coin['id'] not in collected and future_x <= coin['x'] + coin['radius']:
                    target_y = max(0, min(max_y, coin['y'] - height / 2))
                    lookahead = min(6.0, max(0, (coin['x'] - future_x - width / 2) / speed))
                    break
        predicted_y = y + velocity * lookahead + gravity * lookahead * (lookahead + 1) / 2
        return 1000 * count - abs(predicted_y - target_y)

    # Each path stores y, velocity, collected coin IDs, and its FIRST action.
    # frozenset is a set that cannot be changed, so paths can safely share it.
    beam = [(y, velocity, frozenset(), False)]
    chosen = False
    for depth in range(horizon):
        candidates = {}
        future_x = x + speed * (depth + 1)
        terminal = future_x >= params['finishX'] or depth + 1 >= params['framesLeft']
        for old_y, old_velocity, collected, first_action in beam:
            velocity = old_velocity + gravity
            new_y = old_y + velocity
            if new_y > max_y:
                continue
            if new_y < 0:
                new_y, velocity = 0.0, 0.0
            new_collected = set(collected)  # Copy before adding pickups to this path.
            for coin_id, lowest_y, highest_y in pickup_ranges[depth]:
                if lowest_y <= new_y <= highest_y:
                    new_collected.add(coin_id)
            new_collected = frozenset(new_collected)
            for action in (False, True):
                new_velocity = bounce if action and not terminal else velocity
                starting_action = action if depth == 0 else first_action
                path = (new_y, new_velocity, new_collected, starting_action)
                score = rank(new_y, new_velocity, new_collected, future_x)
                # Merge nearly identical flights; keep the better actual state.
                key = (round(new_y / 2), round(new_velocity), new_collected, starting_action)
                if key not in candidates or score > candidates[key][0]:
                    candidates[key] = (score, path)
        if not candidates:
            break  # Use the best first action from the deepest surviving layer.
        ordered = sorted(candidates.values(), key=lambda item: item[0], reverse=True)
        beam = [path for _, path in ordered[:BEAM_WIDTH]]
        chosen = beam[0][3]

    return {'shouldBounce': chosen, 'log': f'lookahead={horizon}, need={coins_needed}'}
