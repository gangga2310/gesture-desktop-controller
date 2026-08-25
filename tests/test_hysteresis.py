"""
Unit tests for HysteresisFilter.

Author:
    Gangga Prakarsa Miharja
"""

import pytest

from src.filters.hysteresis import HysteresisFilter


# ==========================================================
# Initialization
# ==========================================================

def test_initial_state():
    """
    Default initial state should be False.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.5,
    )

    assert h.state is False


def test_initial_state_true():
    """
    initial=True should start ON.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.5,
        initial=True,
    )

    assert h.state is True


# ==========================================================
# Transitions
# ==========================================================

def test_turns_on_below_lower():
    """
    Value below threshold-band should turn ON.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.5,
    )

    h.update(5.0)

    assert h.update(2.0) is True


def test_stays_on_inside_band():
    """
    Value inside the band should keep ON.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.5,
    )

    h.update(2.0)  # ON

    assert h.update(3.2) is True


def test_turns_off_above_upper():
    """
    Value above threshold+band should turn OFF.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.5,
    )

    h.update(2.0)  # ON

    assert h.update(4.0) is False


def test_stays_off_inside_band():
    """
    Value inside the band should keep OFF.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.5,
    )

    h.update(4.0)  # OFF

    assert h.update(2.8) is False


# ==========================================================
# Changed Flag
# ==========================================================

def test_changed_flag():
    """
    changed should only be True on a transition.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.5,
    )

    h.update(5.0)
    h.update(2.0)

    assert h.changed is True

    h.update(2.5)

    assert h.changed is False


# ==========================================================
# Zero Band
# ==========================================================

def test_zero_band_acts_as_threshold():
    """
    band=0 behaves like a simple threshold.
    """

    h = HysteresisFilter(
        threshold=3.0,
        band=0.0,
    )

    h.update(2.9)

    assert h.state is True

    h.update(3.1)

    assert h.state is False


# ==========================================================
# Invalid Band
# ==========================================================

def test_invalid_band():
    """
    Negative band should raise ValueError.
    """

    with pytest.raises(ValueError):
        HysteresisFilter(
            threshold=3.0,
            band=-1.0,
        )
