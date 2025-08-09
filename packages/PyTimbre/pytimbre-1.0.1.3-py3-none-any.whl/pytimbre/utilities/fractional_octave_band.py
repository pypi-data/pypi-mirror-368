import sys
import numpy as np
import scipy.signal
from scipy.stats import norm


__docformat__ = 'reStructuredText'


# TODO: Fix docstring internal links
# TODO: Fix html formatting of table
# TODO: Test for rounded band numbers

class FractionalOctaveBandTools:
    """
    Conversion and manipulation for fractional octave band center frequencies and band numbers.
    """

    @staticmethod
    def detect_peaks(array, freq=0, cthr=0.2, unprocessed_array=False, fs=44100):
        """
        Function detects the peaks in array, based from the mirpeaks algorithm.

        :param array:               Array in which to detect peaks
        :param freq:                Scale representing the x axis (sample length as array)
        :param cthr:                Threshold for checking adjacent peaks
        :param unprocessed_array:   Array that in unprocessed (normalised), if False will default to the same as array.
        :param fs:                  Sampe rate of the array

        :return:                     index of peaks, values of peaks, peak value on freq.

        Refactored intt PyTimbre by Dr. Frank Mobley, 2023
        """
        # flatten the array for correct processing
        array = array.flatten()

        if np.isscalar(freq):
            # calculate the frerquency scale - assuming a samplerate if none provided
            freq = np.linspace(0, fs / 2.0, len(array))

        if np.isscalar(unprocessed_array):
            unprocessed_array = array

        # add values to allow peaks at the first and last values
        array_appended = np.insert(array, [0, len(array)], -2.0)  # to allow peaks at start and end (default of mir)
        # unprocessed array to get peak values
        array_unprocess_appended = np.insert(unprocessed_array, [0, len(unprocessed_array)], -2.0)
        # append the frequency scale for precise freq calculation
        freq_appended = np.insert(freq, [0, len(freq)], -1.0)

        # get the difference values
        diff_array = np.diff(array_appended)

        # find local maxima
        mx = np.array(np.where((array >= cthr) & (diff_array[0:-1] > 0) & (diff_array[1:] <= 0))) + 1

        # initialise arrays for output
        finalmx = []
        peak_value = []
        peak_x = []
        peak_idx = []

        if np.size(mx) > 0:
            # unpack the array if peaks found
            mx = mx[0]

            j = 0  # scans the peaks from beginning to end
            mxj = mx[j]  # the current peak under evaluation
            jj = j + 1
            bufmin = 2.0
            bufmax = array_appended[mxj]

            if mxj > 1:
                oldbufmin = min(array_appended[:mxj - 1])
            else:
                oldbufmin = array_appended[0]

            while jj < len(mx):
                # if adjacent mx values are too close, returns no array
                if mx[jj - 1] + 1 == mx[jj] - 1:
                    bufmin = min([bufmin, array_appended[mx[jj - 1]]])
                else:
                    bufmin = min([bufmin, min(array_appended[mx[jj - 1]:mx[jj] - 1])])

                if bufmax - bufmin < cthr:
                    # There is no contrastive notch
                    if array_appended[mx[jj]] > bufmax:
                        # new peak is significant;y higher than the old peak,
                        # the peak is transfered to the new position
                        j = jj
                        mxj = mx[j]  # the current peak
                        bufmax = array_appended[mxj]
                        oldbufmin = min([oldbufmin, bufmin])
                        bufmin = 2.0
                    elif array_appended[mx[jj]] - bufmax <= 0:
                        bufmax = max([bufmax, array_appended[mx[jj]]])
                        oldbufmin = min([oldbufmin, bufmin])

                else:
                    # There is a contrastive notch
                    if bufmax - oldbufmin < cthr:
                        # But the previous peak candidate is too weak and therefore discarded
                        oldbufmin = min([oldbufmin, bufmin])
                    else:
                        # The previous peak candidate is OK and therefore stored
                        finalmx.append(mxj)
                        oldbufmin = bufmin

                    bufmax = array_appended[mx[jj]]
                    j = jj
                    mxj = mx[j]  # The current peak
                    bufmin = 2.0

                jj += 1
            if bufmax - oldbufmin >= cthr and (bufmax - min(array_appended[mx[j] + 1:]) >= cthr):
                # The last peak candidate is OK and stored
                finalmx.append(mx[j])

            ''' Sort the values according to their level '''
            finalmx = np.array(finalmx)
            sort_idx = np.argsort(array_appended[finalmx])[::-1]  # descending sort
            finalmx = finalmx[sort_idx]

            peak_idx = finalmx - 1  # indexes were for the appended array, -1 to return to original array index
            peak_value = array_unprocess_appended[finalmx]
            peak_x = freq_appended[finalmx]

            ''' Interpolation for more precise peak location '''
            corrected_value = []
            corrected_position = []
            for current_peak_idx in finalmx:
                # if there enough space to do the fitting
                if 1 < current_peak_idx < (len(array_unprocess_appended) - 2):
                    y0 = array_unprocess_appended[current_peak_idx]
                    ym = array_unprocess_appended[current_peak_idx - 1]
                    yp = array_unprocess_appended[current_peak_idx + 1]
                    p = (yp - ym) / (2 * (2 * y0 - yp - ym))
                    corrected_value.append(y0 - (0.25 * (ym - yp) * p))
                    if p >= 0:
                        correct_pos = ((1 - p) * freq_appended[current_peak_idx]) + (
                                    p * freq_appended[current_peak_idx + 1])
                        corrected_position.append(correct_pos)
                    elif p < 0:
                        correct_pos = ((1 + p) * freq_appended[current_peak_idx]) - (
                                    p * freq_appended[current_peak_idx - 1])
                        corrected_position.append(correct_pos)
                else:
                    corrected_value.append(array_unprocess_appended[current_peak_idx])
                    corrected_position.append(freq_appended[current_peak_idx])

            if corrected_position:
                peak_x = corrected_position
                peak_value = corrected_value

        return peak_idx, peak_value, peak_x



    @staticmethod
    def midbands(minimum_frequency, maximum_frequency, sample_rate):
        """
        Divides the frequency range into third octave bands using filters

        :param minimum_frequency:
            the minimum third octave band
        :param maximum_frequency:
            the maximum third octave band
        :param sample_rate:
            The number of samples per second
        """

        # set defaults
        lowest_band = 25
        highest_band = 20000
        Nyquist_frequency = sample_rate / 2.0
        upper_frequency = (2 ** (1 / 6.0)) * maximum_frequency

        fr = 1000  # reference frequency is 1000Hz
        i = np.arange(-16, 14, 1)
        lab_freq = np.array(
            [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
             2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000])

        lower_band_edge = np.where(lab_freq >= minimum_frequency)[0][0]
        upper_band_edge = np.where(lab_freq >= maximum_frequency)[0][0]

        # compare value of upper_band_edge to nyquist
        while lab_freq[upper_band_edge] > Nyquist_frequency:
            upper_band_edge -= 1

        # indices to find exact midband frequencies
        j = i[np.arange(lower_band_edge, upper_band_edge + 1, 1)]

        # Exact midband frequencies (Calculated as base two exact)
        ff = (2.0 ** (j / 3.0)) * fr
        F = lab_freq[np.arange(lower_band_edge, upper_band_edge + 1, 1)]
        return ff, F, j

    @staticmethod
    def filter_third_octaves_downsample(waveform, reference_level: float = 100.0, minimum_frequency: float = 25.0,
                                        maximum_frequency: float = 12500.0, filter_order: int = 4):
        """
        Filters the audio file into third octave bands

        :param x:
            the waveform object
        :param reference_level:
            the reference level for calculating decibels - does not allow for negative values; default: 100
        :param minimum_frequency:
            the minimum frequency; default: 25
        :param maximum_frequency:
            the maximum frequency (must be at least 2500 Hz); default: 12500
        :param filter_order:
            the filter order; default: 4

        :returns:
        """
        # identify midband frequencies
        [ff, frequencies, j] = FractionalOctaveBandTools.midbands(minimum_frequency,
                                                                  maximum_frequency,
                                                                  waveform.sample_rate)

        # apply filters
        band_pressures = np.zeros(len(j))
        # Determines where downsampling will commence (5000 Hz and below)
        if 7 in j:
            k = np.where(j == 7)[0][0]
        else:
            k = len(j)

        m = len(waveform._samples)

        # For frequencies of 6300 Hz or higher, direct implementation of filters.
        for i in range(len(j) - 1, k, -1):
            f1 = (2.0 ** (-1.0 / 6)) * ff[i]
            f2 = (2.0 ** (1.0 / 6)) * ff[i]
            f1 /= (waveform.sample_rate / 2.0)
            f2 /= (waveform.sample_rate / 2.0)

            # force f2 to be 1.0 for cases where the upper bandwidth from 3rd_octave_downsample produce higher
            # frequencies
            if f2 >= 1.0:
                f2 = 0.9999999999
            B, A = scipy.signal.butter(filter_order, [f1, f2], 'bandpass')

            if i == k + 3:  # Upper 1/3-oct. band in last octave.
                Bu = B
                Au = A
            if i == k + 2:  # Center 1/3-oct. band in last octave.
                Bc = B
                Ac = A
            if i == k + 1:  # Lower 1/3-oct. band in last octave.
                Bl = B
                Al = A
            y = scipy.signal.lfilter(B, A, waveform._samples)
            if np.max(y) > 0:
                band_pressures[i] = 20 * np.log10(np.sqrt(np.sum(y ** 2.0) / m))  # Convert to decibels.
            else:
                band_pressures[i] = -1.0 * np.inf

        # 5000 Hz or lower, multirate filter implementation.
        pressures = waveform._samples
        fs = waveform.sample_rate
        try:
            for i in range(k, 1, -3):  # = k:-3:1;
                # Design anti-aliasing filter (IIR Filter)
                Wn = 0.4
                C, D = scipy.signal.cheby1(2, 0.1, Wn)

                # Filter
                pressures = scipy.signal.lfilter(C, D, pressures)

                # Downsample
                idx = np.arange(1, len(pressures), 2)
                pressures = pressures[idx]
                fs = fs / 2.0
                m = len(pressures)

                # Performs the filtering
                y = scipy.signal.lfilter(Bu, Au, pressures)
                if np.max(y) > 0:
                    band_pressures[i] = 20 * np.log10(np.sqrt(np.sum(y ** 2.0) / m))
                else:
                    band_pressures[i] = -1.0 * np.inf
                y = scipy.signal.lfilter(Bc, Ac, pressures)
                if np.max(y) > 0:
                    band_pressures[i - 1] = 20 * np.log10(np.sqrt(np.sum(y ** 2.0) / m))
                else:
                    band_pressures[i - 1] = -1.0 * np.inf
                y = scipy.signal.lfilter(Bl, Al, pressures)
                if np.max(y) > 0:
                    band_pressures[i - 2] = 20 * np.log10(np.sqrt(np.sum(y ** 2.0) / m))
                else:
                    band_pressures[i - 2] = -1.0 * np.inf
        except ValueError:
            band_pressures = band_pressures[1:len(j)]

        # "calibrate" the readings based from Pref, chosen as 100 in most uses
        band_pressures = band_pressures + reference_level

        # log transformation
        total_pressure = np.sum(10 ** (band_pressures / 10.0))
        if total_pressure > 0:
            total_pressure = 10 * np.log10(total_pressure)
        else:
            total_pressure = -1.0 * np.inf

        return total_pressure, band_pressures, frequencies

    @staticmethod
    def exact_band_number(resolution, frequency):
        """
        Determine the exact non-integer value of band number of a frequency for a specific fractional octave
        band interval.

        :param resolution: Used to specify the fractional octave band interval as 1/resolution.
            Intervals of 1, 1/3, 1/6, 1/12, and 1/24 are available. See 'center_frequency'_ for band
            number/frequency pairs for common intervals.
        :type resolution: int
        :param frequency: The frequency in Hz
        :type frequency: float
        :return:  The exact band number value
        :rtype: float

        :Example:

        >>> from pytimbre.spectral.fractional_octave_band import FractionalOctaveBandTools
        >>> resolution = 1 # Select 1 Octave Band inberval
        >>> FractionalOctaveBandTools.exact_band_number(resolution, frequency=1000.0)
        0.0

        >>> FractionalOctaveBandTools.exact_band_number(resolution, frequency=1111.0)
        0.15185881672700494
        """

        band = 0.0

        if resolution == 1:
            band = np.log(frequency / 1000) / np.log(2.0)
        elif resolution == 3:
            band = np.log(frequency / 1000) / np.log(2.0)
            band *= 3.0
            band += 30
        elif resolution == 6:
            band = np.log(frequency / (1000 * 2.0 ** (1.0 / 12.0))) / np.log(2.0)
            band *= 6
        elif resolution == 12:
            band = np.log(frequency / (1000 * 2.0 ** (1.0 / 24.0))) / np.log(2.0)
            band *= 12
        elif resolution == 24:
            band = np.log(frequency / (1000 * 2.0 ** (1.0 / 48.0))) / np.log(2.0)
            band *= 24

        return band

    @staticmethod
    def center_frequency(resolution, band):
        """
        Calculate the exact center frequency of a corresponding band number for a specific fractional
        octave band interval.

        :param resolution: Used to specify the fractional octave band interval as 1/resolution.
            Intervals of 1, 1/3, 1/6, 1/12, and 1/24 are available. See 'center_frequency'_ for band
            number/frequency pairs for common intervals.
        :type resolution: int, float
        :param band:  fractional octave band number
        :type band: int, float
        :return: band center frequency in Hz
        :rtype: float

        Note:
        =====
        The band numbers that correspond to preferred band center frequencies include::

            +-----------------+----+------+----+----+----+------+----+----+----+----+-----+-----+-----+-----+-----+
            |                 | 10 | 12.5 | 16 | 20 | 25 | 31.5 | 40 | 50 | 63 | 80 | 100 | 125 | 160 | 200 | 250 |
            +=================+====+======+====+====+====+======+====+====+====+====+=====+=====+=====+=====+=====+
            | 1 Octave Band   |    |      | -6 |    |    | -5   |    |    | -4 |    |     | -3  |     |     | -2  |
            +-----------------+----+------+----+----+----+------+----+----+----+----+-----+-----+-----+-----+-----+
            | 1/3 Octave Band | 10 | 11   | 12 | 13 | 14 | 15   | 16 | 17 | 18 | 19 | 20  | 21  | 22  | 23  | 24  |
            +-----------------+----+------+----+----+----+------+----+----+----+----+-----+-----+-----+-----+-----+

            +-----------------+-----+-----+-----+-----+-----+------+------+------+------+------+------+------+
            |                 | 315 | 400 | 500 | 630 | 800 | 1000 | 1250 | 1600 | 2000 | 2500 | 3150 | 4000 |
            +=================+=====+=====+=====+=====+=====+======+======+======+======+======+======+======+
            | 1 Octave Band   |     |     | -1  |     |     | 0    |      |      | 1    |      |      | 2    |
            +-----------------+-----+-----+-----+-----+-----+------+------+------+------+------+------+------+
            | 1/3 Octave Band | 25  | 26  | 27  | 28  | 29  | 30   | 31   | 32   | 33   | 34   | 35   | 36   |
            +-----------------+-----+-----+-----+-----+-----+------+------+------+------+------+------+------+
        """

        # TODO Consider revision of equations IAW ANSI S1.11
        frequency = 0
        band = np.round(band)
        if resolution == 1:
            frequency = 1000.0 * 2.0 ** band
        elif resolution == 3:
            frequency = 1000 * 2.0 ** ((band - 30.0) / 3.0)
        elif resolution == 6:
            frequency = 1000 * 2.0 ** (1 / 12) * 2.0 ** (band / 6)
        elif resolution == 12:
            frequency = 1000 * 2.0 ** (1.0 / 24.0) * 2.0 ** (band / 12)
        elif resolution == 24:
            frequency = 1000 * 2.0 ** (1 / 48) * 2.0 ** (band / 24)
        return frequency

    @staticmethod
    def lower_frequency(resolution, band):
        """
        Calculate the exact lower frequency of a corresponding band number for a specific fractional
        octave band interval.

        :param resolution: Used to specify the fractional octave band interval as 1/resolution.
            Intervals of 1, 1/3, 1/6, 1/12, and 1/24 are available. See 'center_frequency'_ for band
            number/frequency pairs for common intervals.
        :type resolution: int, float
        :param band:  fractional octave band number
        :type band: int, float
        :return: band lower frequency in Hz
        :rtype: float
        """
        return 2.0 ** (-1.0 / (2.0 * resolution)) * FractionalOctaveBandTools.center_frequency(resolution, band)

    @staticmethod
    def upper_frequency(resolution, band):
        """
        Calculate the exact upper frequency of a corresponding band number for a specific fractional
        octave band interval.

        :param resolution: Used to specify the fractional octave band interval as 1/resolution.
            Intervals of 1, 1/3, 1/6, 1/12, and 1/24 are available. See 'center_frequency'_ for band
            number/frequency pairs for common intervals.
        :type resolution: int, float
        :param band:  fractional octave band number
        :type band: int, float
        :return: band upper frequency in Hz
        :rtype: float
        """
        return 2.0 ** (+1.0 / (2.0 * resolution)) * FractionalOctaveBandTools.center_frequency(resolution, band)

    @staticmethod
    def band_width(resolution, band):
        """
        Calculate the exact frequency band width of a corresponding band number for a specific fractional
        octave band interval.

        :param resolution: Used to specify the fractional octave band interval as 1/resolution.
            Intervals of 1, 1/3, 1/6, 1/12, and 1/24 are available. See 'center_frequency'_ for band
            number/frequency pairs for common intervals.
        :type resolution: int, float
        :param band:  fractional octave band number
        :type band: int, float
        :return: frequency band width in Hz
        :rtype: float
        """
        return FractionalOctaveBandTools.upper_frequency(resolution, band) - FractionalOctaveBandTools.lower_frequency(
            resolution,
            band)

    @staticmethod
    def frequencies(start_band, end_band, resolution) -> list:
        """
        Calculate the exact band center frequencies between a start and stop band number for a specific fractional
        octave band interval.

        :param start_band:  starting fractional octave band number of the array
        :type start_band: int, float
        :param end_band:  ending fractional octave band number of the array
        :type end_band: int, float
        :param resolution: Used to specify the fractional octave band interval as 1/resolution.
            Intervals of 1, 1/3, 1/6, 1/12, and 1/24 are available. See 'center_frequency'_ for band
            number/frequency pairs for common intervals.
        :type resolution: int, float
        :rtype: float, array-like
        :return: frequencies from the start to the stop bands in Hz
        """
        if isinstance(start_band, int) and isinstance(end_band, int) and isinstance(resolution, int):
            f = []
            for index in range(start_band, end_band + 1):
                f.append(FractionalOctaveBandTools.center_frequency(resolution, index))
            return f
        else:
            raise ValueError("You must supply integer values for the start and stop bands, and the frequency "
                             "resolution")

    @staticmethod
    def min_audible_field(frequency):
        """
        This function calculates a curve fit to the minimum audible field according to an equation provided
        by NASA in the AUDIB code.  Reference USAAMRDL-TR-74-102A.

        @author: Gregory Bowers and Frank Mobley

        :type frequency: double
        :param frequency: frequency to calculate the minimum audible field

        :rtype: double
        :return: minimum audible field at the selected frequency
        """

        # log10f = np.log10(frequency)
        # log10fpower = log10f
        # result = 273.3674 - 584.1369 * log10fpower
        # log10fpower *= log10f
        # result += 860.3995 * log10fpower
        # log10fpower *= log10f
        # result -= 690.0302 * log10fpower
        # log10fpower *= log10f
        # result += 283.4491 * log10fpower
        # log10fpower *= log10f
        # result -= 56.89755 * log10fpower
        # log10fpower *= log10f
        # return result + 4.440361 * log10fpower

        c = [273.3674, - 584.1369, 860.3995, -690.0302, 283.4491, -56.897558, +4.440361][::-1]
        x = np.log10(frequency)

        return np.polyval(c, x)

    @staticmethod
    def get_min_audible_fields():
        """
        Gather the minimum audible field values within the calculated frequencies from 10 Hz to 10 kHz

        :rtype: double, array-like
        :return: the minimum audible field based on the NASA interpolation at the exact frequencies from 10 Hz to 10 kHz
        """

        results = []
        for f in FractionalOctaveBandTools.tob_frequencies():
            results.append(FractionalOctaveBandTools.min_audible_field(f))

        return np.array(results)

    @staticmethod
    def frequencies_ansi_preferred(f0: float = 10, f1: float = 10000, bandwidth: int = 3):
        """
        This function provides the list of accepted frequencies from the ANSI S1.6 definition of the shape of fractional
        octave bands.
        """
        import warnings

        warnings.warn("These should be used for labeling purposes only. All calculations relying on frequency band "
                      "centers or band limits should use the 'frequencies' object within the spectral class.",
                      UserWarning,
                      stacklevel=3)

        ansi_preferred_frequencies = np.array([1, 1.25, 1.6, 2, 2.5, 3.15, 4, 5, 6.3, 8])
        ansi_preferred_frequencies = np.concatenate((
            ansi_preferred_frequencies,
            ansi_preferred_frequencies * 10,
            ansi_preferred_frequencies * 100,
            ansi_preferred_frequencies * 1000,
            ansi_preferred_frequencies * 10000,
            ansi_preferred_frequencies * 100000
        ))

        #   If the data is octave, only sample every third element

        if bandwidth == 1:
            ansi_preferred_frequencies = ansi_preferred_frequencies[np.arange(0, len(ansi_preferred_frequencies), 3)]
        elif (bandwidth != 3) & (bandwidth != 1):
            raise ValueError("The ANSI standard only defines the correct frequencies for the full and one-third "
                             "octaves")

        return ansi_preferred_frequencies[np.where((ansi_preferred_frequencies >= f0) &
                                                   (ansi_preferred_frequencies <= f1))[0]]

    @staticmethod
    def tob_frequencies_ansi():
        """
        The accepted frequencies for the one-third-octave bands from 10 Hz to 10 kHz
        """
        output = [10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80
            , 100, 125, 160, 200, 250, 315, 400, 500, 630, 800
            , 1000, 1250, 1600, 2000, 2500, 3150, 4000
            , 5000, 6300, 8000, 10000]
        return output

    @staticmethod
    def tob_frequencies():
        """
        The exact frequencies from 10 Hz to 10 kHz using the center_frequency function at the one-third frequency
        resolution.
        """

        output = np.array([9.843133, 12.401571, 15.625, 19.686266, 24.803141
                              , 31.25, 39.372533, 49.606283, 62.5, 78.745066
                              , 99.212566, 125.0, 157.490131, 198.425131, 250.0, 314.980262
                              , 396.850263, 500.0, 629.960525, 793.700526
                              , 1000.0, 1259.92105, 1587.401052, 2000.0, 2519.8421, 3174.802104
                              , 4000.0, 5039.6842, 6349.604208, 8000.0, 10079.3684], dtype=float)

        return output

    @staticmethod
    def tob_to_erb(x, spl):
        """
        Convert the data form the one-third-octave bandwidth to the equivalent rectangular band bandwidth

        :type x: double/int
        :param x: the band frequency to convert (double) or the band index within the spectrum from 10 Hz t0 10 kHz (int)
        :type spl: double
        :param spl: the sound pressure level at the selected frequency

        :rtype: double
        :return: the sound pressure level adjusted for the difference between the TOB and ERB bandwidths
        """

        if isinstance(x, int):
            index = x - 10
            delta = 20 * np.log10(FractionalOctaveBandTools.center_frequency_to_erb(
                FractionalOctaveBandTools.tob_frequencies()[index]) / FractionalOctaveBandTools.band_width(3, x))
        elif isinstance(x, float):
            bandwidth = (np.power(2.0, 1.0 / 6.0) - np.power(2.0, -1.0 / 6.0)) * x
            delta = 20 * np.log10(FractionalOctaveBandTools.center_frequency_to_erb(x) / bandwidth)

        if delta > 0:
            return spl
        else:
            return spl + delta

    @staticmethod
    def center_frequency_to_erb(frequency):
        """
        This function converts the center frequency to the Equivalent Rectangular Band (ERB)

        :type frequency: double
        :param frequency: the center frequency of the one-third-octave band, Units: Hz

        :rtype: double
        :return: the bandwidth of the ERB at the selected center frequency
        """
        return 24.7 * (0.00437 * frequency + 1)

    @staticmethod
    def erb_to_center_frequency(erb):
        return ((erb / 24.7) - 1) / 0.00437

    @staticmethod
    def get_frequency_array(band_width: int = 3, f0: float = 10, f1: float = 10000):

        # Build the collection of frequencies based on the input parameters from the argument list
        accepted_bandwidths = np.array([1, 3, 6, 12, 24], dtype=float)

        if band_width not in accepted_bandwidths:
            raise ValueError("You did not provide a valid bandwidth")

        band0 = int(np.floor(FractionalOctaveBandTools.exact_band_number(band_width, f0)))

        freqs = list()

        f1_upper = f1 * 2 ** (1 / (2 * band_width))
        band_no = band0

        while FractionalOctaveBandTools.center_frequency(band_width, band_no) < f1_upper:
            freqs.append(FractionalOctaveBandTools.center_frequency(band_width, band_no))
            band_no += 1

        return np.asarray(freqs)

    @staticmethod
    def filter_shape(bandwidth: float = 3, center_frequency: float = 1000, narrowband_frequencies=None):
        """
        This function defines the shape of the one-third octave band based on the narrowband frequencies that are
        provided. This is based on the information from Matlab scripts provided by Brigham Young University researchers.
        """

        #   Define the band edges of the frequency band
        b = 2 * bandwidth
        f_low = center_frequency * 2 ** (-1 / b)
        f_high = center_frequency * 2 ** (1 / b)

        #   Get the ratio of the bandwidth to the frequency
        qr = center_frequency / (f_high - f_low)
        qd = (np.pi / b) / (np.sin(np.pi / b)) * qr
        qd = qd ** 6

        #   Define the squared weighted shape of the band at these frequencies
        delta_f_psd = narrowband_frequencies / (center_frequency + sys.float_info.epsilon)
        delta_f_fob = center_frequency / (narrowband_frequencies + sys.float_info.epsilon)
        frequency_delta = (delta_f_psd - delta_f_fob) ** 6

        return abs(1 / (1 + qd * frequency_delta))

    @staticmethod
    def ansi_band_limits(class_: int = 0, fc: float = 1000, nth_oct: int = 3):
        """
        This function will calculate the constant percentage bandwidth description of the accepted shape based on the
        ANSI S1.11 standard.

        Parameters
        ----------
        class_: int
            the class of the filter that we are trying to design
        fc : float
            default: 1000 - the center frequency of the band that we are plotting

        Returns
        -------
        frequency : float
            array-like - the collection of frequencies
        shape_lo : float
            array-like - the levels of the lower limit of the filter design
        shape_hi : float
            array-like - the levels of the upper limit of the filter design
        """

        if nth_oct == 1:
            frequency = np.array([2 ** -4, 2 ** -3, 2 ** -2, 2 ** -1, 2 ** -0.5, 2 ** -(3 / 8), 2 ** -0.25,
                                  2 ** (-1 / 8), 2 ** 0, 2 ** (1 / 8), 2 ** 0.25, 2 ** (3 / 8), 2 ** 0.5, 2 ** 1,
                                  2 ** 2, 2 ** 3, 2 ** 4]) * fc
        elif nth_oct == 3:
            frequency = np.array([0.187, 0.32578, 0.52996, 0.77181, 0.89090, 0.91932, 0.94702, 0.97394, 1., 1.02676,
                                  1.05594, 1.08776, 1.12246, 1.29565, 1.88695, 3.06955, 5.43474]) * fc

        if class_ == 0:
            lo = np.array([-75, -62, -42.5, -18, -2.3, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, -2.3, -18, -42.5, -62,
                           -75])
            hi = np.array([-np.infty, -np.infty, -np.infty, -np.infty, -4.5, -1.1, -.4, -.2, -.15, -.2, -.4, -1.1, -4.5,
                           -np.infty, -np.infty, -np.infty, -np.infty])
        elif class_ >= 1:
            lo = []
            hi = []

        return frequency, lo, hi
