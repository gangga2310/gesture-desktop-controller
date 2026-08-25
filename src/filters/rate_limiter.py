"""
Gesture Desktop Controller

Module:
    Rate Limiter

Description:
    Limits how fast a value can change over time.

    Example with max_rate = 20 per second:
        50 -> 52 -> 54 -> ... (gradual)
    instead of:
        50 -> 80 (jump)

Author:
    Gangga Prakarsa Miharja
"""

import time


class RateLimiter:
    """
    Rate-limiting filter.
    """

    def __init__(self, max_rate=20.0):
        """
        Parameters
        ----------
        max_rate : float
            Maximum change per second.
        """

        if max_rate <= 0:
            raise ValueError(
                "max_rate must be greater than 0."
            )

        self.max_rate = max_rate

        self._value = None
        self._t_prev = None

    @property
    def value(self):
        """
        Current limited value.
        """
        return self._value

    def reset(self):
        """
        Reset filter state.
        """
        self._value = None
        self._t_prev = None

    def hold(self, t=None):
        """
        Update the internal timestamp without changing
        the value.

        Call this when the signal is lost so the next
        update does not use the elapsed gap for rate
        calculation (prevents a jump when the signal
        returns to the same position).
        """

        if t is None:
            t = time.time()

        self._t_prev = t

    def update(self, value, t=None):
        """
        Update with a new target value.

        Parameters
        ----------
        value : float
            Target value.

        t : float | None
            Timestamp in seconds.
            If None, use time.time().

        Returns
        -------
        float
            Limited value.
        """

        if t is None:
            t = time.time()

        if self._value is None:
            self._value = value
            self._t_prev = t
            return value

        time_delta = t - self._t_prev

        if time_delta <= 0:
            return self._value

        max_delta = self.max_rate * time_delta

        delta = value - self._value

        if delta > max_delta:
            delta = max_delta
        elif delta < -max_delta:
            delta = -max_delta

        self._value += delta

        self._t_prev = t

        return self._value
