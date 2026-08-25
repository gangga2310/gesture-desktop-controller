"""
Gesture Desktop Controller

Module:
    Dead Zone Filter

Description:
    Filter to ignore small changes in signal values.
    Useful for reducing jitter after EMA filtering.

Author:
    Gangga Prakarsa Miharja
"""


class DeadZoneFilter:
    """
    Dead Zone Filter.

    Small changes below the threshold
    will be ignored.
    """

    def __init__(self, threshold=0.01):
        """
        Parameters
        ----------
        threshold : float
            Minimum change required to update output.
        """

        if threshold <= 0:
            raise ValueError(
                "threshold must be greater than 0."
            )

        self.threshold = threshold
        self._value = None

    @property
    def value(self):
        """
        Current filtered value.
        """
        return self._value

    def reset(self):
        """
        Reset filter state.
        """
        self._value = None

    def update(self, value):
        """
        Update filter.

        Parameters
        ----------
        value : float

        Returns
        -------
        float
        """

        if self._value is None:
            self._value = value
            return value

        if abs(value - self._value) < self.threshold:
            return self._value

        self._value = value

        return self._value