"""
Gesture Desktop Controller

Module:
    Main

Description:
    Final application entry point.

    Control Windows master volume with the pinch gesture
    through the webcam.

    Pipeline
    --------
    Camera
        ↓
    Hand Tracker
        ↓
    Landmark Smoothing (One Euro Filter)
        ↓
    Pinch Distance (cm, palm plane)
        ↓
    EMA Filter
        ↓
    Dead Zone
        ↓
    Volume Mapper
        ↓
    Rate Limiter
        ↓
    Windows Audio (pycaw)
        ↓
    Volume Windows berubah

    Kalibrasi (M/X) otomatis dimuat dari config.json saat
    start dan tersimpan ke config.json saat diubah.

    Kontrol:
        M : set MIN (pinch penuh)
        X : set MAX (tangan terbuka)
        C : reset kalibrasi
        R : reset filter
        ESC : exit

Author:
    Gangga Prakarsa Miharja
"""

import json
import time
from pathlib import Path

import cv2

from src.services.hand_tracker import HandTracker

from src.utils.volume_mapper import VolumeMapper

from src.gesture.pinch import PinchGesture

from src.utils.gesture_utils import (
    pinch_distance_cm,
    pinch_distance,
)

from src.utils.drawing import (
    draw_point,
    draw_line,
    draw_label,
)

from src.filters.landmark_smoother import LandmarkSmoother
from src.filters.rate_limiter import RateLimiter

from src.utils.windows_audio import WindowsAudio

from src.utils.constants import (
    ONE_EURO_MIN_CUTOFF,
    ONE_EURO_BETA,
    ONE_EURO_D_CUTOFF,
    PINCH_CM_THRESHOLD,
    PINCH_CM_MIN,
    PINCH_CM_MAX,
    DEAD_ZONE_CM,
    HYSTERESIS_BAND_CM,
    VOLUME_RATE_LIMIT,
    WINDOW_NAME,
)


# ==========================================================
# Calibration Config
# ==========================================================

CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config.json"
)


def load_calibration():
    """
    Load calibration values from config.json.

    Returns
    -------
    tuple[float, float]
        (min_cm, max_cm)
    """

    try:
        with open(
            CONFIG_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        min_cm = float(data.get("min_cm", PINCH_CM_MIN))
        max_cm = float(data.get("max_cm", PINCH_CM_MAX))

        print(
            f"Kalibrasi dimuat: {min_cm:.1f} - {max_cm:.1f} cm"
        )

        return min_cm, max_cm

    except (OSError, ValueError, TypeError):
        print("Kalibrasi: memakai default")
        return PINCH_CM_MIN, PINCH_CM_MAX


def save_calibration(min_cm, max_cm):
    """
    Save calibration values to config.json.
    """

    data = {
        "min_cm": min_cm,
        "max_cm": max_cm,
    }

    try:
        with open(
            CONFIG_PATH,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(data, file, indent=2)

        print(
            f"Kalibrasi disimpan ke {CONFIG_PATH}"
        )

    except OSError as error:
        print("Gagal menyimpan kalibrasi:", error)


# ==========================================================
# Helper
# ==========================================================

def draw_progress_bar(
    frame,
    value,
    x,
    y,
    width=350,
    height=30,
):
    """
    Draw volume progress bar.
    """

    value = max(
        0,
        min(
            100,
            value,
        ),
    )

    filled = int(
        width * value / 100
    )

    cv2.rectangle(
        frame,
        (x, y),
        (x + width, y + height),
        (255, 255, 255),
        2,
    )

    cv2.rectangle(
        frame,
        (x, y),
        (x + filled, y + height),
        (0, 255, 0),
        -1,
    )


# ==========================================================
# Audio
# ==========================================================

try:
    audio = WindowsAudio()
except Exception as error:
    print("=" * 50)
    print("Error: Gagal mengakses audio Windows.")
    print(error)
    print("=" * 50)
    raise SystemExit(1)

# Seed the rate limiter with the current system volume
# so the first frame never jumps the volume.
rate_limiter = RateLimiter(
    max_rate=VOLUME_RATE_LIMIT,
)

rate_limiter.update(
    audio.get_volume(),
)

# ==========================================================
# Camera
# ==========================================================

tracker = HandTracker()

gesture = PinchGesture(
    threshold=PINCH_CM_THRESHOLD,
    dead_zone=DEAD_ZONE_CM,
    hysteresis_band=HYSTERESIS_BAND_CM,
)

calibration_min, calibration_max = load_calibration()

mapper = VolumeMapper(
    min_value=calibration_min,
    max_value=calibration_max,
)

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

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("=" * 50)
    print("Error: Tidak dapat membuka webcam.")
    print("Periksa koneksi kamera, lalu jalankan ulang.")
    print("=" * 50)
    raise SystemExit(1)

previous_time = time.time()
fps = 0

volume = 0.0

print()

print("=" * 60)
print("Gesture Desktop Controller")
print("=" * 60)
print(f"Pinch threshold : {PINCH_CM_THRESHOLD:.1f} cm (+/-{HYSTERESIS_BAND_CM:.1f})")
print(f"Volume range    : {mapper.min_value:.1f} - {mapper.max_value:.1f} cm")
print(f"Rate limit      : {VOLUME_RATE_LIMIT:.0f} %/s")
print("M : set MIN (pinch penuh)")
print("X : set MAX (tangan terbuka)")
print("C : reset kalibrasi")
print("R : Reset Filter")
print("ESC : Exit")
print("=" * 60)

while True:

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

    raw_cm = 0.0

    filtered = 0.0

    stable = 0.0

    target_volume = 0.0

    state_text = "OPEN"

    state_color = (0, 0, 255)

    if (
        result.hand_landmarks
        and result.hand_world_landmarks
    ):

        detected = True

        # Smoothed image landmarks (for drawing).
        hand = smoother_image.smooth(
            result.hand_landmarks[0],
        )

        # Smoothed world landmarks (for the pinch signal).
        world = smoother_world.smooth(
            result.hand_world_landmarks[0],
        )

        raw_cm = pinch_distance_cm(
            world,
        )

        gesture_state = gesture.process(
            raw_cm,
        )

        filtered = gesture_state.filtered_value

        stable = gesture_state.stable_value

        # -----------------------------------------
        # Windows Volume
        # -----------------------------------------

        target_volume = mapper.map(
            stable,
        )

        volume = rate_limiter.update(
            target_volume,
        )

        audio.set_volume(
            volume,
        )

        # -----------------------------------------
        # Gesture Status
        # -----------------------------------------

        if gesture_state.detected:

            state_text = "PINCH"

            state_color = (0, 255, 0)

        else:

            state_text = "OPEN"

            state_color = (0, 0, 255)

        # -----------------------------------------
        # Landmark Visualization
        # -----------------------------------------

        pixel_distance, thumb, index = pinch_distance(
            hand,
            image_width,
            image_height,
        )

        draw_point(
            frame,
            *thumb,
        )

        draw_point(
            frame,
            *index,
        )

        draw_line(
            frame,
            thumb,
            index,
            color=state_color,
        )

        draw_label(
            frame,
            f"{pixel_distance:.1f}px",
            thumb[0],
            thumb[1] - 15,
            color=(255, 255, 0),
        )

    else:

        # Hand lost: reset smoothers and hold rate limiter
        # so the volume does not jump when the hand returns.
        smoother_image.reset()
        smoother_world.reset()

        rate_limiter.hold()

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

    system_volume = audio.get_volume()

    draw_label(
        frame,
        "Gesture Desktop Controller",
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

    draw_label(
        frame,
        f"Gesture : {state_text}",
        20,
        120,
        color=state_color,
        scale=0.7,
        thickness=2,
    )

    draw_label(
        frame,
        f"Raw : {raw_cm:.2f} cm",
        20,
        160,
    )

    draw_label(
        frame,
        f"EMA : {filtered:.2f} cm",
        20,
        190,
    )

    draw_label(
        frame,
        f"Stable : {stable:.2f} cm",
        20,
        220,
    )

    draw_label(
        frame,
        f"System Volume : {system_volume:.0f} %",
        20,
        260,
        color=(0, 255, 255),
        scale=0.8,
        thickness=2,
    )

    # =============================================
    # Progress Bar
    # =============================================

    draw_progress_bar(
        frame,
        system_volume,
        20,
        290,
    )

    # =============================================
    # Guide
    # =============================================

    draw_label(
        frame,
        "ESC : Exit",
        20,
        360,
        color=(200, 200, 200),
    )

    draw_label(
        frame,
        "R : Reset Filter",
        20,
        390,
        color=(200, 200, 200),
    )

    draw_label(
        frame,
        f"Calib : {mapper.min_value:.1f} - {mapper.max_value:.1f} cm",
        20,
        420,
        color=(200, 200, 200),
    )

    draw_label(
        frame,
        "M : set MIN (pinch)   X : set MAX (open)   C : reset",
        20,
        450,
        color=(200, 200, 200),
    )

    # =============================================
    # Status Indicator
    # =============================================

    if detected:
        indicator_color = (
            (0, 255, 0)
            if state_text == "PINCH"
            else (0, 0, 255)
        )
    else:
        indicator_color = (120, 120, 120)

    cv2.circle(
        frame,
        (image_width - 40, 40),
        15,
        indicator_color,
        -1,
    )

    # =============================================
    # Display
    # =============================================

    cv2.imshow(
        WINDOW_NAME,
        frame,
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("m"):

        if detected:

            mapper.min_value = stable

            save_calibration(
                mapper.min_value,
                mapper.max_value,
            )

            print(
                f"MIN volume = {stable:.2f} cm"
            )

        else:

            print("Tangan tidak terdeteksi.")

    elif key == ord("x"):

        if detected:

            mapper.max_value = stable

            save_calibration(
                mapper.min_value,
                mapper.max_value,
            )

            print(
                f"MAX volume = {stable:.2f} cm"
            )

        else:

            print("Tangan tidak terdeteksi.")

    elif key == ord("c"):

        mapper.min_value = PINCH_CM_MIN
        mapper.max_value = PINCH_CM_MAX

        save_calibration(
            mapper.min_value,
            mapper.max_value,
        )

        print(
            f"Calibration reset: "
            f"{PINCH_CM_MIN:.1f} - {PINCH_CM_MAX:.1f} cm."
        )

    elif key == ord("r"):

        gesture.reset()

        smoother_image.reset()
        smoother_world.reset()

        rate_limiter.reset()
        rate_limiter.update(
            audio.get_volume(),
        )

        print("Gesture filter reset.")

    elif key == 27:

        print()

        print("=" * 50)
        print("Exit Gesture Desktop Controller")
        print("=" * 50)

        break


# ==========================================================
# Cleanup
# ==========================================================

cap.release()

cv2.destroyAllWindows()

print("Camera released.")
print("Selesai.")
