"""
Gesture Desktop Controller

Module:
    Hysteresis Filter

Description:
    Filter for threshold-based states that avoids
    flickering between ON and OFF.

    Uses two thresholds:
    - turn ON  when value <  threshold - band
    - turn OFF when value >  threshold + band

    Values inside the band keep the current state.

Author:
    Gangga Prakarsa Miharja
"""


class HysteresisFilter:
    """
    Hysteresis state filter.
    """

    def __init__(
        self,
        threshold=0.5,
        band=0.1,
        initial=False,
    ):
        """
        Parameters
        ----------
        threshold : float
            Center of the hysteresis band.

        band : float
            Half width of the band.
            band = 0 behaves like a simple threshold.

        initial : bool
            Initial state.
        """

        if band < 0:
            raise ValueError(
                "band must be >= 0."
            )

        self.threshold = threshold
        self.band = band

        self.lower = threshold - band
        self.upper = threshold + band

        self._state = initial
        self._changed = False

    @property
    def state(self):
        """
        Current state.
        """
        return self._state

    @property
    def changed(self):
        """
        True if the state changed in the last update.
        """
        return self._changed

    def reset(self, initial=False):
        """
        Reset the filter state.
        """
        self._state = initial
        self._changed = False

    def update(self, value):
        """
        Update with a new value.

        Returns
        -------
        bool
            Current state.
        """

        self._changed = False

        if self._state:

            # Currently ON: turn OFF only above upper.
            if value > self.upper:
                self._state = False
                self._changed = True

        else:

            # Currently OFF: turn ON only below lower.
            if value < self.lower:
                self._state = True
                self._changed = True

        return self._state
