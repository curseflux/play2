"""Your entry point. Read START.md, then implement act(observation) -> bool."""

DEBUG = {}

import math

def heuristic(state, observation):
    x = observation['x']
    y = observation['y']
    gates = observation.get('gates', [])
    
    # Find the next closest gap not yet crossed by the bird[cite: 2]
    next_gate = None
    for gate in gates:
        if x <= gate['x'] + gate['half_width']:
            next_gate = gate
            break
            
    if next_gate is not None:
        gap_center = (next_gate['gap_lo'] + next_gate['gap_hi']) / 2
        # Since positive y is UP[cite: 2], being below the center means y < gap_center
        if y < gap_center:
            return (True, False)
            
    return (False, True)




def advance(state, action, observation):
    p = observation['physics']
    dt = p['dt']
    gravity = p['gravity']
    flap_speed = p['flap_speed']
    fall_limit = p['fall_limit']
    speed = p['speed']
    
    vy = state['vy']
    if state['pending']:
        vy = flap_speed
        
    pending = action
    vy = max(-fall_limit, vy - gravity * dt)
    y = state['y'] + vy * dt
    x = state['x'] + speed * dt
    tick = observation.get('tick', 0) + 1
    collected = state.get('collected', 0)

    next_state = {
        'x': x,
        'y': y,
        'vy': vy,
        'pending': pending,
        'collected': collected,
        'tick': tick,
    }
    return next_state

def crash_star(state, observation):
    p = observation['physics']
    r = p['radius']
    x = state['x']
    y = state['y']
    t = state.get('tick', observation.get('tick', 0)) * p['dt']
    
    crashed = False
    
    # Check floor and ceiling
    if y - r <= 0 or y + r >= p['height']:
        crashed = True
    else:
        # Check gates
        for gate in observation.get('gates', []):
            center = gate['center'] + gate['amplitude'] * math.sin(gate['omega'] * t + gate['phase'])
            lo = center - gate['gap'] / 2
            hi = center + gate['gap'] / 2
            overlap = (x + r > gate['x'] - gate['half_width'] and x - r < gate['x'] + gate['half_width'])
            if overlap and (y - r < lo or y + r > hi):
                crashed = True
                break
                
    # Check if we got the nearest star
    got_nearest = False
    stars = observation.get('stars', [])
    if stars:
        nearest_star = min(stars, key=lambda s: (x - s['x']) ** 2 + (y - s['y']) ** 2)
        if (x - nearest_star['x']) ** 2 + (y - nearest_star['y']) ** 2 <= (r + nearest_star['radius']) ** 2:
            got_nearest = True
            
    return (crashed, got_nearest)


def max_survival(state, observation, horizon):

    if horizon == 0:
        return (0,False)

    best = (0,False)

    for action in heuristic(state, observation):

        next_state = advance(state, action, observation)
        crashed_star = crash_star(next_state, observation)

        if crashed_star[0]:
            continue

        next_state['collected'] = state['collected'] or crashed_star[1]

        next_max = max_survival(next_state, observation, horizon-1)

        score = (1 + next_max[0], next_state['collected'] or next_max[1])

        if score[0] > best[0]:
            best = score
        elif score[0] == best[0] and score[1] and not best[1]:
            best = score

        if best[0] == horizon and best[1]:
            break

    return best


def act(observation):
    DEBUG.clear()

    state = {
        'x':observation['x'],
        'y':observation['y'],
        'vy':observation['vy'],
        'pending':observation['pending'],
        'collected':observation['collected'],
        'tick':observation['tick'],
    }

    actions = heuristic(state, observation)

    best = (0, False, False)

    # horizon = 10
    # horizon = 12
    horizon = 15

    for action in actions:
        next_state = advance(state, action, observation)
        crashed_star = crash_star(next_state, observation)

        if crashed_star[0]:
            continue

        next_state['collected'] = state['collected'] or crashed_star[1]

        next_max = max_survival(next_state, observation, horizon-1)

        score = (1 + next_max[0], next_state['collected'] or next_max[1])

        if score[0] > best[0]:
            best = (score[0], score[1], action)
        elif score[0] == best[0] and score[1] and not best[1]:
            best = (score[0], score[1], action)

    DEBUG.update(max_survive=best[0], stars=best[1])

    return best[2]

    # {'tick': 0, 'seconds': 0.0, 'frames_left': 232, 'x': 0.0, 'y': 51.885529961058786, 'vy': -1.8944601575387623, 'pending': False, 'collected': 0, 'required': 0, 'finish_x': 670.6290444764564, 'physics': {'dt': 0.11, 'gravity': 18.602808633384825, 'flap_speed': 16.199945851572615, 'fall_limit': 28.989376787024685, 'speed': 26.887001883390056, 'radius': 1.3676336893072212, 'height': 96.20274721409795}, 'gates': [{'id': 0, 'x': 97.59981683670591, 'half_width': 3.3252885348286725, 'center': 58.167349229106954, 'gap': 18.34844093393946, 'amplitude': 0, 'omega': 1.2688945773482097, 'phase': 1.3080470472809589, 'gap_lo': 48.993128762137225, 'gap_hi': 67.34156969607669}, {'id': 1, 'x': 227.73290595231333, 'half_width': 3.578248675581224, 'center': 44.06145953603237, 'gap': 17.823221636856896, 'amplitude': 0, 'omega': 1.1768493258861128, 'phase': 2.907463800562458, 'gap_lo': 35.14984871760392, 'gap_hi': 52.97307035446082}, {'id': 2, 'x': 351.95085465357573, 'half_width': 4.254496708208143, 'center': 66.68340497466, 'gap': 18.34844093393946, 'amplitude': 0, 'omega': 0.8979598321918594, 'phase': 0.7677337584792125, 'gap_lo': 57.509184507690264, 'gap_hi': 75.85762544162972}], 'stars': [{'id': 0, 'x': 88.72710621518719, 'y': 59.686733624238656, 'radius': 3.2}, {'id': 1, 'x': 218.86019533079465, 'y': 41.52915221081286, 'radius': 3.2}]}
