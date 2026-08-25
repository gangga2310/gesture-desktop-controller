"""
Gesture Desktop Controller

Module:
    Landmark Smoother

Description:
    Smooth MediaPipe hand landmarks over time
    using One Euro Filter to reduce visual jitter
    on the reading and the drawn lines.

Author:
    Gangga Prakarsa Miharja
"""

from src.filters.one_euro_filter import OneEuroFilter


class SmoothedLandmark:
    """
    Lightweight landmark object.

    Mirrors the interface of MediaPipe NormalizedLandmark
    so existing code (gesture_utils, drawing) keeps working.
    """

    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class LandmarkSmoother:
    """
    Smooth all landmarks of one hand over time.

    One OneEuroFilter per coordinate (x, y, z)
    for each of the 21 landmarks.
    """

    def __init__(
        self,
        num_landmarks=21,
        min_cutoff=1.0,
        beta=1.0,
        d_cutoff=1.0,
    ):

        self.num_landmarks = num_landmarks

        self._filters = [
            [
                OneEuroFilter(
                    min_cutoff=min_cutoff,
                    beta=beta,
                    d_cutoff=d_cutoff,
                )
                for _ in range(3)
            ]
            for _ in range(num_landmarks)
        ]

    def reset(self):
        """
        Clear all filter states.
        """

        for filters in self._filters:
            for f in filters:
                f.reset()

    def smooth(self, hand_landmarks, t=None):
        """
        Smooth one hand.

        Parameters
        ----------
        hand_landmarks
            MediaPipe hand landmarks
            (21 landmarks with .x, .y, .z attributes).

        t : float | None
            Timestamp in seconds.

        Returns
        -------
        list[SmoothedLandmark]
            21 smoothed landmarks.
        """

        smoothed = []

        for index, landmark in enumerate(hand_landmarks):

            if index >= self.num_landmarks:
                break

            x_filter, y_filter, z_filter = self._filters[index]

            x = x_filter(landmark.x, t)
            y = y_filter(landmark.y, t)
            z = z_filter(landmark.z, t)

            smoothed.append(
                SmoothedLandmark(
                    x=x,
                    y=y,
                    z=z,
                )
            )

        return smoothed
