"""Beam search with named states and sets of collected coin IDs."""
import math

HORIZON = 40
BEAM_WIDTH = 32
COIN_REWARD = 1000


def collection_windows(coins, future_x, bird_width, bird_height):
    """Find the bird heights that would touch each coin at this future x."""
    windows = []
    for coin in coins:
        # Horizontal distance from the coin center to the bird's rectangle.
        nearest_x = max(future_x, min(coin['x'], future_x + bird_width))
        horizontal_distance = abs(coin['x'] - nearest_x)
        if horizontal_distance > coin['radius']:
            continue

        # Circle geometry gives the remaining vertical reach at this x.
        vertical_reach = math.sqrt(max(
            0, coin['radius'] ** 2 - horizontal_distance ** 2))
        windows.append({
            'coin_id': coin['id'],
            'minimum_y': coin['y'] - vertical_reach - bird_height,
            'maximum_y': coin['y'] + vertical_reach,
        })
    return windows


def should_bounce(params):
    bird = params['cosmo']
    gravity = bird['gravity']
    bounce_velocity = bird['bouncePower']
    speed = params['scrollSpeed']
    maximum_y = params['canvasHeight'] - params['groundHeight'] - bird['height']
    coins_needed = max(0, params['coinTarget'] - params['coinsCollected'])
    frames_to_finish = max(1, math.ceil((params['finishX'] - bird['x']) / speed))
    horizon = min(HORIZON, params['framesLeft'], frames_to_finish)

    # Ignore optional coins wholly inside the ground.
    coins = [coin for coin in params['coins']
             if coin['y'] - coin['radius'] <= maximum_y + bird['height']]

    # All paths share the same x at each depth. Calculate pickup geometry once.
    windows_by_step = []
    for step in range(1, horizon + 1):
        future_x = bird['x'] + speed * step
        windows_by_step.append(collection_windows(
            coins, future_x, bird['width'], bird['height']))

    def score_state(state, future_x):
        useful_coins = min(coins_needed, len(state['collected_coin_ids']))
        target_y = maximum_y / 2
        prediction_frames = 4.0

        if useful_coins < coins_needed:
            for coin in coins:
                already_collected = coin['id'] in state['collected_coin_ids']
                already_passed = future_x > coin['x'] + coin['radius']
                if already_collected or already_passed:
                    continue
                target_y = max(0, min(maximum_y, coin['y'] - bird['height'] / 2))
                frames_to_coin = (coin['x'] - future_x - bird['width'] / 2) / speed
                prediction_frames = min(6.0, max(0, frames_to_coin))
                break

        # Estimate where momentum will carry the bird if it glides briefly.
        predicted_y = (state['y'] + state['velocity'] * prediction_frames
                       + gravity * prediction_frames * (prediction_frames + 1) / 2)
        return COIN_REWARD * useful_coins - abs(predicted_y - target_y)

    beam = [{
        'y': bird['y'],
        'velocity': bird['velocity'],
        # A frozenset is a set that cannot be modified accidentally by a branch.
        'collected_coin_ids': frozenset(),
        'first_action': False,
    }]
    chosen_action = False

    for depth in range(horizon):
        candidates = {}
        future_x = bird['x'] + speed * (depth + 1)
        finished = (future_x >= params['finishX']
                    or depth + 1 >= params['framesLeft'])

        for state in beam:
            # Movement happens BEFORE the chosen bounce takes effect.
            velocity_after_movement = state['velocity'] + gravity
            next_y = state['y'] + velocity_after_movement
            if next_y > maximum_y:
                continue  # Ground collision: discard this path.
            if next_y < 0:
                next_y = 0.0
                velocity_after_movement = 0.0

            # Copy this path's coin set so sibling paths stay independent.
            collected_ids = set(state['collected_coin_ids'])
            for window in windows_by_step[depth]:
                if window['minimum_y'] <= next_y <= window['maximum_y']:
                    collected_ids.add(window['coin_id'])
            collected_ids = frozenset(collected_ids)

            for action in (False, True):
                next_velocity = velocity_after_movement
                if action and not finished:
                    next_velocity = bounce_velocity
                next_state = {
                    'y': next_y,
                    'velocity': next_velocity,
                    'collected_coin_ids': collected_ids,
                    'first_action': action if depth == 0 else state['first_action'],
                }
                next_state['score'] = score_state(next_state, future_x)

                # Merge similar states, keeping the better actual state.
                key = (round(next_y / 2), round(next_velocity),
                       collected_ids, next_state['first_action'])
                existing = candidates.get(key)
                if existing is None or next_state['score'] > existing['score']:
                    candidates[key] = next_state

        if not candidates:
            break  # Keep the choice from the deepest surviving layer.
        beam = sorted(candidates.values(),
                      key=lambda state: state['score'], reverse=True)[:BEAM_WIDTH]
        chosen_action = beam[0]['first_action']

    return {'shouldBounce': chosen_action,
            'log': f'lookahead={horizon}, need={coins_needed}'}
