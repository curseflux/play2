"""Small beam search: keep 32 promising flights, plan up to 40 frames ahead."""
import math


def should_bounce(params):
    bird = params['cosmo']
    x, y, velocity = bird['x'], bird['y'], bird['velocity']
    gravity, bounce = bird['gravity'], bird['bouncePower']
    width, height = bird['width'], bird['height']
    speed = params['scrollSpeed']
    floor = params['canvasHeight'] - params['groundHeight'] - height
    need = max(0, params['coinTarget'] - params['coinsCollected'])
    horizon = min(40, params['framesLeft'],
                  max(1, math.ceil((params['finishX'] - x) / speed)))

    # Coins wholly inside the ground cannot be collected alive.
    coins = [c for c in params['coins']
             if c['y'] - c['radius'] <= floor + height]

    # At each future x, turn circle/rectangle contact into a legal y interval.
    # This geometry is shared by every candidate flight at that depth.
    contacts = []
    for step in range(1, horizon + 1):
        future_x = x + speed * step
        intervals = []
        for i, coin in enumerate(coins):
            dx = max(future_x - coin['x'], coin['x'] - future_x - width, 0)
            if dx <= coin['radius']:
                reach = math.sqrt(max(0, coin['radius'] ** 2 - dx ** 2))
                intervals.append((1 << i, coin['y'] - reach - height,
                                  coin['y'] + reach))
        contacts.append(intervals)

    def rank(y, vy, mask, future_x):
        count = min(need, mask.bit_count())
        target_y = floor / 2
        lookahead = 4.0
        if count < need:
            for i, coin in enumerate(coins):
                if not mask & (1 << i) and future_x <= coin['x'] + coin['radius']:
                    target_y = max(0, min(floor, coin['y'] - height / 2))
                    lookahead = min(6.0, max(0, (coin['x'] - future_x - width / 2) / speed))
                    break
        predicted_y = y + vy * lookahead + gravity * lookahead * (lookahead + 1) / 2
        return 1000 * count - abs(predicted_y - target_y)

    # A node contains position, velocity, collected-coin bits and FIRST action.
    beam = [(y, velocity, 0, False)]
    chosen = False
    for depth in range(horizon):
        candidates = {}
        future_x = x + speed * (depth + 1)
        terminal = future_x >= params['finishX'] or depth + 1 >= params['framesLeft']
        for old_y, old_vy, mask, first in beam:
            vy = old_vy + gravity
            new_y = old_y + vy
            if new_y > floor:
                continue
            if new_y < 0:
                new_y, vy = 0.0, 0.0
            new_mask = mask
            for bit, lo, hi in contacts[depth]:
                if lo <= new_y <= hi:
                    new_mask |= bit
            for action in (False, True):
                new_vy = bounce if action and not terminal else vy
                first_action = action if depth == 0 else first
                node = (new_y, new_vy, new_mask, first_action)
                score = rank(new_y, new_vy, new_mask, future_x)
                # Merge nearly identical flights; keep the better actual state.
                key = (round(new_y / 2), round(new_vy), new_mask, first_action)
                if key not in candidates or score > candidates[key][0]:
                    candidates[key] = (score, node)
        if not candidates:
            break  # Use the best first action from the deepest surviving layer.
        ordered = sorted(candidates.values(), key=lambda item: item[0], reverse=True)
        beam = [node for _, node in ordered[:32]]
        chosen = beam[0][3]

    return {'shouldBounce': chosen, 'log': f'lookahead={horizon}, need={need}'}
