"""
Gesture Desktop Controller

Module:
    Gesture State

Description:
    Immutable object representing the current processed
    gesture values.

Author:
    Gangga Prakarsa Miharja
"""

from dataclasses import dataclass


@dataclass(slots=True)
class GestureState:
    """
    Processed gesture information.

    Attributes
    ----------
    raw_value : float
        Raw value from gesture detection.

    filtered_value : float
        Value after EMA filtering.

    stable_value : float
        Value after Dead Zone filtering.

    detected : bool
        True if gesture is detected.
    """

    raw_value: float
    filtered_value: float
    stable_value: float
    detected: bool