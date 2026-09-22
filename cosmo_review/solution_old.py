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

# def heuristics_complex(state, params):
#     c = params['cosmo']
#     speed = params['pipeSpeed']
#     width = params['pipeWidth']

#     pipes = sorted(
#         (
#             p for p in params['pipes']
#             if p['position'] + width > state['x']
#         ),
#         key=lambda p: p['position'],
#     )

#     if not pipes:
#         return (False, True)

#     pipe = pipes[0]

#     # Safe range for the dog's TOP-LEFT y coordinate.
#     low = pipe['topHeight']
#     high = low + pipe['gap'] - c['height']

#     # If another pipe is close, aim where both openings fit.
#     if len(pipes) > 1:
#         other = pipes[1]
#         free_space = other['position'] - (pipe['position'] + width)

#         if free_space < c['width'] + 6 * speed:
#             shared_low = max(low, other['topHeight'])
#             shared_high = min(
#                 high,
#                 other['topHeight'] + other['gap'] - c['height'],
#             )

#             if shared_low <= shared_high:
#                 low, high = shared_low, shared_high

#     target_y = (low + high) / 2

#     # Estimate time until the dog's center reaches the pipe's center.
#     distance = (
#         pipe['position'] + width / 2
#         - (state['x'] + c['width'] / 2)
#     )
#     frames = max(2, min(8, int(distance / speed) + 1))

#     # This frame's position is identical for both actions.
#     velocity = state['velocity'] + c['gravity']
#     next_y = state['y'] + velocity
#     if next_y < 0:
#         next_y = 0
#         velocity = 0

#     remaining = frames - 1

#     def error(bounce):
#         v = c['bouncePower'] if bounce else velocity
#         predicted_y = (
#             next_y
#             + remaining * v
#             + c['gravity'] * remaining * (remaining + 1) / 2
#         )
#         return abs(predicted_y - target_y)

#     if error(True) < error(False):
#         return (True, False)

#     return (False, True)


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











# ----------------------------------------------------------------------

# # def heuristics(state, params):
# #     # use the current frame to guess the best move. return (True, False) if the dog is under the middle of the next closest gap, otherwise (False, True)
    
# #     current_pipe = params['currentPipe']
    
# #     # Calculate the middle of the gap
# #     gap_middle = current_pipe['topHeight'] + current_pipe['gap'] / 2
    
# #     # Check if Cosmo is below the middle of the gap
# #     if state['y'] > gap_middle + current_pipe['gap'] / 4:
# #         return (True, False)  # Cosmo is below middle, should bounce
# #     else:
# #         return (False, True)  # Cosmo is above middle, don't bounce


# def heuristics(state, params):
#     """
#     Returns a list of actions to try, ordered by priority.
#     Each action is a boolean: True = bounce, False = don't bounce
#     """
#     current_pipe = params['currentPipe']
#     cosmo = params['cosmo']
    
#     # Calculate the middle of the gap
#     gap_middle = current_pipe['topHeight'] + current_pipe['gap'] / 2
    
#     # Calculate vertical distance to gap middle
#     distance_to_middle = state['y'] + cosmo['height'] / 2 - gap_middle
    
#     # Predict where Cosmo will be in a few frames if we don't bounce
#     predicted_y = state['y'] + state['velocity'] * 3 + cosmo['gravity'] * 3 * 4 / 2
#     predicted_distance = predicted_y + cosmo['height'] / 2 - gap_middle
    
#     # If we're falling too low or will be too low soon, prioritize bouncing
#     if distance_to_middle > current_pipe['gap'] / 6 or predicted_distance > current_pipe['gap'] / 4:
#         return [True, False]  # Try bounce first, then no-bounce
#     # If we're too high or rising too fast, prioritize not bouncing
#     elif distance_to_middle < -current_pipe['gap'] / 6 or state['velocity'] < -3:
#         return [False, True]  # Try no-bounce first, then bounce
#     else:
#         # We're in a good position, try both but prefer not bouncing (smoother)
#         return [False, True]


# # def crash(state, params):
# #     # use the current frame and check if dog has crashed. return true if crashed, false otherwise. go through the check_collision(cosmo, pipe, pipe_width) in the simulator.py 
    
# #     cosmo = params['cosmo']
# #     current_pipe = state['currentPipe']
# #     pipe_width = params['pipeWidth']
# #     ground_level = params['canvasHeight'] - params['groundHeight']
    
# #     # Check ground collision
# #     if state['y'] + cosmo['height'] > ground_level:
# #         return True
    
# #     # Check pipe collision
# #     # Check if Cosmo's x position overlaps with the pipe
# #     if state['x'] + cosmo['width'] > current_pipe['position'] and state['x'] < current_pipe['position'] + pipe_width:
# #         # Check if Cosmo hits the top or bottom part of the pipe
# #         if state['y'] < current_pipe['topHeight'] or state['y'] + cosmo['height'] > current_pipe['topHeight'] + current_pipe['gap']:
# #             return True
    
# #     return False

# def crash(state, params):
#     cosmo = params['cosmo']
#     current_pipe = state['currentPipe']
#     pipe_width = params['pipeWidth']
#     ground_level = params['canvasHeight'] - params['groundHeight']
    
#     # Check ground collision
#     if state['y'] + cosmo['height'] > ground_level:
#         return True
    
#     # Check pipe collision - using the same logic as check_collision
#     if state['x'] + cosmo['width'] > current_pipe['position'] and state['x'] < current_pipe['position'] + pipe_width:
#         # Check if Cosmo hits the top or bottom part of the pipe
#         if state['y'] < current_pipe['topHeight'] or state['y'] + cosmo['height'] > current_pipe['topHeight'] + current_pipe['gap']:
#             return True
    
#     return False
    



# def advance(state, action, params):
#     cosmo = params['cosmo']
    
#     # Create a copy of the current state
#     next_state = {
#         'x': state['x'],
#         'y': state['y'],
#         'velocity': state['velocity']
#     }
    
#     # 1. Apply gravity
#     next_state['velocity'] += cosmo['gravity']
    
#     # 2. Update vertical position
#     next_state['y'] += next_state['velocity']
    
#     # 3. Check if Cosmo goes above the screen
#     if next_state['y'] < 0:
#         next_state['y'] = 0
#         next_state['velocity'] = 0
    
#     # 4. Update horizontal position
#     next_state['x'] += params['pipeSpeed']
    
#     # 5. Apply bounce AFTER position updates (affects next frame)
#     if action:
#         next_state['velocity'] = cosmo['bouncePower']
    
#     # 6. Update current pipe if Cosmo has passed it
#     next_state['currentPipe'] = state['currentPipe']
    
#     # Check if we've passed the current pipe
#     if next_state['x'] > state['currentPipe']['position'] + params['pipeWidth']:
#         # Find the next pipe
#         for pipe in params['pipes']:
#             if pipe['position'] + params['pipeWidth'] > next_state['x']:
#                 next_state['currentPipe'] = pipe
#                 break
    
#     return next_state

# def max_survival(state, params, horizon):
#     if horizon == 0:
#         return 0
        
#     best = 0
    
#     for action in heuristics(state, params):
#         next_state = advance(state, action, params)
#         crashed = crash(next_state, params)
        
#         if crashed:
#             continue
        
#         score = 1 + max_survival(next_state, params, horizon-1)
        
#         if score > best:
#             best = score
        
#         if best == horizon:
#             break
    
#     return best


# def should_bounce(params):
#     """
#     Calculates whether Cosmo should bounce on each frame.

#     :param params: Dictionary containing game parameters, including:
#         - cosmo: dict with keys: x, y, velocity, gravity, bouncePower, width, height
#         - pipes: list of dicts, each with: position, topHeight, gap
#         - currentPipe: params of pipe closest to Cosmo, with pipe.x > cosmo.x, a dict with: position, topHeight, gap
#         - pipeSpeed: int
#         - canvasHeight: int
#         - groundHeight: int
#         - pipeWidth: int
#         - frameNumber: int
#         - mapName: string
#     :return: A dictionary with:
#         - 'shouldBounce': boolean indicating whether to bound on current frame
#         - 'log': debug message for that frame
#     """
#     # bounce_frames = [5, 15, 35, 75, 110, 140]  # Frames to bounce on

#     # if params['frameNumber'] in bounce_frames:
#     #     return {'shouldBounce': True, 'log': "Bounce!"}
#     # else:
#     #     return {'shouldBounce': False}
    
#     state = {
#         'x': params['cosmo']['x'],
#         'y': params['cosmo']['y'],
#         'velocity': params['cosmo']['velocity'],
#         'currentPipe': params['currentPipe'],
#     }
    
#     actions = heuristics(state, params)
    
#     horizon = 10
#     # horizon = 15
#     # horizon = 25
    
#     best = (0, False)
    
#     for action in actions:
#         next_state = advance(state, action, params)
#         crashed = crash(next_state, params)
        
#         if crashed:
#             continue
        
#         score = 1 + max_survival(next_state, params, horizon-1)
        
#         if score > best[0]:
#             best = (score, action)
        
#         if best[0] == horizon:
#             break
    

    
#     return {'shouldBounce': best[1]}
