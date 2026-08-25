from src.utils.geometry import (
    distance,
    distance_squared,
    midpoint,
    vector,
    vector_length,
    normalize_vector,
    clamp,
    map_range,
)


# =====================================================
# Distance
# =====================================================

def test_distance():
    assert distance((0, 0), (3, 4)) == 5


def test_distance_squared():
    assert distance_squared((0, 0), (3, 4)) == 25


# =====================================================
# Midpoint
# =====================================================

def test_midpoint():
    assert midpoint((0, 0), (10, 10)) == (5, 5)


# =====================================================
# Vector
# =====================================================

def test_vector():
    assert vector((2, 3), (7, 9)) == (5, 6)


def test_vector_length():
    assert vector_length((3, 4)) == 5


def test_normalize_vector():
    x, y = normalize_vector((3, 4))

    assert round(x, 2) == 0.60
    assert round(y, 2) == 0.80


# =====================================================
# Clamp
# =====================================================

def test_clamp():
    assert clamp(10, 0, 5) == 5
    assert clamp(-3, 0, 5) == 0
    assert clamp(3, 0, 5) == 3


# =====================================================
# Map Range
# =====================================================

def test_map_range():
    value = map_range(
        50,
        0,
        100,
        0,
        1,
    )

    assert value == 0.5