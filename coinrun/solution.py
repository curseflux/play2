"""Your submission: act(obs) -> bool. True bounces; False coasts.

Start with BRIEF.md. DEBUG values are optional and appear in the replay.
"""

DEBUG = {}

# # Passed 18/21 | mean score 94.6/100 | slowest decision 30.45 ms - h = 10 - with just state['y'] < midpoint
# # Passed 19/21 | mean score 95.8/100 | slowest decision 31.21 ms - h = 10 - with state['vy'] <= 0
# def heuristic(state, obs):
#     if not obs['pipes']:
#         if state['vy'] < -obs['bounce_velocity']:
#             return (True, False)
#         return (False, True)
    
#     pipe = obs['pipes'][0]
#     midpoint = (pipe['gap_lo'] + pipe['gap_hi']) / 2 - (pipe['gap_hi'] - pipe['gap_lo']) / 4
    
#     # if state['y'] < midpoint:
#     if state['y'] < midpoint and state['vy'] <= 0:
#         return (True, False)
#     return (False, True)


# Passed 20/21 | mean score 96.2/100 | slowest decision 36.04 ms - h = 10 - with just return (False, True)
# Passed 20/21 | mean score 96.2/100 | slowest decision 33.46 ms - h = 10 - with state['vy'] < -obs['bounce_velocity']
# Passed 21/21 | mean score 100.0/100 | slowest decision 399.96 ms - h = 15 - with just return (False, True)
# Passed 21/21 | mean score 100.0/100 | slowest decision 375.96 ms - h = 15 - with state['vy'] < -obs['bounce_velocity']
def heuristic(state, obs):
    # Prioritize coin collection if a coin is visible and close
    if obs['coin'] is not None:
        coin = obs['coin']
        if coin['y'] > state['y']:
            return (True, False)
        return (False, True)

    if not obs['pipes']:
        if state['vy'] < -obs['bounce_velocity']:
            return (True, False)
        return (False, True)
    
    pipe = obs['pipes'][0]
    midpoint = (pipe['gap_lo'] + pipe['gap_hi']) / 2
    
    # Account for downward momentum: bounce early if falling below midpoint
    if state['y'] < midpoint and state['vy'] <= 0:
        return (True, False)
    return (False, True)


def advance(state, obs, bounce=False):
    p = obs
    vy = state['vy']
    
    if bounce:
        vy = p['bounce_velocity']
    
    vy = max(vy - p['gravity'] * p['dt'], -p['max_fall_speed'])
    y = state['y'] + vy * p['dt']
    x = state['x'] + p['scroll_speed'] * p['dt']
    
    return {
        'x': x,
        'y': y,
        'vy': vy,
        'coin_taken': state['coin_taken'],
    }


def max_survival(state, obs, horizon):

    if horizon == 0:
        return (0, False)

    best = (0, False)

    for action in heuristic(state, obs):
        next_state = advance(state, obs, action)
        crash_coin = check_crash(next_state, obs)

        next_state['coin_taken'] = (state['coin_taken'] or crash_coin[1])

        if crash_coin[0]:
            continue
        
        next_max_survival = max_survival(next_state, obs, horizon-1)

        score = (1 + next_max_survival[0], crash_coin[1] or next_max_survival[1])

        if score[0] > best[0] or (score[0] == best[0] and score[1] and not best[1]):
            best = score

        if best[0] == horizon and best[1] == True:
            break

    return best

def check_crash(state, obs):
    r = obs['radius']
    crashed = False
    
    # Check ground or ceiling collision
    if state['y'] - r <= 0 or state['y'] + r >= obs['ceiling']:
        crashed = True
    else:
        # Check pipe collisions
        for pipe in obs['pipes']:
            overlaps = (state['x'] + r > pipe['x'] - pipe['half_width'] and 
                        state['x'] - r < pipe['x'] + pipe['half_width'])
            if overlaps and (state['y'] - r < pipe['gap_lo'] or state['y'] + r > pipe['gap_hi']):
                crashed = True
                break

    # Check coin collection
    coin = False
    if obs['coin'] is not None:
        c = obs['coin']
        reach = r + c['radius']
        if (state['x'] - c['x']) ** 2 + (state['y'] - c['y']) ** 2 <= reach ** 2:
            coin = True

    return (crashed, coin)

def act(obs):
    DEBUG.clear()

    state = {
        'x': obs['x'],
        'y': obs['y'],
        'vy': obs['vy'],
        'coin_taken': False,
    }

    order = heuristic(state, obs)

    horizon = 10
    # horizon = 15
    # horizon = 20

    best = (0, 0, True)

    for action in order:
        next_state = advance(state, obs, action)
        crash_coin = check_crash(next_state, obs)

        next_state['coin_taken'] = (state['coin_taken'] or crash_coin[1])

        if crash_coin[0]:
            continue
        
        next_max_survival = max_survival(next_state, obs, horizon-1)

        score = (1 + next_max_survival[0], crash_coin[1] or next_max_survival[1])

        if score[0] > best[0] or (score[0] == best[0] and score[1] and not best[1]):
            best = (score[0], score[1], action)
        
        if best[0] == horizon and best[1] == True:
            break


    return best[2]

    # {'dt': 0.1, 'gravity': 30.027805305481476, 'bounce_velocity': 19.017610026804935, 'max_fall_speed': 34.03151267954567, 'scroll_speed': 19.561116083397764, 'radius': 1.7724206004727514, 'ceiling': 67.93069063163688, 'frame': 0, 'x': 0.0, 'y': 35.85089214168107, 'vy': 0.0, 'frames_left': 246, 'finish_x': 470.9338697078012, 'coin_lookahead': 54.70641331323863, 'coins_collected': 0, 'coin_target': 0, 'pipes_cleared': 0, 'pipes_total': 6, 'pipes': [{'id': 0, 'x': 64.55168307521262, 'half_width': 3.919731506045534, 'gap_lo': 34.58727655461079, 'gap_hi': 59.53526902351086}, {'id': 1, 'x': 127.14725454208548, 'half_width': 4.230480381641585, 'gap_lo': 26.579861806482405, 'gap_hi': 55.631654333798274}], 'coin': {'id': 0, 'x': 43.03445538347506, 'y': 41.669427422421435, 'radius': 1.1510658700434564}}

