"""
Gesture Desktop Controller

Module:
    One Euro Filter

Description:
    Adaptive low-pass filter for interactive signals.
    Reduces jitter while keeping low latency.

    Reference:
    Casiez, Roussel & Vogel (2012).
    "1\u20ac Filter: A Simple Speed-based Low-pass Filter
     for Noisy Input in Interactive Systems."

Author:
    Gangga Prakarsa Miharja
"""

import math
import time


def smoothing_factor(time_delta, cutoff):
    """
    Compute smoothing factor for a cutoff frequency.
    """

    r = 2.0 * math.pi * cutoff * time_delta

    return r / (r + 1.0)


class OneEuroFilter:
    """
    Speed-based adaptive low-pass filter.

    Parameters
    ----------
    min_cutoff : float
        Minimum cutoff frequency in Hz.

        Lower value = smoother but more lag.

    beta : float
        Speed coefficient.

        Higher value = more responsive during fast motion.

    d_cutoff : float
        Cutoff frequency for the derivative signal.
    """

    def __init__(
        self,
        min_cutoff=1.0,
        beta=1.0,
        d_cutoff=1.0,
    ):

        if min_cutoff <= 0:
            raise ValueError(
                "min_cutoff must be greater than 0."
            )

        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        self._x_prev = None
        self._dx_prev = None
        self._t_prev = None

    def reset(self):
        """
        Clear filter state.
        """

        self._x_prev = None
        self._dx_prev = None
        self._t_prev = None

    def __call__(self, x, t=None):
        """
        Filter a new measurement.

        Parameters
        ----------
        x : float
            Raw value.

        t : float | None
            Timestamp in seconds.
            If None, use time.time().

        Returns
        -------
        float
            Smoothed value.
        """

        if t is None:
            t = time.time()

        # First measurement becomes the initial value.
        if self._x_prev is None:
            self._x_prev = x
            self._dx_prev = 0.0
            self._t_prev = t
            return x

        time_delta = t - self._t_prev

        # Guard against zero/negative time delta.
        if time_delta <= 0:
            return self._x_prev

        # Derivative (speed) of the signal.
        dx = (x - self._x_prev) / time_delta

        # Smooth the derivative.
        alpha_d = smoothing_factor(
            time_delta,
            self.d_cutoff,
        )

        dx_hat = (
            alpha_d * dx
            + (1.0 - alpha_d) * self._dx_prev
        )

        # Adaptive cutoff:
        # faster motion -> higher cutoff -> less lag.
        cutoff = (
            self.min_cutoff
            + self.beta * abs(dx_hat)
        )

        # Smooth the value.
        alpha = smoothing_factor(
            time_delta,
            cutoff,
        )

        x_hat = (
            alpha * x
            + (1.0 - alpha) * self._x_prev
        )

        self._x_prev = x_hat
        self._dx_prev = dx_hat
        self._t_prev = t

        return x_hat
