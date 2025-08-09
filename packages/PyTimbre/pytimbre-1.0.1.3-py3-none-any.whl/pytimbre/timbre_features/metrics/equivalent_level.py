from pytimbre.utilities.audio_analysis_enumerations import WeightingFunctions
from pytimbre.audio import Waveform
from pytimbre.spectral.spectra import Spectrum
from pytimbre.spectral.time_histories import SpectralTimeHistory, OverallLevelTimeHistory
from pytimbre.timbre_features.metrics.level import LevelMetrics
from pytimbre.utilities.audio_analysis_enumerations import LeqDurationMode
from typing import Union
import numpy as np
import datetime


class EquivalentLevelMetrics:
    """
    There are multiple ways to create an equivalent level. This class provides access to the methods through the
    different PyTimbre objects that represent the acoustic pressures. This includes a Waveform, Spectrum,
    and TimeHistory.
    """

    def __init__(self):
        """
        A container class for an equivalent sound pressure level, or acoustic energy averaged over some total duration.
        Commonly abbreviated Leq. Often includes the spectral weighting and equivalent duration in the
        abbreviation, e.g., LAeq8hr.
        Examples:

        Represent one half (50%) of a total allowed daily noise exposure
        >>> import numpy as np
        >>> from pytimbre.timbre_features.metrics.equivalent_level import EquivalentLevelMetrics
        >>> leq = EquivalentLevelMetrics(85., datetime.timedelta(hours=4), WeightingFunctions.a_weighted)
        >>> np.round(leq.leq8hr, decimals=1)
        82.0
        >>> np.round(leq.noise_dose_pct, decimals=1)
        49.9

        What is the sound exposure level for a 30-second exposure to an A-weighted SPL of 120 dB?
        >>> leq = EquivalentLevelMetrics(120., datetime.timedelta(seconds=30), WeightingFunctions.a_weighted)
        >>> np.round(leq.sel, decimals=1)
        134.8

        If the logarithmic average SPL of a passing train from a 1-minute recording is 95 dB, what is
        the SPL for the same noise event averaged over 1 hour?
        >>> np.round(EquivalentLevelMetrics._convert_duration(95., 60, 60 * 60), decimals=1)
        77.2
        """

        self._duration = None
        self._weighting = WeightingFunctions.unweighted
        self._waveform = None
        self._spectrum = None
        self._spectrogram = None
        self._overall_level_time_history = None

    @property
    def waveform(self) -> Waveform:
        return self._waveform

    @waveform.setter
    def waveform(self, waveform):
        self._waveform = waveform

    @property
    def spectrum(self) -> Spectrum:
        return self._spectrum

    @spectrum.setter
    def spectrum(self, spectrum):
        self._spectrum = spectrum

    @property
    def spectrogram(self) -> SpectralTimeHistory:
        return self._spectrogram

    @spectrogram.setter
    def spectrogram(self, spectrogram):
        self._spectrogram = spectrogram

    @property
    def level_time_history(self) -> OverallLevelTimeHistory:
        return self._overall_level_time_history

    @level_time_history.setter
    def level_time_history(self, overall_level_time_history: OverallLevelTimeHistory):
        self._overall_level_time_history = overall_level_time_history

    @property
    def weighting(self) -> WeightingFunctions:
        return self._weighting

    @weighting.setter
    def weighting(self, weighting):
        self._weighting = weighting

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration):
        self._duration = duration

    #   ---------------------------------- Level properties to obtain the various levels -------------------------------

    @property
    def sound_exposure_level(self):
        if self.waveform is not None:
            return self._sound_exposure_level_from_waveform
        if self.spectrum is not None:
            return self._sound_exposure_level_from_spectrum
        if self.level_time_history is not None:
            return self._sound_exposure_level_from_level_time_history
        if self.spectrogram is not None:
            return self._sound_exposure_level_from_spectrogram

    @property
    def eight_hour_equivalent_level(self):
        """
        Eight-hour equivalent level, a common metric for quantifying total daily noise exposure.
        :rtype: float
        """

        if self.waveform is not None:
            return self._eight_hour_equivalent_level_from_waveform
        if self.spectrogram is not None:
            return self._eight_hour_equivalent_level_from_spectrogram
        if self.spectrum is not None:
            return self._eight_hour_equivalent_level_from_spectrum
        if self.level_time_history is not None:
            return self._eight_hour_equivalent_level_from_level_time_history

    @property
    def exact_equivalent_level(self):
        """
        This function will integrate the provided acoustic data to the exact duration of the dataset.
        :return: the equivalent level of the data
        :rtype: float or Spectrum
        """

        if self.waveform is not None:
            return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_waveform,
                                                     self.duration,
                                                     self.duration)
        if self.spectrogram is not None:
            return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_spectrogram,
                                                     self.spectrogram.integration_time,
                                                     self.duration)
        if self.level_time_history is not None:
            return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_level_time_history,
                                                     self.duration,
                                                     self.duration)
        if self.spectrum is not None:
            return self.spectrum

    #   ----------------------------------- Helper functions to reduce the cognitive complexity ------------------------
    @property
    def _eight_hour_equivalent_level_from_level_time_history(self):
        """
        This is a helper function that reduces the cognitive complexity of the eight_hour_equivalent_level property
        :return: the eight-hour equivalent level calculated from a OverallLevelTimeHistory
        :rtype: float
        """

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_level_time_history, self.duration, 8 * 3600)

    @property
    def _eight_hour_equivalent_level_from_spectrogram(self):
        """
        This is a helper function that reduces the cognitive complexity of the eight_hour_equivalent_level property
        :return: the eight-hour equivalent level calculated from a SpectralTimeHistory
        :rtype: float
        """

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_spectrogram, self.duration, 8 * 3600)

    @property
    def _eight_hour_equivalent_level_from_spectrum(self):
        """
        This is a helper function that reduces the cognitive complexity of the eight_hour_equivalent_level property
        :return: the eight-hour equivalent level calculated from a spectrum
        :rtype: float
        """
        if self.duration is None:
            raise ValueError("You must specify a duration to calculate equivalent levels with a single spectrum")

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_spectrum, self.duration, 8 * 3600)

    @property
    def _eight_hour_equivalent_level_from_waveform(self):
        """
        This is a helper function that reduces the cognitive complexity of the eight_hour_equivalent_level property
        :return: the eight-hour equivalent level calculated from the waveform
        :rtype: float
        """

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_waveform, self.duration, 8 * 3600)

    @property
    def _sound_exposure_level_from_waveform(self):
        """
        This is a helper function to calculate the sound exposure level (an equivalent level with a 1 second duration)
        from a waveform.
        :return: the 1-sec equivalent level with associated weightings applied
        :rtype: float
        """

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_waveform, self.duration, 1)

    @property
    def _sound_exposure_level_from_spectrum(self):
        """
        This is a helper function to calculate the sound exposure level (an equivalent level with a 1 second duration)
        from a waveform.
        :return: the 1-sec equivalent level with associated weightings applied
        :rtype: float
        """

        if self.duration is None:
            raise ValueError("You must specify a duration to calculate equivalent levels with a single spectrum")

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_spectrum, self.duration, 1)

    @property
    def _sound_exposure_level_from_level_time_history(self):
        """
        This is a helper function to calculate the sound exposure level (an equivalent level with a 1 second duration)
        from a waveform.
        :return: the 1-sec equivalent level with associated weightings applied
        :rtype: float
        """

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_level_time_history, self.duration, 1)

    @property
    def _sound_exposure_level_from_spectrogram(self):
        """
        This is a helper function to calculate the sound exposure level (an equivalent level with a 1 second duration)
        from a waveform.
        :return: the 1-sec equivalent level with associated weightings applied
        :rtype: float
        """

        return EquivalentLevelMetrics._equivalent_level(self._get_equivalent_level_from_spectrogram, self.duration, 8 * 3600)

    @property
    def _get_equivalent_level_from_waveform(self):
        """
        This is a helper function that defines the equivalent level from a waveform to simplfy the SEL and Leq
        calculations
        :return: equivalent level or array of levels
        :rtype: float or list
        """

        level = 0
        if self.weighting == WeightingFunctions.unweighted:
            level = LevelMetrics.from_waveform(self.waveform).overall_level
        elif self.weighting == WeightingFunctions.a_weighted:
            level = LevelMetrics.from_waveform(self.waveform).overall_a_weighted_level
        elif self.weighting == WeightingFunctions.c_weighted:
            level = LevelMetrics.from_waveform(self.waveform).overall_c_weighted_level

        return level

    @property
    def _get_equivalent_level_from_level_time_history(self):
        """
        This is a helper function that defines the equivalent level from a waveform to simplfy the SEL and Leq
        calculations
        :return: equivalent level or array of levels
        :rtype: float or list
        """

        levels = list()

        if self.weighting == WeightingFunctions.unweighted:
            levels = self.level_time_history.metrics['lz']
        elif self.weighting == WeightingFunctions.a_weighted:
            levels = self.level_time_history.metrics['la']
        elif self.weighting == WeightingFunctions.c_weighted:
            levels = self.level_time_history.metrics['lc']

        return levels

    @property
    def _get_equivalent_level_from_spectrogram(self):
        """
        This is a helper function that defines the equivalent level from a waveform to simplfy the SEL and Leq
        calculations
        :return: equivalent level or array of levels
        :rtype: float or list
        """

        lm = LevelMetrics.from_time_history(self.spectrogram)
        levels = list()

        if self.weighting == WeightingFunctions.unweighted:
            levels = lm.overall_level
        elif self.weighting == WeightingFunctions.a_weighted:
            levels = lm.overall_a_weighted_level
        elif self.weighting == WeightingFunctions.c_weighted:
            levels = lm.overall_c_weighted_level

        return levels

    @property
    def _get_equivalent_level_from_spectrum(self):
        """
        This is a helper function that defines the equivalent level from a waveform to simplfy the SEL and Leq
        calculations
        :return: equivalent level or array of levels
        :rtype: float or list
        """


        level = 0
        if self.weighting == WeightingFunctions.unweighted:
            level = LevelMetrics.from_spectrum(self.spectrum).overall_level
        elif self.weighting == WeightingFunctions.a_weighted:
            level = LevelMetrics.from_spectrum(self.spectrum).overall_a_weighted_level
        elif self.weighting == WeightingFunctions.c_weighted:
            level = LevelMetrics.from_spectrum(self.spectrum).overall_c_weighted_level

        return level

    #   -------------------------- static functions for calculating values ---------------------------------------------

    @staticmethod
    def from_waveform(wfm: Waveform):
        eq = EquivalentLevelMetrics()
        eq.waveform = wfm
        eq.duration = wfm.duration
        return eq

    @staticmethod
    def from_spectrum(s: Spectrum, duration):
        eq = EquivalentLevelMetrics()
        eq.spectrum = s
        if isinstance(duration, float):
            eq.duration = duration
        elif isinstance(duration, datetime.timedelta):
            eq.duration = duration.total_seconds()

        return eq

    @staticmethod
    def from_time_history(th: Union[SpectralTimeHistory, OverallLevelTimeHistory]):
        eq = EquivalentLevelMetrics()
        if isinstance(th, SpectralTimeHistory):
            eq.spectrogram = th
            eq.duration = th.duration
        elif isinstance(th, OverallLevelTimeHistory):
            eq.level_time_history = th
            eq.duration = th.duration
        return eq

    #   ----------------------------- Protected helper functions -------------------------------------------------------

    @staticmethod
    def _convert_duration(level: float, tin: float = 1.0, tout: float = 1.0):
        """
        Rescales the energy of a level from one equivalent time duration to another.  The equivalent durations tin
        and tout should be in the same units of time.

        :param level: The sound pressure level representing the total acoustic intensity averaged evenly over the
            equivalent duration tin
        :type level: float
        :param tin: The equivalent duration time of the input level
        :type tin: float
        :param tout: The desired equivalent duration time over which the total acoustic intensity is to be averaged.
        :type tout: float
        :return: The sound pressure level in decibels converted to the new equivalent duration
        :rtype: float
        """
        if isinstance(tin, datetime.timedelta):
            return level + 10 + np.log10(tin.total_seconds() / tout)
        else:
            return level + 10 * np.log10(tin / tout)

    @staticmethod
    def _equivalent_level(level, t_in: float, t_out: float):
        """
        This function computes the equivalent level at the duration defined by t_in and adjusts the time duration
        to the t_out value.
        :param level: The acoustic levels that have already had the weighting applied. If this is an array, a time
        integration is applied.
        :type level: list or float
        :param t_in: the input duration of the acoustic level
        :type t_in: float
        :param t_out: the output duration of the new equivalent level
        :type t_out: float
        :return: the scaled integrated level to the new time
        :rtype: float
        """

        if isinstance(level, float):
            eq_level = level
        elif isinstance(level, list) or isinstance(level, np.ndarray):
            eq_level = 20 * np.log10(np.mean(20e-6 * 10 ** (level / 20)) / 20e-6)
        else:
            eq_level = 0.0

        return EquivalentLevelMetrics._convert_duration(eq_level, t_in, t_out)
