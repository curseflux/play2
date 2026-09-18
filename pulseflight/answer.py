"""Your submission. Start with START_HERE.md and arena/engine.py.

decide(telemetry) must return the string "glide" or "pulse".
DEBUG is optional; its contents appear alongside each decision in replays.
"""

import math

DEBUG = {}

THRESH = 100

def advance(state, action, telemetry):

    new_x = state['x'] + telemetry['physics']['speed'] * telemetry['physics']['dt']
    new_vy = state['vy']

    new_cooldown = state['cooldown']

    if action == "pulse" and state['cooldown'] == 0:
        new_vy -= telemetry['physics']["impulse"]
        new_cooldown = telemetry['physics']["recharge"]

    new_vy += (telemetry['physics']["gravity"] - telemetry['physics']["drag"] * new_vy) * telemetry['physics']["dt"]
    new_vy = min(telemetry['physics']["fall_cap"], max(-telemetry['physics']["rise_cap"], new_vy))
    
    new_y = state['y'] + new_vy * telemetry['physics']["dt"]
    
    new_cooldown = max(0, new_cooldown - 1)

    next_state = {
        'x':new_x,
        'y':new_y,
        'vy':new_vy,
        'cooldown':new_cooldown,
        'tick':state['tick'] + 1,
    }

    return next_state


def gate_opening(gate, tick):
    """Opening at an absolute frame number, not an offset from now."""
    centre = gate["centre"] + gate["amplitude"] * math.sin(
        2 * math.pi * tick / gate["period"] + gate["phase"])
    return centre - gate["gap"] / 2, centre + gate["gap"] / 2


def check_crashed(state, telemetry):
    bird_c = (state['x'], state['y'])
    radius = telemetry['physics']['radius']

    bird_r = bird_c[0] + radius
    bird_l = bird_c[0] - radius
    bird_t = bird_c[1] - radius
    bird_b = bird_c[1] + radius

    if bird_t <= 0 or bird_b >= telemetry['course']['height']:
        return True

    for gate in telemetry['gates']:
        gate_hi, gate_lo = gate_opening(gate, state['tick'])

        gate_r = gate['x'] + gate['half_width']
        gate_l = gate['x'] - gate['half_width']

        # dist = math.sqrt((bird_c[0])**2 + (bird_c[1])**2)

        if bird_t <= gate_hi or bird_b >= gate_lo:
            if bird_r >= gate_l and gate_r >= bird_l:
                return True

    return False

def heuristics(state, telemetry, level=0):
    if level == 0:
        return ("glide", "pulse")
    
    if level == 1 or level == 2:
        f_gate = None

        for gate in telemetry['gates']:
            if gate['x'] + gate['half_width'] >= state['x'] - telemetry['physics']['radius']:
                f_gate = gate
                break

        if f_gate is None:
            return ("glide", "pulse")

        gate_hi, gate_lo = gate_opening(f_gate, state['tick'])

        if level == 1:
            if state['y'] < (gate_hi + gate_lo) / 2:
                return ("glide", "pulse")
            return ("pulse", "glide")
        
        if level == 2:
            if state['y'] < (gate_hi + gate_lo) / 2:
                if state['vy'] > THRESH:
                    return ("pulse", "glide")
                return ("glide", "pulse")
            if state['y'] > (gate_hi + gate_lo) / 2:
                if state['vy'] < -THRESH:
                    return ("glide", "pulse")
                return ("pulse", "glide")

def max_safe(state, telemetry, n):
    if n == 0:
        return 0

    best = 0

    for action in heuristics(state, telemetry, level=2):
        if action == "pulse" and state['cooldown'] != 0:
            continue

        next_state = advance(state, action, telemetry)
        crashed = check_crashed(next_state, telemetry)

        if crashed:
            continue

        score = 1 + max_safe(next_state, telemetry, n-1)

        if score == n:
            return score
        
        best = max(best, score)

    return best

def decide(telemetry):
    DEBUG.clear()

    state = {
        'x':telemetry['bird']['x'],
        'y':telemetry['bird']['y'],
        'vy':telemetry['bird']['vy'],
        'cooldown':telemetry['bird']['cooldown'],
        'tick':telemetry['clock']['tick'],
    }

    # n = 40
    # n = 30
    n = 20

    best_act = ("glide", 0)

    for action in heuristics(state, telemetry, level=2):
        if action == "pulse" and state['cooldown'] != 0:
            continue

        next_state = advance(state, action, telemetry)
        crashed = check_crashed(next_state, telemetry)

        if crashed:
            continue

        score = 1 + max_safe(next_state, telemetry, n-1)

        if score == n:
            best_act = (action, score)
            break
            
        if score > best_act[1]:
            best_act = (action, score)

    DEBUG.update(act=best_act[0], score=best_act[1])
        
    return best_act[0]





    # max_g = 0
    # max_p = 0

    # next_state = advance(state, "glide", telemetry)
    # crashed = check_crashed(next_state, telemetry)

    # if not crashed:
    #     max_g = 1 + max_safe(next_state, telemetry, n-1)
    #     DEBUG.update(max_g=max_g)

    #     if max_g == n:
    #         return "glide"

    # next_state = advance(state, "pulse", telemetry)
    # crashed = check_crashed(next_state, telemetry)

    # if not crashed:
    #     max_p = 1 + max_safe(next_state, telemetry, n-1)
    #     DEBUG.update(max_g=max_g, max_p=max_p)

    # if max_g > max_p:
    #     return "glide"

    # return "pulse"

    # {'clock': {'tick': 0, 'limit': 363, 'dt': 0.04}, 'bird': {'x': 0.0, 'y': 215.5950005641389, 'vy': 0.0, 'cooldown': 0}, 'course': {'height': 397.6439135264536, 'cleared': 0, 'total': 6}, 'physics': {'dt': 0.04, 'gravity': 336.2915069968503, 'drag': 0.19066378452737584, 'impulse': 72.05971969439541, 'recharge': 3, 'rise_cap': 206.02957722228192, 'fall_cap': 189.72187040480443, 'speed': 142.17868454852166, 'radius': 9.965879856142958}, 'gates': [{'id': 0, 'x': 324.1674007706294, 'half_width': 12.18342762643034, 'centre': 167.02191845435527, 'gap': 79.58317772597394, 'amplitude': 0, 'period': 121.51063598838361, 'phase': 1.7646457961899387, 'top': 127.2303295913683, 'bottom': 206.81350731734224}, {'id': 1, 'x': 580.0890329579684, 'half_width': 19.411890378528064, 'centre': 236.04661027449822, 'gap': 89.99244311246707, 'amplitude': 0, 'period': 116.7313694187013, 'phase': -1.2668491566638753, 'top': 191.05038871826468, 'bottom': 281.04283183073176}, {'id': 2, 'x': 813.2620756175439, 'half_width': 18.158980293532906, 'centre': 272.25955921333093, 'gap': 74.2587230689002, 'amplitude': 0, 'period': 123.02363290869611, 'phase': 2.9645928503124015, 'top': 235.13019767888085, 'bottom': 309.388920747781}]}
