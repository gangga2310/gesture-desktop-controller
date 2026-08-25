Tentu. Berikut **konteks lengkap yang bisa langsung kamu copy-paste ke AI lain**. Aku susun agar AI tersebut bisa melanjutkan project tanpa mengulang pembahasan dari awal.

---

# KONTEKS PROJECT — GestureDesktopController

Saya sedang mengembangkan project Python bernama **GestureDesktopController**.

## 1. Tujuan utama project

Tujuan utama project adalah membuat aplikasi Windows yang dapat **mengontrol volume menggunakan gesture tangan melalui webcam**.

Target akhirnya:

```text
Webcam
   ↓
MediaPipe Hand Landmarker
   ↓
Hand Landmarks
   ↓
Gesture Recognition
   ↓
Pinch Gesture
   ↓
Filtering / Stabilization
   ↓
Volume Mapping
   ↓
Windows Audio API
   ↓
Volume Windows berubah
```

Untuk tahap awal, saya ingin menyelesaikan **Milestone 1: simulasi kontrol volume melalui gesture pinch** terlebih dahulu.

Setelah simulasi stabil, baru menghubungkan hasilnya ke volume Windows menggunakan `pycaw`.

---

# 2. Background saya

Saya masih relatif awam dalam programming, jadi ketika memberikan instruksi yang berhubungan dengan kode:

* berikan **kode lengkap**, bukan hanya potongan kecil;
* jelaskan file mana yang harus dibuat/diubah;
* jangan mengasumsikan saya sudah mengetahui perubahan yang harus dilakukan;
* jangan terlalu lama melakukan refactoring/penataan project jika tidak diperlukan;
* fokus pada tujuan utama: **gesture → volume**.

Jika menyuruh menjalankan sesuatu, berikan perintah terminal yang jelas.

Tidak perlu menyuruh saya melakukan Git commit setiap kali melakukan perubahan kode. Commit hanya dilakukan jika memang relevan.

---

# 3. Environment

OS:

```text
Windows
```

Python:

```text
Python 3.12.4
```

Virtual environment:

```text
venv
```

Saya menjalankan project dari:

```text
C:\Users\USER\Documents\Project\Prog\GestureDesktopController
```

Terminal menggunakan PowerShell.

Contoh prompt:

```text
(venv) (base) PS C:\Users\USER\Documents\Project\Prog\GestureDesktopController>
```

Untuk menjalankan module dari root project:

```powershell
python -m src.debug.debug_pinch
```

---

# 4. Hardware

Laptop:

```text
AMD Ryzen 5 5600H
Radeon RX 5500
RAM 16 GB
```

Webcam digunakan sebagai input gesture.

---

# 5. Library utama

Project menggunakan:

```text
MediaPipe 0.10.35
OpenCV
NumPy
PySide6
pycaw
comtypes
pytest
```

`requirements.txt` saat ini:

```text
absl-py==2.5.0
certifi==2026.6.17
cffi==2.1.0
comtypes==1.4.16
contourpy==1.3.3
cycler==0.12.1
flatbuffers==25.12.19
fonttools==4.63.0
kiwisolver==1.5.0
matplotlib==3.11.0
mediapipe==0.10.35
numpy==2.5.1
opencv-contrib-python==5.0.0.93
opencv-python==5.0.0.93
packaging==26.2
pillow==12.3.0
psutil==7.2.2
pycaw==20251023
pycparser==3.0
pyparsing==3.3.2
PySide6==6.11.1
PySide6_Addons==6.11.1
PySide6_Essentials==6.11.1
python-dateutil==2.9.0.post0
shiboken6==6.11.1
six==1.17.0
sounddevice==0.5.5
```

---

# 6. Struktur project saat ini

Root:

```text
GestureDesktopController/
│
├── .github/
├── .pytest_cache/
├── .vscode/
├── assets/
├── docs/
├── models/
├── src/
├── tests/
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

Di dalam `src`:

```text
src/
│
├── debug/
├── filters/
├── gesture/
├── services/
├── utils/
│
├── __init__.py
├── app_selector.py
├── hand_detect.py
├── landmark_reader.py
└── volume_control.py
```

`utils`:

```text
src/utils/
│
├── __init__.py
├── constants.py
├── drawing.py
├── geometry.py
├── gesture_utils.py
├── math_utils.py
└── windows_audio.py
```

Folder lainnya sudah memiliki beberapa file dari tahap project sebelumnya.

Saya juga pernah menjalankan:

```powershell
tree /F /A > docs\architecture.md
```

tetapi hasilnya sangat panjang, sekitar 12.059 baris karena termasuk file-file yang tidak relevan seperti cache/venv dan sebagainya.

---

# 7. Struktur yang sedang diarahkan

Arsitektur yang ingin dipakai:

```text
src/
│
├── debug/
│   ├── __init__.py
│   ├── debug_pinch.py
│   ├── debug_rotate.py
│   ├── debug_fist.py
│   └── debug_audio.py
│
├── gesture/
│   ├── __init__.py
│   ├── pinch.py
│   ├── rotate.py
│   ├── fist.py
│   └── swipe.py
│
├── filters/
│   ├── __init__.py
│   ├── ema_filter.py
│   └── dead_zone.py
│
├── services/
│   └── hand_tracker.py
│
├── utils/
│   ├── __init__.py
│   ├── constants.py
│   ├── drawing.py
│   ├── geometry.py
│   ├── gesture_utils.py
│   ├── math_utils.py
│   └── windows_audio.py
│
└── main.py
```

Selain itu masih terdapat file lama:

```text
app_selector.py
hand_detect.py
landmark_reader.py
volume_control.py
```

yang belum semuanya dipakai dalam pipeline baru.

---

# 8. MediaPipe model

Model:

```text
models/hand_landmarker.task
```

`HandTracker` menggunakan MediaPipe Tasks API.

---

# 9. HandTracker saat ini

File:

```text
src/services/hand_tracker.py
```

Isi saat ini:

```python
"""
Gesture Desktop Controller

Module:
    Hand Tracker

Description:
    Reusable MediaPipe Hand Landmarker service.

Author:
    Gangga Prakarsa Miharja
"""

from pathlib import Path

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker:
    """
    Wrapper for MediaPipe Hand Landmarker.
    """

    def __init__(
        self,
        model_path=None,
        num_hands=2,
    ):
        """
        Initialize MediaPipe Hand Landmarker.

        Parameters
        ----------
        model_path : str | Path | None
            Path to hand_landmarker.task.
            If None, use default project model.

        num_hands : int
            Maximum number of hands.
        """

        if model_path is None:
            model_path = (
                Path(__file__).resolve().parent.parent.parent
                / "models"
                / "hand_landmarker.task"
            )

        base_options = python.BaseOptions(
            model_asset_path=str(model_path)
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=num_hands,
        )

        self.detector = (
            vision.HandLandmarker.create_from_options(
                options
            )
        )

    def detect(self, frame):
        """
        Detect hands from a BGR OpenCV frame.

        Parameters
        ----------
        frame : numpy.ndarray

        Returns
        -------
        mediapipe.tasks.python.vision.HandLandmarkerResult
        """

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb,
        )

        return self.detector.detect(mp_image)
```

HandTracker sudah berhasil digunakan oleh `debug_pinch.py`.

---

# 10. Geometry

File:

```text
src/utils/geometry.py
```

Isi:

```python
"""
Geometry Utilities

Reusable mathematical functions
for Computer Vision.
"""

import math


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


def midpoint(point1, point2):
    """
    Titik tengah.
    """

    return (
        (point1[0] + point2[0]) / 2,
        (point1[1] + point2[1]) / 2,
    )


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
    Mapping suatu nilai
    dari satu range
    ke range lainnya.
    """

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
```

---

# 11. Gesture utilities

File:

```text
src/utils/gesture_utils.py
```

Saat ini:

```python
"""
Gesture Utilities

Utility functions untuk mengenali gesture tangan.

Author:
    Gangga Prakarsa Miharja
"""

from src.utils.geometry import distance


THUMB_TIP = 4

INDEX_FINGER_MCP = 5
INDEX_FINGER_TIP = 8

PINKY_MCP = 17


def get_landmark(
    hand_landmarks,
    landmark_id,
):
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
    landmark = hand_landmarks[landmark_id]

    return (
        int(landmark.x * image_width),
        int(landmark.y * image_height),
    )


def hand_scale(
    hand_landmarks,
):
    """
    Hand scale is currently:

    Index MCP ↔ Pinky MCP
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
    if scale <= 0:
        return 0.0

    return distance(
        point_a,
        point_b,
    ) / scale


def pinch_ratio(
    hand_landmarks,
):
    """
    thumb-index distance divided by
    index MCP-pinky MCP distance.
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
    Pixel distance for visualization/debugging only.
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
    ratio = pinch_ratio(
        hand_landmarks,
    )

    return ratio <= threshold
```

---

# 12. EMA Filter

File:

```text
src/filters/ema_filter.py
```

Isi:

```python
"""
EMA Filter

Reusable Exponential Moving Average (EMA) filter
for smoothing noisy values.

Author:
    Gangga Prakarsa Miharja
"""


class EMAFilter:
    """
    Exponential Moving Average filter.
    """

    def __init__(self, alpha=0.2):
        if not (0.0 < alpha <= 1.0):
            raise ValueError(
                "alpha must be in range (0.0, 1.0]"
            )

        self.alpha = alpha
        self._value = None

    @property
    def value(self):
        return self._value

    def reset(self):
        self._value = None

    def update(self, measurement):

        if self._value is None:
            self._value = measurement
            return self._value

        self._value = (
            self.alpha * measurement
            + (1.0 - self.alpha) * self._value
        )

        return self._value
```

Test:

```text
tests/test_ema_filter.py
```

Hasil:

```text
10 passed
```

Command:

```powershell
pytest tests/test_ema_filter.py -v
```

Semua PASS.

---

# 13. Dead Zone Filter

File:

```text
src/filters/dead_zone.py
```

Isi:

```python
"""
Gesture Desktop Controller

Module:
    Dead Zone Filter

Description:
    Filter to ignore small changes in signal values.
    Useful for reducing jitter after EMA filtering.

Author:
    Gangga Prakarsa Miharja
"""


class DeadZoneFilter:
    """
    Dead Zone Filter.

    Small changes below the threshold
    will be ignored.
    """

    def __init__(self, threshold=0.01):

        if threshold <= 0:
            raise ValueError(
                "threshold must be greater than 0."
            )

        self.threshold = threshold
        self._value = None

    @property
    def value(self):
        return self._value

    def reset(self):
        self._value = None

    def update(self, value):

        if self._value is None:
            self._value = value
            return value

        if abs(value - self._value) < self.threshold:
            return self._value

        self._value = value

        return self._value
```

Test:

```text
tests/test_dead_zone.py
```

Hasil:

```text
8 passed
```

Command:

```powershell
pytest tests/test_dead_zone.py -v
```

Semua PASS.

---

# 14. GestureState

`PinchGesture` menggunakan:

```python
from src.gesture.gesture_state import GestureState
```

Jadi project memiliki/direncanakan memiliki:

```text
src/gesture/gesture_state.py
```

dengan state:

```text
raw_value
filtered_value
stable_value
detected
```

---

# 15. PinchGesture

File:

```text
src/gesture/pinch.py
```

Versi yang sedang digunakan:

```python
"""
Gesture Desktop Controller

Module:
    Pinch Gesture

Description:
    Process raw pinch ratio into a stable gesture state.

Author:
    Gangga Prakarsa Miharja
"""

from src.filters.ema_filter import EMAFilter
from src.filters.dead_zone import DeadZoneFilter

from src.gesture.gesture_state import GestureState

from src.utils.constants import (
    PINCH_THRESHOLD,
    EMA_ALPHA,
    DEAD_ZONE_THRESHOLD,
)


class PinchGesture:
    """
    Process pinch gesture signal.

    Pipeline
    --------
    Raw Ratio
        ↓
    EMA Filter
        ↓
    Dead Zone
        ↓
    GestureState
    """

    def __init__(
        self,
        threshold=PINCH_THRESHOLD,
        ema_alpha=EMA_ALPHA,
        dead_zone=DEAD_ZONE_THRESHOLD,
    ):

        self.threshold = threshold

        self.ema = EMAFilter(
            alpha=ema_alpha,
        )

        self.dead_zone = DeadZoneFilter(
            threshold=dead_zone,
        )

    def reset(self):

        self.ema.reset()
        self.dead_zone.reset()

    def process(
        self,
        raw_ratio,
    ):

        filtered = self.ema.update(
            raw_ratio,
        )

        stable = self.dead_zone.update(
            filtered,
        )

        detected = stable <= self.threshold

        return GestureState(
            raw_value=raw_ratio,
            filtered_value=filtered,
            stable_value=stable,
            detected=detected,
        )
```

---

# 16. Constants

File:

```text
src/utils/constants.py
```

Saat ini berisi:

```python
"""
Application Constants

Gesture Desktop Controller
"""


CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720


LANDMARK_RADIUS = 5

LANDMARK_COLOR = (0, 255, 0)

LABEL_COLOR = (255, 0, 0)

TEXT_SCALE = 0.5

TEXT_THICKNESS = 1


PINCH_THRESHOLD = 40

FIST_THRESHOLD = 60

ROTATE_THRESHOLD = 25


WINDOW_NAME = "Gesture Desktop Controller"
```

Catatan penting:

`PINCH_THRESHOLD = 40` terlihat berasal dari project lama dan **tidak konsisten** dengan `pinch_ratio()` yang menggunakan nilai normalized ratio seperti `0.35`.

`pinch.py` juga mengharapkan:

```python
EMA_ALPHA
DEAD_ZONE_THRESHOLD
```

Jadi konstanta project masih perlu dirapikan.

Jangan langsung mengubah banyak hal sebelum memahami konteks ini.

---

# 17. Drawing

File:

```text
src/utils/drawing.py
```

Isi:

```python
import cv2


def draw_point(frame, x, y, color=(0, 255, 0), radius=5):
    cv2.circle(
        frame,
        (x, y),
        radius,
        color,
        -1
    )


def draw_label(frame, text, x, y,
               color=(255, 0, 0),
               scale=0.5,
               thickness=1):

    cv2.putText(
        frame,
        str(text),
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness
    )


def draw_line(frame, start, end,
              color=(255, 255, 255),
              thickness=2):

    cv2.line(
        frame,
        start,
        end,
        color,
        thickness
    )
```

---

# 18. Debug Pinch

File:

```text
src/debug/debug_pinch.py
```

Sudah berhasil dibuat dan **sudah berhasil dijalankan**.

Pipeline:

```text
Camera
 ↓
HandTracker
 ↓
Pinch Ratio
 ↓
EMA
 ↓
Dead Zone
 ↓
Volume Simulation
```

Debug menampilkan:

* webcam
* landmark thumb/index
* garis pinch
* pixel distance
* FPS
* hand detected/not detected
* gesture OPEN/PINCH
* Raw Ratio
* EMA Ratio
* Stable Ratio
* simulated volume
* progress bar

Kontrol:

```text
R   = reset filter
ESC = exit
```

Menjalankannya:

```powershell
python -m src.debug.debug_pinch
```

Program **sudah berhasil berjalan tanpa error**.

Output terminal:

```text
============================================================
Gesture Desktop Controller
Debug Pinch
============================================================
R : Reset Filter
ESC : Exit
============================================================

==================================================
Exit Debug Pinch
==================================================
Camera released.
Debug finished.
```

MediaPipe juga mengeluarkan warning seperti:

```text
Feedback manager requires a model with a single signature inference.
```

dan:

```text
Using NORM_RECT without IMAGE_DIMENSIONS is only supported for the square ROI.
```

Namun program tetap berjalan.

---

# 19. Masalah yang ditemukan saat debug

Saat melakukan pinch:

```text
ibu jari + telunjuk bertemu
```

volume justru naik.

Awalnya mapping:

```python
volume = map_range(
    stable,
    0.20,
    1.20,
    100,
    0,
)
```

Kemudian arah dibalik sesuai preferensi saya menjadi:

```python
volume = map_range(
    stable,
    0.20,
    1.20,
    0,
    100,
)
```

Sehingga konsep yang diinginkan sekarang:

```text
Pinch penuh
→ volume rendah / 0%

Tangan terbuka
→ volume tinggi / 100%
```

Saya sudah melakukan pembalikan arah tersebut.

---

# 20. Masalah kedua: range volume

Ditemukan bahwa:

* ketika ibu jari dan telunjuk benar-benar bertemu, volume hanya sekitar **25–40%**, bukan 0%;
* ketika ibu jari dan telunjuk berjarak kurang lebih 2 cm, volume sudah mencapai 100%.

Awalnya kita mencoba menentukan `min_ratio` dan `max_ratio` secara manual.

Tetapi saya menemukan masalah lebih penting:

> Nilai raw/stable berubah berdasarkan jarak tangan terhadap kamera.

Semakin jauh tangan dari kamera, ratio cenderung berubah/membesar; semakin dekat, berubah/mengecil.

Walaupun `pinch_ratio()` sudah menggunakan:

```text
thumb-index distance
--------------------
index MCP-pinky MCP distance
```

yang secara teori scale-invariant, dalam praktik masih ada perubahan akibat:

* perspektif kamera,
* perubahan pose tangan,
* rotasi tangan,
* perubahan landmark,
* noise MediaPipe,
* perubahan bentuk tangan relatif terhadap kamera.

Karena itu kita memutuskan **jangan langsung melakukan kalibrasi min/max**.

---

# 21. VolumeMapper

Tahap 2 yang direncanakan:

buat:

```text
src/utils/volume_mapper.py
```

Tujuannya:

```text
stable ratio
     ↓
VolumeMapper
     ↓
0–100%
```

Konsep awal:

```python
class VolumeMapper:
    def __init__(
        self,
        min_ratio=0.35,
        max_ratio=0.85,
    ):
        ...
```

Tetapi **belum benar-benar diselesaikan/diuji**.

Jangan menganggap `0.35` dan `0.85` sebagai nilai final. Nilai tersebut hanya contoh awal dan sudah diragukan karena masalah jarak kamera.

---

# 22. Hysteresis

Tahap 3 yang direncanakan:

mengganti/meningkatkan mekanisme Dead Zone menjadi **Hysteresis Filter** agar pembacaan tidak mudah bolak-balik karena noise kecil.

Belum dikerjakan.

---

# 23. Rate Limiter

Tahap 4 yang direncanakan:

Tambahkan Rate Limiter setelah filtering supaya perubahan volume tidak melonjak terlalu cepat.

Konsep:

```text
50%
↓
52%
↓
54%
↓
56%
↓
...
```

bukan:

```text
50%
↓
80%
```

Belum dikerjakan.

---

# 24. Perubahan roadmap terbaru

Setelah menyadari bahwa ratio masih terpengaruh jarak kamera, kita **menunda VolumeMapper, Hysteresis, dan Rate Limiter**.

Roadmap terbaru:

```text
debug_pinch.py
       ↓
Hand Scale Analyzer
       ↓
Cari scale/reference yang paling stabil
       ↓
Perbaiki gesture_utils.py
       ↓
VolumeMapper
       ↓
Hysteresis
       ↓
Rate Limiter
       ↓
Windows Audio
```

---

# 25. Langkah berikutnya yang HARUS dilakukan

Kita ingin membuat:

```text
src/debug/debug_hand_scale.py
```

Tujuannya **bukan aplikasi final**.

File ini adalah alat riset/debug untuk membandingkan beberapa kandidat hand scale.

Kita ingin mengukur beberapa kemungkinan reference scale, misalnya:

### Scale A

```text
Index MCP ↔ Pinky MCP
```

Saat ini digunakan oleh `hand_scale()`.

### Scale B

```text
Wrist ↔ Middle MCP
```

### Scale C

```text
Wrist ↔ Middle Tip
```

### Scale D

Referensi palm lainnya yang masuk akal.

Tujuannya adalah melihat mana yang paling stabil ketika:

1. tangan dekat kamera;
2. tangan sedang;
3. tangan jauh;
4. tangan melakukan pinch;
5. tangan terbuka.

Debug analyzer harus menampilkan nilai-nilai tersebut secara real time sehingga saya bisa menggerakkan tangan maju-mundur dan melihat perubahan.

---

# 26. Kenapa kita melakukan Hand Scale Analyzer?

Karena kita tidak ingin "menambal" masalah dengan filter.

Jika raw ratio memang berubah karena reference scale kurang bagus:

```text
Raw Ratio
 ↓
EMA
 ↓
Hysteresis
 ↓
Rate Limiter
```

hanya menyembunyikan masalah.

Kita ingin terlebih dahulu mendapatkan input gesture yang secara geometris lebih stabil.

---

# 27. Arsitektur yang diinginkan

Untuk jangka panjang:

```text
MediaPipe
    ↓
HandTracker
    ↓
gesture_utils
    ↓
Gesture class
    ↓
Filters
    ↓
Mapper
    ↓
Action / Service
```

Untuk pinch:

```text
HandTracker
    ↓
landmarks
    ↓
pinch_ratio
    ↓
PinchGesture
    ↓
EMA
    ↓
Hysteresis
    ↓
RateLimiter
    ↓
VolumeMapper
    ↓
WindowsAudio
```

---

# 28. Windows Audio

File:

```text
src/utils/windows_audio.py
```

Saat ini **masih kosong**.

Project sudah memiliki:

```text
pycaw
comtypes
```

di requirements.

Target akhirnya:

```text
VolumeMapper
    ↓
WindowsAudio
    ↓
pycaw
    ↓
Windows Master Volume
```

Tetapi **belum boleh dikerjakan sebelum gesture simulation stabil**.

---

# 29. volume_control.py

Di root `src` sudah ada:

```text
src/volume_control.py
```

Ini merupakan file lama/project sebelumnya.

Belum diputuskan apakah akan dipakai atau digantikan dengan arsitektur baru.

Jangan membuat duplikasi logic tanpa alasan.

---

# 30. main.py

`main.py` tetap direncanakan sebagai entry point aplikasi final:

```text
src/main.py
```

Namun sekarang fokus masih pada debug.

Kita sepakat bahwa:

```text
debug_pinch.py
```

digunakan untuk menguji gesture.

Sedangkan:

```text
main.py
```

baru digunakan setelah pipeline stabil.

---

# 31. Prinsip pengembangan project

Saya ingin project ini tetap fokus.

**Tujuan utama:**

> membuat aplikasi kontrol volume Windows menggunakan pinch gesture.

Jangan terlalu lama menghabiskan waktu untuk:

* refactoring arsitektur yang belum dibutuhkan;
* membuat dokumentasi berlebihan;
* membuat terlalu banyak abstraksi;
* memindahkan file hanya demi estetika.

Namun struktur tetap harus cukup bersih agar nanti:

```text
pinch
rotate
fist
swipe
```

bisa dikembangkan.

---

# 32. Testing

Pytest sudah terpasang dan berjalan.

Test EMA:

```powershell
pytest tests/test_ema_filter.py -v
```

hasil:

```text
10 passed
```

Test Dead Zone:

```powershell
pytest tests/test_dead_zone.py -v
```

hasil:

```text
8 passed
```

Ketika membuat filter baru seperti Hysteresis dan RateLimiter, sebaiknya buat unit test juga.

---

# 33. GitHub

Repository project:

```text
github.com/gangga2310/gesture-dekstop-controller
```

Saya tidak ingin setiap perubahan kecil selalu disuruh commit.

Jika memang ada milestone penting, boleh sarankan commit.

---

# 34. Kesalahan yang sudah terjadi

Beberapa hal yang perlu diingat agar tidak terulang:

### Import test EMA

Awalnya test mengarah ke:

```python
from src.utils.ema_filter import EMAFilter
```

Padahal file berada di:

```text
src/filters/ema_filter.py
```

Akhirnya diperbaiki.

Hal yang sama harus diperhatikan untuk Dead Zone.

---

### Virtual environment

Prompt:

```text
(venv) (base) PS ...
```

berarti venv sudah aktif.

Jangan mengetik:

```powershell
python (venv) python -m ...
```

Yang benar:

```powershell
python -m src.debug.debug_pinch
```

---

# 35. Instruksi untuk AI berikutnya

Saya ingin AI berikutnya **melanjutkan dari konteks ini**, bukan mengulang dari awal.

Prioritas saat ini:

## LANGKAH SEKARANG

Buat:

```text
src/debug/debug_hand_scale.py
```

yang:

1. memakai `HandTracker`;
2. membaca satu tangan;
3. menghitung beberapa kandidat hand scale;
4. menampilkan nilai scale dan/atau ratio;
5. memungkinkan saya menggerakkan tangan mendekat dan menjauh dari kamera;
6. membantu menentukan reference scale yang paling stabil.

**Berikan kode lengkap `debug_hand_scale.py`**, bukan potongan kode.

Setelah saya menjalankannya dan memberikan hasil pengukuran, bantu saya memilih scale terbaik.

**Jangan langsung membuat Hysteresis, RateLimiter, Windows Audio, atau refactor besar sebelum tahap Hand Scale Analyzer selesai.**

Setelah scale stabil:

```text
Hand Scale
 ↓
pinch_ratio()
 ↓
VolumeMapper
 ↓
Hysteresis
 ↓
RateLimiter
 ↓
WindowsAudio / pycaw
```

Target akhirnya tetap:

> **mengontrol volume Windows dengan pinch gesture melalui webcam.**

---

## STATUS PROJECT SAAT INI

```text
[✓] Project structure
[✓] MediaPipe HandTracker
[✓] Geometry utilities
[✓] Gesture utilities
[✓] EMA Filter
[✓] EMA unit tests — 10/10
[✓] Dead Zone Filter
[✓] Dead Zone unit tests — 8/8
[✓] PinchGesture
[✓] debug_pinch.py
[✓] Webcam + pinch detection berjalan
[✓] EMA + Dead Zone terintegrasi
[✓] Simulasi volume berjalan
[✓] Arah volume sudah dibalik:
       pinch → volume rendah
       open  → volume tinggi

[~] Raw ratio masih terpengaruh jarak kamera
[ ] Hand Scale Analyzer ← **POSISI SEKARANG**
[ ] Pilih reference scale terbaik
[ ] Perbaiki pinch_ratio
[ ] VolumeMapper
[ ] Hysteresis Filter
[ ] Rate Limiter
[ ] Windows Audio / pycaw
[ ] Integrasi final main.py
[ ] Packaging
```

**Milestone 1 belum selesai**, tetapi pipeline gesture dasar sudah berhasil berjalan.
