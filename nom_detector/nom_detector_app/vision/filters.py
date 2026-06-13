"""Signal smoothing helpers."""

from collections import deque
from typing import Deque, Optional


class MovingAverageFilter:
    """Simple moving average over the last N numeric samples."""

    def __init__(self, window_size: int = 7) -> None:
        self._window = max(1, int(window_size))
        self._buf: Deque[float] = deque(maxlen=self._window)

    def reset(self) -> None:
        self._buf.clear()

    def push(self, value: float) -> float:
        self._buf.append(float(value))
        return self.value

    @property
    def value(self) -> float:
        if not self._buf:
            return 0.0
        return sum(self._buf) / len(self._buf)

    @property
    def ready(self) -> bool:
        return len(self._buf) >= self._window

    def last_raw(self) -> Optional[float]:
        if not self._buf:
            return None
        return self._buf[-1]
