"""
Unit tests for RateLimiter.

Author:
    Gangga Prakarsa Miharja
"""

import pytest

from src.filters.rate_limiter import RateLimiter


# ==========================================================
# First Update
# ==========================================================

def test_first_value_returns_input():
    """
    First measurement should become the initial value.
    """

    r = RateLimiter(max_rate=10.0)

    assert r.update(50.0, t=0.0) == 50.0


# ==========================================================
# Rate Limiting
# ==========================================================

def test_gradual_change_limited():
    """
    Large target change should be limited by max_rate.
    """

    r = RateLimiter(max_rate=10.0)

    r.update(0.0, t=0.0)

    # Target 100 after 1s: max move is 10.
    assert r.update(100.0, t=1.0) == pytest.approx(10.0)


def test_small_change_passes():
    """
    Small change below the limit should pass through.
    """

    r = RateLimiter(max_rate=10.0)

    r.update(50.0, t=0.0)

    # Delta 2 over 0.5s: max allowed is 5 -> passes.
    assert r.update(52.0, t=0.5) == pytest.approx(52.0)


def test_negative_direction_limited():
    """
    Rate limiting should apply in both directions.
    """

    r = RateLimiter(max_rate=10.0)

    r.update(50.0, t=0.0)

    # Target 0 after 2s: max move is 20 -> 30.
    assert r.update(0.0, t=2.0) == pytest.approx(30.0)


# ==========================================================
# Reset
# ==========================================================

def test_reset():
    """
    Reset should clear the filter state.
    """

    r = RateLimiter(max_rate=10.0)

    r.update(50.0, t=0.0)

    r.reset()

    assert r.update(100.0, t=5.0) == 100.0


# ==========================================================
# Hold
# ==========================================================

def test_hold_prevents_gap_jump():
    """
    Hold resets the timestamp so a long gap doesn't
    cause a jump when the signal returns.
    """

    r = RateLimiter(max_rate=10.0)

    r.update(50.0, t=0.0)

    # Signal lost for 5 seconds.
    r.hold(t=5.0)

    # dt = 0.033s (one frame) -> max_delta = 0.33
    v = r.update(100.0, t=5.033)

    assert v == pytest.approx(50.33, abs=0.01)


# ==========================================================
# Zero Time Delta
# ==========================================================

def test_zero_time_delta_returns_current():
    """
    Zero time delta should not break the filter.
    """

    r = RateLimiter(max_rate=10.0)

    r.update(50.0, t=0.0)

    assert r.update(100.0, t=0.0) == 50.0


# ==========================================================
# Invalid max_rate
# ==========================================================

def test_invalid_max_rate():
    """
    Invalid max_rate values should raise ValueError.
    """

    with pytest.raises(ValueError):
        RateLimiter(max_rate=0)

    with pytest.raises(ValueError):
        RateLimiter(max_rate=-1.0)
