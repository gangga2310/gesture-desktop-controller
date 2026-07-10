import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from pathlib import Path

print("=" * 50)
print("Current Working Directory :", Path.cwd())
print("Script Location           :", Path(__file__).resolve())

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

print("Model Path                :", MODEL_PATH)
print("Model Exists              :", MODEL_PATH.exists())
print("=" * 50)

# ===========================
# Load Model
# ===========================

base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2
)

detector = vision.HandLandmarker.create_from_options(options)

# ===========================
# Open Camera
# ===========================

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera gagal dibuka")
    exit()

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:

        print("Hand detected :", len(detection_result.hand_landmarks))

    cv2.imshow("Hand Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()