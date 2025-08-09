import numpy as np
import scipy.signal
from pytimbre.audio import Waveform


class TemporalMetrics:
    """
    This class contains all the elements from the Waveform object that are representations of the waveform or the
    waveform's envelope.
    """

    def __init__(self):
        """
        This function creates the class and instantiates it with the waveform object. It will calculate the various
        envelopes based on the waveform's time series of data.

        :param wfm: the audio waveform
        :type wfm: Waveform
        """

        self._coefficient_count = 12
        self._hop_size_seconds = 0.0029
        self._window_size_seconds = 0.0232
        self._cutoff_frequency = 5
        self._centroid_threshold = 0.15
        self._effective_duration_threshold = 0.4

        self._signal_envelope = None
        self._normal_signal_envelope = None
        self._log_attack = None
        self._increase = None
        self._decrease = None
        self._addresses = None
        self._amplitude_modulation = None
        self._frequency_modulation = None
        self._auto_correlation_coefficients = None
        self._zero_cross_rate = None
        self._temporal_centroid = None
        self._effective_duration = None
        self._temporal_feature_times = None

    @property
    def waveform(self):
        return self._waveform

    @waveform.setter
    def waveform(self, wfm: Waveform):
        self._waveform = wfm

        self._calculate_signal_envelope()

    @property
    def sample_rate(self):
        return self.waveform.sample_rate

    @property
    def amplitude_modulation(self):
        if self._amplitude_modulation is None:
            self._frequency_modulation, self._amplitude_modulation = self.calculate_modulation()
        return self._amplitude_modulation

    @property
    def corrected_a_duration(self):
        if self.waveform.is_impulsive:
            if self._corrected_a_duration is None:
                #   TODO: Need to find this process code to determine how and where it needs to go.
                self._process_analysis()
            return self._corrected_a_duration
        else:
            raise ValueError("This waveform is not impulsive")

    @property
    def a_duration(self):
        """"
        -20220329 - SCC - Fixed code. Was flipping polairty of every signal and couldn't find right zero crossing.
        """

        p2 = self.waveform.samples
        p2 -= np.mean(p2[:400000])
        max_p = np.max(p2)
        max_p_idx = np.argmax(np.abs(p2))

        maximum_pressure = self.samples[max_p_idx]
        if maximum_pressure < 0:
            p2 *= -1

        #   Find the start time for the A-duration, whcih is the first zero-crossing before the peak pressure
        if (max_p_idx > 1) and (max_p_idx <= len(p2)):
            e1 = max_p_idx
        else:
            e1 = 0

        located = False
        while (not located) and (e1 > 0):
            e1 -= 1
            if p2[e1] <= 0:
                located = True
                break

        #   Interpolate to determine a more accurate representation of this time
        if (abs(p2[e1] - p2[e1 + 1]) >= 1e-12) and (located is True):
            at1 = (0 - p2[e1]) / (p2[e1 + 1] - p2[e1]) + e1 + 1
        else:
            at1 = e1

        #   find the end time for the A-duration, which is the last zero-crossing after the peak
        if (max_p_idx > 1) and (max_p_idx <= len(p2)):
            e1 = max_p_idx
        else:
            e1 = 1

        located = False
        while (not located) and (e1 < len(p2)):
            e1 += 1
            if p2[e1] <= 0:
                located = True
                break

        #   Interpolate to determine a more accurate representation of this time
        if (abs(p2[e1] - p2[e1 - 1]) >= 1e-12) and (located is True):
            at2 = (0 - p2[e1 - 1]) / (p2[e1] - p2[e1 - 1]) + e1
        else:
            at2 = e1

        return (at2 - at1) / self.waveform.sample_rate

    @property
    def attack(self):
        if self._addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._addresses = self.calculate_log_attack()

        return self._addresses[0]

    @property
    def attack_slope(self):
        """
        The attack slope is defined as the average temporal slope of the energy during the attack segment. We compute
        the local slopes of the energy corresponding to each effort w_i. We then compute a weighted average of the
        slopes. The weights are chosen in order to emphasize slope values in the middle of the attack (the weights are
        the values of a Gaussian function centered around the threshold = 50% and with a standard-deviation of 0.5).
        """
        if self._addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._addresses = self.calculate_log_attack()

        return self._increase

    @property
    def auto_correlation(self):
        if self._auto_correlation_coefficients is None:
            self._temporal_feature_times, self._auto_correlation_coefficients, self._zero_cross_rate = \
                self.instantaneous_temporal_features()
        return self._auto_correlation_coefficients

    @property
    def centroid_threshold(self):
        return self._centroid_threshold

    @property
    def cutoff_frequency(self):
        return self._cutoff_frequency

    @cutoff_frequency.setter
    def cutoff_frequency(self, value):
        self._cutoff_frequency = value

    @property
    def coefficient_count(self):
        """
        The number of coefficients to generate for the available data
        """

        return self._coefficient_count

    @coefficient_count.setter
    def coefficient_count(self, value):
        """
        Set the number of coefficients for the analysis
        """

        self._coefficient_count = value

    @property
    def effective_duration_threshold(self):
        return self._effective_duration_threshold

    @property
    def hop_size_samples(self):
        return int(round(self.hop_size_seconds * self.sample_rate))

    @property
    def hop_size_seconds(self):
        return self._hop_size_seconds

    @hop_size_seconds.setter
    def hop_size_seconds(self, value):
        self._hop_size_seconds = value

    @property
    def window_size_seconds(self):
        return self._window_size_seconds

    @window_size_seconds.setter
    def window_size_seconds(self, value):
        self._window_size_seconds = value

    @property
    def window_size_samples(self):
        return int(np.round(self.window_size_seconds * self.sample_rate))

    @property
    def decrease(self):
        if self._addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._addresses = self.calculate_log_attack()

        return self._addresses[1]

    @property
    def release(self):
        if self._addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._addresses = self.calculate_log_attack()

        return self._addresses[4]

    @property
    def log_attack(self):
        """
        The log-attack-time is simply defined as LAT = log_10(t[-1]-t[0])
        """
        if self._addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._addresses = self.calculate_log_attack()

        return self._log_attack

    @property
    def decrease_slope(self):
        """
        The temporal decrease is a measure of the rate of decrease of the signal energy. It distinguishes non-sustained
        (e.g. percussive, pizzicato) sounds from sustained sounds. Its calculation is based on a decreasing exponential
        model of the energy envelope starting from it maximum.
        """
        if self._addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._addresses = self.calculate_log_attack()

        return self._decrease

    @property
    def temporal_centroid(self):
        """
        The temporal centroid is the center of gravity of the energy envelope. It distinguishes percussive from
        sustained sounds. It has been proven to be a perceptually important descriptor (Peeters et al., 2000).
        """
        if self._temporal_centroid is None:
            self._calculate_signal_envelope()
            self._temporal_centroid = self.calculate_temporal_centroid()

        return self._temporal_centroid

    @property
    def effective_duration(self):
        """
        The effective duration is a measure intended to reflect the perceived duration of the signal. It distinguishes
        percussive sounds from sustained sounds but depends on the event duration. It is approximated by the time the
        energy envelop is above a given threshold. After many empirical tests, we have set this threshold to 40%
        """
        if self._effective_duration is None:
            self._calculate_signal_envelope()
            self._effective_duration = self.calculate_effective_duration()

        return self._effective_duration

    @property
    def frequency_modulation(self):
        if self._frequency_modulation is None:
            self._frequency_modulation, self._amplitude_modulation = self.calculate_modulation()
        return self._frequency_modulation

    @property
    def zero_crossing_rate(self):
        if self._zero_cross_rate is None:
            self._temporal_feature_times, self._auto_correlation_coefficients, self._zero_cross_rate = \
                self.instantaneous_temporal_features()
        return self._zero_cross_rate


    @property
    def signal_envelope(self):
        if self._signal_envelope is None:
            self._calculate_signal_envelope()

        return self._signal_envelope

    @property
    def normal_signal_envelope(self):
        if self._normal_signal_envelope is None:
            self._calculate_signal_envelope()

        return self._normal_signal_envelope

    def _find_attack_endpoints(self, position_value, percent_step, method: int = 3):
        """
        Determine the start and stop positions based on selected method.
        Methods 1 and 2 are using fixed thresholds to estimate the end position. According to Peeters, these are found
        insufficiently robust with real signals. As such he proposed a "weakest-effort method" in 2004 to estimate
        the indices for the start and stop of the attack.

        Parameters
        ----------
        :param position_value:
        :param percent_step:
        :param method: The method for determining the attack endpoints
        :type method: int
        """

        start_attack_position = None
        end_attack_position = None

        if method == 1:  # Equivalent to a value of 80%
            start_attack_position = position_value[0]
            end_attack_position = position_value[int(np.floor(0.8 / percent_step))]
        elif method == 2:  # Equivalent to a value of 100%
            start_attack_position = position_value[0]
            end_attack_position = position_value[int(np.floor(1.0 / percent_step))]
        elif method == 3:
            #   Calculate the position for each threshold
            percent_value_value = np.arange(percent_step, 1 + percent_step, percent_step)
            percent_value_position = np.zeros(percent_value_value.shape)

            for p in range(len(percent_value_value)):
                percent_value_position[p] = np.nonzero(self.normal_signal_envelope >= percent_value_value[p])[0][0]

            #   Define parameters for the calculation of the search for the start and stop of the attack
            #
            #   The terminations for the mean calculation
            m1 = int(round(0.3 / percent_step)) - 1
            m2 = int(round(0.6 / percent_step))

            #   define the multiplicative factor for the effort
            multiplier = 3

            #   Terminations for the start attack correction
            s1att = int(round(0.1 / percent_step)) - 1
            s2att = int(round(0.3 / percent_step))

            #   Terminations for the end attack correction
            e1att = int(round(0.5 / percent_step)) - 1
            e2att = int(round(0.9 / percent_step))

            #   Calculate the effort as the effective difference in adjacent position values
            percent_position_value = np.diff(percent_value_position)

            #   Determine the average effort
            M = np.mean(percent_position_value[m1:m2])

            #   Start the start attack calculation
            #   we start just after the effort to be made (temporal gap between percent) is too large
            position2_value = np.nonzero(percent_position_value[s1att:s2att] > multiplier * M)[0]

            if len(position2_value) > 0:
                index = int(np.floor(position2_value[-1] + s1att))
            else:
                index = int(np.floor(s1att))

            start_attack_position = percent_value_position[index]

            #   refinement: we are looking for the local minimum
            delta = int(np.round(0.25 * (percent_value_position[index + 1] - percent_value_position[index]))) - 1
            n = int(np.floor(percent_value_position[index]))

            if delta == 0:
                min_position = n
                end_attack_position = 2 * n
            elif n - delta >= 0:
                min_position = np.argmin(self.normal_signal_envelope[n - delta:n + delta])
                start_attack_position = min_position + n - delta - 1

            #   Start the end attack calculation
            #   we STOP JUST BEFORE the effort to be made (temporal gap between percent) is too large
            position2_value = np.nonzero(percent_position_value[e1att:e2att] > multiplier * M)[0]

            if len(position2_value) > 0:
                index = int(np.floor(position2_value[0] + e1att))
            else:
                index = int(np.floor(e1att))

            end_attack_position = percent_value_position[index]

            #   refinement: we are looking for the local minimum
            delta = int(np.round(0.25 * (percent_value_position[index] - percent_value_position[index - 1])))
            n = int(np.floor(percent_value_position[index]))

            if delta == 0:
                min_position = n
                end_attack_position = 2 * n
            elif n - delta >= 0:
                min_position = np.argmax(self.normal_signal_envelope[n - delta:n + delta + 1])
                end_attack_position = min_position + n - delta

        return start_attack_position, end_attack_position

    def _calculate_signal_envelope(self):
        #   Calculate the energy envelope of the signal that is required for many of the features

        analytic_signal = scipy.signal.hilbert(self.waveform.samples)
        amplitude_modulation = np.abs(analytic_signal)
        normalized_freq = self.cutoff_frequency / (self.sample_rate / 2)
        sos = scipy.signal.butter(3, normalized_freq, btype='low', analog=False, output='sos')
        self._signal_envelope = scipy.signal.sosfilt(sos, amplitude_modulation)

        #   Normalize the envelope

        self._normal_signal_envelope = (self.signal_envelope - self.signal_envelope.min()) / np.ptp(
            self.signal_envelope
        )

    def calculate_temporal_centroid(self):

        env_max_idx = np.argmax(self.signal_envelope)
        over_threshold_idcs = np.nonzero(self.normal_signal_envelope > self.centroid_threshold)[0]

        over_threshold_start_idx = over_threshold_idcs[0]
        if over_threshold_start_idx == env_max_idx:
            over_threshold_start_idx = over_threshold_start_idx - 1

        over_threshold_end_idx = over_threshold_idcs[-1]

        over_threshold_tee = self.signal_envelope[over_threshold_start_idx - 1:over_threshold_end_idx - 1]
        over_threshold_support = [*range(len(over_threshold_tee))]
        over_threshold_mean = np.divide(
            np.sum(np.multiply(over_threshold_support, over_threshold_tee)),
            np.sum(over_threshold_tee)
        )

        temporal_threshold = ((over_threshold_start_idx + 1 + over_threshold_mean) / self.sample_rate)

        return temporal_threshold

    def calculate_effective_duration(self):

        env_max_idx = np.argmax(self.signal_envelope)
        over_threshold_idcs = np.nonzero(self.normal_signal_envelope > self.effective_duration_threshold)[0]

        over_threshold_start_idx = over_threshold_idcs[0]
        if over_threshold_start_idx == env_max_idx:
            over_threshold_start_idx = over_threshold_start_idx - 1

        over_threshold_end_idx = over_threshold_idcs[-1]

        return (over_threshold_end_idx - over_threshold_start_idx + 1) / self.sample_rate

    def instantaneous_temporal_features(self):
        """
        This function will calculate the instantaneous features within the temporal analysis.  This includes the
        auto-correlation and the zero crossing rate.
        """
        import statsmodels.api as sm

        temporal_feature_times = np.zeros(
            (int(np.floor((len(self.waveform.samples) - self.window_size_samples) / self.hop_size_samples) + 1),)
        )

        auto_coefficients = np.zeros((len(temporal_feature_times), self.coefficient_count))
        zero_crossing_rate = np.zeros((len(temporal_feature_times),))

        #   Loop through the frames
        for n in range(0, len(temporal_feature_times)):
            #   Get the frame
            frame_length = self.window_size_samples
            start = n * self.hop_size_samples
            frame_index = np.arange(start, frame_length + start)
            f_frm_v = self.waveform.samples[frame_index] * np.hamming(self.window_size_samples)
            temporal_feature_times[n] = n * self.hop_size_seconds

            #   Calculate the auto correlation coefficients
            auto_coefficients[n, :] = sm.tsa.acf(f_frm_v, nlags=self.coefficient_count, fft=False)[1:]

            #   Now the zero crossing rate

            i_sign_v = np.sign(f_frm_v - np.mean(f_frm_v))
            i_zcr_v = np.nonzero(np.diff(i_sign_v))[0]
            i_num_zcr = len(i_zcr_v)
            zero_crossing_rate[n] = i_num_zcr / (len(f_frm_v) / self.sample_rate)

        return temporal_feature_times, auto_coefficients, zero_crossing_rate

    def calculate_modulation(self):
        """
        Calculate the frequency/amplitude modulations of the signal.  This can be accomplished with either a Fourier or
        Hilbert method.
        """

        sample_times = np.arange(len(self.signal_envelope) - 1) / self.sample_rate

        if self._addresses is None:
            self._log_attack, self._increase, self._decrease, self._addresses = self.calculate_log_attack()

        sustain_start_time = self._addresses[1]
        sustain_end_time = self._addresses[4]

        is_sustained = False

        if (sustain_end_time - sustain_start_time) > 0.02:
            pos_v = np.nonzero((sustain_start_time <= sample_times) & (sample_times <= sustain_end_time))[0]
            if len(pos_v) > 0:
                is_sustained = True
        else:
            pos_v = np.arange(len(self.normal_signal_envelope))

        if not is_sustained:
            amplitude_modulation = 0
            frequency_modulation = 0
        else:
            envelop_v = self.normal_signal_envelope[pos_v].copy()
            envelop_v[envelop_v <= 0] = np.finfo(envelop_v.dtype).eps
            temps_sec_v = sample_times[pos_v]

            #   Taking the envelope
            y_matrix = np.array([np.sum(np.log(envelop_v)), np.sum(temps_sec_v * np.log(envelop_v))])
            x_matrix = np.array(
                [len(temps_sec_v), np.sum(temps_sec_v),
                 np.sum(temps_sec_v), np.sum(temps_sec_v ** 2)]
            ).reshape((2, 2))
            mon_poly = np.linalg.pinv(x_matrix).dot(y_matrix)
            hat_envelope_v = np.exp(np.polyval(mon_poly[::-1], temps_sec_v))
            signal_v = envelop_v - hat_envelope_v

            sa_v = scipy.signal.hilbert(signal_v)
            sa_amplitude_v = abs(signal_v)
            sa_phase_v = np.unwrap(np.angle(sa_v))
            sa_instantaneous_frequency = (1 / 2 / np.pi) * sa_phase_v / (len(temps_sec_v) / self.sample_rate)

            amplitude_modulation = np.median(sa_amplitude_v)
            frequency_modulation = np.median(sa_instantaneous_frequency)

        return frequency_modulation, amplitude_modulation

    def calculate_log_attack(self):
        """
        This calculates the various global attributes.

        In some cases the calculation of the attack did not return an array, so the error is trapped for when a
        single values is returned rather than an array.

        20230318 - FSM - According to the paper on the Timbre Toolbox, the thresholds were to be estimated on the
        maximum value of the energy envelope, not the values at the start and end of the attack. This was addressed
        in the determination of the value of the threshold.
        """

        import sys

        if self.normal_signal_envelope is None:
            self._calculate_signal_envelope()

        #   Define some specific constants for this calculation
        noise_threshold = 0.15
        decrease_threshold = 0.4
        percent_step = 0.1

        #   Detection of the start (start_attack_position) and stop (end_attack_position) of the attack
        position_value = np.nonzero(self.normal_signal_envelope > noise_threshold)[0]
        start_attack_position, end_attack_position = self._find_attack_endpoints(position_value, percent_step, method=3)

        #   Calculate the Log-attack time
        if start_attack_position == end_attack_position:
            start_attack_position -= 1
        elif start_attack_position < 0 or end_attack_position < 0:
            for method_index in range(1, 3):
                start_attack_position, end_attack_position = self._find_attack_endpoints(
                    position_value, percent_step, method=method_index
                )
                if start_attack_position >= 0 and end_attack_position > 0:
                    break
            if not (start_attack_position >= 0 and end_attack_position > 0):
                raise ValueError("There was a problem determining the starting/ending index of the attack")

        rise_time_n = end_attack_position - start_attack_position
        log_attack_time = np.log10(rise_time_n / self.sample_rate)

        #   Calculate the temporal growth - New 13 Jan 2003
        #   weighted average (Gaussian centered on percent=50%) slopes between start_attack_position and
        #   end_attack_position
        start_attack_position = int(np.round(start_attack_position))
        end_attack_position = int(np.round(end_attack_position))

        if end_attack_position <= start_attack_position or end_attack_position == start_attack_position:
            end_attack_position = start_attack_position + 1

        #   Now that we have determined where the attack occurs, we must define a set of thresholds as a proportion
        #   of the maximum pf the energy envelop. To ensure that the value is within the attack range, we seek for
        #   the maximum within this region.
        threshold_value = np.arange(0.1, 1.1, 0.1)
        threshold_value *= np.max(self.normal_signal_envelope[start_attack_position:end_attack_position])
        threshold_position_seconds = np.zeros(np.size(threshold_value))
        for i in range(len(threshold_value)):
            #   Find the index within the envelope where the value is greater than the selected threshold value
            idx = np.nonzero(
                self.normal_signal_envelope[start_attack_position:end_attack_position] >=
                threshold_value[i]
            )[0]

            if len(idx) > 0:
                threshold_position_seconds[i] = idx[0] / self.sample_rate

        slopes = np.divide(np.diff(threshold_value), np.diff(threshold_position_seconds) + sys.float_info.epsilon)

        #   Calculate the increase
        thresholds = (threshold_value[:-1] + threshold_value[1:]) / 2
        weights = np.exp(-(thresholds - 0.5) ** 2 / (0.5 ** 2))
        increase = np.sum(np.dot(slopes, weights)) / np.sum(weights)

        #   Calculate the time decay

        envelope_max_index = np.nonzero(self.normal_signal_envelope == np.max(self.normal_signal_envelope))[0]
        envelope_max_index = int(np.round(0.5 * (envelope_max_index + end_attack_position)))

        stop_position = np.nonzero(self.normal_signal_envelope > decrease_threshold)[0][-1]

        if envelope_max_index == stop_position:
            if stop_position < len(self.normal_signal_envelope):
                stop_position += 1
            elif envelope_max_index > 1:
                envelope_max_index -= 1

        #   Calculate the decrease
        X = np.arange(envelope_max_index, stop_position) / self.sample_rate
        x_index = np.arange(envelope_max_index, stop_position)
        env = self.normal_signal_envelope[x_index].copy()
        env[env <= 0] = np.finfo(env.dtype).eps
        Y = np.log(env)
        y_matrix = np.array([np.sum(Y), np.sum(X * Y)])
        x_matrix = np.array([len(X), np.sum(X), np.sum(X), np.sum(X ** 2)]).reshape((2, 2))
        polynomial_fit = np.linalg.pinv(x_matrix).dot(y_matrix)
        decrease = polynomial_fit[0]

        #   Create the list of addresses that we are interested in storing for later consumption

        addresses = np.array([start_attack_position, envelope_max_index, 0, 0, stop_position]) / self.sample_rate

        return log_attack_time, increase, decrease, addresses

    def get_features(self):
        """
        This function calculates the various features within the global time analysis and stores the results in the
        class object.  At the end, a dictionary of the values is available and returned to the calling function.

        Returns
        -------
        features : dict()
            The dictionary containing the various values calculated within this method.


        Remarks
        -------
        2024-Sept-10 - FSM Adjusted the function to take in the boolean on whether the temporal features were calculated
        and adjusted the creation of the data dictionary that is returned.
        """

        features = dict()

        if self.waveform.is_continuous:
            #   Create the dictionary that will hold the data for return to the user
            features['attack'] = self.attack
            features['decrease'] = self.decrease
            features['release'] = self.release
            features['log_attack'] = self.log_attack
            features['attack slope'] = self.attack_slope
            features['decrease slope'] = self.decrease_slope
            features['temporal centroid'] = self.temporal_centroid
            features['effective duration'] = self.effective_duration
            features['amplitude modulation'] = self.amplitude_modulation
            features['frequency modulation'] = self.frequency_modulation
            features['auto-correlation_01'] = np.mean(self.auto_correlation, axis=0)[0]
            features['auto-correlation_02'] = np.mean(self.auto_correlation, axis=0)[1]
            features['auto-correlation_03'] = np.mean(self.auto_correlation, axis=0)[2]
            features['auto-correlation_04'] = np.mean(self.auto_correlation, axis=0)[3]
            features['auto-correlation_05'] = np.mean(self.auto_correlation, axis=0)[4]
            features['auto-correlation_06'] = np.mean(self.auto_correlation, axis=0)[5]
            features['auto-correlation_07'] = np.mean(self.auto_correlation, axis=0)[6]
            features['auto-correlation_08'] = np.mean(self.auto_correlation, axis=0)[7]
            features['auto-correlation_09'] = np.mean(self.auto_correlation, axis=0)[8]
            features['auto-correlation_10'] = np.mean(self.auto_correlation, axis=0)[9]
            features['auto-correlation_11'] = np.mean(self.auto_correlation, axis=0)[10]
            features['auto-correlation_12'] = np.mean(self.auto_correlation, axis=0)[11]
            features['zero crossing rate'] = np.mean(self.zero_crossing_rate)
            #
            # if include_sq_metrics:
            #     features['boominess'] = self.boominess
            #     features['loudness'] = self.loudness
            #     features['roughness'] = self.roughness
            #     features['sharpness'] = self.sharpness
            #
            # if include_speech_features:
            #     from python_speech_features import mfcc, fbank, ssc, logfbank
            #     window_length = 0.025
            #     nfft = 512
            #     frame_length = self.sample_rate * window_length
            #     if frame_length > nfft:
            #         nfft = int(np.floor(2 ** (np.ceil(np.log2(frame_length)))))
            #     vect = np.mean(mfcc(self.samples, self.sample_rate, winlen=window_length, nfft=nfft), axis=0)
            #     for index in range(len(vect)):
            #         features['mfcc_{:02.0f}'.format(index)] = vect[index]
            #
            #     vect = np.mean(ssc(self.samples, self.sample_rate, winlen=window_length, nfft=nfft), axis=0)
            #     for index in range(len(vect)):
            #         features['ssc_{:02.0f}'.format(index)] = vect[index]

        # elif self.waveform.is_impulsive:
        #     features = {'a-duration': self.a_duration}
        # 'equivalent level (T)': self.leqT,
        # 'equivalent level a-weighted (T)': self.liaeqT,
        # 'equivalent level a-weighted (8 hr)': self.liaeq8hr,
        # 'equivalent level a-weighted (100ms)': self.liaeq100ms,
        # 'peak level (dB)': self.peak_level,
        # 'peak pressure (Pa)': self.peak_pressure,
        # 'sound exposure level': self.SEL,
        # 'a-weighted sound exposure level': self.SELA}

        return features

    @staticmethod
    def from_waveform(wfm: Waveform):
        tm = TemporalMetrics()
        tm.waveform = wfm

        return tm