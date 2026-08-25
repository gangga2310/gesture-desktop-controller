"""
Gesture Desktop Controller

Module:
    Pinch Gesture

Description:
    Process raw pinch ratio into a stable gesture state.

Author:
    Gangga Prakarsa Miharja
"""

from src.filters.ema_filter import EMAFilter
from src.filters.dead_zone import DeadZoneFilter
from src.filters.hysteresis import HysteresisFilter

from src.gesture.gesture_state import GestureState

from src.utils.constants import (
    PINCH_THRESHOLD,
    EMA_ALPHA,
    DEAD_ZONE_THRESHOLD,
)


class PinchGesture:
    """
    Process pinch gesture signal.

    Pipeline
    --------
    Raw Ratio
        ↓
    EMA Filter
        ↓
    Dead Zone
        ↓
    GestureState
    """

    def __init__(
        self,
        threshold=PINCH_THRESHOLD,
        ema_alpha=EMA_ALPHA,
        dead_zone=DEAD_ZONE_THRESHOLD,
        hysteresis_band=0.0,
    ):
        """
        Initialize gesture processor.

        hysteresis_band : float
            If greater than 0, gesture detection uses
            a hysteresis filter around the threshold
            (band = half width) to avoid flickering.
        """

        self.threshold = threshold

        self.ema = EMAFilter(
            alpha=ema_alpha,
        )

        self.dead_zone = DeadZoneFilter(
            threshold=dead_zone,
        )

        self.hysteresis_band = hysteresis_band

        self.hysteresis = None

        if hysteresis_band > 0:

            self.hysteresis = HysteresisFilter(
                threshold=threshold,
                band=hysteresis_band,
            )

    def reset(self):
        """
        Reset all filters.
        """

        self.ema.reset()
        self.dead_zone.reset()

        if self.hysteresis:
            self.hysteresis.reset()

    def process(
        self,
        raw_ratio,
    ):
        """
        Process raw pinch ratio.

        Parameters
        ----------
        raw_ratio : float

        Returns
        -------
        GestureState
        """

        filtered = self.ema.update(
            raw_ratio,
        )

        stable = self.dead_zone.update(
            filtered,
        )

        if self.hysteresis:
            detected = self.hysteresis.update(stable)
        else:
            detected = stable <= self.threshold

        return GestureState(
            raw_value=raw_ratio,
            filtered_value=filtered,
            stable_value=stable,
            detected=detected,
        )