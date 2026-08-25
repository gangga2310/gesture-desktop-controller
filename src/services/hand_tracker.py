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