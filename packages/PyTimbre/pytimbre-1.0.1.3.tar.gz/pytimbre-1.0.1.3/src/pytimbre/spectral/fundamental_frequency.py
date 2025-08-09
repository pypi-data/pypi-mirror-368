import numpy as np
from pytimbre.audio import Waveform
from pytimbre.spectral.spectra import Spectrum


class FundamentalFrequencyCalculator:
    """
    There are many ways to calculate the fundamental frequency of a waveform. However, many of the methods require
    information that can easily be combined with the functions and classes that exist within the PyTimbre modules.
    This class gathers the methods into one system and builds a collection of public and protected elements to access
    the fundamental frequency calculators.
    """

    def __init__(self,
                 f0: float = 10,
                 f1: float = 10000,
                 frequency_window_size: int = 2048,
                 temporal_window: int = 256):
        """
        This build the class and initializes the element that are required for the calculation of the fundamental
        frequency.

        :param f0: float
            the starting frequency for the analysis
        :param f1: float
            the ending frequency for the analysis
        """

        self._start_frequency = f0
        self._stop_frequency = f1
        self._window_size = frequency_window_size
        self._waveform = None
        self._hop_size = temporal_window

    def fundamental_by_time(self, wfm: Waveform):
        """
        This function calculates the fundamental frequency based on the YIN function that only requires the collection
        of samples to determine the fundamental frequency

        :param wfm: Waveform
            The PyTimbre object that holds the samples, sample rate and start time of the signal we want to process.
        """

        self._waveform = wfm
        return np.median(self._yin()[0])

    def fundamental_swipe(self, spectrum: Spectrum):
        return self._swipe_spectral_estimation(spectrum)

    def fundamental_by_peaks(self, spectrum: Spectrum):
        """
        This function attempts to determine the fundamental by first scanning the frequency spectrum for peaks. Then
        the peaks are examined to determine the harmonic relationship between the peaks within the spectrum. If there
        are insufficient peaks within the spectrum, we return the frequency with the maximum value. Otherwise, we return
        the value that has the closest set of harmonically related frequencies.
        """
        from scipy.signal import find_peaks

        #   Find local maxima
        peak_frequency_indices = find_peaks(spectrum.pressures_pascals,
                                            threshold=np.median(spectrum.pressures_pascals),
                                            distance=2)[0]

        #   If function doesn't have many candidate just return frequency at max value
        if len(peak_frequency_indices) < 5:
            if len(peak_frequency_indices) == 0:
                return np.nan

            #   find the index of the maximum peak
            peak_index = np.argmax(spectrum.pressures_decibels[peak_frequency_indices])
            return spectrum.frequencies[peak_frequency_indices[peak_index]]
        else:
            #   If one of the frequencies is the fundamental, it will possess a nearly integer relationship with the
            #   remaining peak values.
            #   Cut down to potential frequencies to the frequencies with the top 5 amplitudes
            maximum_amplitudes_indices = np.argpartition(spectrum.pressures_pascals[peak_frequency_indices], -5)[-5:]
            potential_fundamental_frequencies = spectrum.frequencies[peak_frequency_indices[maximum_amplitudes_indices]]

            #   empty array
            sim = np.zeros((5,))

            #   Loop through the frequencies with the top five maximum amplitudes.
            for f_index in range(len(potential_fundamental_frequencies)):
                f = potential_fundamental_frequencies[f_index]

                #   Determine the ratio of selected frequencies. If one is a harmonic then it should possess a near
                #   integer multiple relationship with one of the selected frequencies.
                ratio = potential_fundamental_frequencies / f

                #   correct decimals to whole number integers
                for j in range(len(ratio)):
                    if ratio[j] < 1.0:
                        ratio[j] = 1 / ratio[j]

                #   subtract whole integer from real value and calculate mean across each comp array
                sim[f_index] = (np.mean(np.abs((np.round(ratio, 0) - ratio))))

            return potential_fundamental_frequencies[np.argmin(sim)]

    def _swipe_spectral_estimation(self, x: Spectrum, strength_threshold: float = 0):

        # Compute pitch candidates
        pc = x.frequencies
        loudness = x.pressures_pascals ** 2

        # Normalize loudness
        normalization_loudness = np.full_like(loudness, np.sqrt(np.sum(loudness * loudness, axis=0)))
        with np.errstate(divide='ignore', invalid='ignore'):
            loudness = loudness / normalization_loudness

        # Create pitch salience matrix
        strengths = np.zeros((len(pc),))

        for j in range(0, len(pc)):
            strengths[j] = self.pitch_strength_one(x.frequencies, loudness, pc[j])

        pitch, strength = self.swipe_parabolic_interpolation(strengths, strength_threshold, pc)

        return pitch

    def _yin(self, threshold=0.15):
        """
        Implementation of the YIN algorithm.

        .. [#] Alain De Cheveigné and Hideki Kawahara.
            "YIN, a fundamental frequency estimator for speech and music."
            The Journal of the Acoustical Society of America 111.4 (2002): 1917-1930.

        Parameters
        ----------

        threshold : float
            Threshold for cumulative mean normalized difference function

        Returns
        -------
        f0 : ndarray
            Estimated F0-trajectory
        t : ndarray
            Time axis
        ap: ndarray
            Aperiodicity (indicator for voicing: the lower, the more reliable the estimate)
        """
        Fs = self._waveform.sample_rate
        F_min = self._start_frequency
        F_max = self._stop_frequency
        N = self._window_size
        H = self._hop_size

        if F_min > F_max:
            raise ValueError("F_min must be smaller than F_max!")

        if F_min < Fs / N:
            F_min = Fs / N

        #   Add zeros for centered estimates
        x_pad = np.concatenate((np.zeros(N // 2), self._waveform._samples, np.zeros(N // 2)))

        #   Compute number of estimates that will be generated
        M = int(np.floor((len(x_pad) - N) / H)) + 1

        #   Estimated fundamental frequencies (0 for unspecified frames)
        f0 = np.zeros(M)

        #   Time axis
        t = np.arange(M) * H / Fs

        #   Aperiodicity
        ap = np.zeros(M)

        #   lag of maximal frequency and minimal frequency in samples
        lag_min = max(int(np.ceil(Fs / F_max)), 1)
        lag_max = int(np.ceil(Fs / F_min))

        #   Loop through the estimates that are to be generated
        for m in range(M):
            #   Take a frame from input signal
            frame = x_pad[m * H:m * H + N]

            #   Cumulative Mean Normalized Difference Function
            cmndf = self.cumulative_mean_normalized_difference_function(frame, lag_max)

            #   Absolute Thresholding
            lag_est = self.absolute_thresholding(cmndf, threshold, lag_min, lag_max, parabolic_interp=True)

            #   Refine estimate by constraining search to vicinity of best local estimate (default: +/- 25 cents)
            tol_cents = 25
            lag_min_local = int(np.round(Fs / ((Fs / lag_est) * 2 ** (tol_cents / 1200))))
            if lag_min_local < lag_min:
                lag_min_local = lag_min
            lag_max_local = int(np.round(Fs / ((Fs / lag_est) * 2 ** (-tol_cents / 1200))))
            if lag_max_local > lag_max:
                lag_max_local = lag_max
            lag_new = self.absolute_thresholding(cmndf, threshold=np.inf, lag_min=lag_min_local, lag_max=lag_max_local,
                                                 parabolic_interp=True)

            #   Compute Fundamental Frequency Estimate
            f0[m] = Fs / lag_new

            #   Compute Aperiodicity
            ap[m] = self.aperiodicity(frame, lag_new)

        return f0, t, ap

    @staticmethod
    def swipe_parabolic_interpolation(pitch_strength, strength_threshold, pc):
        """Parabolic interpolation between pitch candidates using pitch strength"""

        i = np.argmax(pitch_strength)
        strength = pitch_strength[i]

        if strength < strength_threshold:
            return np.nan, np.nan

        #   TODO: since the index must be within the array, we can simplify the first two
        #   elements of this control structure.
        if i == 0:
            return pc[0], pitch_strength[0]
        elif i == len(pc) - 1:
            return pc[-1], pitch_strength[-1]
        else:
            I = np.arange(i - 1, i + 2)
            tc = 1 / pc[I]
            ntc = np.dot((tc / tc[1] - 1), 2 * np.pi)
            if np.any(np.isnan(pitch_strength[I])) or np.any(np.isinf(ntc)):
                s = np.nan
                p = np.nan
            else:
                c = np.polyfit(ntc, pitch_strength[I], 2)
                ftc = 1 / 2 ** np.arange(np.log2(pc[I[0]]), np.log2(pc[I[2]]), 1 / 12 / 64)
                nftc = np.dot((ftc / tc[1] - 1), 2 * np.pi)
                poly = np.polyval(c, nftc)
                k = np.argmax(poly)
                s = poly[k]
                p = 2 ** (np.log2(pc[I[0]]) + k / 12 / 64)
            return p, s

    @staticmethod
    def primes(n):
        """Returns a set of n prime numbers"""
        small_primes = np.array(
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89,
             97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181,
             191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
             283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397,
             401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
             509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619,
             631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743,
             751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863,
             877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997])

        b = small_primes <= n
        return small_primes[b]

    @staticmethod
    def pitch_strength_one(erbs_frequencies, normalized_loudness, pitch_candidate):
        """Compute pitch strength for one pitch candidate"""
        number_of_harmonics = np.floor(erbs_frequencies[-1] / pitch_candidate - 0.75).astype(np.int32)
        k = np.zeros(erbs_frequencies.shape)

        # f_prime / f
        q = erbs_frequencies / pitch_candidate

        n = 0
        for i in np.concatenate(([1], FundamentalFrequencyCalculator.primes(number_of_harmonics))):
            a = np.abs(q - i)
            p = a < 0.25
            k[p] = np.cos(np.dot(2 * np.pi, q[p]))
            v = np.logical_and(0.25 < a, a < 0.75)
            k[v] = k[v] + np.cos(np.dot(2 * np.pi, q[v])) / 2
            n += 1

        # Apply envelope
        k = np.multiply(k, np.sqrt(1.0 / erbs_frequencies))

        # K+-normalize kernel
        k = k / np.linalg.norm(k[k > 0])
        if np.isnan(k).any():
            k = np.nan_to_num(k, nan=0)

        # Compute pitch strength
        return np.dot(k, normalized_loudness)

    @staticmethod
    def cumulative_mean_normalized_difference_function(frame, lag_max):
        """
        Computes Cumulative Mean Normalized Difference Function (CMNDF).

        Parameters
        ----------
        frame : ndarray
            Audio frame
        lag_max : int
            Maximum expected lag in the CMNDF

        Returns
        -------
        cmndf : ndarray
            Cumulative Mean Normalized Difference Function
        """

        cmndf = np.zeros(lag_max + 1)  # Initialize CMNDF
        cmndf[0] = 1
        diff_mean = 0

        for tau in range(1, lag_max + 1):
            # Difference function
            diff = np.sum((frame[0:-tau] - frame[0 + tau:]) ** 2)
            # Iterative mean of the difference function
            diff_mean = diff_mean * (tau - 1) / tau + diff / tau

            cmndf[tau] = diff / (diff_mean + np.finfo(np.float64).eps)

        return cmndf

    @staticmethod
    def absolute_thresholding(cmndf, threshold, lag_min, lag_max, parabolic_interp=True):
        """
        Absolute thresholding:
        Set an absolute threshold and choose the smallest value of tau that gives a minimum of d' deeper than that
        threshold. If none is found, the global minimum is chosen instead.

        Parameters
        ----------
        cmndf : ndarray
            Cumulative Mean Normalized Difference Function
        threshold : float
            Threshold
        lag_min : float
            Minimal lag
        lag_max : float
            Maximal lag
        parabolic_interp : bool
            Switch to activate/deactivate parabolic interpolation

        Returns
        -------

        """

        # take shortcut if search range only allows for one possible lag
        if lag_min == lag_max:
            return lag_min

        # find local minima below absolute threshold in interval [lag_min:lag_max]
        local_min_idxs = (np.argwhere((cmndf[1:-1] < cmndf[0:-2]) & (cmndf[1:-1] < cmndf[2:]))).flatten() + 1
        below_thr_idxs = np.argwhere(cmndf[lag_min:lag_max] < threshold).flatten() + lag_min
        # numba compatible intersection of indices sets
        min_idxs = np.unique(np.array([i for i in local_min_idxs for j in below_thr_idxs if i == j]))

        # if no local minima below threshold are found, return global minimum
        if not min_idxs.size:
            return np.argmin(cmndf[lag_min:lag_max]) + lag_min

        # find first local minimum
        lag = np.min(min_idxs)  # choose first local minimum

        # Optional: Parabolic Interpolation of local minima
        if parabolic_interp:
            lag_corr, cmndf[lag] = FundamentalFrequencyCalculator.parabolic_interpolation(
                cmndf[lag - 1], cmndf[lag], cmndf[lag + 1]
            )
            lag += lag_corr

        return lag

    @staticmethod
    def parabolic_interpolation(y1, y2, y3):
        """
        Parabolic interpolation of an extremal value given three samples with equal spacing on the x-axis.
        The middle value y2 is assumed to be the extremal sample of the three.

        Parameters
        ----------
        y1: f(x1)
        y2: f(x2)
        y3: f(x3)

        Returns
        -------
        x_interp: Interpolated x-value (relative to x3-x2)
        y_interp: Interpolated y-value, f(x_interp)
        """

        a = np.finfo(np.float64).eps + (y1 + y3 - 2 * y2) / 2
        b = (y3 - y1) / 2
        x_interp = -b / (2 * a)
        y_interp = y2 - (b ** 2) / (4 * a)

        return x_interp, y_interp

    @staticmethod
    def aperiodicity(frame, lag_est):
        """
        Compute aperiodicity of given frame (serves as indicator for reliability or voicing detection).

        Parameters
        ----------
        frame : ndarray
            Frame
        lag_est : float
            Estimated lag

        Returns
        -------
        ap: float
            Aperiodicity (the lower, the more reliable the estimate)
        """

        lag_int = int(np.floor(lag_est))  # uncorrected period estimate
        frac = lag_est - lag_int  # residual

        # Pad frame to insure constant size
        frame_pad = np.concatenate((frame, np.flip(frame)))  # mirror padding

        # Shift frame by estimated period
        if frac == 0:
            frame_shift = frame_pad[lag_int:lag_int + len(frame)]
        else:
            # linear interpolation between adjacent shifts
            frame_shift = (1 - frac) * frame_pad[lag_int:lag_int + len(frame)] + \
                          frac * frame_pad[lag_int + 1:lag_int + 1 + len(frame)]

        pwr = (np.mean(frame ** 2) + np.mean(frame_shift ** 2)) / 2  # average power over fixed and shifted frame
        res = np.mean((frame - frame_shift) ** 2) / 2  # residual power
        ap = res / (pwr + np.finfo(np.float64).eps)

        return ap
