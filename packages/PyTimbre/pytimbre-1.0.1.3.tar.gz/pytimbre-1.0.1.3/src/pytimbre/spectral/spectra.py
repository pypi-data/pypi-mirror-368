import warnings
import datetime
import numpy as np
import scipy.fft
import scipy.signal
from pytimbre.utilities.fractional_octave_band import FractionalOctaveBandTools as fob_tools
from pytimbre.audio import Waveform

__docformat__ = 'reStructuredText'


class Spectrum:
    """
    This is the base class that defines the structure of the spectrum object. It does not calculate the frequency
    spectrum from a waveform, but can be used to represent a single spectrum that was previously created.

    Example
    -------
    Make a simple Spectrum object, spec, with a spike at 2 Hz of 10 pascals

    >>> from pytimbre.spectral.spectra import Spectrum

    >>> f = np.arange(0, 5)
    >>> p = np.zeros(len(f))
    >>> p[f == 2] = 10

    >>> spec = Spectrum()
    >>> spec.frequencies = f
    >>> spec.pressures_pascals = p

    >>> print(spec.pressures_pascals)
    [ 0.  0. 10.  0.  0.]

    Remarks::

    2022-12-13 - FSM - Added a function to calculate the sound quality metrics based on the frequency spectrum
    """

    def __init__(self, a: Waveform = None, pressures=None, frequencies=None):
        """
        The default constructor that builds the information within the Spectrum class based on the contents of the
        object "a".

        Parameters
        ----------
        :param a: Waveform - the acoustic samples that define the source of the time-domain information that we are interested
            in processing
        """

        self._waveform = a
        self._frequencies = frequencies
        self._acoustic_pressures_pascals = pressures
        if a is not None:
            if isinstance(self.waveform.start_time, float):
                self._time0 = self.waveform.start_time + self.waveform.duration
            elif isinstance(self.waveform.start_time, datetime.datetime):
                self._time0 = self.waveform.start_time + datetime.timedelta(seconds=self.waveform.duration)
        else:
            self._time0 = None

        #   Fractional octave properties
        self._bandwidth = None
        self._f0 = None
        self._f1 = None

        #   Narrowband properties
        self._fft_size = None
        self._frequencies_double_sided = None
        self._frequencies_nb = None
        self._pressures_double_sided_complex = None

    def __len__(self):
        return len(self.frequencies)

    #   ------------------------------------- Class properties ---------------------------------------------------------

    @property
    def waveform(self):
        if self._waveform is None:
            warnings.warn('No Waveform object has been passed to this Spectrum object.')
        return self._waveform

    @property
    def signal(self):
        return self.waveform.samples

    @property
    def sample_rate(self):
        if self._waveform is None:
            return 48000
        else:
            return self.waveform.sample_rate

    @property
    def duration(self):
        if self._waveform is None:
            raise AttributeError("No waveform has been provided to the Spectrum object.")
        return self.waveform.duration

    @property
    def time(self):
        if self._time0 is None:
            raise AttributeError("No time object has been provided to the Spectrum object.")
        return self._time0

    @property
    def time_past_midnight(self):
        if self._time0 is None:
            raise AttributeError("No time has been provided to the Spectrum object.")

        if isinstance(self._time0, datetime.datetime):
            t0 = 60 * (60 * self._time0.hour + self._time0.minute) + self._time0.second + \
                float(self._time0.microsecond / 1e6)
            return t0
        else:
            return self._time0

    @property
    def frequencies(self):
        return self._frequencies

    @frequencies.setter
    def frequencies(self, values):
        self._frequencies = values

    @property
    def pressures_pascals(self):
        return self._acoustic_pressures_pascals

    @pressures_pascals.setter
    def pressures_pascals(self, values):
        self._acoustic_pressures_pascals = values

    @property
    def pressures_decibels(self):
        """
        Sound pressure levels of the spectrum in units of dB re 20 microPa. Unweighted (i.e. Z-weighted)
        values required.

        :Examples:

        Create Spectrum object and output sound pressure levels in dB

        >>> import numpy as np
        >>> from pytimbre.spectral.spectra import Spectrum
        >>> spec = Spectrum()
        >>> spec.frequencies = np.array([100., 125., 160.])
        >>> spec.pressures_pascals = np.array([1., 10., 100.])
        >>> spec.pressures_decibels
        array([ 93.97940009, 113.97940009, 133.97940009])

        Set the Spectrum pressures in dB and output pressures in Pa

        >>> spec = Spectrum()
        >>> spec.frequencies = [1000., 2000., 4000.]
        >>> spec.pressures_decibels = np.array([114., 94., 114.])
        >>> spec.pressures_pascals
        array([10.02374467,  1.00237447, 10.02374467])
        """
        return 20 * np.log10(self.pressures_pascals / 20e-6)

    @pressures_decibels.setter
    def pressures_decibels(self, values):
        self._acoustic_pressures_pascals = 10 ** (np.asarray(values) / 20) * 20e-6

    @property
    def fractional_octave_bandwidth(self):
        if self._bandwidth is not None:
            return self._bandwidth
        else:
            if self.is_narrowband_resolution:
                return None
            else:
                f_ratio = np.zeros((len(self.frequencies)-1,))
                for i in range(1, len(self.frequencies)):
                    f_ratio[i-1] = self.frequencies[i] / self.frequencies[i-1]

                log_ratio = np.log2(f_ratio)
                inv_log_ratio = 1 / log_ratio
                return int(np.floor(np.round(np.mean(inv_log_ratio))))

    @fractional_octave_bandwidth.setter
    def fractional_octave_bandwidth(self, value):
        self._bandwidth = value

    @property
    def start_fractional_octave_frequency(self):
        return self._f0

    @start_fractional_octave_frequency.setter
    def start_fractional_octave_frequency(self, value):
        self._f0 = value

    @property
    def stop_fractional_octave_frequency(self):
        return self._f1

    @stop_fractional_octave_frequency.setter
    def stop_fractional_octave_frequency(self, value):
        self._f1 = value

    @property
    def narrowband_frequency_count(self):
        return self._fft_size

    @narrowband_frequency_count.setter
    def narrowband_frequency_count(self, value):
        self._fft_size = value

        self.bin_size = self.sample_rate / self._fft_size
        self.sample_rate_x = self.sample_rate / self.hop_size
        self.sample_rate_y = self._fft_size / self.sample_rate_x
        self.window = np.hamming(self.window_size)
        self.window_overlap = self.window_size - self.hop_size

    @property
    def doublesided_frequency_array(self):
        return self._frequencies_double_sided

    @property
    def frequency_increment(self):
        return np.diff(self.frequencies)[0]

    @property
    def fft_size(self):
        return self._fft_size

    @property
    def power_spectral_density(self):
        """
        Numpy array of single-sided real-values. Pressures scaled by frequency, in units of Pascals / sqrt(Hz).
        """
        return self.pressures_pascals / np.sqrt(np.diff(self.frequencies)[0])

    @property
    def settle_time(self):
        if self.fractional_octave_bandwidth is None:
            return None
        else:
            return self.settle_samples / self.sample_rate

    @property
    def settle_samples(self):
        """
        Based on requirements of Matlab filtering, you must have at least 3 times the number of coefficients to
        accurately filter data. So this will start with that minimum, and then move through the full octave frequency
        band numbers to determine the minimum number of samples that are required for the filter to adequately settle.
        """

        if self.fractional_octave_bandwidth is None:
            return -1

        #   Determine the band number for the lowest band
        low_band = int(np.floor(fob_tools.exact_band_number(1, self.start_fractional_octave_frequency)))
        hi_band = int(np.floor(fob_tools.exact_band_number(1, self.stop_fractional_octave_frequency)))

        minimum_required_points = 3 * 9

        for band_index in range(low_band + 1, hi_band + 1):
            minimum_required_points *= 2

        return minimum_required_points

    @property
    def is_narrowband_resolution(self):
        df = np.diff(self.frequencies)
        for i in range(len(df)-1):
            if abs(df[i+1]-df[i]) > 1e-5:
                return False
        return True

    @property
    def is_fractional_octave_resolution(self):
        return not self.is_narrowband_resolution

    def calculate_engineering_unit_scale_factor(self, calibration_level: float = 94, calibration_frequency=1000):
        """
        This will take the data within the class and build the spectral time history and then determine the value of the
        scale factor to get a specific sound pressure level at a certain frequency.

        :param calibration_level: The value of the acoustic level for the calibration
        :type calibration_level: float
        :param calibration_frequency: The value of the frequency that is supposed to be used for the calibration
        :type calibration_frequency: float
        :return: The engineering scale factor that can be directly applied to the acoustic data
        :rtype: float

        """

        if self.fractional_octave_bandwidth is None:
            raise ValueError("This analysis cannot be accomplished on a narrowband spectrum")

        #   Now determine the index of the band within the spectral time history that should be examined for the
        #   calculation of the engineering scaling units.

        idx = np.argmin(np.abs(self.frequencies - calibration_frequency))

        #   Now this may select the nearest band as the band just above the actual band.  So ensure that the lower band
        #   is below the desired center frequency
        #
        # if fob_tools.lower_frequency(3, idx + 10) > calibration_frequency:
        #     idx -= 1

        #   From the spectrum obtain the values of the frequency

        calibration_values = self.pressures_decibels[idx]

        #   Calculate the sensitivity of each time history spectra

        sens = calibration_level - calibration_values
        sens /= 20
        sens *= -1
        sens = 10.0 ** sens

        return sens

    @staticmethod
    def from_fourier_transform(wfm: Waveform, fft_size: int = None):
        """
        This function replaces the entire SpectrumByFFT class and inserts only the function for calculations of the
        spectral levels
        :param wfm: The audio to transform
        :type wfm: Waveform
        :param fft_size: the number of analysis frequency bins
        :type fft_size: int
        :return: the Spectral sound pressure levels
        :rtype: Spectrum
        """

        if fft_size is None:
            fft_size = 2**int(np.floor(np.log2(len(wfm.samples))))
        elif fft_size > len(wfm.samples):
            raise ValueError('FFT block size cannot be greater than the total length of the signal.')

        if wfm.is_continuous:
            ss_pressures, ss_frequencies, pressures, frequencies = Spectrum._calculation_continuous_fft(wfm, fft_size)

            spectrum = Spectrum(wfm, ss_pressures, ss_frequencies)
            spectrum._frequencies_double_sided = frequencies
            spectrum._pressures_double_sided_complex = pressures
            spectrum._fft_size = fft_size
            return spectrum
        elif wfm.is_impulsive:
            ss_pressures, ss_frequencies, pressures, frequencies = Spectrum._calculate_impulse_fft(wfm, fft_size)

            spectrum = Spectrum(wfm, ss_pressures, ss_frequencies)
            spectrum._frequencies_double_sided = frequencies
            spectrum._pressures_double_sided_complex = pressures
            spectrum._fft_size = fft_size
            return spectrum

    @staticmethod
    def from_digital_filters(
            wfm: Waveform, frequency_resolution: int = 3, start_frequency: float = 10.0,
            stop_frequency: float = 10000.0
            ):
        """
        This function processes the waveform using a sequence of digital filters defined for the highest octave
        filter band and sequentially moved down an octave through decimation of the input signal.
        :param wfm: The audio to process
        :type wfm: Waveform
        :param frequency_resolution: the fractional octave frequency resolution
        :type frequency_resolution: int
        :param start_frequency: the lowest desired frequency within the spectrum
        :type start_frequency: float
        :param stop_frequency: the highest desired frequency within the spectrum
        :type stop_frequency: float
        :return: the audio spectrum organized with fractional octave center frequencies
        :rtype: Spectrum
        """

        return Spectrum._calculate_spectrum_with_filters(wfm, frequency_resolution, start_frequency, stop_frequency)

    @staticmethod
    def _get_top_fractional_octave_band_index(frequency_resolution: int, hi_band: int):
        """
        This is a helper function that determines the index of the fractional octave band at the upper limit of the
        analysis.
        :return: the index of the upper band in the full octave resolution
        :rtype: int
        """
        return int(
            np.floor(
                fob_tools.exact_band_number(
                    frequency_resolution,
                    fob_tools.upper_frequency(1, hi_band)
                )
            )
        )

    @staticmethod
    def _define_filter_coefficients(fractional_octave_bandwidth: int, stop_frequency: float, sample_rate: float):
        """
        This function uses the desired frequencies and frequency resolution to determine the number and shape of the
        fractional octave bands for the octave within the desired spectral levels. It designs a set of digital
        filters that represent the full octave for the highest frequency.
        :param fractional_octave_bandwidth: the number of bands to make within the last full octave band
        :type fractional_octave_bandwidth: int
        :param stop_frequency: the center frequency of the desired highest fractional octave band
        :type stop_frequency: float
        :param sample_rate: The number of samples per second within the waveform
        :type sample_rate: float
        :return: the coefficients for each fractional octave band within the highest full octave of the desired spectrum
        :rtype: tuple
        """
        b_coefficients = list()
        a_coefficients = list()

        #   Determine the center frequency of the highest octave
        full_band = int(np.floor(fob_tools.exact_band_number(1, stop_frequency)))
        f_full = fob_tools.center_frequency(1, full_band)
        f_lo = fob_tools.lower_frequency(1, full_band)
        f_hi = fob_tools.upper_frequency(1, full_band)

        #   Now that the know the center frequency of the highest band, determine the upper limit, and then the closest
        #   center frequency in the desired bandwidth
        f_band = int(np.floor(fob_tools.exact_band_number(fractional_octave_bandwidth, f_hi)))
        nyquist = sample_rate / 2.0

        #   Loop through the frequencies within the highest octave band and create the associated digital filters for
        #   the element based on the calculated high and low frequencies.
        while fob_tools.lower_frequency(fractional_octave_bandwidth, f_band) >= f_lo * 0.90:
            #   Define the window for the bandpass filter
            upper = fob_tools.upper_frequency(fractional_octave_bandwidth, f_band)
            lower = fob_tools.lower_frequency(fractional_octave_bandwidth, f_band)
            window = np.array([lower, upper]) / nyquist

            #   Create the filter coefficients for this frequency band and add it to the list for each coefficient set
            b, a = scipy.signal.butter(
                3,
                window,
                btype='bandpass',
                analog=False,
                output='ba'
            )

            b_coefficients.append(b)
            a_coefficients.append(a)

            #   Decrement the band number to move to the next band down.
            f_band -= 1

        return b_coefficients, a_coefficients

    @staticmethod
    def _calculate_spectrum_with_filters(
            wfm: Waveform,
            frequency_resolution: int = 3,
            start_frequency: float = 10.0,
            stop_frequency: float = 10000.0
            ):
        """
        This will take the waveform that exist within the class and calculate the fractional octave pressures within
        each band that is adequately covered by the length of the waveform.
        :param wfm: The audio to process
        :type wfm: Waveform
        :param frequency_resolution: the fractional octave frequency resolution
        :type frequency_resolution: int
        :param start_frequency: the lowest desired frequency within the spectrum
        :type start_frequency: float
        :param stop_frequency: the highest desired frequency within the spectrum
        :type stop_frequency: float
        :returns: The spectrum with the sound pressure levels and frequencies determined from the waveform using filters
        :rtype: Spectrum
        """
        from pytimbre.utilities.audio_filtering import WaveformFilter

        #   Get the coefficients of the highest fractional octave band
        b_list, a_list = Spectrum._define_filter_coefficients(frequency_resolution, stop_frequency, wfm.sample_rate)

        #   Create the list that will hold the frequencies and band pressures
        pressures = list()
        frequency = list()

        #   Determine the octave bands that will need to be calculated to cover the desired frequency range.
        low_band = int(np.floor(fob_tools.exact_band_number(1, start_frequency)))
        hi_band = int(np.floor(fob_tools.exact_band_number(1, stop_frequency)))

        #   Get the index of the band at the top of the full octave filter
        fob_band_index = Spectrum._get_top_fractional_octave_band_index(frequency_resolution, hi_band)

        #   Make a copy of the waveform that can be decimated
        dec_wfm = Waveform(
            pressures=wfm.samples.copy(),
            sample_rate=wfm.sample_rate,
            start_time=wfm.start_time,
            header=wfm.header
        )

        #   Loop through the frequencies in reverse order
        for band_index in range(hi_band, low_band - 1, -1):
            #   if there are insufficient number of points in the waveform, terminate the process now
            if len(dec_wfm.samples) < 3 * len(b_list):
                warnings.warn(
                    "The number of points within the Waveform are insufficient to calculate digital filters "
                    "lower than these frequencies"
                )
                break

            #   Now loop through the filter definitions that are presented in decreasing frequency magnitude
            for filter_index in range(len(b_list)):
                filtered_waveform = WaveformFilter.apply_iir_filter(dec_wfm, b_list[filter_index], a_list[filter_index])

                frequency.append(fob_tools.center_frequency(frequency_resolution, fob_band_index))
                pressures.append(np.std(filtered_waveform._samples))

                fob_band_index -= 1

            #   Decimate the waveform, halving the sample rate and making the filter definitions move down a full octave
            if len(wfm.samples) / 2 < 3 * len(b_list):
                warnings.warn(
                    "The number of points within the Waveform are insufficient to calculate digital filters "
                    "lower than these frequencies"
                )

                break

            dec_wfm = Waveform(
                pressures=scipy.signal.decimate(dec_wfm.samples, 2),
                sample_rate=dec_wfm.sample_rate,
                start_time=dec_wfm.start_time,
                header=dec_wfm.header
            )

        #   Convert the information within the pressures and frequency arrays into the correct elements for the class
        frequency = np.asarray(frequency)[::-1]
        pressures = np.asarray(pressures)[::-1]

        idx0 = np.nonzero(
            frequency > fob_tools.lower_frequency(
                frequency_resolution,
                fob_tools.exact_band_number(
                    frequency_resolution,
                    start_frequency
                )
            )
        )[0][0]
        idx1 = np.nonzero(
            frequency < fob_tools.upper_frequency(
                frequency_resolution,
                fob_tools.exact_band_number(
                    frequency_resolution,
                    stop_frequency
                )
            )
        )[0][-1]
        frequencies = frequency[np.arange(idx0, idx1 + 1)]
        acoustic_pressures_pascals = pressures[np.arange(idx0, idx1 + 1)]

        spectrum = Spectrum(wfm, acoustic_pressures_pascals, frequencies)
        spectrum.start_fractional_octave_frequency = start_frequency
        spectrum.stop_fractional_octave_frequency = stop_frequency
        spectrum.fractional_octave_bandwidth = frequency_resolution
        spectrum._waveform = wfm

        return spectrum

    @staticmethod
    def _calculate_impulse_fft(wfm: Waveform, fft_size: int):
        #   Create the frequency arrays
        frequencies_double_sided = (wfm.sample_rate * np.arange(0, fft_size)) / fft_size
        frequencies_nb = frequencies_double_sided[:int(fft_size / 2)]
        df = frequencies_nb[1] - frequencies_nb[0]

        #   enforce a zero mean value
        x = wfm.samples - np.mean(wfm.samples)

        #   Generate a Tukey window
        ww = scipy.signal.windows.tukey(fft_size, alpha=0.1)
        W = np.mean(ww ** 2)

        #   Divide the total data into blocks with 50% overlap and Hanning window
        blocks = np.zeros(shape=(int(np.floor(2 * len(x) / fft_size - 1)), fft_size))

        for k in range(blocks.shape[0]):
            i = int(k * fft_size / 2)
            j = i + blocks.shape[1]
            blocks[k, :] = ww * x[i:j]

        #   Determine complex pressure amplitude
        pressures_double_sided_complex = np.sqrt(
            2 * df / fft_size /
            wfm.sample_rate / W
        ) * scipy.fft.fft(blocks, n=fft_size)

        #   Now assign the values for the acoustic pressures using this information, but only using the first hold of
        #   the frequency data.
        pressures_single_sided = pressures_double_sided_complex[:, :len(frequencies_nb)]
        ss_pressures = np.sqrt(np.mean((pressures_single_sided * np.conj(pressures_single_sided)).real, axis=0))

        return ss_pressures, frequencies_nb, pressures_double_sided_complex, frequencies_double_sided

    @staticmethod
    def _calculation_continuous_fft(wfm: Waveform, fft_size: int):

        #   Create the frequency arrays
        frequencies_double_sided = (wfm.sample_rate * np.arange(0, fft_size)) / fft_size
        frequencies_nb = frequencies_double_sided[:int(fft_size / 2)]
        df = np.diff(frequencies_nb)[0]

        #   enforce a zero mean value
        x = wfm.samples - np.mean(wfm.samples)

        #   Generate a Hanning window
        ww = np.hanning(fft_size)
        W = np.mean(ww ** 2)

        #   Divide the total data into blocks with 50% overlap and Hanning window
        blocks = np.zeros(shape=(int(np.floor(2 * len(x) / fft_size - 1)), fft_size))

        for k in range(blocks.shape[0]):
            i = int(k * fft_size / 2)
            j = i + blocks.shape[1]
            blocks[k, :] = ww * x[i:j]

        #   Determine complex pressure amplitude
        pressures_double_sided_complex = scipy.fft.fft(blocks, n=fft_size)
        pressures_double_sided_complex *= np.sqrt(2 * df / fft_size / wfm.sample_rate / W)

        #   Now assign the values for the acoustic pressures using this information, but only using the first hold
        #   of the frequency data.
        pressures_single_sided = pressures_double_sided_complex[:, :len(frequencies_nb)]
        ss_pressures = np.sqrt(np.mean((pressures_single_sided * np.conj(pressures_single_sided)).real, axis=0))
        return ss_pressures, frequencies_nb, pressures_double_sided_complex, frequencies_double_sided

    @staticmethod
    def convert_nb_to_fob(
            frequencies_nb,
            pressures_pascals_nb,
            fob_band_width: int = 3,
            f0: float = 10,
            f1: float = 10000
    ):
        """
        This function converts the frequency and pressure arrays sampled in narrowband resolution to the fractional
        octave band resolution.

        :param frequencies_nb: nd_array - the collection of narrowband frequencies that we want to convert
        :param pressures_pascals_nb: nd_array - the collection of pressures in units of pascals for the frequencies
        :param fob_band_width: int, default = 3 - the fractional octave band resolution that we desire
        :param f0: float, default = 10 - The start frequency of the output fractional octave frequencies
        :param f1: float, default = 10000 - The end frequency of the output fractional octave frequencies

        :return: frequencies_fob - nd_array - the collection of frequencies from f0 to f1 with the resolution of fob_band_width
            pressures_pascals_fob - nd_array - the fractional octave pressure in pascals at the associated frequencies
        """

        frequencies_fob = fob_tools.get_frequency_array(fob_band_width, f0, f1)

        #   Build the array of pressures that are the same size as the list of frequencies
        pressures_pascals_fob = np.zeros((len(frequencies_fob),))

        for i in range(len(frequencies_fob)):
            pressures_pascals_fob[i] = np.sqrt(
                sum(
                    pressures_pascals_nb ** 2 *
                    fob_tools.filter_shape(
                        fob_band_width,
                        frequencies_fob[i],
                        frequencies_nb
                    )
                )
            )

        return frequencies_fob, pressures_pascals_fob

    def to_fractional_octave_band(self, bandwidth: int = 3, f0: float = 10, f1: float = 10000):
        """
        This function will convert the spectrum from a narrowband resolution to a factional octave band resolution by
        applying the shape functions to the narrowband spectral values and determining the weighted value within the
        fractional octave band.

        :param bandwidth: float, default = 3 - the fractional octave resolution that we will sample the frequency spectrum
        :param f0: float, default = 10 - the lowest frequency within the spectrum
        :param f1: float, default = 10000 - the heighest frequency within the spectrum

        :return: Spectrum - a spectrum object with the frequencies at the specified resolution and between the specified
            frequency values.
        """

        f_fob, p_fob = self.convert_nb_to_fob(self.frequencies, self.pressures_pascals, bandwidth, f0, f1)
        s = Spectrum()
        s.frequencies = f_fob
        s.pressures_pascals = p_fob
        s.start_fractional_octave_frequency = f0
        s.stop_fractional_octave_frequency = f1
        s.fractional_octave_bandwidth = bandwidth
        s._time0 = self.time
        s._waveform = self.waveform

        return s


if __name__ == "__main__":
    import doctest

    doctest.testmod()
