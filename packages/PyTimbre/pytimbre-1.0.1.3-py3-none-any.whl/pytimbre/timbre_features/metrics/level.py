from pytimbre.spectral.spectra import Spectrum
from pytimbre.audio import Waveform
from pytimbre.spectral.time_histories import SpectralTimeHistory
from pytimbre.utilities.audio_analysis_enumerations import WeightingFunctions, TrimmingMethods
from pytimbre.utilities.acoustic_weights import AcousticWeights
import datetime
import numpy as np


class LevelMetrics:
    """
    This class combines the various level metrics that have existed within the Spectra, TimeHistory, and Waveform
    classes. But as some of these metrics can be calculated from different methods, this class provides a method to
    represent the creation of these levels.
    """

    def __init__(self):
        """
        Create the local copy of all the data that will be provided as properties
        """

        self._overall_level = None
        self._overall_a_weighted_level = None
        self._impulse_analysis_method = None

        #   The objects that contain the underlying data
        self._waveform = None
        self._spectrum = None
        self._time_history = None

    @property
    def waveform(self) -> Waveform:
        return self._waveform

    @property
    def spectrum(self) -> Spectrum:
        return self._spectrum

    @property
    def time_history(self) -> SpectralTimeHistory:
        return self._time_history

    @staticmethod
    def from_waveform(wfm: Waveform):
        """
        This calculates the applicable metrics within the level metric based on the methods that exist within the class
        for the Waveform class.
        :param wfm: The audio data object
        :type wfm: Waveform
        :return: The collection of level metrics that were created from the waveform
        :rtype: LevelMetrics
        """

        lm = LevelMetrics()
        lm._waveform = wfm

        return lm

    @staticmethod
    def from_spectrum(s: Spectrum):
        """
        This function inserts a spectrum object into the class that will be used for the calculation of the various
        metrics.
        :param s: The object containing the sound pressure levels and the frequencies for the waveform
        :type s: Spectrum
        :return: The collection of level metrics organized into the class
        :rtype: LevelMetrics
        """

        lm = LevelMetrics()
        lm._spectrum = s

        return lm

    @staticmethod
    def from_time_history(time_history: SpectralTimeHistory):
        """
        This will put the time history object as the root data object and permit the determination of the elements
        from the contents of the time history.
        :param time_history: The collection of spectra for the calculation of data
        :type time_history: SpectralTimeHistory
        :return: The LevelMetrics object that holds the acoustic data
        :rtype: LevelMetrics
        """

        lm = LevelMetrics()
        lm._time_history = time_history

        return lm

    @staticmethod
    def _overall_level_from_waveform(
            wfm: Waveform,
            integration_time: float = None,
            weighting: WeightingFunctions = WeightingFunctions.unweighted
    ):
        """
        Integrate the levels within the waveform to generate the weighted level. This will permit different weighting
        functions to be applied before the calculation of the overall level.

        Parameters
        ----------
        integration_time: float, default: None - The amount of time that we will collect prior to determining the
            RMS level within the samples.
        weighting: weighting_function, default: unweighted - the weighting to be applied prior to determining the RMS
            value of the signal.

        Returns
        -------
        float, array-like - A collection of the overall levels, with applicable weighting, with the number being equal
            to the int(np.floor(duration / integration_time))

        Revision
        20221007 - FSM - updated the method when the start_time is a datetime rather than a floating point value
        """
        from pytimbre.utilities.audio_filtering import WaveformFilter

        if integration_time is None:
            n = 1
            integration_time = wfm.duration
        else:
            n = int(np.floor(wfm.duration / integration_time))

        if weighting == WeightingFunctions.a_weighted:
            wfm = WaveformFilter.apply_a_weight(wfm)
        elif weighting == WeightingFunctions.c_weighted:
            wfm = WaveformFilter.apply_c_weight(wfm)
        else:
            wfm = Waveform(wfm.samples, wfm.sample_rate, wfm.start_time)
        level = list()

        t0 = wfm.start_time
        if isinstance(t0, datetime.datetime):
            t0 = 60 * (60 * t0.hour + t0.minute) + t0.second + t0.microsecond / 1e6

        for i in range(n):
            subset = wfm.trim(t0, t0 + integration_time, TrimmingMethods.times_absolute)
            level.append(np.std(subset.samples))

            t0 += integration_time

        return 20 * np.log10(np.array(level) / 20e-6)

    @property
    def overall_level(self):
        """
        Overall sound pressure level, unweighted (i.e. flat weighted, Z-weighted).  Calculated as the energetic sum
        of the power spectrum.
        """

        if self._spectrum is not None:
            return AcousticWeights.lf(self._spectrum.pressures_decibels)

        if self._waveform is not None:
            return LevelMetrics._overall_level_from_waveform(self._waveform)

        if self._time_history is not None:
            level = np.zeros((len(self._time_history.spectra),))
            for i in range(len(self._time_history.spectra)):
                level[i] = LevelMetrics.from_spectrum(self._time_history.spectra[i]).overall_level

            return level

    @property
    def overall_a_weighted_level(self):
        """
        A-weighted overall sound pressure level.  Calculated as the energetic sum
        of the A-weighted power spectrum.
        """

        if self._spectrum is not None:
            return AcousticWeights.la(self._spectrum.pressures_decibels, self._spectrum.frequencies)[0]

        if self._waveform is not None:
            return LevelMetrics._overall_level_from_waveform(
                self._waveform, weighting=WeightingFunctions.a_weighted
                )

        if self._time_history is not None:
            level = np.zeros((len(self._time_history.spectra),))
            for i in range(len(self._time_history.spectra)):
                level[i] = LevelMetrics.from_spectrum(self._time_history.spectra[i]).overall_a_weighted_level

            return level

    @property
    def overall_c_weighted_level(self):
        """
        C-weighted overall sound pressure level.  Calculated as the energetic sum
        of the C-weighted power spectrum.
        """

        if self._spectrum is not None:
            return AcousticWeights.lc(self._spectrum.pressures_decibels, self._spectrum.frequencies)[0]

        if self._waveform is not None:
            return LevelMetrics._overall_level_from_waveform(
                self._waveform, weighting=WeightingFunctions.c_weighted
            )

        if self._time_history is not None:
            level = np.zeros((len(self._time_history.spectra),))
            for i in range(len(self._time_history.spectra)):
                level[i] = LevelMetrics.from_spectrum(self._time_history.spectra[i]).overall_c_weighted_level

            return level

    @property
    def perceived_noise_level(self):
        from pytimbre.utilities.fractional_octave_band import FractionalOctaveBandTools as fob

        if self.waveform is not None:
            raise ValueError("You must provide a one-third-octave spectrum to calculate the perceived noise level.")
        if self.spectrum is not None:
            if self.spectrum.is_narrowband_resolution or self.spectrum.fractional_octave_bandwidth != 3:
                raise ValueError("You must provide a fractional octave resolution with 1/3 octave bandwidth")
            else:
                #   The calculation is expecting values from 10 Hz to 10 kHz. So if the spectral levels are not within this
                #   range we need to expand the values by concatenating zeros with the spectral array.
                spl = np.zeros((31,))
                f = self.spectrum.frequencies
                band_nos = np.round(fob.exact_band_number(3, f))

                for tob_band_no in range(10, 41):
                    idx = np.nonzero(band_nos == tob_band_no)[0]

                    if len(idx) != 0:
                        spl[tob_band_no-10] = self.spectrum.pressures_decibels[idx[0]]

                return AcousticWeights.perceived_noise_level(spl)

        if self.time_history is not None and (self.time_history.is_fractional_octave_resolution and
                                              self.time_history.fractional_octave_bandwidth == 3):
            pnl = np.zeros((len(self.time_history.times),))
            for i in range(len(pnl)):
                pnl[i] = LevelMetrics.from_spectrum(self.time_history.spectra[i]).perceived_noise_level

            return pnl

    def get_features(self):
        features = {'lz': self.overall_level,
                'la': self.overall_a_weighted_level,
                'lc': self.overall_c_weighted_level}

        if (self.spectrum is not None and self.spectrum.is_fractional_octave_resolution and
                self.spectrum.fractional_octave_bandwidth) == 3:
            features['pnl'] = self.perceived_noise_level

        return features