from pytimbre.spectral.spectra import Spectrum
import numpy as np


class HarmonicMetrics:
    """
    This class encapsulates the ability of the spectrum to determine harmonic values and return relevant features
    based on the fundamental frequency.
    """

    def __init__(self, s: Spectrum):

        self.pitch_threshold = 0.01
        self.partial_frequencies_indices = None
        self._fundamental_frequency = None
        self._harmonic_energy = None
        self._noise_energy = None
        self._noisiness = None
        self._tri_stimulus = None
        self._harmonic_spectral_deviation = None
        self._odd_even_ratio = None
        self._inharmonicity = None

        self._spectrum = s

        self._calculate_fundamental_frequency()
        self._calculate_partial_pressures()

    @property
    def spectrum(self) -> Spectrum:
        return self._spectrum

    @property
    def pressures_pascals(self):
        return self.spectrum.pressures_pascals

    @property
    def frequencies(self):
        return self.spectrum.frequencies

    @property
    def harmonic_energy(self):
        """
        This is the energy within the signal that is explained by the harmonic partial frequencies and amplitudes. It
        is the square of all the amplitudes determined for the harmonic frequencies.
        """

        if self._harmonic_energy is not None:
            return self._harmonic_energy

        self._harmonic_energy = 0

        for idx in self.partial_frequencies_indices:
            self._harmonic_energy += self.pressures_pascals[idx] ** 2

        return self._harmonic_energy

    @property
    def noise_energy(self):
        """
        This is the energy of the signal not represented by the harmonic frequencies. It is simply the difference
        between the total energy and the energy explained by the harmonics.
        """

        if self._noise_energy is not None:
            return self._noise_energy

        self._noise_energy = np.sum(self.spectrum.pressures_pascals ** 2, axis=0) - self.harmonic_energy

        return self._noise_energy

    @property
    def noisiness(self):
        """
        This is the ratio of the noise energy to the total energy. The higher the noisiness, the more noise-like the
        signal must be.
        """

        if self._noisiness is not None:
            return self._noisiness

        self._noisiness = self.noise_energy / np.sum(self.spectrum.pressures_pascals ** 2, axis=0)

        return self._noisiness

    @property
    def tri_stimulus(self):
        """
        This is a set of values that were first introduced by H. Pollard (Pollard, H. and Jansson, E. (1982) "A
        tristimulus method for the specification of musical timbre," Acustica 51, 162-171) as a timbral equivalent to
        visual color attributes. It is three different energy ratios based on the description of the fundamental
        frequency.
        """
        if self._tri_stimulus is None:

            harmonic_pressure_sum = np.sum(self.pressures_pascals[self.partial_frequencies_indices])
            t01 = self.pressures_pascals[self.partial_frequencies_indices[0]] / harmonic_pressure_sum

            t02 = np.sum(self.pressures_pascals[self.partial_frequencies_indices[1:4]]) / harmonic_pressure_sum
            t03 = np.sum(self.pressures_pascals[self.partial_frequencies_indices[4:]]) / harmonic_pressure_sum

            self._tri_stimulus = [t01, t02, t03]

        return self._tri_stimulus

    @property
    def harmonic_spectral_deviation(self):
        """
        This measures the deviation of the amplitudes of the partials from the harmonics from the global or smoothed
        spectral envelope.
        """
        if self._harmonic_spectral_deviation is None:

            deviations = list()
            self._harmonic_spectral_deviation = 0
            for h in range(1, len(self.partial_frequencies_indices)):
                n = self.partial_frequencies_indices[h] - 1
                m = self.partial_frequencies_indices[h] + 1
                if n < 0:
                    n = 0

                if m >= len(self.pressures_pascals):
                    m = self.partial_frequencies_indices[-1]

                avg_pressure = np.mean(self.pressures_pascals[n:m + 1])
                deviations.append(self.pressures_pascals[self.partial_frequencies_indices[h]] - avg_pressure)

            self._harmonic_spectral_deviation = np.mean(np.array(deviations))

        return self._harmonic_spectral_deviation

    @property
    def odd_even_ratio(self):
        """
        In musical instruments, certain signals contain mostly even (trumpet) or odd (clarinet) harmonics. This ratio
        determines where the system is mostly odd or even.
        """

        import sys

        if self._odd_even_ratio is None:

            odd_energy = 0
            even_energy = 0
            for i in range(1, len(self.partial_frequencies_indices)):
                if (i + 1) % 2 == 0:
                    even_energy += self.pressures_pascals[self.partial_frequencies_indices[i]] ** 2
                else:
                    odd_energy += self.pressures_pascals[self.partial_frequencies_indices[i]] ** 2

            self._odd_even_ratio = odd_energy / (even_energy + sys.float_info.epsilon)

        return self._odd_even_ratio

    @property
    def inharmonicity(self):
        """
        This is a measure of the deviation of the partial frequencies from the purely harmonic frequency.
        """
        if self._inharmonicity is None:

            f0 = self.fundamental_frequency

            if f0 is np.nan:
                self._inharmonicity = np.nan
            else:
                frequency_departure = 0
                for i in range(1, len(self.partial_frequencies_indices)):
                    frequency_departure += (self.frequencies[self.partial_frequencies_indices[i]] - (2 ** i) * f0) * \
                                           self.pressures_pascals[self.partial_frequencies_indices[i]]

                self._inharmonicity = (2 / f0) * frequency_departure / np.sum(
                    self.pressures_pascals[self.partial_frequencies_indices] ** 2
                )

        return self._inharmonicity

    @property
    def fundamental_frequency(self):
        if self._fundamental_frequency is None:
            self._calculate_fundamental_frequency()

        return self._fundamental_frequency

    def get_features(self):
        return {"fundamental_frequency": self.fundamental_frequency,
                "harmonic_energy": self.harmonic_energy,
                "harmonic_spectral_deviation": self.harmonic_spectral_deviation,
                "inharmonicity": self.inharmonicity,
                "noise_energy": self.noise_energy,
                "odd_even_ratio": self.odd_even_ratio,
                'tri_stimulus_01': self.tri_stimulus[0],
                'tri_stimulus_02': self.tri_stimulus[1],
                'tri_stimulus_03': self.tri_stimulus[2],}

    def _calculate_fundamental_frequency(self):
        from pytimbre.spectral.fundamental_frequency import FundamentalFrequencyCalculator

        calculator = FundamentalFrequencyCalculator(frequency_window_size=self.spectrum._fft_size)

        f0 = list()
        f0.append(calculator.fundamental_swipe(self.spectrum))
        if np.any(np.isnan(f0)):
            f0.append(calculator.fundamental_by_peaks(self.spectrum))

        #   Convert the list to an array and remove any Nan values
        f0 = np.asarray(f0)
        f0 = f0[np.logical_not(np.isnan(f0))]

        if len(f0) < 1:
            self._fundamental_frequency = np.nan
        else:
            self._fundamental_frequency = np.median(f0)

    def _calculate_partial_pressures(self):
        """
        We need to locate the partial pressure frequencies and amplitudes by calculating the index of each integer
        multiple of the fundamental frequency.
        """

        #   Determine the ratio of the frequencies to the fundamental frequencies. We want to keep only the values
        #   that are close to a whole integer multiple.
        f_ratio = self.frequencies / self.fundamental_frequency

        #   Using the last ratio, determine the maximum number of partial pressure that might exist within this spectrum
        max_partial_frequencies = int(np.floor(f_ratio[-1]))
        max_power = int(np.floor(np.log(max_partial_frequencies)/np.log(2)))
        pfi = list()
        ratio = 2**np.arange(max_power+1)

        for i in ratio:
            pfi.append(np.nonzero(f_ratio >= i)[0][0])

        self.partial_frequencies_indices = np.array(pfi)