"""
Unit tests for gesture utilities (pinch_distance_cm).

Author:
    Gangga Prakarsa Miharja
"""

from types import SimpleNamespace

import pytest

from src.utils.gesture_utils import pinch_distance_cm


# ==========================================================
# Helper
# ==========================================================

def make_world_landmarks(points):
    """
    Build a fake 21-landmark world hand.

    points : dict {index: (x, y, z)} in meters
    """

    landmarks = []

    for i in range(21):
        x, y, z = points.get(i, (0.0, 0.0, 0.0))
        landmarks.append(
            SimpleNamespace(
                x=x,
                y=y,
                z=z,
            )
        )

    return landmarks


# ==========================================================
# Distance
# ==========================================================

def test_zero_distance():
    """
    Tips at the same position -> 0 cm.
    """

    world = make_world_landmarks({
        4: (0.0, 0.0, 0.0),
        8: (0.0, 0.0, 0.0),
    })

    assert pinch_distance_cm(world) == 0.0


def test_five_cm_lateral():
    """
    Tips 0.05 m apart in xy -> 5 cm.
    """

    world = make_world_landmarks({
        4: (0.0, 0.0, 0.0),
        8: (0.05, 0.0, 0.0),
    })

    assert pinch_distance_cm(world) == pytest.approx(5.0)


def test_z_ignored():
    """
    Depth difference must NOT affect the distance.
    """

    world = make_world_landmarks({
        4: (0.0, 0.0, 0.10),   # thumb far in front
        8: (0.0, 0.0, 0.0),
    })

    assert pinch_distance_cm(world) == 0.0


def test_diagonal_3_4_5():
    """
    xy triangle 3-4-5: dx=0.03, dy=0.04 -> 5 cm.
    """

    world = make_world_landmarks({
        4: (0.0, 0.0, 0.0),
        8: (0.03, 0.04, 0.0),
    })

    assert pinch_distance_cm(world) == pytest.approx(5.0)
