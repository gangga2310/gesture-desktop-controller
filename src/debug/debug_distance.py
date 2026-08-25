"""
Gesture Desktop Controller

Module:
    Debug Distance

Description:
    Validate MediaPipe world-coordinate distance estimates (in cm)
    against real physical measurements using a ruler.

    Pairs
    -----
    Pinch        : Thumb Tip (4)  <-> Index Tip (8)
    Palm width   : Index MCP (5)  <-> Pinky MCP (17)
    Palm length  : Wrist (0)      <-> Middle MCP (9)
    Hand length  : Wrist (0)      <-> Middle Tip (12)

    Cara pakai:
    1. Ukur jarak antar ujung jari dengan penggaris
       (misal 2 cm, 5 cm, 8 cm) dan bandingkan nilai di layar.
    2. Ukur lebar telapak & panjang tangan asli, bandingkan.
    3. SPACE = freeze + catat ke terminal, R = reset, ESC = exit.

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

from src.utils.drawing import (
    draw_point,
    draw_label,
    draw_line,
)


# ==========================================================
# Landmark Indices
# ==========================================================

WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12
PINKY_MCP = 17


# ==========================================================
# Distance Pairs (label, index_a, index_b)
# ==========================================================

PAIRS = [
    ("Pinch (T4-I8)", THUMB_TIP, INDEX_TIP),
    ("Palm width (5-17)", INDEX_MCP, PINKY_MCP),
    ("Palm length (0-9)", WRIST, MIDDLE_MCP),
    ("Hand length (0-12)", WRIST, MIDDLE_TIP),
]


# ==========================================================
# Helpers
# ==========================================================

def get_point_3d(landmarks, index):
    """
    Return (x, y, z) of a landmark.
    """

    landmark = landmarks[index]

    return (landmark.x, landmark.y, landmark.z)


def distance_xy(point1, point2):
    """
    Euclidean distance in 2D (x, y only).

    MediaPipe world coordinates:
    xy = plane of the palm
    z  = perpendicular to the palm

    For pinch we want the lateral distance
    in the palm plane, without the thumb's
    depth offset.
    """

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]

    return math.sqrt(
        dx * dx + dy * dy
    )


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

stats = {}

for label, index_a, index_b in PAIRS:
    stats[label] = RollingStats()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError(
        "Cannot open webcam."
    )

previous_time = time.time()
fps = 0

paused = False

measurement_count = 0

WINDOW_NAME = "Distance Checker"

print()

print("=" * 60)
print("Gesture Desktop Controller")
print("Debug Distance (validasi cm)")
print("=" * 60)
print("Jarak di bidang telapak (xy-plane, tanpa z).")
print("Bandingkan nilai di layar dengan penggaris:")
print("1. Jarak ujung jari 2 cm, 5 cm, 8 cm")
print("2. Lebar telapak & panjang tangan asli")
print("SPACE : freeze + catat ke terminal")
print("R : Reset")
print("ESC : Exit")
print("=" * 60)

while True:

    if paused:

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

        # -----------------------------------------
        # Pinch line visualization
        # -----------------------------------------

        thumb_px = (
            int(hand[THUMB_TIP].x * image_width),
            int(hand[THUMB_TIP].y * image_height),
        )

        index_px = (
            int(hand[INDEX_TIP].x * image_width),
            int(hand[INDEX_TIP].y * image_height),
        )

        draw_point(
            frame,
            *thumb_px,
        )

        draw_point(
            frame,
            *index_px,
        )

        draw_line(
            frame,
            thumb_px,
            index_px,
            color=(0, 255, 255),
        )

        # -----------------------------------------
        # Distances in cm
        # -----------------------------------------

        stats_result = {}

        for label, index_a, index_b in PAIRS:

            cm = distance_xy(
                get_point_3d(world, index_a),
                get_point_3d(world, index_b),
            ) * 100.0

            stats_result[label] = stats[label].update(cm)

    else:

        smoother_image.reset()
        smoother_world.reset()

        for key_stat in stats:
            stats[key_stat].reset()

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
        "Distance Checker (3D world)",
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

    if stats_result is not None:

        y = 130

        for label, index_a, index_b in PAIRS:

            mean, std = stats_result[label]

            draw_label(
                frame,
                f"{label} : {mean:.1f} cm  +/-{std:.1f}",
                20,
                y,
                scale=0.6,
                thickness=2,
            )

            y += 28

        draw_label(
            frame,
            "SPACE : Freeze & catat    R : Reset    ESC : Exit",
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

            for label, index_a, index_b in PAIRS:

                mean, std = stats_result[label]

                print(
                    f"{label:>20} : {mean:.1f} cm  "
                    f"+/-{std:.1f}"
                )

            print("=" * 44)

        else:

            print("Belum ada data tangan (tangan tidak terdeteksi).")

    elif key == ord("r"):

        smoother_image.reset()
        smoother_world.reset()

        for key_stat in stats:
            stats[key_stat].reset()

        print("Checker reset.")

    elif key == 27:

        print()

        print("=" * 50)
        print("Exit Debug Distance")
        print("=" * 50)

        break


# ==========================================================
# Cleanup
# ==========================================================

cap.release()

cv2.destroyAllWindows()

print("Camera released.")
print("Debug finished.")
