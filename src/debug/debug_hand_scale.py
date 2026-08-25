"""
Gesture Desktop Controller

Module:
    Debug Hand Scale

Description:
    Research/debug tool to compare candidate hand scale
    references for pinch ratio normalization.

    Goal:
    Find the reference scale that keeps the pinch ratio
    most stable when the hand moves closer to or
    farther from the camera.

    Candidates
    ----------
    A : Index MCP (5)  <-> Pinky MCP (17)   (current hand_scale)
    B : Wrist (0)      <-> Middle MCP (9)
    C : Wrist (0)      <-> Middle Tip (12)
    D : Average of several palm segments
    E : 3D ratio using world landmarks (meters)
    F : Angle between thumb and index vectors (degrees)

    Display
    -------
    Setiap kandidat menampilkan nilai saat ini + std dev
    (jendela 30 frame). Kandidat terbaik = nilai paling
    stabil (std dev kecil) saat tangan digerakkan
    dekat-sedang-jauh dan saat pinch/terbuka.

Author:
    Gangga Prakarsa Miharja
"""

import math
import time
from collections import deque

import cv2

from src.services.hand_tracker import HandTracker

from src.filters.landmark_smoother import LandmarkSmoother

from src.utils.constants import (
    ONE_EURO_MIN_CUTOFF,
    ONE_EURO_BETA,
    ONE_EURO_D_CUTOFF,
)

from src.utils.geometry import (
    distance,
    clamp,
)

from src.utils.drawing import (
    draw_point,
    draw_label,
    draw_line,
)


# ==========================================================
# Landmark Indices
# ==========================================================

WRIST = 0
THUMB_MCP = 2
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12
RING_MCP = 13
PINKY_MCP = 17


# ==========================================================
# Geometry Helpers
# ==========================================================

def get_point(landmarks, index):
    """
    Return (x, y) of a landmark.
    """

    landmark = landmarks[index]

    return (landmark.x, landmark.y)


def get_point_3d(landmarks, index):
    """
    Return (x, y, z) of a landmark.
    """

    landmark = landmarks[index]

    return (landmark.x, landmark.y, landmark.z)


def distance_3d(point1, point2):
    """
    Euclidean distance in 3D.
    """

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    dz = point2[2] - point1[2]

    return math.sqrt(
        dx * dx + dy * dy + dz * dz
    )


def vector_3d(start, end):
    """
    Vector from start to end in 3D.
    """

    return (
        end[0] - start[0],
        end[1] - start[1],
        end[2] - start[2],
    )


def angle_between_vectors(vec1, vec2):
    """
    Angle between two vectors in degrees.
    """

    dot = (
        vec1[0] * vec2[0]
        + vec1[1] * vec2[1]
        + vec1[2] * vec2[2]
    )

    length1 = math.sqrt(
        vec1[0] ** 2
        + vec1[1] ** 2
        + vec1[2] ** 2
    )

    length2 = math.sqrt(
        vec2[0] ** 2
        + vec2[1] ** 2
        + vec2[2] ** 2
    )

    if length1 == 0 or length2 == 0:
        return 0.0

    cosine = clamp(
        dot / (length1 * length2),
        -1.0,
        1.0,
    )

    return math.degrees(
        math.acos(cosine)
    )


def safe_ratio(numerator, denominator):
    """
    Return numerator / denominator, or 0.0 if invalid.
    """

    if denominator <= 0:
        return 0.0

    return numerator / denominator


# ==========================================================
# Rolling Statistics
# ==========================================================

class RollingStats:
    """
    Track mean and standard deviation of recent values.
    """

    def __init__(self, window=30):
        self.window = window
        self.values = deque(maxlen=window)

    def reset(self):
        """
        Clear history.
        """
        self.values.clear()

    def update(self, value):
        """
        Add a value and return (mean, std_dev).
        """

        self.values.append(value)

        if len(self.values) < 2:
            return value, 0.0

        mean = sum(self.values) / len(self.values)

        variance = sum(
            (v - mean) ** 2
            for v in self.values
        ) / (len(self.values) - 1)

        return mean, math.sqrt(variance)


# ==========================================================
# Candidates
# ==========================================================

def compute_candidates(hand, world, image_width, image_height):
    """
    Compute all candidate scales and ratios.

    Parameters
    ----------
    hand : list
        Smoothed image landmarks.

    world : list
        Smoothed world landmarks (meters).

    Returns
    -------
    dict
    """

    thumb = get_point(hand, THUMB_TIP)
    index = get_point(hand, INDEX_TIP)

    pinch_2d = distance(thumb, index)

    thumb_px = (
        int(thumb[0] * image_width),
        int(thumb[1] * image_height),
    )

    index_px = (
        int(index[0] * image_width),
        int(index[1] * image_height),
    )

    # ---------------- reference scales (2D) ----------------

    scale_a = distance(
        get_point(hand, INDEX_MCP),
        get_point(hand, PINKY_MCP),
    )

    scale_b = distance(
        get_point(hand, WRIST),
        get_point(hand, MIDDLE_MCP),
    )

    scale_c = distance(
        get_point(hand, WRIST),
        get_point(hand, MIDDLE_TIP),
    )

    scale_d = (
        scale_a
        + scale_b
        + distance(
            get_point(hand, INDEX_MCP),
            get_point(hand, RING_MCP),
        )
        + distance(
            get_point(hand, MIDDLE_MCP),
            get_point(hand, PINKY_MCP),
        )
    ) / 4.0

    # ---------------- ratios (2D) ----------------

    ratio_a = safe_ratio(pinch_2d, scale_a)
    ratio_b = safe_ratio(pinch_2d, scale_b)
    ratio_c = safe_ratio(pinch_2d, scale_c)
    ratio_d = safe_ratio(pinch_2d, scale_d)

    # ---------------- 3D (world landmarks) ----------------

    pinch_3d = distance_3d(
        get_point_3d(world, THUMB_TIP),
        get_point_3d(world, INDEX_TIP),
    )

    scale_e = distance_3d(
        get_point_3d(world, INDEX_MCP),
        get_point_3d(world, PINKY_MCP),
    )

    ratio_e = safe_ratio(pinch_3d, scale_e)

    # ---------------- angle ----------------

    thumb_vector = vector_3d(
        get_point_3d(world, THUMB_MCP),
        get_point_3d(world, THUMB_TIP),
    )

    index_vector = vector_3d(
        get_point_3d(world, INDEX_MCP),
        get_point_3d(world, INDEX_TIP),
    )

    angle_f = angle_between_vectors(
        thumb_vector,
        index_vector,
    )

    return {
        "thumb_px": thumb_px,
        "index_px": index_px,
        "pinch_2d": pinch_2d,
        "pinch_3d": pinch_3d,
        "scale_a": scale_a,
        "scale_b": scale_b,
        "scale_c": scale_c,
        "scale_d": scale_d,
        "scale_e": scale_e,
        "ratio_a": ratio_a,
        "ratio_b": ratio_b,
        "ratio_c": ratio_c,
        "ratio_d": ratio_d,
        "ratio_e": ratio_e,
        "angle_f": angle_f,
    }


# ==========================================================
# Main
# ==========================================================

tracker = HandTracker()

smoother_image = LandmarkSmoother(
    min_cutoff=ONE_EURO_MIN_CUTOFF,
    beta=ONE_EURO_BETA,
    d_cutoff=ONE_EURO_D_CUTOFF,
)

smoother_world = LandmarkSmoother(
    min_cutoff=ONE_EURO_MIN_CUTOFF,
    beta=ONE_EURO_BETA,
    d_cutoff=ONE_EURO_D_CUTOFF,
)

stats = {
    "pinch_2d": RollingStats(),
    "pinch_3d": RollingStats(),
    "ratio_a": RollingStats(),
    "ratio_b": RollingStats(),
    "ratio_c": RollingStats(),
    "ratio_d": RollingStats(),
    "ratio_e": RollingStats(),
    "angle_f": RollingStats(),
}

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError(
        "Cannot open webcam."
    )

previous_time = time.time()
fps = 0

WINDOW_NAME = "Hand Scale Analyzer"

print()

print("=" * 60)
print("Gesture Desktop Controller")
print("Debug Hand Scale")
print("=" * 60)
print("Gerakkan tangan dekat - sedang - jauh,")
print("posisi pinch & terbuka, lalu bandingkan")
print("nilai rata-rata (1 detik) dan +/- (std dev).")
print("SPACE : freeze tampilan (untuk mencatat)")
print("R : Reset")
print("ESC : Exit")
print("=" * 60)

paused = False

measurement_count = 0

while True:

    if paused:

        # Freeze: keep showing the last frame with its values.
        draw_label(
            frame,
            "PAUSED - SPACE untuk lanjut",
            20,
            30,
            color=(0, 255, 255),
            scale=0.7,
            thickness=2,
        )

        cv2.imshow(
            WINDOW_NAME,
            frame,
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            paused = False
            print("LANJUT.")

        elif key == 27:
            break

        continue

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(
        frame,
        1,
    )

    image_height, image_width = frame.shape[:2]

    result = tracker.detect(
        frame,
    )

    detected = False

    values = None

    stats_result = None

    if result.hand_landmarks:

        detected = True

        hand = smoother_image.smooth(
            result.hand_landmarks[0],
        )

        if result.hand_world_landmarks:
            world = smoother_world.smooth(
                result.hand_world_landmarks[0],
            )
        else:
            world = hand

        values = compute_candidates(
            hand,
            world,
            image_width,
            image_height,
        )

        # -----------------------------------------
        # Visualization
        # -----------------------------------------

        draw_point(
            frame,
            *values["thumb_px"],
        )

        draw_point(
            frame,
            *values["index_px"],
        )

        draw_line(
            frame,
            values["thumb_px"],
            values["index_px"],
            color=(0, 255, 255),
        )

        # -----------------------------------------
        # Rolling statistics
        # -----------------------------------------

        stats_result = {}

        for key in stats:
            stats_result[key] = stats[key].update(values[key])

    else:

        smoother_image.reset()
        smoother_world.reset()

        for key in stats:
            stats[key].reset()

    # =====================================================
    # FPS
    # =====================================================

    current_time = time.time()

    fps = 1 / (
        current_time - previous_time
    )

    previous_time = current_time

    # =====================================================
    # Information
    # =====================================================

    draw_label(
        frame,
        "Hand Scale Analyzer",
        20,
        30,
        scale=0.8,
        thickness=2,
    )

    draw_label(
        frame,
        f"FPS : {fps:.1f}",
        20,
        60,
    )

    draw_label(
        frame,
        f"Hand : {'Detected' if detected else 'Not Detected'}",
        20,
        90,
    )

    if values is not None:

        pinch_2d_mean = stats_result["pinch_2d"][0]
        pinch_3d_mean = stats_result["pinch_3d"][0]

        draw_label(
            frame,
            f"Pinch 2D : {pinch_2d_mean:.3f}   "
            f"3D : {pinch_3d_mean * 100:.1f} cm",
            20,
            120,
        )

        rows = [
            ("A IdxMCP-PnkMCP", "ratio_a"),
            ("B Wrist-MidMCP", "ratio_b"),
            ("C Wrist-MidTip", "ratio_c"),
            ("D Palm-avg x4", "ratio_d"),
            ("E 3D-world", "ratio_e"),
            ("F Angle (deg)", "angle_f"),
        ]

        y = 155

        for label, key in rows:

            mean, std = stats_result[key]

            draw_label(
                frame,
                f"{label} : {mean:.3f}  +/-{std:.3f}",
                20,
                y,
            )

            y += 25

        draw_label(
            frame,
            "SPACE : Freeze    R : Reset    ESC : Exit",
            20,
            y + 10,
            color=(200, 200, 200),
        )

    # =====================================================
    # Display
    # =====================================================

    cv2.imshow(
        WINDOW_NAME,
        frame,
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord(" "):

        paused = True

        print("PAUSED - SPACE untuk lanjut")

        if stats_result is not None:

            measurement_count += 1

            print()
            print("=" * 44)
            print(
                f"Pengukuran #{measurement_count}  "
                f"({time.strftime('%H:%M:%S')})"
            )
            print("=" * 44)

            print(
                f"Pinch 2D : {stats_result['pinch_2d'][0]:.3f}   "
                f"3D : {stats_result['pinch_3d'][0] * 100:.1f} cm"
            )

            rows_terminal = [
                ("A IdxMCP-PnkMCP", "ratio_a"),
                ("B Wrist-MidMCP", "ratio_b"),
                ("C Wrist-MidTip", "ratio_c"),
                ("D Palm-avg x4", "ratio_d"),
                ("E 3D-world", "ratio_e"),
                ("F Angle (deg)", "angle_f"),
            ]

            for label, stat_key in rows_terminal:

                mean, std = stats_result[stat_key]

                print(
                    f"{label:>14} : {mean:.3f}  "
                    f"+/-{std:.3f}"
                )

            print("=" * 44)

        else:

            print("Belum ada data tangan (tangan tidak terdeteksi).")

    elif key == ord("r"):

        smoother_image.reset()
        smoother_world.reset()

        for key_stat in stats:
            stats[key_stat].reset()

        print("Analyzer reset.")

    elif key == 27:

        print()

        print("=" * 50)
        print("Exit Debug Hand Scale")
        print("=" * 50)

        break


# ==========================================================
# Cleanup
# ==========================================================

cap.release()

cv2.destroyAllWindows()

print("Camera released.")
print("Debug finished.")
