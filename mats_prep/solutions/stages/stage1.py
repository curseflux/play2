"""Stage 1 - the reflex. "Falling too fast? burn. Off centre? nudge."

Scores 0/17 and 1% on random scenarios. It fails for a reason worth
understanding: holding a slow descent burns MORE fuel than a fast one,
because fuel is spent per frame and a slow descent has more frames.
"""
# "stage 1": the reactive heuristic almost everyone writes first
def policy(obs):
    if obs["vy"] < -3.0:
        return "up"
    if obs["x"] > 2.0 and obs["vx"] > -2.0:
        return "left"
    if obs["x"] < -2.0 and obs["vx"] < 2.0:
        return "right"
    return "off"
