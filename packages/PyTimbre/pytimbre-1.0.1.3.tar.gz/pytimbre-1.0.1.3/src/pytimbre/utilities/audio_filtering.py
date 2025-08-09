from pytimbre.audio import Waveform
from scipy.signal import bilinear, convolve, lfilter, butter
from scipy.signal.windows import hamming, tukey
import numpy as np
from pytimbre.utilities.audio_analysis_enumerations import WindowingMethods


def ac_filter_design(fs):
    """
    AC_Filter_Design.py

    Created on Mon Oct 18 19:27:36 2021

    @author: Conner Campbell, Ball Aerospace

    Description
    ----------
    coefficients_a, coeff_c = AC_Filter_Design(fs)

    returns ba, aa, and bc, ac which are arrays of IRIR filter
    coefficients for A and C-weighting.  fs is the sampling
    rate in Hz.

    This program is a recreation of adsgn and cdsgn
    by Christophe Couvreur, see	Matlab FEX ID 69.


    Parameters
    ----------
    fs : double
        sampling rate in Hz

    Returns
    -------

    coefficients_a: list
        List of two numpy arrays, feedforward and feedback filter
        coefficients for A-weighting filter. Form of lists is [ba,aa]

    Coeff_c: list
        List of two numpy arrays, feedforward and feedback filter
        coefficients for C-weighting filter. Form of lists is [bc,ac]

    Code Dependencies
    -------
    This program requires the following python packages:
    scipy.signal, numpy

    References
    -------
    IEC/CD 1672: Electroacoustics-Sound Level Meters, Nov. 1996.

    ANSI S1.4: Specifications for Sound Level Meters, 1983.

    ACdsgn.m: Christophe Couvreur, Faculte Polytechnique de Mons (Belgium)
    couvreur@thor.fpms.ac.be
    """

    # Define filter poles for A/C weight IIR filter according to IEC/CD 1672
    f1 = 20.598997
    f2 = 107.65265
    f3 = 737.86223
    f4 = 12194.217
    a1000 = 1.9997
    c1000 = 0.0619
    pi = np.pi

    # Calculate denominator and numerator of filter transfer functions
    coefficient_1 = (2 * pi * f4) ** 2 * (10 ** (c1000 / 20))
    coefficient_2 = (2 * pi * f4) ** 2 * (10 ** (a1000 / 20))

    numerator_1 = np.array([coefficient_1, 0.0])
    denominator_1 = np.array([1, 4 * pi * f4, (2 * pi * f4) ** 2])

    numerator_2 = np.array([1, 0.0])
    denominator_2 = np.array([1, 4 * pi * f1, (2 * pi * f1) ** 2])

    numerator_3 = np.array([coefficient_2 / coefficient_1, 0.0, 0.0])
    denominator_3 = convolve(np.array([1, 2 * pi * f2]).T, (np.array([1, 2 * pi * f3])))

    # Use scipy.signal.bilinear function to get numerator and denominator of
    # the transformed digital filter transfer functions.
    b1, a1 = bilinear(numerator_1, denominator_1, fs)
    b2, a2 = bilinear(numerator_2, denominator_2, fs)
    b3, a3 = bilinear(numerator_3, denominator_3, fs)

    ac = convolve(a1, a2)
    aa = convolve(ac, a3)

    bc = convolve(b1, b2)
    ba = convolve(bc, b3)

    return [ba, aa], [bc, ac]


class WaveformFilter:
    """
    This class contains a series of functions that operate on a Waveform to alter the internal representation of the
    data through the use of various digital filters.
    """

    @staticmethod
    def apply_window(wfm: Waveform, window_method: WindowingMethods = WindowingMethods.hanning,
                     windowing_parameter=None):
        """
        This will apply a window with the specific method that is supplied by the window argument and returns a
        generic_time_waveform with the window applied

        :param wfm: The audio waveform to apply the window to
        :param window_method: windowing_methods - the enumeration that identifies what type of window to apply to the
        waveform
        :param windowing_parameter: int or float - an additional parameter that is required for the window
        :returns: generic_time_waveform - the waveform with the window applied
        """

        window = []

        if window_method == WindowingMethods.tukey:
            window = tukey(len(wfm.samples), windowing_parameter)

        elif window_method == WindowingMethods.rectangular:
            window = tukey(len(wfm.samples), 0)

        elif window_method == WindowingMethods.hanning:
            window = tukey(len(wfm.samples), 1)

        elif window_method == WindowingMethods.hamming:
            window = hamming(len(wfm.samples))

        return Waveform(wfm.samples * window, wfm.fs, wfm.start_time, header=wfm.header, remove_dc_offset=False)

    @staticmethod
    def apply_iir_filter(wfm: Waveform, b, a):
        """
        This function will be able to apply a filter to the samples within the file and return a new
        generic_time_waveform object

        :param wfm: The audio waveform to filter
        :type wfm: Waveform
        :param b: double, array-like - the forward coefficients of the filter definition
        :param a: double, array-like - the reverse coefficients of the filter definition
        """

        return Waveform(pressures=lfilter(b, a, wfm.samples),
                        sample_rate=wfm.sample_rate,
                        start_time=wfm.start_time,
                        remove_dc_offset=False,
                        header=wfm.header)

    @staticmethod
    def apply_a_weight(wfm: Waveform):
        """
        This function specifically applies the a-weighting filter to the acoustic data, and returns a new waveform with
        the filter applied.

        :returns:
            generic_time_waveform - the filtered waveform
        """
        a, _ = ac_filter_design(wfm.sample_rate)

        return WaveformFilter.apply_iir_filter(wfm, a[0], a[1])

    @staticmethod
    def apply_c_weight(wfm: Waveform):
        """
        This function specifically applies the a-weighting filter to the acoustic data, and returns a new waveform with
        the filter applied.

        :returns: generic_time_waveform - the filtered waveform
        """
        _, c = ac_filter_design(wfm.sample_rate)

        return WaveformFilter.apply_iir_filter(wfm, c[0], c[1])

    @staticmethod
    def apply_lowpass(wfm: Waveform, cutoff: float, order: int = 4):
        """
        This function applies a Butterworth filter to the samples within this class.

        :param wfm:
        :type wfm:
        :param cutoff: double - the true frequency in Hz
        :param order: double (default: 4) - the order of the filter that will be created and applied

        :returns: generic_time_waveform - the filtered waveform
        """

        b, a = WaveformFilter._design_low_pass(wfm, cutoff, order)

        #   Filter the data and return the new waveform object
        return WaveformFilter.apply_iir_filter(wfm, b, a)

    @staticmethod
    def apply_head_auditory_response_filters(wfm: Waveform):
        """
        To calculate the integrated loudness of the signal, we need to first filter the signal for a specific type of
        response due to the head and the auditory system. This originates in the pyloudnorm.meter class where the two
        filters are defined.

        """
        G = 4.0
        fc = 1500.0
        Q = np.sqrt(2.0) / 2.0

        A = 10 ** (G / 40.0)
        w0 = 2.0 * np.pi * (fc / wfm.sample_rate)
        alpha = np.sin(w0) / (2.0 * Q)

        #   Define the filter shape for the high shelf
        passband_gain = 1.0
        b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
        b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
        a2 = (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0

        new_wfm = WaveformFilter.apply_iir_filter(wfm, b, a)
        new_wfm.samples *= passband_gain

        #   Now the high pass
        G = 0
        fc = 38.8
        Q = 0.5

        A = 10 ** (G / 40.0)
        w0 = 2.0 * np.pi * (fc / wfm.sample_rate)
        alpha = np.sin(w0) / (2.0 * Q)

        b0 = (1 + np.cos(w0)) / 2
        b1 = -(1 + np.cos(w0))
        b2 = (1 + np.cos(w0)) / 2
        a0 = 1 + alpha
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha

        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0

        new_wfm = WaveformFilter.apply_iir_filter(wfm, b, a)
        new_wfm.samples *= passband_gain

        return new_wfm

    @staticmethod
    def apply_highpass(wfm: Waveform, cutoff: float, order: int = 4):
        """
        This function applies a Butterworth filter to the samples within this class.

        :param cutoff: double - the true frequency in Hz
        :param order: double (default: 4) - the order of the filter that will be created and applied

        :returns: Waveform - the filtered waveform
        """


        #   Filter the data and return the new waveform object
        return WaveformFilter.apply_iir_filter(wfm, b, a)

    @staticmethod
    def apply_bandpass(wfm: Waveform, low_cutoff: float, high_cutoff: float, order: int = 3):
        """
        This function determines the bandpass Butterworth filter coefficients and sends them and the current waveform
        into the function that will filter the data with an IIR filter coefficient set

        Parameters
        ----------
        low_cutoff: float - the regular frequency cutoff for the low edge of the band pass filter (Units: Hz)
        high_cutoff: float - the regular frequency cutoff for the upper edge of the band pass filter (Units: Hz)
        order: int - default: 3, the order of the filter
        """

        #   Determine the nyquist frequency for the upper and lower edges of the band
        nyquist = wfm.sample_rate / 2.0
        upper = high_cutoff / nyquist
        lower = low_cutoff / nyquist

        #   Design the filter
        b, a = butter(order, [lower, upper], btype='bandpass', analog=False, output='ba')

        #   send this waveform and the coefficients into the filtering algorithm and return the filtered waveform
        return WaveformFilter.apply_iir_filter(wfm, b, a)

    @staticmethod
    def _design_low_pass(wfm: Waveform, cutoff: float, order: int = 4):
        """
        The current design did not really have a method to separate the generation of the coefficients any longer.
        This function was created to build the coefficients in a manner that can be tested. It will generate a
        Butterworth filter of desired length with the specified cut-off frequency.
        :param wfm: The audio that contains the sample rate
        :type wfm: Waveform
        :param cutoff: The frequency where the roll-off begins
        :type cutoff: float
        :param order: the number of coefficients to create within the filter
        :type order: int
        :return: the two sets of coefficients
        :rtype: tuple
        """

        #   Determine the nyquist frequency
        nyquist = wfm.sample_rate / 2.0

        #   Determine the normalized frequency
        normalized_cutoff = cutoff / nyquist

        #   Design the filter
        return butter(order, normalized_cutoff, btype='low', analog=False, output='ba')

    @staticmethod
    def _design_high_pass(wfm: Waveform, cutoff: float, order: int = 4):
        #   Determine the nyquist frequency
        nyquist = wfm.sample_rate / 2.0

        #   Determine the normalized frequency
        normalized_cutoff = cutoff / nyquist

        #   Design the filter
        return butter(order, normalized_cutoff, btype='high', analog=False, output='ba')