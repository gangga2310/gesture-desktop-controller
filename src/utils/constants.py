"""
Application Constants

Gesture Desktop Controller
"""

# ==========================================
# Camera
# ==========================================

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# ==========================================
# Drawing
# ==========================================

LANDMARK_RADIUS = 5

LANDMARK_COLOR = (0, 255, 0)

LABEL_COLOR = (255, 0, 0)

TEXT_SCALE = 0.5

TEXT_THICKNESS = 1

# ==========================================
# Gesture (Relative Geometry)
# ==========================================

# Relative pinch ratio.
# Smaller value = fingers are closer.
PINCH_THRESHOLD = 0.35

# Exponential Moving Average
EMA_ALPHA = 0.25

# Ignore tiny changes after EMA
DEAD_ZONE_THRESHOLD = 0.015

# Expected pinch ratio range
#
# Completely closed hand
MIN_PINCH_RATIO = 0.20

# Completely open hand
MAX_PINCH_RATIO = 1.20

# ==========================================
# Pinch Distance (cm) — world landmarks
# ==========================================

# Pinch threshold in cm (palm plane distance)
PINCH_CM_THRESHOLD = 3.0

# Expected pinch distance range (cm)
# Default awal; bisa dikalibrasi per-user
# lewat tombol M/X di debug_pinch.py
PINCH_CM_MIN = 1.5
PINCH_CM_MAX = 8.0

# Dead zone untuk nilai cm (abaikan perubahan < 1.5 mm)
DEAD_ZONE_CM = 0.15

# Hysteresis band untuk status PINCH (cm)
# PINCH aktif saat < threshold-band, mati saat > threshold+band
HYSTERESIS_BAND_CM = 0.5

# Rate limiter volume (% per detik)
VOLUME_RATE_LIMIT = 40.0

# ==========================================
# Landmark Smoothing (One Euro Filter)
# ==========================================

# Lower min_cutoff  = smoother, but more lag
# Higher beta       = more responsive during fast motion
ONE_EURO_MIN_CUTOFF = 1.0
ONE_EURO_BETA = 1.0
ONE_EURO_D_CUTOFF = 1.0

# ==========================================
# Window
# ==========================================

WINDOW_NAME = "Gesture Desktop Controller"
