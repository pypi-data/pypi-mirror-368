import sys

import numpy as np
import datetime
import warnings


class AcousticWeights:
    """
    This class contains a number of calculations for various community noise metrics that are useful for a variety of
    calculations across the study of acoustics.

    FSM - the math module was replaced with references to the numpy module to facilitate use with numpy arrays and the
    pandas DataFrame objects
    """

    @staticmethod
    def calculate_boominess(loudness_spectrum):
        """
        Calculates the Booming Index as described by Hatano, S., and Hashimoto, T. "Booming index as a measure for
        evaluating booming sensation", The 29th International congress and Exhibition on Noise Control Engineering, 2000.

        :param loudness_spectrum:
            The spectrum that is converted to the loudness spectrum rather than the one-third-octave band

        :returns:
            Single value for the waveform that was processed to represent the boominess of the signal.
        """
        #   TODO: Loudness is calculated only with one-third-octave band and must contain data from 25 Hz to 12.5 kHz.

        # generate the loudness spectrum from the loudness_1991 code results in values from 0.1 to 24 Bark in 0.1 steps,
        # and convert these Bark values to frequency
        z = np.arange(0.1, 24.05, 0.1)
        f = 600 * np.sinh(z / 6.0)
        center_frequencies = [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250,
                              1600,
                              2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500]

        # now convert f onto the center_frequencies scale
        log_center_frequency = np.log10(center_frequencies)
        frequency_step = log_center_frequency[1] - log_center_frequency[0]
        minimum_frequency = log_center_frequency[0]

        # get the log version of estimated frequencies, and estimate the indexes of the bark scale on the 3rd octave
        # scale
        log_frequency = np.log10(f)
        estimated_index = ((log_frequency - minimum_frequency) / float(frequency_step)) + 1

        # weighting function based from the estimated indexes
        weighting_function = 2.13 * np.exp(-0.151 * estimated_index)

        # change the LF indexes to roll off
        weighting_function[0] = 0.8
        weighting_function[1] = 1.05
        weighting_function[2] = 1.10
        weighting_function[3] = 1.18

        # identify index where frequency is less than 280Hz
        below_280_idx = np.where(f >= 280)[0][0]

        band_sum = 10 * np.log10(np.sum(10 ** (loudness_spectrum * weighting_function / 10.0)))
        return band_sum * (np.sum(loudness_spectrum[:below_280_idx]) / np.sum(loudness_spectrum))


    @staticmethod
    def lf(spl):
        """
        Compute the equal weighted acoustic level across the level array

        spl : double, array-like
            the sound pressure levels across a specific frequency array.  The frequencies are not provided for this
            function because there is an equal weighting across all frequencies.

        return : double
            the overall acoustic level with equal weighting
        """

        x = np.asarray(spl).copy()

        x /= 10.0
        x = 10.0 ** x
        x = np.sum(x, axis=len(x.shape) - 1)
        return 10 * np.log10(x)

    @staticmethod
    def la(spl, frequency):
        """
        Compute the A-weighted acoustic level across the level array

        spl : double, array-like
            the sound pressure levels across a specific frequency array
        frequency : double, array-like
            the array of frequencies to calculate the weighting

        return : double
            the overall acoustic level with equal weighting
        """

        x = np.asarray(spl).copy()
        if len(x.shape) == 1:
            x = np.reshape(x, (len(x), 1)).transpose()

        weights = np.ones((x.shape[0], 1)).dot(np.reshape(AcousticWeights.a_weighting_weights(frequency),
                                                          (len(frequency), 1)).transpose())

        x += weights
        x /= 10
        x = 10.0 ** x
        x = np.nansum(x, axis=(len(x.shape) - 1))
        return 10.0 * np.log10(x)

    @staticmethod
    def lc(spl, frequency):
        """
        Compute the A-weighted acoustic level across the level array

        spl : double, array-like
            the sound pressure levels across a specific frequency array
        frequency : double, array-like
            the array of frequencies to calculate the weighting

        return : double
            the overall acoustic level with equal weighting
        """

        x = np.asarray(spl).copy()
        if len(x.shape) == 1:
            x = np.reshape(x, (len(x), 1)).transpose()

        weights = np.ones((x.shape[0], 1)).dot(
            np.reshape(
                AcousticWeights.c_weighting_weights(frequency),
                (len(frequency), 1)
                ).transpose()
            )

        x += weights
        x /= 10
        x = 10.0 ** x
        x = np.nansum(x, axis=(len(x.shape) - 1))
        return 10.0 * np.log10(x)

    @staticmethod
    def a_weighting_weights(frequency):
        """
        Given a frequency, determine the A-weighted correction for the acoustic level

        frequency : double, possible array-like
            the number of cycles per second to calculate the weight at
        """

        frequency = np.asarray(frequency).copy() + sys.float_info.epsilon

        f2 = 107.65265
        f3 = 737.86223
        K3 = 1.562339
        numerator = K3 * frequency ** 4.0
        denominator = (frequency ** 2 + f2 ** 2) * (frequency ** 2 + f3 ** 2)

        return 10 * np.log10(numerator / denominator) + AcousticWeights.c_weighting_weights(frequency)

    @staticmethod
    def c_weighting_weights(frequency):
        """
        Given a frequency, determine the C-weighted correction for the acoustic level

        frequency : double, possible array-like
            the number of cycles per second to calculate the weight at
        """
        frequency += sys.float_info.epsilon

        f1 = 20.598997
        f4 = 12194.22
        K1 = 2.24e16
        numerator = K1 * np.float64(frequency) ** 4
        denominator = ((frequency ** 2 + f1 ** 2) ** 2.0) * ((frequency ** 2 + f4 ** 2) ** 2.0)

        frac = numerator / denominator
        return 10 * np.log10(frac)

    @staticmethod
    def perceived_noise_level(sound_pressure_level):
        """
        Determine the single number perceived noise level (PNL) based on the conversion from dB to Noys

        dSPL : double, array-like
            the sound pressure levels from 10 Hz to 10 kHz

        returns : double
            returns the perceived noise level in NOYS

        Remarks:
        2022-12-13 - FSM - Changed the end of the code to ensure that there is a non-infinite results when the sume of
            the levels is zero because the level is too quiet.
        """

        ld = [49, 44, 39, 34, 30, 27, 24, 21, 18, 16, 16, 16, 16, 16, 15, 12, 9, 5, 4, 5, 6, 10, 17, 21]
        le = [55, 51, 46, 42, 39, 36, 33, 30, 27, 25, 25, 25, 25, 25, 23, 21, 18, 15, 14, 14, 15, 17, 23, 29]
        lb = [64, 60, 56, 53, 51, 48, 46, 44, 42, 40, 40, 40, 40, 40, 38, 34, 32, 30, 29, 29, 30, 31, 37, 41]
        la = [91.01, 85.88, 87.32, 79.85, 79.76, 75.96, 73.96, 74.91, 94.63, 1000, 1000, 1000, 1000, 1000, 1000, 1000,
              1000, 1000, 1000, 1000, 1000, 1000, 44.29, 50.72]
        lc = [52, 51, 49, 47, 46, 45, 43, 42, 41, 40, 40, 40, 40, 40, 38, 34, 32, 30, 29, 29, 30, 31, 34, 37]
        md = [0.079520, 0.068160, 0.068160, 0.059640, 0.053013, 0.053013, 0.053013, 0.053013, 0.053013, 0.053013,
              0.053013, 0.053013, 0.053013, 0.053013, 0.059640, 0.053013, 0.053013, 0.047712, 0.047712, 0.053013,
              0.053013, 0.068160, 0.079520, 0.059640]
        me = [0.058098, 0.058098, 0.052288, 0.047534, 0.043573, 0.043573, 0.040221, 0.037349, 0.034859, 0.034859,
              0.034859, 0.034859, 0.034859, 0.034859, 0.034859, 0.040221, 0.037349, 0.034859, 0.034859, 0.034859,
              0.034859, 0.037349, 0.037349, 0.043573]
        mc = [0.030103, 0.030103, 0.030103, 0.030103, 0.030103, 0.030103, 0.030103, 0.030103, 0.030103, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0.02996, 0.02996]
        mb = [0.043478, 0.04057, 0.036831, 0.036831, 0.035336, 0.033333, 0.033333, 0.032051, 0.030675, 0.030103,
              0.030103, 0.030103, 0.030103, 0.030103, 0.030103, 0.02996, 0.02996, 0.02996, 0.02996, 0.02996, 0.02996,
              0.02996, 0.042285, 0.042285]
        dfn = np.zeros((31,))
        for j in range(0, 7, 1):
            dfn[j] = 0
        for i in range(7, 31, 1):
            if sound_pressure_level[i] > 250:
                return -1000

            if sound_pressure_level[i] >= la[i - 7]:
                dfn[i] = AcousticWeights.inverse_log_base_10(mc[i - 7] * (sound_pressure_level[i] - lc[i - 7]))

            elif lb[i - 7] <= sound_pressure_level[i] < la[i - 7]:
                dfn[i] = AcousticWeights.inverse_log_base_10(mb[i - 7] * (sound_pressure_level[i] - lb[i - 7]))

            elif le[i - 7] <= sound_pressure_level[i] < lb[i - 7]:
                dfn[i] = AcousticWeights.inverse_log_base_10(me[i - 7] * (sound_pressure_level[i] - lb[i - 7]))

            elif ld[i - 7] <= sound_pressure_level[i] < le[i - 7]:
                dfn[i] = 0.1 * AcousticWeights.inverse_log_base_10(md[i - 7] * (sound_pressure_level[i] - ld[i - 7]))

            if abs(dfn[i]) > 300 or abs(dfn[i]) < -300 or abs(dfn[i]) < 1e-10:
                dfn[i] = 0

            if dfn[i] > 2048:
                return -2000

        dfn[np.isinf(dfn)[0]] = 0
        d_max = np.max(dfn[7:])
        d_sum = np.sum(dfn[7:])

        d_sum = (d_sum - d_max) * 0.15 + d_max

        if d_sum == 0:
            d_sum = 1
        return 40 + 33.22 * np.log10(d_sum)

    @staticmethod
    def inverse_log_base_10(x):
        """
        Determine the inverse log10, or 10**x
        """

        return 10.0 ** x

    @staticmethod
    def tone_correction(sound_pressure_levels):
        import copy
        """
        This function determines the tone correction applied to the sound pressure level spectrum.  It is based on the
        description of the calculation within the FAR part 36, Appendix A36.4.3.1.

        :param sound_pressure_levels: double, array-like
            the collection of sound pressure levels from 10 Hz to 10 kHz

        returns : double
            the single value tone correction for the spectrum to be applied to the integrated acoustic levels.
        """

        #   Step 1 - Calculate the changes in adjacent sound pressure levels (or slopes)
        slopes = np.zeros(len(sound_pressure_levels))
        slopes[10:] = np.diff(sound_pressure_levels)[9:]

        #   Step 2 - find any slope changes greater than 5
        large_slope_changes = abs(slopes) > 5

        #   Step 3 - select the sound pressure level that needs to be corrected
        select_sound_pressure_level = np.zeros((len(sound_pressure_levels),), dtype=bool)
        for i in range(1, len(select_sound_pressure_level), 1):
            if large_slope_changes[i]:
                if slopes[i] > 0 and slopes[i] > slopes[i - 1]:
                    select_sound_pressure_level[i] = True
                elif slopes[i] <= 0 < slopes[i - 1]:
                    select_sound_pressure_level[i - 1] = True

        #   Step 4 - Adjust selected sound pressure levels
        spl_prime = np.zeros(len(sound_pressure_levels))
        for i in range(0, len(select_sound_pressure_level), 1):
            if not select_sound_pressure_level[i]:
                spl_prime[i] = sound_pressure_levels[i]
            else:
                if 8 < i < 30:
                    spl_prime[i] = 0.5 * (sound_pressure_levels[i - 1] + sound_pressure_levels[i + 1])
                # elif i ==30:
                #     spl_pr ime[i] = sound_pressure_levels[i - 1] + slopes[i - 1]

        if select_sound_pressure_level[-1]:
            spl_prime[-1] = sound_pressure_levels[-2] + slopes[-2]

        #   Step 5 - recompute new slopes
        slope_prime = np.zeros(len(sound_pressure_levels) + 1)
        slope_prime[1:-1] = np.diff(spl_prime)
        slope_prime[-1] = slope_prime[-2]

        #   Step 6 - compute the arithmetic mean of adjacent three slopes
        mean_slope = np.zeros((30,))
        for i in range(0, len(mean_slope), 1):
            mean_slope[i] = (1.0 / 3.0) * (slope_prime[i] + slope_prime[i + 1] + slope_prime[i + 2])

        # Step 7 - compute the final one-third-octave sound pressure levels
        final_spl = np.zeros((31,))
        final_spl[:10] = sound_pressure_levels[:10]
        for i in range(10, len(final_spl), 1):
            final_spl[i] = final_spl[i - 1] + mean_slope[i - 1]

        #   Step 8 - calculate the differences between the original and final SPL values
        final_sound_pressure_level_difference = np.asarray(sound_pressure_levels) - np.asarray(final_spl)

        #   Step 9 - for each of the relevant one-third-octave bands, determine tone correction factors from the sound
        #   pressure level differences (F[i]) and the table in the FAR
        tone_corrections = np.zeros(len(sound_pressure_levels))
        for i in range(0, len(sound_pressure_levels), 1):
            if 17 <= i <= 27:
                if 1.5 <= final_sound_pressure_level_difference[i] < 3:
                    tone_corrections[i] = 1
                elif 3 <= final_sound_pressure_level_difference[i] < 20:
                    tone_corrections[i] = final_sound_pressure_level_difference[i] / 3
                elif 20 <= final_sound_pressure_level_difference[i]:
                    tone_corrections[i] = 2 * (3.0 + (1.0 / 3.0))
            else:
                if 1.5 <= final_sound_pressure_level_difference[i] < 3:
                    tone_corrections[i] = 0.5
                elif 3 <= final_sound_pressure_level_difference[i] < 20:
                    tone_corrections[i] = final_sound_pressure_level_difference[i] / 6.0
                elif 20 <= final_sound_pressure_level_difference[i]:
                    tone_corrections[i] = 3.0 + (1.0 / 3.0)

        #   Return the maximum of the corrections
        return max(tone_corrections)
