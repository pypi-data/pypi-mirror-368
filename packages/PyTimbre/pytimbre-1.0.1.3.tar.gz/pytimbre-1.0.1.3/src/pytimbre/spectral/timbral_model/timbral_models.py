from pytimbre.waveform import Waveform
from pytimbre.spectral.spectra import Spectrum
import numpy as np
from pytimbre.spectral.timbral_model.timbral_util import *


class TimbralFeatures:
    """
    This collection of code was extracted from the Timbral_model package. The code is refactored to use the PyTimbre
    classes to read/write the audio data. Rather than using a series of different files and individual functions,
    this will combine all required functions into a single file and class.
    """

    @staticmethod
    def timbral_brightness(
            fname, fs=0, dev_output=False, clip_output=False, phase_correction=False, threshold=0,
            ratio_crossover=2000, centroid_crossover=100, stepSize=1024, blockSize=2048, minFreq=20
            ):
        """
          This function calculates the apparent Brightness of an audio file.
          This version of timbral_brightness contains self loudness normalising methods and can accept arrays as an input
          instead of a string filename.

          Version 0.4

          Required parameter
           :param fname:               string or numpy array
                                       string, audio filename to be analysed, including full file path and extension.
                                       numpy array, array of audio samples, requires fs to be set to the sample rate.

          Optional parameters
           :param fs:                  int/float, when fname is a numpy array, this is a required to be the sample rate.
                                       Defaults to 0.
           :param dev_output:          bool, when False return the brightness, when True return all extracted features.
           :param clip_output:         bool, force the output to be between 0 and 100.
           :param phase_correction:    bool, Perform phase checking before summing to mono.
           :param threshold:           Threshold below which to ignore the energy in a time window, default to 0.
           :param ratio_crossover:     Crossover frequency for calculating the HF energy ratio, default to 2000 Hz.
           :param centroid_crossover:  Highpass frequency for calculating the spectral centroid, default to 100 Hz.
           :param stepSize:            Step size for calculating spectrogram, default to 1024.
           :param blockSize:           Block size (fft length) for calculating spectrogram, default to 2048.
           :param minFreq:             Frequency for high-pass filtering audio prior to all analysis, default to 20 Hz.

           :return:                    Apparent brightness of audio file, float.

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
        '''
          Read input
        '''
        audio_samples, fs = timbral_util.file_read(fname, fs, phase_correction=phase_correction)

        '''
          Filter audio
        '''
        # highpass audio at minimum frequency
        audio_samples = timbral_util.filter_audio_highpass(audio_samples, crossover=minFreq, fs=fs)
        audio_samples = timbral_util.filter_audio_highpass(audio_samples, crossover=minFreq, fs=fs)
        audio_samples = timbral_util.filter_audio_highpass(audio_samples, crossover=minFreq, fs=fs)

        # get highpass audio at ratio crossover
        ratio_highpass_audio = timbral_util.filter_audio_highpass(audio_samples, ratio_crossover, fs)
        ratio_highpass_audio = timbral_util.filter_audio_highpass(ratio_highpass_audio, ratio_crossover, fs)
        ratio_highpass_audio = timbral_util.filter_audio_highpass(ratio_highpass_audio, ratio_crossover, fs)

        # get highpass audio at centroid crossover
        centroid_highpass_audio = timbral_util.filter_audio_highpass(audio_samples, centroid_crossover, fs)
        centroid_highpass_audio = timbral_util.filter_audio_highpass(centroid_highpass_audio, centroid_crossover, fs)
        centroid_highpass_audio = timbral_util.filter_audio_highpass(centroid_highpass_audio, centroid_crossover, fs)

        '''
         Get spectrograms 
        '''
        # normalise audio to the maximum value in the unfiltered audio
        ratio_highpass_audio *= (1.0 / max(abs(audio_samples)))
        centroid_highpass_audio *= (1.0 / max(abs(audio_samples)))
        audio_samples *= (1.0 / max(abs(audio_samples)))

        # set FFT parameters
        nfft = blockSize
        hop_size = int(3 * nfft / 4)

        # check that audio is long enough to generate spectrograms
        if len(audio_samples) >= nfft:
            # get spectrogram
            ratio_all_freq, ratio_all_time, ratio_all_spec = spectrogram(
                audio_samples, fs, 'hamming', nfft,
                hop_size, nfft, 'constant', True, 'spectrum'
                )
            ratio_hp_freq, ratio_hp_time, ratio_hp_spec = spectrogram(
                ratio_highpass_audio, fs, 'hamming', nfft,
                hop_size, nfft, 'constant', True, 'spectrum'
                )
            centroid_hp_freq, centroid_hp_time, centroid_hp_spec = spectrogram(
                centroid_highpass_audio, fs, 'hamming', nfft,
                hop_size, nfft, 'constant', True, 'spectrum'
                )
        else:
            ratio_all_freq, ratio_all_time, ratio_all_spec = spectrogram(
                audio_samples, fs, 'hamming',
                len(audio_samples),
                len(audio_samples) - 1,
                nfft, 'constant', True, 'spectrum'
                )
            ratio_hp_freq, ratio_hp_time, ratio_hp_spec = spectrogram(
                ratio_highpass_audio, fs, 'hamming',
                len(ratio_highpass_audio),
                len(ratio_highpass_audio) - 1,
                nfft, 'constant', True, 'spectrum'
                )
            centroid_hp_freq, centroid_hp_time, centroid_hp_spec = spectrogram(
                centroid_highpass_audio, fs, 'hamming',
                len(centroid_highpass_audio),
                len(centroid_highpass_audio) - 1,
                nfft, 'constant', True, 'spectrum'
                )

        # initialise variables for storing data
        all_ratio = []
        all_hp_centroid = []
        all_tpower = []
        all_hp_centroid_tpower = []

        # set threshold level at zero
        threshold_db = threshold
        if threshold_db == 0:
            threshold = 0
            hp_threshold = 0
        else:
            max_power = max(np.sum(ratio_all_spec, axis=1))
            threshold = max_power * timbral_util.db2mag(threshold_db)
            # get the threshold for centroid
            # centroid_hp_max_power = max(np.sum(centroid_hp_spec, axis=1))
            # hp_min_power = min(np.sum(hp_spec, axis=1))
            # hp_threshold = hp_max_power * timbral_util.db2mag(threshold_db)
        # threshold = 0.0

        '''
          Calculate features for each time window
        '''
        for idx in range(len(ratio_hp_time)):  #
            # get the current spectrum for this time window
            current_ratio_hp_spec = ratio_hp_spec[:, idx]
            current_ratio_all_spec = ratio_all_spec[:, idx]
            current_centroid_hp_spec = centroid_hp_spec[:, idx]

            # get the power within each spectrum
            tpower = np.sum(current_ratio_all_spec)
            hp_tpower = np.sum(current_ratio_hp_spec)
            # check there is energy in the time window before calculating the ratio (greater than 0)
            if tpower > threshold:
                # get the ratio
                all_ratio.append(hp_tpower / tpower)
                # store the powef for weighting
                all_tpower.append(tpower)

            # get the tpower to assure greater than zero
            hp_centroid_tpower = np.sum(current_centroid_hp_spec)
            if hp_centroid_tpower > 0.0:
                # get the centroid
                all_hp_centroid.append(
                    np.sum(current_centroid_hp_spec * centroid_hp_freq[:len(current_centroid_hp_spec)]) /
                    np.sum(current_centroid_hp_spec)
                    )
                # store the tpower for weighting
                all_hp_centroid_tpower.append(hp_centroid_tpower)

        '''
          Get mean and weighted average values
        '''
        mean_ratio = np.mean(all_ratio)
        mean_hp_centroid = np.mean(all_hp_centroid)

        weighted_mean_ratio = np.average(all_ratio, weights=all_tpower)
        weighted_mean_hp_centroid = np.average(all_hp_centroid, weights=all_hp_centroid_tpower)

        if dev_output:
            # return the ratio and centroid
            return np.log10(weighted_mean_ratio), np.log10(weighted_mean_hp_centroid)
        else:
            # perform thye linear regression
            all_metrics = np.ones(3)
            all_metrics[0] = np.log10(weighted_mean_ratio)
            all_metrics[1] = np.log10(weighted_mean_hp_centroid)
            # all_metrics[2] = np.log10(weighted_mean_ratio) * np.log10(weighted_mean_hp_centroid)

            coefficients = np.array([4.613128018020465, 17.378889309312974, 17.434733750553022])

            # coefficients = np.array([-2.9197705625030235, 9.048261758526614, 3.940747859061009, 47.989783427908705])
            bright = np.sum(all_metrics * coefficients)

            if clip_output:
                bright = timbral_util.output_clip(bright)

            return bright

    @staticmethod
    def timbral_depth(
            fname, fs=0, dev_output=False, phase_correction=False, clip_output=False, threshold_db=-60,
            low_frequency_limit=20, centroid_crossover_frequency=2000, ratio_crossover_frequency=500,
            db_decay_threshold=-40
            ):
        """
         This function calculates the apparent Depth of an audio file.
         This version of timbral_depth contains self loudness normalising methods and can accept arrays as an input
         instead of a string filename.

         Version 0.4

         Required parameter
          :param fname:                        string or numpy array
                                               string, audio filename to be analysed, including full file path and extension.
                                               numpy array, array of audio samples, requires fs to be set to the sample rate.

         Optional parameters
          :param fs:                           int/float, when fname is a numpy array, this is a required to be the sample rate.
                                               Defaults to 0.
          :param phase_correction:             bool, perform phase checking before summing to mono.  Defaults to False.
          :param dev_output:                   bool, when False return the depth, when True return all extracted
                                               features.  Default to False.
          :param threshold_db:                 float/int (negative), threshold, in dB, for calculating centroids.
                                               Should be negative.  Defaults to -60.
          :param low_frequency_limit:          float/int, low frequency limit at which to highpass filter the audio, in Hz.
                                               Defaults to 20.
          :param centroid_crossover_frequency: float/int, crossover frequency for calculating the spectral centroid, in Hz.
                                               Defaults to 2000
          :param ratio_crossover_frequency:    float/int, crossover frequency for calculating the ratio, in Hz.
                                               Defaults to 500.

          :param db_decay_threshold:           float/int (negative), threshold, in dB, for estimating duration.  Should be
                                               negative.  Defaults to -40.

          :return:                             float, aparent depth of audio file, float.

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
        '''
          Read input
        '''
        audio_samples, fs = timbral_util.file_read(fname, fs, phase_correction=phase_correction)

        '''
          Filter audio
        '''
        # highpass audio - run 3 times to get -18dB per octave - unstable filters produced when using a 6th order
        audio_samples = timbral_util.filter_audio_highpass(audio_samples, crossover=low_frequency_limit, fs=fs)
        audio_samples = timbral_util.filter_audio_highpass(audio_samples, crossover=low_frequency_limit, fs=fs)
        audio_samples = timbral_util.filter_audio_highpass(audio_samples, crossover=low_frequency_limit, fs=fs)

        # running 3 times to get -18dB per octave rolloff, greater than second order filters are unstable in python
        lowpass_centroid_audio_samples = timbral_util.filter_audio_lowpass(
            audio_samples, crossover=centroid_crossover_frequency, fs=fs
            )
        lowpass_centroid_audio_samples = timbral_util.filter_audio_lowpass(
            lowpass_centroid_audio_samples, crossover=centroid_crossover_frequency, fs=fs
            )
        lowpass_centroid_audio_samples = timbral_util.filter_audio_lowpass(
            lowpass_centroid_audio_samples, crossover=centroid_crossover_frequency, fs=fs
            )

        lowpass_ratio_audio_samples = timbral_util.filter_audio_lowpass(
            audio_samples, crossover=ratio_crossover_frequency, fs=fs
            )
        lowpass_ratio_audio_samples = timbral_util.filter_audio_lowpass(
            lowpass_ratio_audio_samples, crossover=ratio_crossover_frequency, fs=fs
            )
        lowpass_ratio_audio_samples = timbral_util.filter_audio_lowpass(
            lowpass_ratio_audio_samples, crossover=ratio_crossover_frequency, fs=fs
            )

        '''
          Get spectrograms and normalise
        '''
        # normalise audio
        lowpass_ratio_audio_samples *= (1.0 / max(abs(audio_samples)))
        lowpass_centroid_audio_samples *= (1.0 / max(abs(audio_samples)))
        audio_samples *= (1.0 / max(abs(audio_samples)))

        # set FFT parameters
        nfft = 4096
        hop_size = int(3 * nfft / 4)
        # get spectrogram
        if len(audio_samples) > nfft:
            freq, time, spec = spectrogram(
                audio_samples, fs, 'hamming', nfft, hop_size,
                nfft, 'constant', True, 'spectrum'
                )
            lp_centroid_freq, lp_centroid_time, lp_centroid_spec = spectrogram(
                lowpass_centroid_audio_samples, fs,
                'hamming', nfft, hop_size, nfft,
                'constant', True, 'spectrum'
                )
            lp_ratio_freq, lp_ratio_time, lp_ratio_spec = spectrogram(
                lowpass_ratio_audio_samples, fs, 'hamming', nfft,
                hop_size, nfft, 'constant', True, 'spectrum'
                )

        else:
            # file is shorter than 4096, just take the fft
            freq, time, spec = spectrogram(
                audio_samples, fs, 'hamming', len(audio_samples), len(audio_samples) - 1,
                nfft, 'constant', True, 'spectrum'
                )
            lp_centroid_freq, lp_centroid_time, lp_centroid_spec = spectrogram(
                lowpass_centroid_audio_samples, fs,
                'hamming',
                len(lowpass_centroid_audio_samples),
                len(lowpass_centroid_audio_samples) - 1,
                nfft, 'constant', True, 'spectrum'
                )
            lp_ratio_freq, lp_ratio_time, lp_ratio_spec = spectrogram(
                lowpass_ratio_audio_samples, fs, 'hamming',
                len(lowpass_ratio_audio_samples),
                len(lowpass_ratio_audio_samples) - 1,
                nfft, 'constant', True, 'spectrum'
                )

        threshold = timbral_util.db2mag(threshold_db)

        '''
          METRIC 1 - limited weighted mean normalised lower centroid
        '''
        # define arrays for storing metrics
        all_normalised_lower_centroid = []
        all_normalised_centroid_tpower = []

        # get metrics for each time segment of the spectrogram
        for idx in range(len(time)):
            # get overall spectrum of time frame
            current_spectrum = spec[:, idx]
            # calculate time window power
            tpower = np.sum(current_spectrum)
            all_normalised_centroid_tpower.append(tpower)

            # estimate if time segment contains audio energy or just noise
            if tpower > threshold:
                # get the spectrum
                lower_spectrum = lp_centroid_spec[:, idx]
                lower_power = np.sum(lower_spectrum)

                # get lower centroid
                lower_centroid = np.sum(lower_spectrum * lp_centroid_freq) / float(lower_power)

                # append to list
                all_normalised_lower_centroid.append(lower_centroid)
            else:
                all_normalised_lower_centroid.append(0)

        # calculate the weighted mean of lower centroids
        weighted_mean_normalised_lower_centroid = np.average(
            all_normalised_lower_centroid,
            weights=all_normalised_centroid_tpower
            )
        # limit to the centroid crossover frequency
        if weighted_mean_normalised_lower_centroid > centroid_crossover_frequency:
            limited_weighted_mean_normalised_lower_centroid = np.float64(centroid_crossover_frequency)
        else:
            limited_weighted_mean_normalised_lower_centroid = weighted_mean_normalised_lower_centroid

        '''
         METRIC 2 - weighted mean normalised lower ratio
        '''
        # define arrays for storing metrics
        all_normalised_lower_ratio = []
        all_normalised_ratio_tpower = []

        # get metrics for each time segment of the spectrogram
        for idx in range(len(time)):
            # get time frame of broadband spectrum
            current_spectrum = spec[:, idx]
            tpower = np.sum(current_spectrum)
            all_normalised_ratio_tpower.append(tpower)

            # estimate if time segment contains audio energy or just noise
            if tpower > threshold:
                # get the lowpass spectrum
                lower_spectrum = lp_ratio_spec[:, idx]
                # get the power of this
                lower_power = np.sum(lower_spectrum)
                # get the ratio of LF to all energy
                lower_ratio = lower_power / float(tpower)
                # append to array
                all_normalised_lower_ratio.append(lower_ratio)
            else:
                all_normalised_lower_ratio.append(0)

        # calculate
        weighted_mean_normalised_lower_ratio = np.average(
            all_normalised_lower_ratio, weights=all_normalised_ratio_tpower
            )

        '''
          METRIC 3 - Approximate duration/decay-time of sample 
        '''
        all_my_duration = []

        # get envelpe of signal
        envelope = timbral_util.sample_and_hold_envelope_calculation(audio_samples, fs)
        # estimate onsets
        onsets = timbral_util.calculate_onsets(audio_samples, envelope, fs)

        # get RMS envelope - better follows decays than the sample-and-hold
        rms_step_size = 256
        rms_envelope = timbral_util.calculate_rms_enveope(audio_samples, step_size=rms_step_size)

        # convert decay threshold to magnitude
        decay_threshold = timbral_util.db2mag(db_decay_threshold)
        # rescale onsets to rms stepsize - casting to int
        time_convert = fs / float(rms_step_size)
        onsets = (np.array(onsets) / float(rms_step_size)).astype('int')

        for idx, onset in enumerate(onsets):
            if onset == onsets[-1]:
                segment = rms_envelope[onset:]
            else:
                segment = rms_envelope[onset:onsets[idx + 1]]

            # get location of max RMS frame
            max_idx = np.argmax(segment)
            # get the segment from this max until the next onset
            post_max_segment = segment[max_idx:]

            # estimate duration based on decay or until next onset
            if min(post_max_segment) >= decay_threshold:
                my_duration = len(post_max_segment) / time_convert
            else:
                my_duration = np.where(post_max_segment < decay_threshold)[0][0] / time_convert

            # append to array
            all_my_duration.append(my_duration)

        # calculate the lof of mean duration
        mean_my_duration = np.log10(np.mean(all_my_duration))

        '''
          METRIC 4 - f0 estimation with peak picking
        '''
        # get the overall spectrum
        all_spectrum = np.sum(spec, axis=1)
        # normalise this
        norm_spec = (all_spectrum - np.min(all_spectrum)) / (np.max(all_spectrum) - np.min(all_spectrum))
        # set limit for peak picking
        cthr = 0.01
        # detect peaks
        peak_idx, peak_value, peak_freq = timbral_util.detect_peaks(
            norm_spec, cthr=cthr, unprocessed_array=norm_spec,
            freq=freq
            )
        # estimate peak
        pitch_estimate = np.log10(min(peak_freq)) if peak_freq[0] > 0 else 0

        # get outputs
        if dev_output:
            return limited_weighted_mean_normalised_lower_centroid, weighted_mean_normalised_lower_ratio, mean_my_duration, \
                pitch_estimate, weighted_mean_normalised_lower_ratio * mean_my_duration, \
                                timbral_util.sigmoid(weighted_mean_normalised_lower_ratio) * mean_my_duration
        else:
            '''
             Perform linear regression to obtain depth
            '''
            # coefficients from linear regression
            coefficients = np.array(
                [-0.0043703565847874465, 32.83743202462131, 4.750862716905235, -14.217438690256062,
                 3.8782339862813924, -0.8544826091735516, 66.69534393444391]
                )

            # what are the best metrics
            metric1 = limited_weighted_mean_normalised_lower_centroid
            metric2 = weighted_mean_normalised_lower_ratio
            metric3 = mean_my_duration
            metric4 = pitch_estimate
            metric5 = metric2 * metric3
            metric6 = timbral_util.sigmoid(metric2) * metric3

            # pack metrics into a matrix
            all_metrics = np.zeros(7)

            all_metrics[0] = metric1
            all_metrics[1] = metric2
            all_metrics[2] = metric3
            all_metrics[3] = metric4
            all_metrics[4] = metric5
            all_metrics[5] = metric6
            all_metrics[6] = 1.0

            # perform linear regression
            depth = np.sum(all_metrics * coefficients)

            if clip_output:
                depth = timbral_util.output_clip(depth)

            return depth

    @staticmethod
    def timbral_hardness(
            fname, fs=0, dev_output=False, phase_correction=False, clip_output=False, max_attack_time=0.1,
            bandwidth_thresh_db=-75
            ):
        """
         This function calculates the apparent hardness of an audio file.
         This version of timbral_hardness contains self loudness normalising methods and can accept arrays as an input
         instead of a string filename.

         Version 0.4

         Required parameter
          :param fname:                 string or numpy array
                                        string, audio filename to be analysed, including full file path and extension.
                                        numpy array, array of audio samples, requires fs to be set to the sample rate.

         Optional parameters
          :param fs:                    int/float, when fname is a numpy array, this is a required to be the sample rate.
                                        Defaults to 0.
          :param phase_correction:      bool, perform phase checking before summing to mono.  Defaults to False.
          :param dev_output:            bool, when False return the depth, when True return all extracted
                                        features.  Default to False.
          :param clip_output:           bool, force the output to be between 0 and 100.
          :param max_attack_time:       float, set the maximum attack time, in seconds.  Defaults to 0.1.
          :param bandwidth_thresh_db:   float, set the threshold for calculating the bandwidth, Defaults to -75dB.


          :return:                      float, Apparent hardness of audio file, float (dev_output = False/default).
                                        With dev_output set to True returns the weighted mean bandwidth,
                                        mean attack time, harmonic-percussive ratio, and unitless attack centroid.

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

        '''
          Read input
        '''
        audio_samples, fs = timbral_util.file_read(fname, fs, phase_correction=phase_correction)

        '''
          Calculate the midband level
        '''
        # get the level in the midband
        midband_level, weighed_midband_level = timbral_util.weighted_bark_level(
            audio_samples, fs, low_bark_band=70,
            upper_bark_band=140
            )
        log_weighted_midband_level = np.log10(weighed_midband_level)

        '''
          Calculate the harmonic-percussive ratio pre zero-padding the signal
        '''
        HP_ratio = timbral_util.get_percussive_audio(audio_samples, return_ratio=True)
        log_HP_ratio = np.log10(HP_ratio)

        '''
         Zeropad the signal
        '''
        # zero pad the signal
        nperseg = 4096  # default value for spectrogram analysis
        audio_samples = np.pad(audio_samples, (nperseg + 1, 0), 'constant', constant_values=(0.0, 0.0))

        '''
          Calculate the envelope and onsets
        '''
        # calculate the envelope of the signal
        envelope = timbral_util.sample_and_hold_envelope_calculation(audio_samples, fs, decay_time=0.1)
        envelope_time = np.arange(len(envelope)) / fs

        # calculate the onsets
        original_onsets = timbral_util.calculate_onsets(audio_samples, envelope, fs, nperseg=nperseg)
        onset_strength = librosa.onset.onset_strength(audio_samples, fs)
        # If onsets don't exist, set it to time zero
        if not original_onsets:
            original_onsets = [0]
        # set to start of file in the case where there is only one onset
        if len(original_onsets) == 1:
            original_onsets = [0]

        onsets = np.array(original_onsets) - nperseg
        onsets[onsets < 0] = 0

        '''
          Calculate the spectrogram so that the bandwidth can be created
        '''
        bandwidth_step_size = 128
        mag = timbral_util.db2mag(bandwidth_thresh_db)  # calculate threshold in linear from dB
        bandwidth, t, f = timbral_util.get_bandwidth_array(
            audio_samples, fs, nperseg=nperseg,
            overlap_step=bandwidth_step_size, rolloff_thresh=mag,
            normalisation_method='none'
            )
        # bandwidth sample rate
        bandwidth_fs = fs / float(bandwidth_step_size)  # fs due to spectrogram step size

        '''
          Set all parameters for holding data per onset
        '''
        all_bandwidth_max = []
        all_attack_time = []
        all_max_strength = []
        all_max_strength_bandwidth = []
        all_attack_centroid = []

        '''
          Get bandwidth onset times and max bandwidth
        '''
        bandwidth_onset = np.array(onsets / float(bandwidth_step_size)).astype('int')  # overlap_step=128

        '''
          Iterate through onsets and calculate metrics for each
        '''
        for onset_count in range(len(bandwidth_onset)):
            '''
              Calculate the bandwidth max for the attack portion of the onset
            '''
            # get the section of the bandwidth array between onsets
            onset = bandwidth_onset[onset_count]
            if onset == bandwidth_onset[-1]:
                bandwidth_seg = np.array(bandwidth[onset:])
            else:
                next_onset = bandwidth_onset[onset_count + 1]
                bandwidth_seg = np.array(bandwidth[onset:next_onset])

            if max(bandwidth_seg) > 0:
                # making a copy of the bandqwidth segment to avoid array changes
                hold_bandwidth_seg = list(bandwidth_seg)

                # calculate onset of the attack in the bandwidth array
                if max(bandwidth_seg) > 0:
                    bandwidth_attack = timbral_util.calculate_attack_time(
                        bandwidth_seg, bandwidth_fs,
                        calculation_type='fixed_threshold',
                        max_attack_time=max_attack_time
                        )
                else:
                    bandwidth_attack = []

                # calculate the badiwdth max for the attack portion
                if bandwidth_attack:
                    start_idx = bandwidth_attack[2]
                    if max_attack_time > 0:
                        max_attack_time_samples = int(max_attack_time * bandwidth_fs)
                        if len(hold_bandwidth_seg[start_idx:]) > start_idx + max_attack_time_samples:
                            all_bandwidth_max.append(
                                max(hold_bandwidth_seg[start_idx:start_idx + max_attack_time_samples])
                                )
                        else:
                            all_bandwidth_max.append(max(hold_bandwidth_seg[start_idx:]))
                    else:
                        all_bandwidth_max.append(max(hold_bandwidth_seg[start_idx:]))
            else:
                # set as blank so bandwith
                bandwidth_attack = []

            '''
              Calculate the attack time
            '''
            onset = original_onsets[onset_count]
            if onset == original_onsets[-1]:
                attack_seg = np.array(envelope[onset:])
                strength_seg = np.array(onset_strength[int(onset / 512):])  # 512 is librosa default window size
                audio_seg = np.array(audio_samples[onset:])
            else:
                attack_seg = np.array(envelope[onset:original_onsets[onset_count + 1]])
                strength_seg = np.array(onset_strength[int(onset / 512):int(original_onsets[onset_count + 1] / 512)])
                audio_seg = np.array(audio_samples[onset:original_onsets[onset_count + 1]])

            attack_time = timbral_util.calculate_attack_time(attack_seg, fs, max_attack_time=max_attack_time)
            all_attack_time.append(attack_time[0])

            '''
              Get the attack strength for weighting the bandwidth max
            '''
            all_max_strength.append(max(strength_seg))
            if bandwidth_attack:
                all_max_strength_bandwidth.append(max(strength_seg))

            '''
              Get the spectral centroid of the attack (125ms after attack start)
            '''
            # identify the start of the attack
            th_start_idx = attack_time[2]
            # define how long the attack time can be
            centroid_int_samples = int(0.125 * fs)  # number of samples for attack time integration

            # start of attack section from attack time calculation
            if th_start_idx + centroid_int_samples >= len(audio_seg):
                audio_seg = audio_seg[th_start_idx:]
            else:
                audio_seg = audio_seg[th_start_idx:th_start_idx + centroid_int_samples]

            # check that there's a suitable legnth of samples to get attack centroid
            # minimum length arbitrarily set to 512 samples
            if len(audio_seg) > 512:
                # get all spectral features for this attack section
                spectral_features_hold = timbral_util.get_spectral_features(audio_seg, fs)

                # store unitless attack centroid if exists
                if spectral_features_hold:
                    all_attack_centroid.append(spectral_features_hold[0])

        '''
          Calculate mean and weighted average values for features
        '''
        # attack time
        mean_attack_time = np.mean(all_attack_time)

        # get the weighted mean of bandwidth max and limit lower value
        if len(all_bandwidth_max):
            mean_weighted_bandwidth_max = np.average(all_bandwidth_max, weights=all_max_strength_bandwidth)
            # check for zero values so the log bandwidth max can be taken
            if mean_weighted_bandwidth_max <= 512.0:
                mean_weighted_bandwidth_max = fs / 512.0  # minimum value
        else:
            mean_weighted_bandwidth_max = fs / 512.0  # minimum value

        # take the logarithm
        log_weighted_bandwidth_max = np.log10(mean_weighted_bandwidth_max)

        # get the mean of the onset strenths
        mean_max_strength = np.mean(all_max_strength)
        log_mean_max_strength = np.log10(mean_max_strength)

        if all_attack_centroid:
            mean_attack_centroid = np.mean(all_attack_centroid)
        else:
            mean_attack_centroid = 200.0

        # limit the lower limit of the attack centroid to allow for log to be taken
        if mean_attack_centroid <= 200:
            mean_attack_centroid = 200.0
        log_attack_centroid = np.log10(mean_attack_centroid)

        '''
          Either return the raw features, or calculaste the linear regression.
        '''
        if dev_output:
            return log_weighted_bandwidth_max, log_attack_centroid, log_weighted_midband_level, log_HP_ratio, log_mean_max_strength, mean_attack_time
        else:
            '''
             Apply regression model
            '''
            all_metrics = np.ones(7)
            all_metrics[0] = log_weighted_bandwidth_max
            all_metrics[1] = log_attack_centroid
            all_metrics[2] = log_weighted_midband_level
            all_metrics[3] = log_HP_ratio
            all_metrics[4] = log_mean_max_strength
            all_metrics[5] = mean_attack_time

            # coefficients = np.array([13.5330599736, 18.1519030059, 13.1679266873, 5.03134507433, 5.22582123237, -3.71046018962, -89.8935449357])

            # recalculated values when using loudnorm
            coefficients = np.array(
                [12.079781720638145, 18.52100377170042, 14.139883645260355, 5.567690321917516,
                 3.9346817690405635, -4.326890461087848, -85.60352209068202]
                )

            hardness = np.sum(all_metrics * coefficients)

            # clip output between 0 and 100
            if clip_output:
                hardness = timbral_util.output_clip(hardness)

            return hardness

    @staticmethod
    def sharpness_Fastl(loudspec):
        """
          Calculates the sharpness based on FASTL (1991)
          Expression for weighting function obtained by fitting an
          equation to data given in 'Psychoacoustics: Facts and Models'
          using MATLAB basic fitting function
          Original Matlab code by Claire Churchill Sep 2004
          Transcoded by Andy Pearce 2018
        """
        n = len(loudspec)
        gz = np.ones(140)
        z = np.arange(141, n + 1)
        gzz = 0.00012 * (z / 10.0) ** 4 - 0.0056 * (z / 10.0) ** 3 + 0.1 * (z / 10.0) ** 2 - 0.81 * (z / 10.0) + 3.5
        gz = np.concatenate((gz, gzz))
        z = np.arange(0.1, n / 10.0 + 0.1, 0.1)

        sharp = 0.11 * np.sum(loudspec * gz * z * 0.1) / np.sum(loudspec * 0.1)
        return sharp

    @staticmethod
    def warm_region_cal(audio_samples, fs):
        """
          Function for calculating various warmth parameters.

        :param audio_samples:   numpy.array, an array of the audio samples, reques only one dimension.
        :param fs:              int, the sample ratr of the audio file.

        :return:                four outputs: mean warmth region, weighted-average warmth region, mean high frequency level,
                                weighted-average high frequency level.
        """
        # window the audio
        windowed_samples = timbral_util.window_audio(audio_samples)

        # need to define a function for the roughness stimuli, emphasising the 20 - 40 region (of the bark scale)
        min_bark_band = 10
        max_bark_band = 40
        mean_bark_band = (min_bark_band + max_bark_band) / 2.0
        array = np.arange(min_bark_band, max_bark_band)
        x = timbral_util.normal_dist(array, theta=0.01, mean=mean_bark_band)
        x -= np.min(x)
        x /= np.max(x)

        wr_array = np.zeros(240)
        wr_array[min_bark_band:max_bark_band] = x

        # need to define a second array emphasising the 20 - 40 region (of the bark scale)
        min_bark_band = 80
        max_bark_band = 240
        mean_bark_band = (min_bark_band + max_bark_band) / 2.0
        array = np.arange(min_bark_band, max_bark_band)
        x = timbral_util.normal_dist(array, theta=0.01, mean=mean_bark_band)
        x -= np.min(x)
        x /= np.max(x)

        hf_array = np.zeros(240)
        hf_array[min_bark_band:max_bark_band] = x

        windowed_loud_spec = []
        windowed_rms = []

        wr_vals = []
        hf_vals = []

        for i in range(windowed_samples.shape[0]):
            samples = windowed_samples[i, :]
            N_entire, N_single = timbral_util.specific_loudness(samples, reference_value_decibels=100.0, fs=fs, field_type=0)

            # append the loudness spec
            windowed_loud_spec.append(N_single)
            windowed_rms.append(np.sqrt(np.mean(samples * samples)))

            wr_vals.append(np.sum(wr_array * N_single))
            hf_vals.append(np.sum(hf_array * N_single))

        mean_wr = np.mean(wr_vals)
        mean_hf = np.mean(hf_vals)
        weighted_wr = np.average(wr_vals, weights=windowed_rms)
        weighted_hf = np.average(hf_vals, weights=windowed_rms)

        return mean_wr, weighted_wr, mean_hf, weighted_hf

    @staticmethod
    def timbral_warmth(
            fname, dev_output=False, phase_correction=False, clip_output=False, max_FFT_frame_size=8192,
            max_WR=12000, fs=0
            ):
        """
         This function estimates the perceptual Warmth of an audio file.

         This model of timbral_warmth contains self loudness normalising methods and can accept arrays as an input
         instead of a string filename.

         Version 0.4

         Required parameter
        :param fname:                   string, Audio filename to be analysed, including full file path and extension.

        Optional parameters
        :param dev_output:              bool, when False return the warmth, when True return all extracted features in a
                                        list.
        :param phase_correction:        bool, if the inter-channel phase should be estimated when performing a mono sum.
                                        Defaults to False.
        :param max_FFT_frame_size:      int, Frame size for calculating spectrogram, default to 8192.
        :param max_WR:                  float, maximun allowable warmth region frequency, defaults to 12000.

        :return:                        Estimated warmth of audio file.

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
        '''
          Read input
        '''
        audio_samples, fs = timbral_util.file_read(fname, fs, phase_correction=phase_correction)

        # get the weighted high frequency content
        mean_wr, _, _, weighted_hf = warm_region_cal(audio_samples, fs)

        # calculate the onsets
        envelope = timbral_util.sample_and_hold_envelope_calculation(audio_samples, fs, decay_time=0.1)
        envelope_time = np.arange(len(envelope)) / float(fs)

        # calculate the onsets
        nperseg = 4096
        original_onsets = timbral_util.calculate_onsets(audio_samples, envelope, fs, nperseg=nperseg)
        # If onsets don't exist, set it to time zero
        if not original_onsets:
            original_onsets = [0]
        # set to start of file in the case where there is only one onset
        if len(original_onsets) == 1:
            original_onsets = [0]
        '''
          Initialise lists for storing features
        '''
        # set defaults for holding
        all_rms = []
        all_ratio = []
        all_SC = []
        all_WR_Ratio = []
        all_decay_score = []

        # calculate metrics for each onset
        for idx, onset in enumerate(original_onsets):
            if onset == original_onsets[-1]:
                # this is the last onset
                segment = audio_samples[onset:]
            else:
                segment = audio_samples[onset:original_onsets[idx + 1]]

            segment_rms = np.sqrt(np.mean(segment * segment))
            all_rms.append(segment_rms)

            # get FFT of signal
            segment_length = len(segment)
            if segment_length < max_FFT_frame_size:
                freq, time, spec = spectrogram(segment, fs, nperseg=segment_length, nfft=max_FFT_frame_size)
            else:
                freq, time, spec = spectrogram(segment, fs, nperseg=max_FFT_frame_size, nfft=max_FFT_frame_size)

                # flatten the audio to 1 dimension.  Catches some strange errors that cause crashes
                if spec.shape[1] > 1:
                    spec = np.sum(spec, axis=1)
                    spec = spec.flatten()

            # normalise for this onset
            spec = np.array(list(spec)).flatten()
            this_shape = spec.shape
            spec /= max(abs(spec))

            '''
              Estimate of fundamental frequency
            '''
            # peak picking algorithm
            peak_idx, peak_value, peak_x = timbral_util.detect_peaks(spec, freq=freq, fs=fs)
            # find lowest peak
            fundamental = np.min(peak_x)
            fundamental_idx = np.min(peak_idx)

            '''
             Warmth region calculation
            '''
            # estimate the Warmth region
            WR_upper_f_limit = fundamental * 3.5
            if WR_upper_f_limit > max_WR:
                WR_upper_f_limit = 12000
            tpower = np.sum(spec)
            WR_upper_f_limit_idx = int(np.where(freq > WR_upper_f_limit)[0][0])

            if fundamental < 260:
                # find frequency bin closest to 260Hz
                top_level_idx = int(np.where(freq > 260)[0][0])
                # sum energy up to this bin
                low_energy = np.sum(spec[fundamental_idx:top_level_idx])
                # sum all energy
                tpower = np.sum(spec)
                # take ratio
                ratio = low_energy / float(tpower)
            else:
                # make exception where fundamental is greater than
                ratio = 0

            all_ratio.append(ratio)

            '''
             Spectral centroid of the segment
            '''
            # spectral centroid
            top = np.sum(freq * spec)
            bottom = float(np.sum(spec))
            SC = np.sum(freq * spec) / float(np.sum(spec))
            all_SC.append(SC)

            '''
             HF decay
             - linear regression of the values above the warmth region
            '''
            above_WR_spec = np.log10(spec[WR_upper_f_limit_idx:])
            above_WR_freq = np.log10(freq[WR_upper_f_limit_idx:])
            np.ones_like(above_WR_freq)
            metrics = np.array([above_WR_freq, np.ones_like(above_WR_freq)])

            # create a linear regression model
            model = linear_model.LinearRegression(fit_intercept=False)
            model.fit(metrics.transpose(), above_WR_spec)
            decay_score = model.score(metrics.transpose(), above_WR_spec)
            all_decay_score.append(decay_score)

        '''
         get mean values
        '''
        mean_SC = np.log10(np.mean(all_SC))
        mean_decay_score = np.mean(all_decay_score)
        weighted_mean_ratio = np.average(all_ratio, weights=all_rms)

        if dev_output:
            return mean_SC, weighted_hf, mean_wr, mean_decay_score, weighted_mean_ratio
        else:

            '''
             Apply regression model
            '''
            all_metrics = np.ones(6)
            all_metrics[0] = mean_SC
            all_metrics[1] = weighted_hf
            all_metrics[2] = mean_wr
            all_metrics[3] = mean_decay_score
            all_metrics[4] = weighted_mean_ratio

            coefficients = np.array(
                [-4.464258317026696,
                 -0.08819320850778556,
                 0.29156539973575546,
                 17.274733561081554,
                 8.403340066029507,
                 45.21212125085579]
                )

            warmth = np.sum(all_metrics * coefficients)

            # clip output between 0 and 100
            if clip_output:
                warmth = timbral_util.output_clip(warmth)

            return warmth