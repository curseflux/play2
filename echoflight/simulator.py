"""Public EchoFlight environment. Coordinates increase upward."""
import math


def opening(gate, seconds):
    center = gate['center'] + gate['amplitude'] * math.sin(
        gate['omega'] * seconds + gate['phase'])
    return center - gate['gap'] / 2, center + gate['gap'] / 2


class World:
    def __init__(self, course):
        self.course = course
        self.tick = 0
        self.x = 0.0
        self.y = course['start']['y']
        self.vy = course['start']['vy']
        self.pending = course['start']['pending']
        self.collected = 0
        self.star_states = ['ahead'] * len(course['stars'])
        self.done = self.won = False
        self.reason = 'flying'

    def observe(self):
        c, p = self.course, self.course['physics']
        gates = []
        for i, gate in enumerate(c['gates']):
            if gate['x'] + gate['half_width'] >= self.x - p['radius']:
                lo, hi = opening(gate, self.tick * p['dt'])
                gates.append(dict(id=i, **gate, gap_lo=lo, gap_hi=hi))
        stars = [dict(id=i, **star) for i, star in enumerate(c['stars'])
                 if self.star_states[i] == 'ahead']
        return dict(tick=self.tick, seconds=self.tick * p['dt'],
                    frames_left=c['limit'] - self.tick,
                    x=self.x, y=self.y, vy=self.vy, pending=self.pending,
                    collected=self.collected, required=c['required'],
                    finish_x=c['finish_x'], physics=dict(p),
                    gates=gates[:3], stars=stars[:2])

    def step(self, action):
        if self.done:
            raise RuntimeError('cannot step a finished episode')
        if type(action) is not bool:
            raise ValueError('act(observation) must return a Python bool')
        c, p = self.course, self.course['physics']
        # Last frame's command fires now. This frame's command fires NEXT step.
        if self.pending:
            self.vy = p['flap_speed']
        self.pending = action
        self.vy = max(-p['fall_limit'], self.vy - p['gravity'] * p['dt'])
        self.y += self.vy * p['dt']
        self.x += p['speed'] * p['dt']
        self.tick += 1
        r = p['radius']
        if self.y - r <= 0:
            self.done, self.reason = True, 'floor'
        elif self.y + r >= p['height']:
            self.done, self.reason = True, 'ceiling'
        else:
            for i, gate in enumerate(c['gates']):
                lo, hi = opening(gate, self.tick * p['dt'])
                overlap = (self.x + r > gate['x'] - gate['half_width']
                           and self.x - r < gate['x'] + gate['half_width'])
                if overlap and (self.y - r < lo or self.y + r > hi):
                    self.done, self.reason = True, f'gate {i + 1} collision'
                    break
        for i, star in enumerate(c['stars']):
            if self.star_states[i] != 'ahead':
                continue
            if not self.done and ((self.x - star['x']) ** 2 + (self.y - star['y']) ** 2
                                 <= (r + star['radius']) ** 2):
                self.star_states[i] = 'collected'
                self.collected += 1
            elif self.x - r > star['x'] + star['radius']:
                self.star_states[i] = 'missed'
        if not self.done:
            if self.x >= c['finish_x']:
                self.done = True
                self.won = self.collected >= c['required']
                self.reason = 'complete' if self.won else 'finished below star target'
            elif self.tick >= c['limit']:
                self.done, self.reason = True, 'timeout'
        return self.observe()

    def snapshot(self):
        return dict(tick=self.tick, x=self.x, y=self.y, vy=self.vy,
                    pending=self.pending, collected=self.collected,
                    star_states=list(self.star_states), done=self.done, reason=self.reason)

    def result(self, error=None):
        c = self.course
        progress = min(1.0, self.x / c['finish_x'])
        reward = min(1.0, self.collected / c['required']) if c['required'] else 1.0
        score = 50 * (progress + reward) if c['required'] else 100 * progress
        return dict(name=c['name'], passed=self.won and error is None,
                    progress=progress, collected=self.collected, required=c['required'],
                    score=0.0 if error else score, ticks=self.tick, reason=error or self.reason)
