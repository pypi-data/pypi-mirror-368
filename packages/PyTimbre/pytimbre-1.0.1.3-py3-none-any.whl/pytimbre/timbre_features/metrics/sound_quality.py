import numpy as np
from pytimbre.audio import Waveform
from pytimbre.spectral.spectra import Spectrum
from pytimbre.utilities.audio_filtering import WaveformFilter

class SoundQualityMetrics:
    def __init__(self):
        self._waveform = None
        self._spectrum = None

        self._boominess = None
        self._loudness = None
        self._roughness = None
        self._sharpness = None
        self._integrated_loudness = None
        self._specific_loudness = None

    @property
    def waveform(self):
        return self._waveform

    @property
    def boominess(self):
        return self._boominess

    @property
    def loudness(self):
        return self._loudness

    @property
    def roughness(self):
        return self._roughness

    @property
    def sharpness(self):
        return self._sharpness

    @staticmethod
    def from_waveform(wfm: Waveform):
        sqm = SoundQualityMetrics()
        sqm._waveform = wfm
        sqm._boominess = sqm._wfm_boominess()
        sqm._loudness = sqm._wfm_loudness()
        sqm._roughness = sqm._wfm_roughness()
        sqm._sharpness = sqm._wfm_sharpness()

        return sqm

    def from_spectrum(self, spectra: Spectrum):
        self._spectrum = spectra

    def _wfm_boominess(self):
        """
        This is an implementation of the hasimoto booming index feature. There are a few fudge factors with the code to
        convert between the internal representation of the sound using the same loudness calculation as the sharpness
        code.  The equation for calculating the booming index is not specifically quoted anywhere, so I've done the
        best I
        can with the code that was presented.

        Shin, SH, Ih, JG, Hashimoto, T., and Hatano, S.: "Sound quality evaluation of the booming sensation for
        passenger
        cars", Applied Acoustics, Vol. 70, 2009.

        Hatano, S., and Hashimoto, T. "Booming index as a measure for evaluating booming sensation",
        The 29th International congress and Exhibition on Noise Control Engineering, 2000.

        This function calculates the apparent Boominess of an audio Waveform.

        This version of timbral_booming contains self loudness normalising methods and can accept arrays as an input
        instead of a string filename. (FSM) This current version was modified from the original to use the PyTimbre
        features rather that the soundfile methods for reading the files and use the Waveform.

        Version 0.5

        Returns
        -------
        :returns:
            the boominess of the audio file

        Copyright 2018 Andy Pearce, Institute of Sound Recording, University of Surrey, UK.

        Licensed under the Apache License, Version 2.0 (the "License");
        you may not use this file except in compliance with the License.
        You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

        Unless required by applicable law or agreed to in writing, software
        distributed under the License is distributed on an "AS IS" BASIS,
        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        See the License for the specific language governing permissions and
        limitations under the License.

        Refactored by Dr. Frank Mobley 2023
        """
        from pytimbre.utilities.acoustic_weights import AcousticWeights
        from pytimbre.utilities.fractional_octave_band import FractionalOctaveBandTools

        # window the audio file into 4096 sample sections
        wfm = SoundQualityMetrics.normalize_waveform_loudness(self.waveform, -24, False)
        windowed_audio = wfm.split_by_time(4096 / wfm.sample_rate)

        #   Create the lists that will hold information regarding the various
        windowed_booming = []
        windowed_rms = []

        #   Loop through the windowed audio
        for i in range(windowed_audio.shape[0]):
            # get the rms value and append to list
            windowed_rms.append(np.sqrt(np.mean(windowed_audio[i]._samples ** 2)))

            # calculate the specific loudness
            # n_entire, n_single = windowed_audio[i].specific_loudness
            n_entire, n_single = SoundQualityMetrics.specific_loudness(windowed_audio[i])

            # calculate the booming index if it contains a level
            if n_entire > 0:
                booming_index = AcousticWeights.calculate_boominess(n_single)
            else:
                booming_index = 0

            windowed_booming.append(booming_index)

        # get level of low frequencies
        ll, _ = SoundQualityMetrics._weighted_bark_level(wfm, 0, 70)

        ll = np.log10(ll)

        # convert to numpy arrays for fancy indexing
        windowed_booming = np.array(windowed_booming)
        windowed_rms = np.array(windowed_rms)

        # get the weighted average
        rms_boom = np.average(windowed_booming, weights=(windowed_rms * windowed_rms))
        rms_boom = np.log10(rms_boom)

        # perform the linear regression
        all_metrics = np.ones(3)
        all_metrics[0] = rms_boom
        all_metrics[1] = ll

        coefficients = np.array([43.67402696195865, -10.90054738389845, 26.836530575185435])

        return np.sum(all_metrics * coefficients)

    def _wfm_loudness(self):
        return SoundQualityMetrics.specific_loudness(self.waveform)[0]

    def _wfm_roughness(self):
        """
        This function is an implementation of the Vassilakis [2007] model of roughness.
        The peak picking algorithm implemented is based on the MIR toolbox's implementation.

        This version of timbral_roughness contains self loudness normalising methods and can accept arrays as an input
        instead of a string filename.

        Version 0.4


        Vassilakis, P. 'SRA: A Aeb-based researh tool for spectral and roughness analysis of sound signals', Proceedings
        of the 4th Sound and Music Computing Conference, Lefkada, Greece, July, 2007.

        Required parameter
        :param fname:                 string, Audio filename to be analysed, including full file path and extension.

        Optional parameters
        :param dev_output:            bool, when False return the roughness, when True return all extracted features
                                    (current none).
        :param phase_correction:      bool, if the inter-channel phase should be estimated when performing a mono sum.
                                    Defaults to False.

        :return:                      Roughness of the audio signal.

        Copyright 2018 Andy Pearce, Institute of Sound Recording, University of Surrey, UK.

        Licensed under the Apache License, Version 2.0 (the "License");
        you may not use this file except in compliance with the License.
        You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

        Unless required by applicable law or agreed to in writing, software
        distributed under the License is distributed on an "AS IS" BASIS,
        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        See the License for the specific language governing permissions and
        limitations under the License.

        Refactored into Waveform class by Dr. Frank Mobley, 2023
        """
        from pytimbre.utilities.fractional_octave_band import FractionalOctaveBandTools as fob

        wfm = SoundQualityMetrics.normalize_waveform_loudness(self.waveform, -24.0, False)

        # pad audio
        audio_samples = np.pad(wfm.samples, (512, 0), 'constant', constant_values=(0.0, 0.0))

        '''
          Reshape audio into time windows of 50ms.
        '''
        # reshape audio
        audio_len = len(audio_samples)
        time_step = 0.05
        step_samples = int(self._waveform.sample_rate * time_step)
        nfft = step_samples
        window = np.hamming(nfft + 2)
        window = window[1:-1]
        olap = nfft / 2
        num_frames = int(audio_len / (step_samples - olap))
        next_pow_2 = np.log(step_samples) / np.log(2)
        next_pow_2 = 2 ** int(next_pow_2 + 1)

        reshaped_audio = np.zeros([next_pow_2, num_frames])

        i = 0
        start_idx = int((i * (nfft / 2.0)))

        # check if audio is too short to be reshaped
        if audio_len > step_samples:
            # get all the audio
            while start_idx + step_samples <= audio_len:
                audio_frame = audio_samples[start_idx:start_idx + step_samples]

                # apply window
                audio_frame = audio_frame * window

                # append zeros
                reshaped_audio[:step_samples, i] = audio_frame

                # increase the step
                i += 1
                start_idx = int((i * (nfft / 2.0)))
        else:
            # reshaped audio is just padded audio samples
            reshaped_audio[:audio_len, i] = audio_samples

        spec = np.fft.fft(reshaped_audio, axis=0)
        spec_len = int(next_pow_2 / 2) + 1
        spec = spec[:spec_len, :]
        spec = np.absolute(spec)

        freq = self.waveform.sample_rate / 2 * np.linspace(0, 1, spec_len)

        # normalise spectrogram based from peak TF bin
        norm_spec = (spec - np.min(spec)) / (np.max(spec) - np.min(spec))

        ''' Peak picking algorithm '''
        _, no_segments = np.shape(spec)

        all_peak_levels = list()
        all_peak_frequency = list()

        for i in range(0, no_segments):
            # find peak candidates and add it to the lists for later usage
            _, peak_level, peak_x = fob.detect_peaks(
                norm_spec[:, i],
                cthr=0.01,
                unprocessed_array=spec[:, i],
                freq=freq
            )

            all_peak_frequency.append(peak_x)
            all_peak_levels.append(peak_level)

        all_roughness = list()

        for frame_index in range(len(all_peak_levels)):

            frame_frequency = all_peak_frequency[frame_index]
            frame_level = all_peak_levels[frame_index]

            #   Get the levels and frequencies that we will use to calculate the roughness
            if len(frame_frequency) > 1:
                f2 = np.kron(np.ones([len(frame_frequency), 1]), frame_frequency)
                f1 = f2.T
                v2 = np.kron(np.ones([len(frame_level), 1]), frame_level)
                v1 = v2.T

                X = v1 * v2
                Y = (2 * v2) / (v1 + v2)

                """
                Plomp's algorithm for estimating roughness.

                :param f1:  float, frequency of first frequency of the pair
                :param f2:  float, frequency of second frequency of the pair
                :return:
                """
                b1 = 3.51
                b2 = 5.75
                xstar = 0.24
                s1 = 0.0207
                s2 = 18.96
                s = np.tril(xstar / ((s1 * np.minimum(f1, f2)) + s2))
                Z = np.exp(-b1 * s * np.abs(f2 - f1)) - np.exp(-b2 * s * np.abs(f2 - f1))

                rough = (X ** 0.1) * (0.5 * (Y ** 3.11)) * Z

                all_roughness.append(np.sum(rough))
            else:
                all_roughness.append(0)

        mean_roughness = np.mean(all_roughness)

        '''
          Perform linear regression
        '''
        # cap roughness for low end
        if mean_roughness < 0.01:
            return 0
        else:
            roughness = np.log10(mean_roughness) * 13.98779569 + 48.97606571545886

            return roughness

    def _wfm_sharpness(self):
        """
        This is an implementation of the matlab sharpness function found at:
        https://www.salford.ac.uk/research/sirc/research-groups/acoustics/psychoacoustics/sound-quality-making-products-sound-better/accordion/sound-quality-testing/matlab-codes

        This function calculates the apparent Sharpness of an audio file.
        This version of timbral_sharpness contains self loudness normalising methods and can accept arrays as an input
        instead of a string filename.

        Version 0.4

        Originally coded by Claire Churchill Sep 2004
        Transcoded by Andy Pearce 2018
        Refactored by Dr. Frank Mobley 2023

        :return                         Apparent sharpness of the audio file.


        Copyright 2018 Andy Pearce, Institute of Sound Recording, University of Surrey, UK.

        Licensed under the Apache License, Version 2.0 (the "License");
        you may not use this file except in compliance with the License.
        You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

        Unless required by applicable law or agreed to in writing, software
        distributed under the License is distributed on an "AS IS" BASIS,
        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        See the License for the specific language governing permissions and
        limitations under the License.

        """
        #   Prepare the audio file
        wfm = SoundQualityMetrics.normalize_waveform_loudness(self.waveform, -24.0, False)
        wfm = wfm.split_by_time(4096 / wfm.sample_rate)

        windowed_sharpness = []
        windowed_rms = []
        for i in range(wfm.shape[0]):
            # calculate the rms and append to list
            windowed_rms.append(np.sqrt(np.mean(wfm[i]._samples ** 2)))

            # calculate the specific loudness
            n_entire, n_single = SoundQualityMetrics.specific_loudness(wfm[i])

            # calculate the sharpness if section contains audio
            if n_entire > 0:
                """
                Calculates the sharpness based on FASTL (1991). Expression for weighting function obtained by fitting an
                equation to data given in 'Psychoacoustics: Facts and Models' using MATLAB basic fitting function.

                Original Matlab code by Claire Churchill Sep 2004
                Transcoded by Andy Pearce 2018

                Integrated into PyTimbre by Dr. Frank Mobley 2023
                """
                n = len(n_single)
                gz = np.ones(140)
                z = np.arange(141, n + 1)
                gzz = 0.00012 * (z / 10.0) ** 4 - 0.0056 * (z / 10.0) ** 3 + 0.1 * (z / 10.0) ** 2 - 0.81 * (
                        z / 10.0) + 3.5
                gz = np.concatenate((gz, gzz))
                z = np.arange(0.1, n / 10.0 + 0.1, 0.1)

                sharpness = 0.11 * np.sum(n_single * gz * z * 0.1) / np.sum(n_single * 0.1)
            else:
                sharpness = 0

            windowed_sharpness.append(sharpness)

        # convert lists to numpy arrays for fancy indexing
        windowed_rms = np.array(windowed_rms)
        windowed_sharpness = np.array(windowed_sharpness)

        # calculate the sharpness as the rms-weighted average of sharpness
        rms_sharpness = np.average(windowed_sharpness, weights=(windowed_rms * windowed_rms))

        # take the logarithm to better much subjective ratings
        rms_sharpness = np.log10(rms_sharpness)

        all_metrics = np.ones(2)
        all_metrics[0] = rms_sharpness

        # coefficients from linear regression
        coefficients = [102.50508921364404, 34.432655185001735]

        return np.sum(all_metrics * coefficients)

    @staticmethod
    def integrated_loudness(wfm: Waveform):
        """
        As part of the determination of various values used in the Timbral_models the meter object from pyloudnorm is
        used to determine the integrated loudness. This function will replicate the signal function calculation without
        the majority of the error checking for the mono channel data within the waveform.

        Taken from pyloudnorm.meter.

        Returns
        -------
        Integrated loudness with filters for head and auditory system applied
        """

        wfm = WaveformFilter.apply_head_auditory_response_filters(wfm)
        if wfm._samples.ndim == 1:
            input_data = np.reshape(wfm._samples, (wfm._samples.shape[0], 1))
        else:
            input_data = wfm._samples

        num_channels = input_data.shape[1]
        num_samples = input_data.shape[0]
        block_size = 0.4

        G = [1.0, 1.0, 1.0, 1.41, 1.41]  # channel gains
        t_g = block_size  # 400 ms gating block standard
        gamma_a = -70.0  # -70 LKFS = absolute loudness threshold
        overlap = 0.75  # overlap of 75% of the block duration
        step = 1.0 - overlap  # step size by percentage

        T = num_samples / wfm.sample_rate  # length of the input in seconds
        num_blocks = int(np.round(((T - t_g) / (t_g * step))) + 1)  # total number of gated blocks (see end of eq. 3)
        j_range = np.arange(0, num_blocks)  # indexed list of total blocks
        z = np.zeros(shape=(num_channels, num_blocks))  # instantiate array - transponse of input

        for i in range(num_channels):  # iterate over input channels
            for j in j_range:  # iterate over total frames
                l = int(t_g * (j * step) * wfm.sample_rate)  # lower bound of integration (in samples)
                u = int(t_g * (j * step + 1) * wfm.sample_rate)  # upper bound of integration (in samples)
                # calculate mean square of the filtered for each block (see eq. 1)
                z[i, j] = (1.0 / (t_g * wfm.sample_rate)) * np.sum(np.square(input_data[l:u, i]))

        # loudness for each jth block (see eq. 4)
        l = [-0.691 + 10.0 * np.log10(np.sum([G[i] * z[i, j] for i in range(num_channels)])) for j in j_range]

        # find gating block indices above absolute threshold
        j_g = [j for j, l_j in enumerate(l) if l_j >= gamma_a]

        # calculate the average of z[i,j] as show in eq. 5
        z_avg_gated = [np.mean([z[i, j] for j in j_g]) for i in range(num_channels)]
        # calculate the relative threshold value (see eq. 6)
        gamma_r = -0.691 + 10.0 * np.log10(np.sum([G[i] * z_avg_gated[i] for i in range(num_channels)])) - 10.0

        # find gating block indices above relative and absolute thresholds  (end of eq. 7)
        j_g = [j for j, l_j in enumerate(l) if (l_j > gamma_r and l_j > gamma_a)]

        # calculate the average of z[i,j] as show in eq. 7 with blocks above both thresholds
        z_avg_gated = np.nan_to_num(np.array([np.mean([z[i, j] for j in j_g]) for i in range(num_channels)]))

        return -0.691 + 10.0 * np.log10(np.sum([G[i] * z_avg_gated[i] for i in range(num_channels)]))

    @staticmethod
    def specific_loudness(waveform: Waveform):
        """
        This function originates with the timbral_models package. This is the specific_loudness function from the
        timbral_utils.py. This function calculates loudness in one-third-octave bands based on ISO 532 B / DIN 45631
        source: BASIC code in Journal of Acoustical Society of Japan (E) 12, 1 (1991). This code always calculates the
        value for a free-field

        Returns
        -------
        n_entire = entire loudness[sone]
        n_single = partial loudness[sone / Bark]

        Original Matlab code by Claire Churchill Jun. 2004
        Transcoded by Andy Pearce 2018
        Refactored by Frank Mobley 2023
        """
        from pytimbre.utilities.fractional_octave_band import FractionalOctaveBandTools as fob

        # 'Generally used third-octave band filters show a leakage towards neighbouring filters of about -20 dB. This
        # means that a 70dB, 1 - kHz tone produces the following levels at different centre
        # frequencies: 10dB at 500Hz, 30dB at 630Hz, 50dB at 800Hz and 70dB at 1kHz.
        # P211 Psychoacoustics: Facts and Models, E.Zwicker and H.Fastl
        # (A filter order of 4 gives approx this result)

        # set default
        minimum_frequency = 25
        maximum_frequency = 12500

        #   If the values are too big for the sample rate of the waveform, we must decrease the maximum frequency
        if maximum_frequency > waveform.sample_rate / 2:
            #   Find the band that is closest to the Nyquist frequency, and decrement by one to ensure that we are
            #   below the theoretical limit
            band_idx = fob.exact_band_number(3, waveform.sample_rate / 2) - 1

            maximum_frequency = fob.center_frequency(3, band_idx)

        order = 4

        # filter the audio into appropriate one-third-octave representation
        _, band_pressures_decibels, _ = fob.filter_third_octaves_downsample(
            waveform, 100.0, minimum_frequency, maximum_frequency, order
        )

        # set more defaults for perceptual filters
        # Centre frequencies of 1 / 3 Oct bands(center_frequencies)
        center_frequencies = np.array(
            [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
             1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500]
        )

        # Ranges of 1 / 3 Oct bands for correction at low frequencies according to equal loudness contours
        low_frequency_corrections = np.array([45, 55, 65, 71, 80, 90, 100, 120])

        # Reduction of 1/3 Oct Band levels at low frequencies according to equal loudness contours
        # within the eight ranges defined by low_frequency_corrections(equal_loudness_corrections)
        equal_loudness_corrections = np.array(
            [[-32, -24, -16, -10, -5, 0, -7, -3, 0, -2, 0],
             [-29, -22, -15, -10, -4, 0, -7, -2, 0, -2, 0],
             [-27, -19, -14, -9, -4, 0, -6, -2, 0, -2, 0],
             [-25, -17, -12, -9, -3, 0, -5, -2, 0, -2, 0],
             [-23, -16, -11, -7, -3, 0, -4, -1, 0, -1, 0],
             [-20, -14, -10, -6, -3, 0, -4, -1, 0, -1, 0],
             [-18, -12, -9, -6, -2, 0, -3, -1, 0, -1, 0],
             [-15, -10, -8, -4, -2, 0, -3, -1, 0, -1, 0]]
        )

        # Critical band level at absolute threshold without taking into account the
        # transmission characteristics of the ear
        # Threshold due to internal noise Hearing thresholds for the excitation levels (each number corresponds to a
        # critical band 12.5kHz is not included)
        critical_band_threshold_noise = np.array([30, 18, 12, 8, 7, 6, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])

        # Attenuation representing transmission between free-field and our hearing system
        # Attenuation due to transmission in the middle ear
        # Moore et al disagrees with this being flat for low frequencies
        transmission_attenuation_delta = np.array(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -0.5, -1.6, -3.2, -5.4, -5.6, -4,
             -1.5, 2, 5, 12]
        )

        # Level correction to convert from a free field to a diffuse field(last critical band 12.5 kHz is not included)
        diffuse_field_correction = np.array(
            [0, 0, 0.5, 0.9, 1.2, 1.6, 2.3, 2.8, 3, 2, 0, -1.4, -2, -1.9, -1, 0.5,
             3, 4, 4.3, 4]
        )

        # Correction factor because using third octave band levels(rather than critical bands)
        tob_level_corrections = np.array(
            [-0.25, -0.6, -0.8, -0.8, -0.5, 0, 0.5, 1.1, 1.5, 1.7, 1.8, 1.8, 1.7, 1.6,
             1.4, 1.2, 0.8, 0.5, 0, -0.5]
        )

        # Upper limits of the approximated critical bands
        critical_band_uppler_limits = np.array(
            [0.9, 1.8, 2.8, 3.5, 4.4, 5.4, 6.6, 7.9, 9.2, 10.6, 12.3, 13.8, 15.2,
             16.7, 18.1, 19.3, 20.6, 21.8, 22.7, 23.6, 24]
        )

        # Range of specific loudness for the determination of the steepness of the upper slopes in the specific loudness
        # - critical band rate pattern(used to plot the correct righthand_loudness_slope curve)
        specific_loudness_slopes = np.array(
            [21.5, 18, 15.1, 11.5, 9, 6.1, 4.4, 3.1, 2.13, 1.36, 0.82, 0.42, 0.30,
             0.22, 0.15, 0.10, 0.035, 0]
        )

        # This is used to design the right hand slope of the loudness
        righthand_loudness_slope = np.array(
            [[13.0, 8.2, 6.3, 5.5, 5.5, 5.5, 5.5, 5.5],
             [9.0, 7.5, 6.0, 5.1, 4.5, 4.5, 4.5, 4.5],
             [7.8, 6.7, 5.6, 4.9, 4.4, 3.9, 3.9, 3.9],
             [6.2, 5.4, 4.6, 4.0, 3.5, 3.2, 3.2, 3.2],
             [4.5, 3.8, 3.6, 3.2, 2.9, 2.7, 2.7, 2.7],
             [3.7, 3.0, 2.8, 2.35, 2.2, 2.2, 2.2, 2.2],
             [2.9, 2.3, 2.1, 1.9, 1.8, 1.7, 1.7, 1.7],
             [2.4, 1.7, 1.5, 1.35, 1.3, 1.3, 1.3, 1.3],
             [1.95, 1.45, 1.3, 1.15, 1.1, 1.1, 1.1, 1.1],
             [1.5, 1.2, 0.94, 0.86, 0.82, 0.82, 0.82, 0.82],
             [0.72, 0.67, 0.64, 0.63, 0.62, 0.62, 0.62, 0.62],
             [0.59, 0.53, 0.51, 0.50, 0.42, 0.42, 0.42, 0.42],
             [0.40, 0.33, 0.26, 0.24, 0.24, 0.22, 0.22, 0.22],
             [0.27, 0.21, 0.20, 0.18, 0.17, 0.17, 0.17, 0.17],
             [0.16, 0.15, 0.14, 0.12, 0.11, 0.11, 0.11, 0.11],
             [0.12, 0.11, 0.10, 0.08, 0.08, 0.08, 0.08, 0.08],
             [0.09, 0.08, 0.07, 0.06, 0.06, 0.06, 0.06, 0.05],
             [0.06, 0.05, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02]]
        )

        # apply weighting factors
        Xp = np.zeros(11)
        Ti = np.zeros(11)
        for i in range(11):
            j = 0
            while ((band_pressures_decibels[i] > (low_frequency_corrections[j] - equal_loudness_corrections[j, i])) &
                   (j < 7)):
                j += 1
            Xp[i] = band_pressures_decibels[i] + equal_loudness_corrections[j, i]
            Ti[i] = 10.0 ** (Xp[i] / 10.0)

        # Intensity values in first three critical bands calculated
        critical_band_summation = np.array([np.sum(Ti[0:6]), np.sum(Ti[6:9]), np.sum(Ti[9:11])])

        if np.max(critical_band_summation) > 0.0:
            FNGi = 10 * np.log10(critical_band_summation)
        else:
            FNGi = -1.0 * np.inf
        LCB = np.zeros_like(critical_band_summation)
        for i in range(3):
            if critical_band_summation[i] > 0:
                LCB[i] = FNGi[i]
            else:
                LCB[i] = 0

        # Calculate the main loudness in each critical band
        Le = np.ones(20)
        Lk = np.ones_like(Le)
        Nm = np.ones(21)
        for i in range(20):
            Le[i] = band_pressures_decibels[i + 8]
            if i <= 2:
                Le[i] = LCB[i]
            Lk[i] = Le[i] - transmission_attenuation_delta[i]
            Nm[i] = 0
            if Le[i] > critical_band_threshold_noise[i]:
                Le[i] = Lk[i] - tob_level_corrections[i]
                S = 0.25
                MP1 = 0.0635 * 10.0 ** (0.025 * critical_band_threshold_noise[i])
                MP2 = (1 - S + S * 10 ** (0.1 * (Le[i] - critical_band_threshold_noise[i]))) ** 0.25 - 1
                Nm[i] = MP1 * MP2
                if Nm[i] <= 0:
                    Nm[i] = 0
        Nm[20] = 0

        KORRY = 0.4 + 0.32 * Nm[0] ** 0.2
        if KORRY > 1:
            KORRY = 1

        Nm[0] = Nm[0] * KORRY

        # Add masking curves to the main loudness in each third octave band
        N = 0
        z1 = 0  # critical band rate starts at 0
        n1 = 0  # loudness level starts at 0
        j = 17
        iz = 0
        z = 0.1
        ns = []

        for i in range(21):
            # Determines where to start on the slope
            ig = i - 1
            if ig > 7:
                ig = 7
            control = 1
            while (z1 < critical_band_uppler_limits[i]) | (
                    control == 1):  # critical_band_uppler_limits is the upper limit of the approximated critical band
                # Determines which of the slopes to use
                if n1 < Nm[i]:  # Nm is the main loudness level
                    j = 0
                    while specific_loudness_slopes[j] > Nm[i]:  # the value of j is used below to build a slope
                        j += 1  # j becomes the index at which Nm(i) is first greater than specific_loudness_slopes

                # The flat portions of the loudness graph
                if n1 <= Nm[i]:
                    z2 = critical_band_uppler_limits[i]  # z2 becomes the upper limit of the critical band
                    n2 = Nm[i]
                    N = N + n2 * (z2 - z1)  # Sums the output(n_entire)
                    for k in np.arange(z, z2 + 0.01, 0.1):
                        if not ns:
                            ns.append(n2)
                        else:
                            if iz == len(ns):
                                ns.append(n2)
                            elif iz < len(ns):
                                ns[iz] = n2

                        if k < (z2 - 0.05):
                            iz += 1
                    z = k  # z becomes the last value of k
                    z = round(z * 10) * 0.1

                # The sloped portions of the loudness graph
                if n1 > Nm[i]:
                    n2 = specific_loudness_slopes[j]
                    if n2 < Nm[i]:
                        n2 = Nm[i]
                    dz = (n1 - n2) / righthand_loudness_slope[j, ig]  # righthand_loudness_slope = slopes
                    dz = round(dz * 10) * 0.1
                    if dz == 0:
                        dz = 0.1
                    z2 = z1 + dz
                    if z2 > critical_band_uppler_limits[i]:
                        z2 = critical_band_uppler_limits[i]
                        dz = z2 - z1
                        n2 = n1 - dz * righthand_loudness_slope[j, ig]  # righthand_loudness_slope = slopes
                    N = N + dz * (n1 + n2) / 2.0  # Sums the output(n_entire)
                    for k in np.arange(z, z2 + 0.01, 0.1):
                        if not ns:
                            ns.append(n1 - (k - z1) * righthand_loudness_slope[j, ig])
                        else:
                            if iz == len(ns):
                                ns.append(n1 - (k - z1) * righthand_loudness_slope[j, ig])
                            elif iz < len(ns):
                                ns[iz] = n1 - (k - z1) * righthand_loudness_slope[j, ig]
                        if k < (z2 - 0.05):
                            iz += 1
                    z = k
                    z = round(z * 10) * 0.1
                if n2 == specific_loudness_slopes[j]:
                    j += 1
                if j > 17:
                    j = 17
                n1 = n2
                z1 = z2
                z1 = round(z1 * 10) * 0.1
                control += 1

        if N < 0:
            N = 0

        if N <= 16:
            N = np.floor(N * 1000 + 0.5) / 1000.0
        else:
            N = np.floor(N * 100 + .05) / 100.0

        LN = 40.0 * (N + 0.0005) ** 0.35

        if LN < 3:
            LN = 3

        if N >= 1:
            LN = 10 * np.log10(N) / np.log10(2) + 40

        n_single = np.zeros(240)
        for i in range(240):
            n_single[i] = ns[i]

        n_entire = N
        return n_entire, n_single

    @staticmethod
    def normalize_waveform_loudness(wfm, target_loudness: float = -24.0, inplace: bool = True):
        """
        This function will normalize the data within the waveform to a specific loudness

        Parameters
        ----------
        :param target_loudness:
            The targeted loudness that we are normalizing this audio data to
        :param inplace:
            Boolean flag to determine whether the current object is modified, or a new object is retured

        Returns
        -------

        """

        #   The minimum number of samples is 0.4 seconds
        if wfm.duration < 0.4:
            additional_samples_required = int(np.floor(wfm.sample_rate * 0.4)) - len(wfm._samples)

            wfm._samples = np.pad(wfm._samples, (0, additional_samples_required), 'constant', constant_values=0.0)

        gain = np.power(10.0, (target_loudness - SoundQualityMetrics.integrated_loudness(wfm)) / 20.0)

        if inplace:
            wfm._samples *= gain
        else:
            return Waveform(
                pressures=wfm._samples * gain,
                sample_rate=wfm.sample_rate,
                start_time=wfm.start_time,
                remove_dc_offset=False
            )

    def get_features(self):
        """
        This will collect the different features and return a new dictionary
        :return: The features available
        :rtype: dict
        """

        return {'boominess': self.boominess,
                'loudness': self.loudness,
                'roughness': self.roughness,
                'sharpness': self.sharpness}

    @staticmethod
    def _weighted_bark_level(samples, low_bark_band: int = 0, upper_bark_band: int = 70):
        """
        This function determines the weighted low frequency levels

        :param samples:
            A waveform representing the audio to analyze
        :param low_bark_band:
            The index of the lowest frequency band; default: 0
        :param upper_bark_band:
            The index of the highest frequency band; default: 70

        :return: average_weight, weighted_weight
        """

        samples = samples.split_by_time(4096 / samples.sample_rate)

        # need to define a function for the roughness stimuli, emphasising the 20 - 40 region (of the bark scale)
        mean_bark_band = (low_bark_band + upper_bark_band) / 2.0
        array = np.arange(low_bark_band, upper_bark_band)
        theta = 0.01
        x = (1.0 / (theta * np.sqrt(2.0 * np.pi))) * np.exp(
            (-1.0 * ((array - mean_bark_band) ** 2.0)) / 2.0 * (theta ** 2.0)
            )
        # x = normal_dist(array, theta=0.01, mean=mean_bark_band)
        x -= np.min(x)
        x /= np.max(x)

        weight_array = np.zeros(240)
        weight_array[low_bark_band:upper_bark_band] = x

        windowed_loud_spec = []
        windowed_rms = []
        weighted_vals = []

        for i in range(samples.shape[0]):
            n_entire, n_single = SoundQualityMetrics.specific_loudness(samples[i])

            # append the loudness spec
            windowed_loud_spec.append(n_single)
            windowed_rms.append(np.sqrt(np.mean(samples[i]._samples * samples[i]._samples)))
            weighted_vals.append(np.sum(weight_array * n_single))

        mean_weight = np.mean(weighted_vals)
        weighted_weight = np.average(weighted_vals, weights=windowed_rms)

        return mean_weight, weighted_weight