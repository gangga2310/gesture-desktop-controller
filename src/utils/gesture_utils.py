"""
Gesture Utilities

Utility functions untuk mengenali gesture tangan.

Author:
    Gangga Prakarsa Miharja
"""

import math

from src.utils.geometry import distance

# ==========================================================
# MediaPipe Hand Landmark Index
# ==========================================================

THUMB_TIP = 4

INDEX_FINGER_MCP = 5
INDEX_FINGER_TIP = 8

PINKY_MCP = 17


# ==========================================================
# Landmark Utilities
# ==========================================================

def get_landmark(
    hand_landmarks,
    landmark_id,
):
    """
    Return normalized landmark coordinate.

    Parameters
    ----------
    hand_landmarks
        MediaPipe hand landmarks.

    landmark_id : int
        Landmark index.

    Returns
    -------
    tuple[float, float]
        (x, y) normalized coordinate.
    """

    landmark = hand_landmarks[landmark_id]

    return (
        landmark.x,
        landmark.y,
    )


def get_landmark_pixel(
    hand_landmarks,
    landmark_id,
    image_width,
    image_height,
):
    """
    Convert normalized landmark coordinate
    into pixel coordinate.

    Returns
    -------
    tuple[int, int]
    """

    landmark = hand_landmarks[landmark_id]

    return (
        int(landmark.x * image_width),
        int(landmark.y * image_height),
    )


# ==========================================================
# Hand Geometry
# ==========================================================

def hand_scale(
    hand_landmarks,
):
    """
    Calculate hand scale.

    Hand scale is defined as the distance between
    Index MCP and Pinky MCP.

    Returns
    -------
    float
    """

    index_mcp = get_landmark(
        hand_landmarks,
        INDEX_FINGER_MCP,
    )

    pinky_mcp = get_landmark(
        hand_landmarks,
        PINKY_MCP,
    )

    return distance(
        index_mcp,
        pinky_mcp,
    )


def relative_distance(
    point_a,
    point_b,
    scale,
):
    """
    Calculate scale-invariant distance.

    Parameters
    ----------
    point_a
        First point.

    point_b
        Second point.

    scale
        Reference distance.

    Returns
    -------
    float
    """

    if scale <= 0:
        return 0.0

    return distance(
        point_a,
        point_b,
    ) / scale


# ==========================================================
# Pinch Gesture
# ==========================================================

def pinch_ratio(
    hand_landmarks,
):
    """
    Calculate normalized pinch ratio.

    Returns
    -------
    float

    Notes
    -----
    ratio =
        distance(thumb_tip, index_tip)
        /
        distance(index_mcp, pinky_mcp)
    """

    thumb = get_landmark(
        hand_landmarks,
        THUMB_TIP,
    )

    index = get_landmark(
        hand_landmarks,
        INDEX_FINGER_TIP,
    )

    scale = hand_scale(
        hand_landmarks,
    )

    return relative_distance(
        thumb,
        index,
        scale,
    )


def pinch_distance(
    hand_landmarks,
    image_width,
    image_height,
):
    """
    Calculate pinch distance in pixel.

    This function is only intended for
    visualization/debugging.

    Returns
    -------
    tuple

    (
        pixel_distance,
        thumb_pixel,
        index_pixel,
    )
    """

    thumb = get_landmark_pixel(
        hand_landmarks,
        THUMB_TIP,
        image_width,
        image_height,
    )

    index = get_landmark_pixel(
        hand_landmarks,
        INDEX_FINGER_TIP,
        image_width,
        image_height,
    )

    return (
        distance(
            thumb,
            index,
        ),
        thumb,
        index,
    )


def is_pinch(
    hand_landmarks,
    threshold=0.35,
):
    """
    Determine whether pinch gesture
    is detected.

    Parameters
    ----------
    threshold : float

        Relative pinch threshold.

    Returns
    -------
    bool
    """

    ratio = pinch_ratio(
        hand_landmarks,
    )

    return ratio <= threshold


def pinch_distance_cm(
    world_landmarks,
):
    """
    Pinch distance in cm, measured in the palm plane.

    Uses MediaPipe world landmarks (meters).
    Only x and y are used because z is perpendicular
    to the palm and would inflate the distance when
    the thumb is in front of the index.

    Parameters
    ----------
    world_landmarks
        MediaPipe hand world landmarks
        (21 landmarks with .x, .y, .z in meters).

    Returns
    -------
    float
        Distance in cm.
    """

    thumb = world_landmarks[THUMB_TIP]
    index = world_landmarks[INDEX_FINGER_TIP]

    dx = thumb.x - index.x
    dy = thumb.y - index.y

    return math.sqrt(
        dx * dx + dy * dy
    ) * 100.0