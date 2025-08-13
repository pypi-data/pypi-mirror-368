from abc import ABC, abstractmethod

import numpy as np


class Schedule(ABC):
    @abstractmethod
    def value(self, step: int) -> float: ...


class ConstantSchedule(Schedule):
    """Constant schedule, always returning the same value."""

    def __init__(self, v: float):
        self.v = v

    def value(self, step):
        return self.v


class LinearSchedule(Schedule):
    """Linear schedule from `start` to `stop` over `n_steps`. After `n_steps`,
    it stays fixed at `stop`."""

    def __init__(self, start: float, stop: float, n_steps: int):
        self.start = start
        self.stop = stop
        self.n_steps = n_steps

    def value(self, step: int) -> float:
        frac = step / self.n_steps

        if frac < 0.0:
            frac = 0.0
        elif frac > 1.0:
            frac = 1.0

        return self.start + frac * (self.stop - self.start)


class ExponentialDecaySchedule(Schedule):
    """Exponential decay from `start` to 0, with a decay constant `decay`."""

    def __init__(self, start: float, decay: float):
        self.start = start
        self.decay = decay

    def value(self, step) -> float:
        return self.start * np.exp(-self.decay * step)
