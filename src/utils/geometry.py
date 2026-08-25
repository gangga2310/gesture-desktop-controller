"""
Geometry Utilities

Reusable mathematical functions
for Computer Vision.
"""

import math


# =====================================================
# Distance
# =====================================================

def distance(point1, point2):
    """
    Euclidean distance.

    point = (x, y)
    """

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]

    return math.sqrt(dx * dx + dy * dy)


def distance_squared(point1, point2):
    """
    Squared distance.

    Lebih cepat daripada distance()
    jika hanya digunakan untuk
    membandingkan jarak.
    """

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]

    return dx * dx + dy * dy


# =====================================================
# Mid Point
# =====================================================

def midpoint(point1, point2):
    """
    Titik tengah.
    """

    return (
        (point1[0] + point2[0]) / 2,
        (point1[1] + point2[1]) / 2,
    )


# =====================================================
# Vector
# =====================================================

def vector(start, end):
    """
    Membuat vector.

    start -> end
    """

    return (
        end[0] - start[0],
        end[1] - start[1],
    )


def vector_length(vec):
    """
    Panjang vector.
    """

    return math.sqrt(
        vec[0] ** 2 +
        vec[1] ** 2
    )


def normalize_vector(vec):
    """
    Mengubah vector
    menjadi panjang 1.
    """

    length = vector_length(vec)

    if length == 0:
        return (0.0, 0.0)

    return (
        vec[0] / length,
        vec[1] / length,
    )


# =====================================================
# Utility
# =====================================================

def clamp(value, minimum, maximum):
    """
    Membatasi nilai.
    """

    return max(minimum, min(value, maximum))


def map_range(
    value,
    input_min,
    input_max,
    output_min,
    output_max,
):
    """
    Map a value from one range to another.
    """

    if input_min == input_max:
        raise ValueError(
            "input_min and input_max cannot be equal."
        )

    value = clamp(
        value,
        input_min,
        input_max,
    )

    return (
        (value - input_min)
        /
        (input_max - input_min)
    ) * (
        output_max - output_min
    ) + output_min