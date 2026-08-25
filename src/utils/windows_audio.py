"""
Gesture Desktop Controller

Module:
    Windows Audio

Description:
    Control Windows master volume using pycaw.

Author:
    Gangga Prakarsa Miharja
"""

from pycaw.pycaw import AudioUtilities


class WindowsAudio:
    """
    Wrapper for Windows master volume (pycaw).

    Uses AudioDevice.EndpointVolume property
    (lazy-loads the IAudioEndpointVolume interface).
    """

    def __init__(self):
        """
        Initialize the default audio endpoint.
        """

        device = AudioUtilities.GetSpeakers()

        self._volume = device.EndpointVolume

    def get_volume(self):
        """
        Current master volume.

        Returns
        -------
        float
            0.0 - 100.0
        """

        scalar = (
            self._volume.GetMasterVolumeLevelScalar()
        )

        return scalar * 100.0

    def set_volume(self, percent):
        """
        Set master volume.

        Parameters
        ----------
        percent : float
            0.0 - 100.0
        """

        percent = max(
            0.0,
            min(
                100.0,
                percent,
            ),
        )

        self._volume.SetMasterVolumeLevelScalar(
            percent / 100.0,
            None,
        )

    def get_mute(self):
        """
        True if master volume is muted.
        """

        return bool(
            self._volume.GetMute()
        )

    def set_mute(self, muted):
        """
        Mute/unmute master volume.
        """

        self._volume.SetMute(
            bool(muted),
            None,
        )
