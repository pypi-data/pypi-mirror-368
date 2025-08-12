# Adapted from https://github.com/semitable/easing-functions
# synchronized names with Penner and added docstrings

import math

class EasingBase:
    limit = (0, 1)

    def __init__(self, start=0, end=1, duration=1):
        self.start = start
        self.end = end
        self.duration = duration

    @classmethod
    def func(cls, t):
        raise NotImplementedError

    def ease(self, alpha):
        t = self.limit[0] * (1 - alpha) + self.limit[1] * alpha
        t /= self.duration
        a = self.func(t)
        return self.end * a + self.start * (1 - a)

    def __call__(self, alpha):
        return self.ease(alpha)

class linear(EasingBase):
    def func(self, t):
        return t

class easeInQuad(EasingBase):
    def func(self, t):
        return t * t

class easeOutQuad(EasingBase):
    def func(self, t):
        return -(t * (t - 2))

class easeInOutQuad(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 2 * t * t
        return (-2 * t * t) + (4 * t) - 1

class easeInCubic(EasingBase):
    def func(self, t):
        return t * t * t

class easeOutCubic(EasingBase):
    def func(self, t):
        return (t - 1) * (t - 1) * (t - 1) + 1

class easeInOutCubic(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 4 * t * t * t
        p = 2 * t - 2
        return 0.5 * p * p * p + 1

class easeInQuartic(EasingBase):
    def func(self, t):
        return t * t * t * t

class easeOutQuartic(EasingBase):
    def func(self, t):
        return (t - 1) * (t - 1) * (t - 1) * (1 - t) + 1

class easeInOutQuartic(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 8 * t * t * t * t
        p = t - 1
        return -8 * p * p * p * p + 1

class easeInQuintic(EasingBase):
    def func(self, t):
        return t * t * t * t * t

class easeOutQuintic(EasingBase):
    def func(self, t):
        return (t - 1) * (t - 1) * (t - 1) * (t - 1) * (t - 1) + 1

class easeInOutQuintic(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 16 * t * t * t * t * t
        p = (2 * t) - 2
        return 0.5 * p * p * p * p * p + 1

class easeInSine(EasingBase):
    def func(self, t):
        return math.sin((t - 1) * math.pi / 2) + 1

class easeOutSine(EasingBase):
    def func(self, t):
        return math.sin(t * math.pi / 2)

class easeInOutSine(EasingBase):
    def func(self, t):
        return 0.5 * (1 - math.cos(t * math.pi))

class easeInCirc(EasingBase):
    def func(self, t):
        return 1 - math.sqrt(1 - (t * t))

class easeOutCirc(EasingBase):
    def func(self, t):
        return math.sqrt((2 - t) * t)

class easeInOutCirc(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 0.5 * (1 - math.sqrt(1 - 4 * (t * t)))
        return 0.5 * (math.sqrt(-((2 * t) - 3) * ((2 * t) - 1)) + 1)

class easeInExpo(EasingBase):
    def func(self, t):
        if t == 0:
            return 0
        return math.pow(2, 10 * (t - 1))

class easeOutExpo(EasingBase):
    def func(self, t):
        if t == 1:
            return 1
        return 1 - math.pow(2, -10 * t)

class easeInOutExpo(EasingBase):
    def func(self, t):
        if t == 0 or t == 1:
            return t

        if t < 0.5:
            return 0.5 * math.pow(2, (20 * t) - 10)
        return -0.5 * math.pow(2, (-20 * t) + 10) + 1

class easeInElastic(EasingBase):
    def func(self, t):
        return math.sin(13 * math.pi / 2 * t) * math.pow(2, 10 * (t - 1))

class easeOutElastic(EasingBase):
    def func(self, t):
        return math.sin(-13 * math.pi / 2 * (t + 1)) * math.pow(2, -10 * t) + 1

class easeInOutElastic(EasingBase):
    def func(self, t):
        if t < 0.5:
            return (
                0.5
                * math.sin(13 * math.pi / 2 * (2 * t))
                * math.pow(2, 10 * ((2 * t) - 1))
            )
        return 0.5 * (
            math.sin(-13 * math.pi / 2 * ((2 * t - 1) + 1))
            * math.pow(2, -10 * (2 * t - 1))
            + 2
        )

class easeInBack(EasingBase):
    def func(self, t):
        return t * t * t - t * math.sin(t * math.pi)

class easeOutBack(EasingBase):
    def func(self, t):
        p = 1 - t
        return 1 - (p * p * p - p * math.sin(p * math.pi))

class easeInOutBack(EasingBase):
    def func(self, t):
        if t < 0.5:
            p = 2 * t
            return 0.5 * (p * p * p - p * math.sin(p * math.pi))
        p = 1 - (2 * t - 1)
        return 0.5 * (1 - (p * p * p - p * math.sin(p * math.pi))) + 0.5

class easeInBounce(EasingBase):
    def func(self, t):
        return 1 - BounceEaseOut().func(1 - t)

class easeOutBounce(EasingBase):
    def func(self, t):
        if t < 4 / 11:
            return 121 * t * t / 16
        elif t < 8 / 11:
            return (363 / 40.0 * t * t) - (99 / 10.0 * t) + 17 / 5.0
        elif t < 9 / 10:
            return (4356 / 361.0 * t * t) - (35442 / 1805.0 * t) + 16061 / 1805.0
        return (54 / 5.0 * t * t) - (513 / 25.0 * t) + 268 / 25.0

class easeInOutBounce(EasingBase):
    def func(self, t):
        if t < 0.5:
            return 0.5 * BounceEaseIn().func(t * 2)
        return 0.5 * BounceEaseOut().func(t * 2 - 1) + 0.5
