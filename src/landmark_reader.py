import cv2
import mediapipe as mp

from pathlib import Path

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from utils.drawing import (
    draw_point,
    draw_label
)

# =====================================================
# Load Model
# =====================================================

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2
)

detector = vision.HandLandmarker.create_from_options(options)

# =====================================================
# Open Camera
# =====================================================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Gagal membuka kamera")
    exit()

print("Tekan ESC untuk keluar.")

while True:

    success, frame = cap.read()

    if not success:
        break

    # Mirror agar seperti bercermin
    frame = cv2.flip(frame, 1)

    image_height, image_width, _ = frame.shape

    # BGR -> RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    detection_result = detector.detect(mp_image)

    # =====================================================
    # Jika tangan terdeteksi
    # =====================================================

    if detection_result.hand_landmarks:

        for hand_index, hand_landmarks in enumerate(detection_result.hand_landmarks):

            # -----------------------------
            # Left / Right Hand
            # -----------------------------
            handedness = detection_result.handedness[hand_index][0].category_name

            wrist = hand_landmarks[0]

            wrist_x = int(wrist.x * image_width)
            wrist_y = int(wrist.y * image_height)

            draw_label(
                frame,
                handedness,
                wrist_x,
                wrist_y - 20,
                color=(0, 0, 255),
                scale=0.7,
                thickness=2
            )

            # -----------------------------
            # Draw Landmark
            # -----------------------------
            for idx, landmark in enumerate(hand_landmarks):

                x = int(landmark.x * image_width)
                y = int(landmark.y * image_height)

                # Gambar titik
                draw_point(frame, x, y)

                # Nomor landmark
                draw_label(
                    frame,
                    idx,
                    x + 6,
                    y - 6
                )

            # -----------------------------
            # Landmark 8 (Index Finger Tip)
            # -----------------------------
            index_tip = hand_landmarks[8]

            print(
                f"{handedness} | "
                f"Index Tip -> "
                f"x={index_tip.x:.3f}, "
                f"y={index_tip.y:.3f}, "
                f"z={index_tip.z:.3f}"
            )

    cv2.imshow("Landmark Reader", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()