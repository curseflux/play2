"""Survival search matched to the supplied engine.py. No external dependencies."""

HORIZON = 10
MAX_FRAMES = 10000  # The supplied engine's limit.


def heuristics(state, params):
    """Order actions only; the search still checks actual safety."""
    cosmo = params['cosmo']
    # Use the simulated position, not the original currentPipe observation.
    remaining = [p for p in params['pipes']
                 if p['position'] + params['pipeWidth'] > state['x']]
    if not remaining:
        return (False, True)
    pipe = min(remaining, key=lambda p: p['position'])
    middle = pipe['topHeight'] + pipe['gap'] / 2
    distance = state['y'] + cosmo['height'] / 2 - middle

    # Three coasting steps, with gravity applied before movement each step.
    # This estimate ignores a possible ceiling clamp; it only orders branches.
    predicted_y = (state['y'] + 3 * state['velocity']
                   + 6 * cosmo['gravity'])
    predicted_distance = predicted_y + cosmo['height'] / 2 - middle
    if distance > pipe['gap'] / 6 or predicted_distance > pipe['gap'] / 4:
        return (True, False)
    return (False, True)


def crash(state, params):
    cosmo = params['cosmo']
    if state['y'] + cosmo['height'] > params['canvasHeight'] - params['groundHeight']:
        return True
    for pipe in params['pipes']:
        overlaps = (state['x'] + cosmo['width'] > pipe['position']
                    and state['x'] < pipe['position'] + params['pipeWidth'])
        if overlaps and (state['y'] < pipe['topHeight']
                         or state['y'] + cosmo['height'] > pipe['topHeight'] + pipe['gap']):
            return True
    return False


def advance(state, action, params):
    """One exact engine step. Terminal steps do not apply the chosen bounce."""
    cosmo = params['cosmo']
    velocity = state['velocity'] + cosmo['gravity']
    result = dict(x=state['x'], y=state['y'] + velocity,
                  velocity=velocity, crashed=False, finished=False)

    # The engine checks the ground BEFORE clamping y or advancing x.
    if result['y'] + cosmo['height'] > params['canvasHeight'] - params['groundHeight']:
        result['crashed'] = True
        return result

    # Ceiling contact is a clamp, not a fatal collision.
    if result['y'] < 0:
        result['y'] = 0
        result['velocity'] = 0

    result['x'] += params['pipeSpeed']
    result['crashed'] = crash(result, params)
    if result['crashed']:
        return result

    # A pipe is passed only when its right edge is STRICTLY behind the dog.
    result['finished'] = all(
        pipe['position'] + params['pipeWidth'] < result['x']
        for pipe in params['pipes']
    )
    if result['finished']:
        return result

    # The chosen bounce affects movement starting on the following frame.
    if action:
        result['velocity'] = cosmo['bouncePower']
    return result


def max_survival(state, params, horizon):
    if state['finished']:
        return horizon  # Success satisfies all remaining survival requirements.
    if horizon == 0:
        return 0

    best = 0
    for action in heuristics(state, params):
        next_state = advance(state, action, params)
        if next_state['crashed']:
            continue
        score = 1 + max_survival(next_state, params, horizon - 1)
        best = max(best, score)
        if best == horizon:
            break  # No branch can score more than the remaining horizon.
    return best


def should_bounce(params):
    cosmo = params['cosmo']
    state = dict(x=cosmo['x'], y=cosmo['y'], velocity=cosmo['velocity'],
                 crashed=False, finished=False)
    horizon = min(HORIZON, max(0, MAX_FRAMES - params['frameNumber']))
    best_score, best_action = 0, False

    for action in heuristics(state, params):
        if horizon == 0:
            break
        next_state = advance(state, action, params)
        if next_state['crashed']:
            continue
        score = 1 + max_survival(next_state, params, horizon - 1)
        if score > best_score:
            best_score, best_action = score, action
        if best_score == horizon:
            break

    return {'shouldBounce': best_action}
