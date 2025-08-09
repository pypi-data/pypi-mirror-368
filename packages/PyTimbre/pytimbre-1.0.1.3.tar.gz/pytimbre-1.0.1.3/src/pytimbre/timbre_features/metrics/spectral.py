from pytimbre.spectral.spectra import Spectrum
import numpy as np


class SpectralMetrics:
    """
    This class represents spectral metrics from the spectrum.
    """

    def __init__(self):
        """
        This creates the internal representation of the spectral timbre metrics
        """

        self._spectrum = None
        self._centroid = None
        self._probability_distribution = None
        self._integration_variable = None
        self._spread = None
        self._skewness = None
        self._kurtosis = None
        self._slope = None
        self._decrease = None
        self._roll_off = None
        self._energy = None
        self._flatness = None
        self._crest = None
        self._arithmetic_mean = None
        self._geometric_mean = None
        self._mean_center = None

    @property
    def spectral_data(self) -> Spectrum:
        return self._spectrum

    @spectral_data.setter
    def spectral_data(self, spectral_data):
        self._spectrum = spectral_data
        self._integration_variable = self.spectral_data.frequencies

    @property
    def spectral_centroid(self):
        """
        Spectral centroid represents the spectral center of gravity.
        """

        if self._centroid is None:

            if self._probability_distribution is None or self._integration_variable is None:
                self._calculate_normalized_distribution()

            self._centroid = np.sum(self._integration_variable * self._probability_distribution, axis=0)

        return self._centroid

    @property
    def spectral_spread(self):
        """
        Spectral spread or spectral standard-deviation represents the spread of the spectrum around its mean value.
        """
        if self.mean_center is None:
            self._calculate_mean_center()

        if self._probability_distribution is None or self._integration_variable is None:
            self._calculate_normalized_distribution()

        if self._spread is None:
            self._spread = np.sqrt(np.sum(self.mean_center ** 2 * self._probability_distribution, axis=0))

        return self._spread

    @property
    def spectral_skewness(self):
        """
        Spectral skewness gives a measure of the asymmetry of the spectrum around its mean value. A value of 0 indicates
        a symmetric distribution, a value < 0 more energy at frequencies lower than the mean value, and values > 0 more
        energy at higher frequencies.
        """
        if self.mean_center is None:
            self._calculate_mean_center()

        if self._probability_distribution is None or self._integration_variable is None:
            self._calculate_normalized_distribution()

        if self._skewness is None:
            self._skewness = np.sum(self.mean_center ** 3 * self._probability_distribution, axis=0) / \
                             self.spectral_spread ** 3

        return self._skewness

    @property
    def spectral_kurtosis(self):
        """
        Spectral kurtosis gives a measure of the flatness of the spectrum around its mean value. Values approximately 3
        indicate a normal (Gaussian) distribution, values less than 3 indicate a flatter distributions, and values
        greater than 3 indicate a peakier distribution.
        """
        if self.mean_center is None:
            self._calculate_mean_center()

        if self._probability_distribution is None or self._integration_variable is None:
            self._calculate_normalized_distribution()

        if self._kurtosis is None:
            self._kurtosis = np.sum(self.mean_center ** 4 * self._probability_distribution, axis=0) / \
                             self.spectral_spread ** 4

        return self._kurtosis

    @property
    def spectral_slope(self):
        """
        Spectral slope is computed using a linear regression over the spectral amplitude values. It should be noted that
        the spectral slope is linearly dependent on the spectral centroid.
        """

        if self._probability_distribution is None or self._integration_variable is None:
            self._calculate_normalized_distribution()

        if self._slope is None:
            numerator = len(self.spectral_data.frequencies)
            numerator *= self.spectral_data.frequencies.transpose().dot(self._probability_distribution)
            numerator -= np.sum(self.spectral_data.frequencies) * np.sum(self._probability_distribution, axis=0)
            denominator = len(self.spectral_data.frequencies) * sum(self.spectral_data.frequencies ** 2)
            denominator -= np.sum(self.spectral_data.frequencies) ** 2
            self._slope = numerator / denominator

        return self._slope

    @property
    def spectral_decrease(self):
        """
        Spectral decrease was proposed by Krimphoff (1993) in relation to perceptual studies. It averages the set of
        slopes between frequency f[k] and f[1]. It therefore emphasizes the slopes of the lowest frequencies.
        """

        if self._probability_distribution is None or self._integration_variable is None:
            self._calculate_normalized_distribution()

        if self._decrease is None:
            numerator = self._probability_distribution[1:] - self._probability_distribution[0]
            denominator = (1 / np.arange(1, len(self.spectral_data.frequencies)))
            self._decrease = (denominator.dot(numerator)).transpose().reshape((-1,))
            self._decrease /= np.sum(self._probability_distribution[1:], axis=0)

        return self._decrease[0]

    @property
    def spectral_roll_off(self):
        """
        Spectral roll-off was proposed by Scheirer and Slaney (1997). It is defined as the frequency below which 95%
        of the signal energy is contained. The value is returned as the normalized frequency (i.e. you must multiply
        by the sample rate to determine the actual frequency of the roll-off.
        """

        if self._roll_off is None:
            threshold = 0.95
            cum_sum = np.cumsum(self.spectral_data.pressures_pascals, axis=0)
            _sum = np.ones((len(self.spectral_data.frequencies),)) * (
                        threshold * np.sum(self.spectral_data.pressures_pascals))

            _bin = np.cumsum(1 * (cum_sum > _sum), axis=0)
            idx = np.nonzero(_bin == 1)[0]

            self._roll_off = self.spectral_data.frequencies[idx][0]

        return self._roll_off

    @property
    def spectral_energy(self):
        """
        A summation of the energy within the spectrum
        """
        if self._energy is None:
            self._energy = np.sum(self.spectral_data.pressures_pascals ** 2, axis=0)

        return self._energy

    @property
    def spectral_flatness(self):
        """
        Spectral flatness is obtained by comparing the geometrical mean and the arithmetical mean of the spectrum. The
        original formulation first splot the spectrum into various frequency bands (Johnston, 1988). However, in the
        context of timbre characterization, we use a single frequency band covering the whole frequency range. For
        tonal signals, the spectral flatness is close to 0( a peaky spectrum), whereas for noisy signals it is close to
        1 (flat spectrum).
        """

        if self._flatness is None:
            self._geometric_mean = np.exp(
                (1 / len(self.spectral_data.frequencies)) * np.sum(
                    np.log(self.spectral_data.pressures_pascals),
                    axis=0
                )
            )
            self._arithmetic_mean = np.mean(self.spectral_data.pressures_pascals, axis=0)
            self._flatness = self._geometric_mean / self._arithmetic_mean

        return self._flatness

    @property
    def spectral_crest(self):
        """
        The spectral crest measure is obtained by comparing the maximum value and arithmetical mean of the spectrum.
        """

        if self._arithmetic_mean is None:
            self._arithmetic_mean = np.mean(self.spectral_data.pressures_pascals, axis=0)

        if self._crest is None:
            self._crest = np.max(self.spectral_data.pressures_pascals, axis=0) / self._arithmetic_mean

        return self._crest

    @property
    def mean_center(self):
        if self._mean_center is None:
            self._calculate_mean_center()

        return self._mean_center

    @staticmethod
    def from_spectrum(spec: Spectrum):
        """
        This creates an instance of the class and updates the internal representations of the spectral features that
        are calculated for a single spectrum.
        :param spec: the sound pressure level spectrum for the spectral metrics
        :type spec: Spectrum
        :return: the class with the various spectral timbre features
        :rtype: SpectralMetrics
        """
        sm = SpectralMetrics()
        sm.spectral_data = spec

        return sm

    def get_features(self):
        return{"mean_center": self.mean_center,
               "spectral_centroid": self.spectral_centroid,
               "spectral_crest": self.spectral_crest,
               "spectral_decrease": self.spectral_decrease,
               "spectral_energy": self.spectral_energy,
               "spectral_flatness": self.spectral_flatness,
               "spectral_kurtosis": self.spectral_kurtosis,
               "spectral_roll_off": self.spectral_roll_off,
               "spectral_skewness": self.spectral_skewness,
               "spectral_slope": self.spectral_slope,
               "spectral_spread": self.spectral_spread}

    def _calculate_normalized_distribution(self):
        """
        This function updates the internal representation of the energy envelope of the spectrum and normalizes the
        data to a value of 1.
        """
        s = np.sum(self.spectral_data.pressures_pascals, axis=0)
        if s == 0:
            if not np.any(self.spectral_data.pressures_pascals):
                self._probability_distribution = np.array(
                    [1 / self.spectral_data.pressures_pascals.shape[0] for _ in self.spectral_data.pressures_pascals]
                )
            else:
                self._probability_distribution = np.array([np.nan for _ in self.spectral_data.pressures_pascals])
        else:
            self._probability_distribution = self.spectral_data.pressures_pascals / s

    def _calculate_mean_center(self):
        """
        This function determines the average center frequency of the spectrum.
        """
        if self._probability_distribution is None:
            self._calculate_normalized_distribution()

        if self._mean_center is None:
            self._mean_center = self._integration_variable - self.spectral_centroid

        return self._mean_center