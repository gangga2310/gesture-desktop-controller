"""
Unit tests for EMAFilter.

Author:
    Gangga Prakarsa Miharja
"""

import pytest

from src.filters.ema_filter import EMAFilter


# ==========================================================
# Initialization
# ==========================================================

def test_initialize_filter():
    """
    EMAFilter should initialize correctly.
    """

    ema = EMAFilter(alpha=0.2)

    assert ema.alpha == 0.2
    assert ema.value is None


# ==========================================================
# First Update
# ==========================================================

def test_first_update_returns_input():
    """
    The first measurement should become
    the initial EMA value.
    """

    ema = EMAFilter(alpha=0.2)

    result = ema.update(10.0)

    assert result == 10.0
    assert ema.value == 10.0


# ==========================================================
# Multiple Updates
# ==========================================================

def test_multiple_updates():
    """
    EMA should follow the exponential
    moving average formula.
    """

    ema = EMAFilter(alpha=0.5)

    ema.update(10.0)

    result = ema.update(20.0)

    assert result == pytest.approx(15.0)

    result = ema.update(30.0)

    assert result == pytest.approx(22.5)


# ==========================================================
# Reset
# ==========================================================

def test_reset():
    """
    Reset should clear the filter state.
    """

    ema = EMAFilter(alpha=0.3)

    ema.update(10)

    ema.reset()

    assert ema.value is None


# ==========================================================
# Invalid Alpha
# ==========================================================

@pytest.mark.parametrize(
    "alpha",
    [
        0,
        -0.1,
        -5,
        1.5,
        10,
    ],
)
def test_invalid_alpha(alpha):
    """
    Invalid alpha values should
    raise ValueError.
    """

    with pytest.raises(ValueError):

        EMAFilter(alpha=alpha)


# ==========================================================
# Value Property
# ==========================================================

def test_value_property():
    """
    Property 'value' should always
    return the latest EMA value.
    """

    ema = EMAFilter(alpha=0.25)

    ema.update(100)

    ema.update(80)

    assert ema.value == pytest.approx(95.0)