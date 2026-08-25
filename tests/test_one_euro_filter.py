"""
Unit tests for OneEuroFilter.

Author:
    Gangga Prakarsa Miharja
"""

import pytest

from src.filters.one_euro_filter import OneEuroFilter


# ==========================================================
# First Value
# ==========================================================

def test_first_value_returns_input():
    """
    First measurement should become the initial value.
    """

    f = OneEuroFilter()

    assert f(10.0, t=0.0) == 10.0


# ==========================================================
# Constant Signal
# ==========================================================

def test_constant_signal_converges():
    """
    Constant input should converge to that value.
    """

    f = OneEuroFilter(
        min_cutoff=1.0,
        beta=0.0,
    )

    f(10.0, t=0.0)

    value = None

    for i in range(1, 60):
        value = f(10.0, t=i * 0.033)

    assert value == pytest.approx(10.0, abs=1e-6)


# ==========================================================
# Jitter Reduction
# ==========================================================

def test_reduces_jitter():
    """
    Noisy alternating input should produce
    a smoother output (smaller steps).
    """

    f = OneEuroFilter(
        min_cutoff=1.0,
        beta=0.0,
    )

    noisy = [10.0, 12.0, 9.0, 11.0, 10.0, 12.0, 9.0]

    smoothed = []

    for i, x in enumerate(noisy):
        smoothed.append(f(x, t=i * 0.033))

    input_steps = [
        abs(b - a)
        for a, b in zip(noisy, noisy[1:])
    ]

    smoothed_steps = [
        abs(b - a)
        for a, b in zip(smoothed, smoothed[1:])
    ]

    assert max(smoothed_steps) < max(input_steps)


# ==========================================================
# Ramp Tracking
# ==========================================================

def test_tracks_ramp():
    """
    Gradual trend should be followed with small lag.
    """

    f = OneEuroFilter(
        min_cutoff=1.0,
        beta=1.0,
    )

    f(0.0, t=0.0)

    final = None

    for i in range(1, 100):
        final = f(
            float(i) * 0.1,
            t=i * 0.033,
        )

    # Input ends at 9.9. Output should be close to it.
    assert final == pytest.approx(9.9, abs=1.0)


# ==========================================================
# Reset
# ==========================================================

def test_reset():
    """
    Reset should clear the filter state.
    """

    f = OneEuroFilter()

    f(10.0, t=0.0)
    f(20.0, t=0.033)

    f.reset()

    assert f(30.0, t=1.0) == 30.0


# ==========================================================
# Invalid min_cutoff
# ==========================================================

def test_invalid_min_cutoff():
    """
    Invalid min_cutoff values should raise ValueError.
    """

    with pytest.raises(ValueError):
        OneEuroFilter(min_cutoff=0)

    with pytest.raises(ValueError):
        OneEuroFilter(min_cutoff=-1.0)


# ==========================================================
# Same Timestamp
# ==========================================================

def test_same_timestamp_returns_previous():
    """
    Zero time delta should not break the filter.
    """

    f = OneEuroFilter()

    f(10.0, t=0.0)

    assert f(20.0, t=0.0) == 10.0
