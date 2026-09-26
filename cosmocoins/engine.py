"""Public Cosmo Coins engine: screen coordinates, delayed bounce, no pipes."""
import copy


def touches_coin(cosmo, coin):
    # Nearest point on the bird's rectangle to the coin's center.
    nearest_x = max(cosmo['x'], min(coin['x'], cosmo['x'] + cosmo['width']))
    nearest_y = max(cosmo['y'], min(coin['y'], cosmo['y'] + cosmo['height']))
    return ((coin['x'] - nearest_x) ** 2 + (coin['y'] - nearest_y) ** 2
            <= coin['radius'] ** 2)


class World:
    def __init__(self, course):
        self.course = course
        self.cosmo = copy.deepcopy(course['cosmo'])
        self.frame = self.collected = 0
        self.coin_states = ['available'] * len(course['coins'])
        self.done = self.passed = False
        self.reason = 'flying'

    def observe(self):
        c = self.course
        coins = [dict(id=i, **coin) for i, coin in enumerate(c['coins'])
                 if self.coin_states[i] == 'available']
        return dict(cosmo=dict(self.cosmo), coins=coins,
                    currentCoin=coins[0] if coins else None,
                    coinsCollected=self.collected, coinTarget=c['coinTarget'],
                    coinsTotal=len(c['coins']), scrollSpeed=c['scrollSpeed'],
                    frameTime=c['frameTime'], frameNumber=self.frame,
                    framesLeft=c['maxFrames']-self.frame,
                    canvasHeight=c['canvasHeight'], canvasWidth=c['canvasWidth'],
                    groundHeight=c['groundHeight'], finishX=c['finishX'],
                    mapName=c['mapName'])

    def step(self, action):
        if self.done:
            raise RuntimeError('episode has finished')
        if type(action) is not bool:
            raise ValueError('shouldBounce must be a Python bool')
        c, bird = self.course, self.cosmo
        bird['velocity'] += bird['gravity']
        bird['y'] += bird['velocity']
        self.frame += 1

        # Same timing as cosmo_review: fatal ground precedes ceiling clamp/x.
        if bird['y'] + bird['height'] > c['canvasHeight'] - c['groundHeight']:
            self.done, self.reason = True, 'ground collision'
            return self.observe()
        if bird['y'] < 0:
            bird['y'], bird['velocity'] = 0.0, 0.0
        bird['x'] += c['scrollSpeed']

        for i, coin in enumerate(c['coins']):
            if self.coin_states[i] != 'available':
                continue
            if touches_coin(bird, coin):
                self.coin_states[i] = 'collected'
                self.collected += 1
            elif bird['x'] > coin['x'] + coin['radius']:
                self.coin_states[i] = 'missed'

        if bird['x'] >= c['finishX']:
            self.done = True
            self.passed = self.collected >= c['coinTarget']
            self.reason = 'complete' if self.passed else 'finished below coin target'
        elif self.frame >= c['maxFrames']:
            self.done, self.reason = True, 'frame limit'

        # Bounce sets velocity AFTER movement and only on an unfinished frame.
        if not self.done and action:
            bird['velocity'] = bird['bouncePower']
        return self.observe()

    def snapshot(self):
        return dict(frame=self.frame, **self.cosmo, collected=self.collected,
                    coin_states=list(self.coin_states), done=self.done,
                    reason=self.reason)

    def result(self, error=None):
        c = self.course
        progress = min(1.0, max(0.0, (self.cosmo['x'] - c['cosmo']['x']) /
                              (c['finishX'] - c['cosmo']['x'])))
        reward = min(1.0, self.collected / c['coinTarget']) if c['coinTarget'] else 1.0
        score = 100 * progress if not c['coinTarget'] else 50 * (progress + reward)
        return dict(name=c['mapName'], challenge=c['challenge'],
                    passed=self.passed and error is None, coins=self.collected,
                    target=c['coinTarget'], total=len(c['coins']), progress=progress,
                    score=0.0 if error else score, frames=self.frame,
                    reason=error or self.reason)
