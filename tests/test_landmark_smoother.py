"""
Unit tests for LandmarkSmoother.

Author:
    Gangga Prakarsa Miharja
"""

from types import SimpleNamespace

import pytest

from src.filters.landmark_smoother import (
    LandmarkSmoother,
    SmoothedLandmark,
)


# ==========================================================
# Helper
# ==========================================================

def make_hand(values):
    """
    Build a fake 21-landmark hand.

    values : list of (x, y, z)
    """

    hand = []

    for x, y, z in values:
        hand.append(
            SimpleNamespace(
                x=x,
                y=y,
                z=z,
            )
        )

    return hand


# ==========================================================
# First Smooth
# ==========================================================

def test_first_smooth_returns_inputs():
    """
    First call should return the input values unchanged.
    """

    smoother = LandmarkSmoother()

    hand = make_hand(
        [
            (float(i), float(i) + 0.5, 0.0)
            for i in range(21)
        ]
    )

    smoothed = smoother.smooth(hand, t=0.0)

    assert len(smoothed) == 21
    assert smoothed[0].x == 0.0
    assert smoothed[4].y == 4.5


# ==========================================================
# Output Shape
# ==========================================================

def test_output_has_x_y_z():
    """
    Output landmarks should expose .x, .y, .z.
    """

    smoother = LandmarkSmoother()

    hand = make_hand(
        [(0.5, 0.5, 0.0)] * 21
    )

    smoothed = smoother.smooth(hand, t=0.0)

    assert isinstance(smoothed[0], SmoothedLandmark)
    assert hasattr(smoothed[0], "x")
    assert hasattr(smoothed[0], "y")
    assert hasattr(smoothed[0], "z")


# ==========================================================
# Constant Hand
# ==========================================================

def test_constant_hand_converges():
    """
    Constant landmarks should converge
    to the same values.
    """

    smoother = LandmarkSmoother(
        min_cutoff=1.0,
        beta=0.0,
    )

    hand = make_hand(
        [(0.5, 0.5, 0.0)] * 21
    )

    smoother.smooth(hand, t=0.0)

    result = None

    for i in range(1, 60):
        result = smoother.smooth(hand, t=i * 0.033)

    assert result[10].x == pytest.approx(0.5, abs=1e-6)
    assert result[10].y == pytest.approx(0.5, abs=1e-6)


# ==========================================================
# Reset
# ==========================================================

def test_reset():
    """
    Reset should clear all filter states.
    """

    smoother = LandmarkSmoother()

    hand = make_hand(
        [(0.0, 0.0, 0.0)] * 21
    )

    smoother.smooth(hand, t=0.0)
    smoother.smooth(hand, t=0.033)

    smoother.reset()

    result = smoother.smooth(hand, t=1.0)

    assert result[0].x == 0.0
