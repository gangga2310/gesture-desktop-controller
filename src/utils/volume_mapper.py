"""
Gesture Desktop Controller

Module:
    Volume Mapper

Description:
    Convert a value (pinch ratio or pinch distance in cm)
    into volume percentage.

Author:
    Gangga Prakarsa Miharja
"""

from src.utils.geometry import (
    clamp,
    map_range,
)


class VolumeMapper:
    """
    Map a value range to volume percentage (0-100).
    """

    def __init__(
        self,
        min_value=0.0,
        max_value=1.0,
    ):
        """
        Parameters
        ----------
        min_value : float
            Value that maps to 0% volume.
            For pinch in cm: full pinch distance.

        max_value : float
            Value that maps to 100% volume.
            For pinch in cm: full open hand distance.
        """

        self.min_value = min_value
        self.max_value = max_value

    def map(self, value):
        """
        Convert value -> volume percentage.

        Returns
        -------
        float
            0 - 100
        """

        value = clamp(
            value,
            self.min_value,
            self.max_value,
        )

        return map_range(
            value,
            self.min_value,
            self.max_value,
            0,
            100,
        )
