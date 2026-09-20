"""Implement choose(view) -> 'press' or 'release'. Read START.md first."""

DEBUG = {}


def advance(state, action, view):
    p = view["physics"]
    pressed = action == "press"
    
    vy = state["vy"]
    if pressed and not state["held"]:
        vy = -p["flap_speed"]
    held = pressed

    gravity = p["gravity_loaded"] if state["carrying"] else p["gravity_empty"]
    vy = min(p["fall_limit"], vy + gravity * p["dt"])
    y = state["y"] + vy * p["dt"]
    x = state["x"] + p["speed"] * p["dt"]

    next_state = {
        "x": x,
        "y": y,
        "vy": vy,
        "held": held,
        "carrying": state["carrying"],
    }
    return next_state

def crash_station(state, view):
    p = view["physics"]
    r = p["radius"]
    x = state["x"]
    y = state["y"]
    
    crashed = False
    if y - r <= 0 or y + r >= p["height"]:
        crashed = True
    else:
        for gate in view.get("gates", []):
            overlap = (x + r > gate["x"] - gate["half_width"] and 
                       x - r < gate["x"] + gate["half_width"])
            if overlap and (y - r < gate["top"] or y + r > gate["bottom"]):
                crashed = True
                break
                
    station = 0
    prev_x = x - p["speed"] * p["dt"]
    for s in view.get("stations", []):
        if prev_x < s["x"] <= x:
            fits = y - r >= s["top"] and y + r <= s["bottom"]
            if fits:
                station = s["kind"]
                break
                
    return (crashed, station)

def heuristics(state, view):
    target_y = None
    stations = view.get("stations", [])
    gates = view.get("gates", [])
    
    if stations:
        target_y = (stations[0]["top"] + stations[0]["bottom"]) / 2
    elif gates:
        target_y = (gates[0]["top"] + gates[0]["bottom"]) / 2
    else:
        target_y = view["physics"]["height"] / 2

    is_higher = state["y"] < target_y
    actions = ("release", "press") if is_higher else ("press", "release")

    if state["held"]:
        return ("release", "press")
    
    return actions


def max_survival(state, view, horizon):
    if horizon == 0:
        return (0, False, state['carrying'])

    best = (0, False, state['carrying'])

    for action in heuristics(state, view):
        if action == "press" and state['held']:
            continue

        next_state = advance(state, action, view)
        crashed_station = crash_station(next_state, view)

        if crashed_station[0]:
            continue

        delivered = False
        pickup_made = False
        if crashed_station[1] == "depot" and next_state['carrying']:
            delivered = True
            next_state['carrying'] = False
        elif crashed_station[1] == "pickup" and not next_state['carrying']:
            pickup_made = True
            next_state['carrying'] = True

        next_max = max_survival(next_state, view, horizon-1)

        # Prioritize deliveries, then pickups, then survival ticks
        score = (
            1 + next_max[0], 
            delivered or next_max[1], 
            pickup_made or next_max[2], 
            next_state['carrying']
        )

        if score[1] > best[1]: # Deliveries first
            best = score
        elif score[1] == best[1] and score[2] > best[2]: # Pickups second
            best = score
        elif score[1] == best[1] and score[2] == best[2] and score[0] > best[0]: # Survival third
            best = score

        if best[0] == horizon and best[1] and best[3]:
            break

    return best

def choose(view):
    DEBUG.clear()

    state = {
        'x': view['bird']['x'],
        'y': view['bird']['y'],
        'vy': view['bird']['vy'],
        'held': view['bird']['held'],
        'carrying': view['bird']['carrying'],
    }

    actions = heuristics(state, view)

    # horizon = 10
    horizon = 15

    best = (0, False, False, False, "press")

    for action in actions:
        if action == "press" and state['held']:
            continue

        next_state = advance(state, action, view)
        crashed_station = crash_station(next_state, view)

        if crashed_station[0]:
            continue

        delivered = False
        pickup_made = False
        if crashed_station[1] == "depot" and next_state['carrying']:
            delivered = True
            next_state['carrying'] = False
        elif crashed_station[1] == "pickup" and not next_state['carrying']:
            pickup_made = True
            next_state['carrying'] = True

        next_max = max_survival(next_state, view, horizon-1)

        score = (
            1 + next_max[0], 
            delivered or next_max[1], 
            pickup_made or next_max[2], 
            next_state['carrying'], 
            action
        )

        if score[1] > best[1]:
            best = score
        elif score[1] == best[1] and score[2] > best[2]:
            best = score
        elif score[1] == best[1] and score[2] == best[2] and score[0] > best[0]:
            best = score

        if best[0] == horizon and best[1] and best[3]:
            break

    return best[4]


    # {'tick': 0, 'frames_left': 226, 'bird': {'x': 0.0, 'y': 42.96138026622304, 'vy': -2.4122892154968527, 'held': False, 'carrying': False}, 'mission': {'delivered': 0, 'required': 0, 'finish_x': 361.99762745063657}, 'physics': {'dt': 0.08, 'gravity_empty': 40.580086750919975, 'gravity_loaded': 52.75411277619597, 'flap_speed': 25.700721608915984, 'fall_limit': 47.34343454273997, 'speed': 20.498166899809544, 'radius': 1.3458132530809506, 'height': 95.84602289313766}, 'gates': [{'id': 0, 'x': 60.67457402343621, 'half_width': 4.031827645509747, 'top': 15.086151494109238, 'bottom': 39.02397161543008}, {'id': 1, 'x': 150.86650838259828, 'half_width': 4.131752147923368, 'top': 40.22199829545243, 'bottom': 67.84773670069686}], 'stations': [{'id': 0, 'x': 40.97993526609922, 'kind': 'pickup', 'top': 21.46885419443726, 'bottom': 35.16048070059916}, {'id': 1, 'x': 86.89582912167265, 'kind': 'depot', 'top': 19.55563837108722, 'bottom': 33.24726487724912}]}


