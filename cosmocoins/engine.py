"""Cosmo Coins: one simulation loop, like cosmo_review."""
from solution import should_bounce


def touches_coin(cosmo, coin):
    nearest_x = max(cosmo['x'], min(coin['x'], cosmo['x'] + cosmo['width']))
    nearest_y = max(cosmo['y'], min(coin['y'], cosmo['y'] + cosmo['height']))
    return ((coin['x'] - nearest_x) ** 2 + (coin['y'] - nearest_y) ** 2
            <= coin['radius'] ** 2)


def simulate_game(params):
    cosmo = params['cosmo']
    coins = [dict(id=i, **coin) for i, coin in enumerate(params['coins'])]
    coin_states = ['available'] * len(coins)
    bounce_plan, logs = [], []
    collected = 0
    game_over = mission_complete = False

    # Output fields used by the grader to display the final state.
    params.update(coinStates=coin_states, coinsCollected=0,
                  framesElapsed=0, reason='flying')

    for frame in range(params['maxFrames']):
        available = [dict(coin) for i, coin in enumerate(coins)
                     if coin_states[i] == 'available']
        answer = should_bounce({
            'cosmo': cosmo.copy(),
            'coins': available,
            'currentCoin': available[0] if available else None,
            'coinsCollected': collected,
            'coinTarget': params['coinTarget'],
            'coinsTotal': len(coins),
            'scrollSpeed': params['scrollSpeed'],
            'frameTime': params['frameTime'],
            'frameNumber': frame,
            'framesLeft': params['maxFrames'] - frame,
            'canvasHeight': params['canvasHeight'],
            'canvasWidth': params['canvasWidth'],
            'groundHeight': params['groundHeight'],
            'finishX': params['finishX'],
            'mapName': params['mapName'],
        })
        if not isinstance(answer, dict) or type(answer.get('shouldBounce')) is not bool:
            raise ValueError('return a dict containing bool shouldBounce')
        bounce = answer['shouldBounce']

        cosmo['velocity'] += cosmo['gravity']
        cosmo['y'] += cosmo['velocity']
        params['framesElapsed'] = frame + 1
        if cosmo['y'] + cosmo['height'] > params['canvasHeight'] - params['groundHeight']:
            game_over = True
            params['reason'] = 'ground collision'
            break
        if cosmo['y'] < 0:
            cosmo['y'], cosmo['velocity'] = 0.0, 0.0
        cosmo['x'] += params['scrollSpeed']

        for i, coin in enumerate(coins):
            if coin_states[i] != 'available':
                continue
            if touches_coin(cosmo, coin):
                coin_states[i] = 'collected'
                collected += 1
            elif cosmo['x'] > coin['x'] + coin['radius']:
                coin_states[i] = 'missed'
        params['coinsCollected'] = collected

        if cosmo['x'] >= params['finishX']:
            mission_complete = collected >= params['coinTarget']
            params['reason'] = 'complete' if mission_complete else 'finished below coin target'
            break
        if frame + 1 >= params['maxFrames']:
            params['reason'] = 'frame limit'
            break

        if bounce:
            cosmo['velocity'] = cosmo['bouncePower']
        bounce_plan.append(bounce)
        if 'log' in answer:
            logs.append({'frame': frame, 'msg': answer['log']})

    return bounce_plan, logs, game_over, mission_complete, collected
