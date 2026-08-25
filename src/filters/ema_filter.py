"""
EMA Filter

Reusable Exponential Moving Average (EMA) filter
for smoothing noisy values.

Author:
    Gangga Prakarsa Miharja
"""


class EMAFilter:
    """
    Exponential Moving Average filter.

    Parameters
    ----------
    alpha : float
        Smoothing factor in range (0.0, 1.0].

        Smaller alpha
            -> smoother
            -> slower response

        Larger alpha
            -> faster response
            -> less smoothing
    """

    def __init__(self, alpha=0.2):
        if not (0.0 < alpha <= 1.0):
            raise ValueError(
                "alpha must be in range (0.0, 1.0]"
            )

        self.alpha = alpha
        self._value = None

    @property
    def value(self):
        """
        Return current filtered value.
        """
        return self._value

    def reset(self):
        """
        Reset filter state.
        """
        self._value = None

    def update(self, measurement):
        """
        Update filter with a new measurement.

        Parameters
        ----------
        measurement : float

        Returns
        -------
        float
            Smoothed value.
        """

        if self._value is None:
            self._value = measurement
            return self._value

        self._value = (
            self.alpha * measurement
            + (1.0 - self.alpha) * self._value
        )

        return self._value