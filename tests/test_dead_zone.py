"""
Unit tests for DeadZoneFilter.

Author:
    Gangga Prakarsa Miharja
"""

import pytest

from src.filters.dead_zone import DeadZoneFilter


def test_initialize():
    dz = DeadZoneFilter(threshold=0.1)

    assert dz.threshold == 0.1
    assert dz.value is None


def test_first_update():
    dz = DeadZoneFilter()

    assert dz.update(1.0) == 1.0


def test_small_change_is_ignored():
    dz = DeadZoneFilter(threshold=0.1)

    dz.update(1.0)

    assert dz.update(1.05) == 1.0


def test_large_change_is_updated():
    dz = DeadZoneFilter(threshold=0.1)

    dz.update(1.0)

    assert dz.update(1.2) == 1.2


def test_reset():
    dz = DeadZoneFilter()

    dz.update(5.0)

    dz.reset()

    assert dz.value is None


@pytest.mark.parametrize(
    "threshold",
    [
        0,
        -1,
        -0.5,
    ]
)
def test_invalid_threshold(threshold):
    with pytest.raises(ValueError):
        DeadZoneFilter(threshold)