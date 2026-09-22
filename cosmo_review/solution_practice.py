"""Small survival search: longer lookahead, cached failures, precomputed gaps."""

HORIZON = 60


def should_bounce(params):
    c = params['cosmo']
    gravity, bounce_speed = c['gravity'], c['bouncePower']
    height, width = c['height'], c['width']
    floor_y = params['canvasHeight'] - params['groundHeight'] - height
    pipe_width = params['pipeWidth']
    pipes = sorted(params['pipes'], key=lambda p: p['position'])
    finish_x = max(p['position'] + pipe_width for p in pipes)
    horizon = min(HORIZON, 10000 - params['frameNumber'])

    # Horizontal movement is identical for every action sequence.
    # Precompute legal top-left y ranges at each future frame.
    xs = [c['x']]
    for _ in range(horizon):
        xs.append(xs[-1] + params['pipeSpeed'])
    bounds = []
    targets = []
    for x in xs:
        low, high = 0.0, floor_y
        for p in pipes:
            if x + width > p['position'] and x < p['position'] + pipe_width:
                low = max(low, p['topHeight'])
                high = min(high, p['topHeight'] + p['gap'] - height)
        bounds.append((low, high))
        ahead = next((p for p in pipes if p['position'] + pipe_width > x), None)
        targets.append((ahead['topHeight'] + ahead['gap']/2, ahead['gap'])
                       if ahead else (floor_y/2 + height/2, floor_y + height))

    failed = set()
    nodes = 0
    best_depth, fallback = -1, False

    def search(depth, y, velocity, first_action=False):
        nonlocal nodes, best_depth, fallback
        nodes += 1
        if depth > best_depth:
            best_depth, fallback = depth, first_action
        if xs[depth] > finish_x or depth == horizon:
            return []

        # Ignore tiny floating-point differences when remembering failures.
        # This can skip a near-identical alternative; it never invents a safe path.
        key = (depth, round(y, 6), velocity)
        if key in failed:
            return None

        # Movement comes before this frame's bounce in the supplied engine.
        new_velocity = velocity + gravity
        new_y = y + new_velocity
        if new_y > floor_y:
            failed.add(key)
            return None
        if new_y < 0:
            new_y, new_velocity = 0.0, 0.0
        low, high = bounds[depth + 1]
        if not low <= new_y <= high:
            failed.add(key)
            return None

        # Keep the original simple ordering heuristic.
        middle, gap = targets[depth]
        distance = y + height/2 - middle
        predicted_distance = y + 3*velocity + 6*gravity + height/2 - middle
        prefer_bounce = distance > gap/6 or predicted_distance > gap/4
        for action in (prefer_bounce, not prefer_bounce):
            next_velocity = bounce_speed if action else new_velocity
            path = search(depth + 1, new_y, next_velocity,
                          action if depth == 0 else first_action)
            if path is not None:
                return [action] + path

        failed.add(key)
        return None

    path = search(0, c['y'], c['velocity'])
    action = path[0] if path else fallback
    return {'shouldBounce': action,
            'log': f'horizon={horizon}, safe_depth={best_depth}, nodes={nodes}, '
                   f'cached_failures={len(failed)}'}
