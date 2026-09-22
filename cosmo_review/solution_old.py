# def heuristics(state, params):
#     # use the current frame to guess the best move. return (True, False) if the dog is under the middle of the next closest gap, otherwise (False, True)
    
#     current_pipe = params['currentPipe']
    
#     # Calculate the middle of the gap
#     gap_middle = current_pipe['topHeight'] + current_pipe['gap'] / 2
    
#     # Check if Cosmo is below the middle of the gap
#     if state['y'] > gap_middle + current_pipe['gap'] / 4:
#         return (True, False)  # Cosmo is below middle, should bounce
#     else:
#         return (False, True)  # Cosmo is above middle, don't bounce


def heuristics(state, params):
    """
    Returns a list of actions to try, ordered by priority.
    Each action is a boolean: True = bounce, False = don't bounce
    """
    current_pipe = params['currentPipe']
    cosmo = params['cosmo']
    
    # Calculate the middle of the gap
    gap_middle = current_pipe['topHeight'] + current_pipe['gap'] / 2
    
    # Calculate vertical distance to gap middle
    distance_to_middle = state['y'] + cosmo['height'] / 2 - gap_middle
    
    # Predict where Cosmo will be in a few frames if we don't bounce
    predicted_y = state['y'] + state['velocity'] * 3 + cosmo['gravity'] * 3 * 4 / 2
    predicted_distance = predicted_y + cosmo['height'] / 2 - gap_middle
    
    # If we're falling too low or will be too low soon, prioritize bouncing
    if distance_to_middle > current_pipe['gap'] / 6 or predicted_distance > current_pipe['gap'] / 4:
        return [True, False]  # Try bounce first, then no-bounce
    # If we're too high or rising too fast, prioritize not bouncing
    elif distance_to_middle < -current_pipe['gap'] / 6 or state['velocity'] < -3:
        return [False, True]  # Try no-bounce first, then bounce
    else:
        # We're in a good position, try both but prefer not bouncing (smoother)
        return [False, True]


# def crash(state, params):
#     # use the current frame and check if dog has crashed. return true if crashed, false otherwise. go through the check_collision(cosmo, pipe, pipe_width) in the simulator.py 
    
#     cosmo = params['cosmo']
#     current_pipe = state['currentPipe']
#     pipe_width = params['pipeWidth']
#     ground_level = params['canvasHeight'] - params['groundHeight']
    
#     # Check ground collision
#     if state['y'] + cosmo['height'] > ground_level:
#         return True
    
#     # Check pipe collision
#     # Check if Cosmo's x position overlaps with the pipe
#     if state['x'] + cosmo['width'] > current_pipe['position'] and state['x'] < current_pipe['position'] + pipe_width:
#         # Check if Cosmo hits the top or bottom part of the pipe
#         if state['y'] < current_pipe['topHeight'] or state['y'] + cosmo['height'] > current_pipe['topHeight'] + current_pipe['gap']:
#             return True
    
#     return False

def crash(state, params):
    cosmo = params['cosmo']
    current_pipe = state['currentPipe']
    pipe_width = params['pipeWidth']
    ground_level = params['canvasHeight'] - params['groundHeight']
    
    # Check ground collision
    if state['y'] + cosmo['height'] > ground_level:
        return True
    
    # Check pipe collision - using the same logic as check_collision
    if state['x'] + cosmo['width'] > current_pipe['position'] and state['x'] < current_pipe['position'] + pipe_width:
        # Check if Cosmo hits the top or bottom part of the pipe
        if state['y'] < current_pipe['topHeight'] or state['y'] + cosmo['height'] > current_pipe['topHeight'] + current_pipe['gap']:
            return True
    
    return False
    



def advance(state, action, params):
    cosmo = params['cosmo']
    
    # Create a copy of the current state
    next_state = {
        'x': state['x'],
        'y': state['y'],
        'velocity': state['velocity']
    }
    
    # 1. Apply gravity
    next_state['velocity'] += cosmo['gravity']
    
    # 2. Update vertical position
    next_state['y'] += next_state['velocity']
    
    # 3. Check if Cosmo goes above the screen
    if next_state['y'] < 0:
        next_state['y'] = 0
        next_state['velocity'] = 0
    
    # 4. Update horizontal position
    next_state['x'] += params['pipeSpeed']
    
    # 5. Apply bounce AFTER position updates (affects next frame)
    if action:
        next_state['velocity'] = cosmo['bouncePower']
    
    # 6. Update current pipe if Cosmo has passed it
    next_state['currentPipe'] = state['currentPipe']
    
    # Check if we've passed the current pipe
    if next_state['x'] > state['currentPipe']['position'] + params['pipeWidth']:
        # Find the next pipe
        for pipe in params['pipes']:
            if pipe['position'] + params['pipeWidth'] > next_state['x']:
                next_state['currentPipe'] = pipe
                break
    
    return next_state

def max_survival(state, params, horizon):
    if horizon == 0:
        return 0
        
    best = 0
    
    for action in heuristics(state, params):
        next_state = advance(state, action, params)
        crashed = crash(next_state, params)
        
        if crashed:
            continue
        
        score = 1 + max_survival(next_state, params, horizon-1)
        
        if score > best:
            best = score
        
        if best == horizon:
            break
    
    return best


def should_bounce(params):
    """
    Calculates whether Cosmo should bounce on each frame.

    :param params: Dictionary containing game parameters, including:
        - cosmo: dict with keys: x, y, velocity, gravity, bouncePower, width, height
        - pipes: list of dicts, each with: position, topHeight, gap
        - currentPipe: params of pipe closest to Cosmo, with pipe.x > cosmo.x, a dict with: position, topHeight, gap
        - pipeSpeed: int
        - canvasHeight: int
        - groundHeight: int
        - pipeWidth: int
        - frameNumber: int
        - mapName: string
    :return: A dictionary with:
        - 'shouldBounce': boolean indicating whether to bound on current frame
        - 'log': debug message for that frame
    """
    # bounce_frames = [5, 15, 35, 75, 110, 140]  # Frames to bounce on

    # if params['frameNumber'] in bounce_frames:
    #     return {'shouldBounce': True, 'log': "Bounce!"}
    # else:
    #     return {'shouldBounce': False}
    
    state = {
        'x': params['cosmo']['x'],
        'y': params['cosmo']['y'],
        'velocity': params['cosmo']['velocity'],
        'currentPipe': params['currentPipe'],
    }
    
    actions = heuristics(state, params)
    
    horizon = 10
    # horizon = 15
    # horizon = 25
    
    best = (0, False)
    
    for action in actions:
        next_state = advance(state, action, params)
        crashed = crash(next_state, params)
        
        if crashed:
            continue
        
        score = 1 + max_survival(next_state, params, horizon-1)
        
        if score > best[0]:
            best = (score, action)
        
        if best[0] == horizon:
            break
    

    
    return {'shouldBounce': best[1]}
