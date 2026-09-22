from solution import should_bounce

def check_collision(cosmo, pipe, pipe_width):
    if cosmo["x"] + cosmo["width"] > pipe["position"] and cosmo["x"] < pipe["position"] + pipe_width:
        return cosmo["y"] < pipe["topHeight"] or cosmo["y"] + cosmo["height"] > pipe["topHeight"] + pipe["gap"]
    return False

def simulate_game(params):
    MAX_FRAMES = 10000
    bounce_plan = []
    logs = []
    cosmo = params['cosmo']
    pipes = [{
        "position": pipe['position'],
        "topHeight": pipe['topHeight'],
        "gap": pipe['gap'],
        "passed": False
    } for pipe in params['pipes']]

    score = 0
    mission_complete = False
    game_over = False
    current_pipe = pipes[0]
    for frame in range(MAX_FRAMES):
        bounce_result = should_bounce({
            "cosmo": cosmo.copy(),
            "currentPipe": {
                "position": current_pipe['position'],
                "topHeight": current_pipe['topHeight'],
                "gap": current_pipe['gap']
            },
            "pipes": [{
                "position": pipe['position'],
                "topHeight": pipe['topHeight'],
                "gap": pipe['gap']
            } for pipe in params['pipes']],
            "pipeSpeed": params['pipeSpeed'],
            "frameTime": params['frameTime'],
            "canvasHeight": params['canvasHeight'],
            "canvasWidth": params['canvasWidth'],
            "groundHeight": params['groundHeight'],
            "pipeWidth": params['pipeWidth'],
            "frameNumber": frame,
            "mapName": params['mapName']
        })
        should_bounce_frame = bounce_result['shouldBounce']

        cosmo["velocity"] += cosmo['gravity']
        cosmo["y"] += cosmo["velocity"]
    
        if cosmo["y"] + cosmo["height"] > params['canvasHeight'] - params['groundHeight']:
            game_over = True
            break
        if cosmo["y"] < 0:
            cosmo["y"] = 0
            cosmo["velocity"] = 0
        
        cosmo["x"] += params['pipeSpeed']

        for pipe in pipes:
            if check_collision(cosmo, pipe, params['pipeWidth']):
                game_over = True
                break

            if not pipe["passed"] and pipe["position"] + params['pipeWidth'] < cosmo['x']:
                pipe["passed"] = True
                score += 1
                if score == len(pipes):
                    mission_complete = True
                    break
        for pipe in pipes:
            if pipe["position"] + params['pipeWidth'] > cosmo["x"]:
                current_pipe = pipe
                break

        if game_over or mission_complete:
            break
        
        if should_bounce_frame:
            cosmo["velocity"] = cosmo['bouncePower']

        bounce_plan.append(should_bounce_frame)
        if 'log' in bounce_result:
            logs.append({'frame': frame, 'msg': bounce_result['log']})
        
    return bounce_plan, logs, game_over, mission_complete, score
