import numpy as np
from pytimbre.audio import Waveform
from pytimbre.utilities.audio_analysis_enumerations import TrimmingMethods


class FrameBuilder:
    """
    This class provides a method to store the start and stop samples/times for the Waveform.trim function. It
    overwrites the ability to create the subset of the waveform that is passed to the Spectrum object for the
    creation of the frequency spectrum.
    """

    def __init__(
            self, fs: float = 48000, overlap_pct: float = 0, frame_width_sec: float = 0.25, data_length: int =
            48000
    ):
        """
        This function creates the new windowing function to create the subsets of the Waveform with specific
        increments in the representation. The function is used within the TimeHistory classes to create the subset of
        audio that is passed to the Spectrum object. The length of the subset is defined by the frame_width_sec as a
        duration in seconds. The amount of time that we increment the start time is defined by the relationship
        between the frame width and the overlap.
        :param fs: the sample rate of the waveform
        :type fs: float
        :param overlap_pct: the amount of the frame length that we want the next frame to overlap the current frame
        :type overlap_pct: float
        :param frame_width_sec: the width of the frame in seconds
        :type frame_width_sec: float
        :param data_length: The number of samples in the waveform
        :type data_length: int
        """

        if overlap_pct > 1.0:
            raise ValueError("The percentage must be normalized to 1.0")

        self._sample_rate = fs
        self._overlap_pct = overlap_pct
        self._frame_length_sec = frame_width_sec
        self._s0 = 0
        self._s1 = self.frame_length_samples
        self._length = data_length

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def overlap_percentage(self):
        return self._overlap_pct

    @property
    def frame_length_samples(self):
        return int(np.floor(self._frame_length_sec * self.sample_rate))

    @property
    def overlap_samples(self):
        return self.frame_length_samples * self.overlap_percentage

    @property
    def time_increment(self):
        return self._frame_length_sec * (1 - self.overlap_percentage)

    @property
    def sample_increment(self):
        return int(np.floor(self.time_increment * self.sample_rate))

    @property
    def frame_length_seconds(self):
        return self._frame_length_sec

    @property
    def duration(self):
        return float(self._length) / float(self.sample_rate)

    @property
    def excess_duration(self):
        """
        This is the amount of time that will contain only partial frames
        :return:
        :rtype: float
        """

        return self.frame_length_seconds * self.overlap_percentage

    @property
    def complete_frame_count(self):
        """
        This will determine the number of complete frames (all samples within the frame are filled from the original
        waveform).
        :return: the number of complete frames
        :rtype: int
        """

        return int(np.floor((self.duration - self.excess_duration) / self.time_increment))

    @property
    def start_sample(self):
        return self._s0

    @property
    def stop_sample(self):
        return self._s1

    def get_next_waveform_subset(self, wfm: Waveform):
        """
        This function takes the current starting and ending samples, increments them by the appropriate amount and
        returns the next subset of the waveform. It also increments the internal representation of the start and stop
        samples.
        :return:
            A new waveform that is the next increment in the waveform.
        :rtype: Waveform
        """

        wfm2 = wfm.trim(self._s0, self._s1, method=TrimmingMethods.samples)

        self._s0 += self.sample_increment
        self._s1 = self._s0 + self.frame_length_samples

        return wfm2

    @staticmethod
    def from_waveform(wfm: Waveform, overlap_pct: float = 0, frame_width_sec: float = 0.25):
        return FrameBuilder(wfm.sample_rate, overlap_pct, frame_width_sec, len(wfm.samples))
