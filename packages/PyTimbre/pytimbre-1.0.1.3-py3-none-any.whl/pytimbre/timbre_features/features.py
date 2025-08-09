from pytimbre.timbre_features.metrics.level import LevelMetrics
from pytimbre.timbre_features.metrics.harmonic import HarmonicMetrics
from pytimbre.timbre_features.metrics.spectral import SpectralMetrics
from pytimbre.timbre_features.metrics.temporal import TemporalMetrics
from pytimbre.timbre_features.metrics.sound_quality import SoundQualityMetrics
from pytimbre.audio import Waveform
from pytimbre.spectral.spectra import Spectrum
from pytimbre.spectral.time_histories import SpectralTimeHistory
import pandas as pd


class TimbreFeatures:
    """
    Since there are many different types of features that exist, we will use this class to determine which features
    are appropriate to use for this analysis. If the system is created from a waveform only, then only the temporal
    and level metrics that can be calculated will be available. If the system is created from a Spectrum, only those
    associated with a sound pressure level spectrum will be available. However, a Spectrum can also contain a
    waveform. So, if a Waveform exists within the Spectrum, the feature available for the Waveform will also be
    added. The same is then true for the time varying time history.
    """

    @staticmethod
    def from_waveform(wfm: Waveform) -> dict:
        """
        This will load the data from the Waveform into the LevelMetrics, TemporalMetrics, and SoundQualityMetrics to
        determine the list of features that are available.
        :param wfm: The audio data to use in the creation of the features
        :type wfm: Waveform
        :return: A dictionary of the features appropriate and available for a Waveform
        :rtype: dict
        """

        lm = LevelMetrics.from_waveform(wfm)
        tm = TemporalMetrics.from_waveform(wfm)
        sqm = SoundQualityMetrics.from_waveform(wfm)

        features = sqm.get_features()
        features.update(tm.get_features())
        features.update(lm.get_features())

        return features

    @staticmethod
    def from_spectra(s: Spectrum) -> dict:
        """
        This function performs a similar analysis and will return the data from the appropriate metrics for a spectrum
        object.
        :param s: The spectral data object
        :type s: Spectrum
        :return: the timbre features calculated on the spectrum and waveform, if contained within the spectrum.
        :rtype: dict
        """

        features = LevelMetrics.from_spectrum(s).get_features()
        features.update(SpectralMetrics.from_spectrum(s).get_features())
        features.update(HarmonicMetrics(s).get_features())
        if s.waveform is not None:
            features.update(TemporalMetrics.from_waveform(s.waveform).get_features())
            features.update(SoundQualityMetrics.from_waveform(s.waveform).get_features())

        return features

    @staticmethod
    def from_time_history(time_history: SpectralTimeHistory) -> pd.DataFrame:
        """
        This will build the collection of features based on a dictionary that was from each of the spectra within the
        TimeHistory object, returned as a DataFrame
        :param time_history:
        :type time_history:
        :return:
        :rtype:
        """

        features = pd.DataFrame()

        for s in time_history.spectra:
            if features.shape[0] == 0:
                features = pd.DataFrame([TimbreFeatures.from_spectra(s)])
            else:
                features = pd.concat([features, pd.DataFrame([TimbreFeatures.from_spectra(s)])])

        return features


class ImpulseFeatures:
    """
    Similar to the TimbreFeatures class, this class provides the information that can be used to represent the
    impulsive acoustics and will not return data for the continuous signals.
    """

    def __init__(self):
        self._waveform = None
        self._spectrum = None
        self._time_history = None

    @staticmethod
    def from_waveform(wfm: Waveform):
        """
        This function will create an instance of the class with the data from the waveform provided to the class
        :param wfm: The impulsive audio data
        :type wfm: Waveform
        :return: The impulse feature class
        :rtype: ImpulseFeatures
        """

        im = ImpulseFeatures()
        im._waveform = wfm

        return wfm

    @staticmethod
    def from_spectra(s: Spectrum):

        im = ImpulseFeatures()
        im._spectrum = s

        return im

    @staticmethod
    def from_time_history(time_history: SpectralTimeHistory):
        im = ImpulseFeatures()
        im._time_history = time_history
        return im

