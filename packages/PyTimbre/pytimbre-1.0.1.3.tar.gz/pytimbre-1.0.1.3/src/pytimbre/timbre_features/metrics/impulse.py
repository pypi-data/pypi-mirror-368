import numpy as np
from pytimbre.utilities.audio_analysis_enumerations import AnalysisMethod, LeqDurationMode, WeightingFunctions


class ImpulseMetrics:
    """
    This class contains the information that is required to process a specific set of impulse metrics.
    """

    def __init__(self):
        self._waveform = None
        self._spectrum = None
        self._spectrogram = None
        self._impulse_analysis_method = AnalysisMethod.MIL_STD_1474E_AFRL_PREF

    @property
    def waveform(self):
        return self._waveform

    @property
    def spectrum(self):
        return self._spectrum

    @property
    def spectrogram(self):
        return self._spectrogram

    @property
    def impulse_100ms_equivalent_level(self):
        if self.waveform is not None:
            return None

        if self.spectrogram is not None:
            return None

        if self.spectrogram is not None:
            return None

    @property
    def impulse_equivalent_level_arbitrary_time(self):
        if self.waveform is not None:
            return None

        if self.spectrogram is not None:
            return None

        if self.spectrogram is not None:
            return None

        @property
        def impulse_analysis_method(self):
            return self._impulse_analysis_method

        @impulse_analysis_method.setter
        def impulse_analysis_method(self, method):
            self._impulse_analysis_method = method
            self._liaeqT = None
            self._liaeq8hr = None
            self._noise_dose = None
            self._corrected_a_duration = None


    @property
    def impulse_eight_hour_equivalent_level(self):
        if self.waveform is not None:
            return None

        if self.spectrogram is not None:
            return None

        if self.spectrogram is not None:
            return None

    def _process_impulse_analysis(self):
        from pytimbre.utilities.audio_analysis_enumerations import AnalysisMethod
        # Method with MIL STD 1474E
        if self.impulse_analysis_method == AnalysisMethod.MIL_STD_1474E:
            self._process_mil_std_1474e()

            # Method with MIL STD 1474E and a_durations corrected at liaegT instead of liaeq8hr.
        elif self.impulse_analysis_method == AnalysisMethod.MIL_STD_1474E_AFRL_PREF:
            self._process_mil_std_1474e_afrl_pref()

        # Method without a duration corrections in MIL STD 1474E
        elif self.impulse_analysis_method == AnalysisMethod.NO_A_DURATION_CORRECTIONS:
            self._process_no_a_duration_correction()

        elif self.impulse_analysis_method == AnalysisMethod.NONE:
            raise Warning("You should not call this function without declaring this as an impulsive waveform.")

    def _process_mil_std_1474e(self):
        # Process A-weighted equivalent energy metrics in accordance to MIL-STD 1474E B.5.3.2 EQ 1A
        # Sum and average energy across waveform for total recording time
        self._liaeqT = self.equivalent_level(
            weighting=WeightingFunctions.a_weighted,
            equivalent_duration=self.duration,
            leq_mode=LeqDurationMode.transient
        )
        self._liaeq100ms = self.equivalent_level(
            weighting=WeightingFunctions.a_weighted,
            equivalent_duration=0.1,
            leq_mode=LeqDurationMode.transient
        )

        # Limit A-duration according to Notes 1-3 in MIL-STD-1474E B.5.4.1
        if self.a_duration < 2e-4:
            self._corrected_a_duration = 2e-4
        elif self.a_duration > 2.5e-3:
            self._corrected_a_duration = 2.5e-3
        else:
            self._corrected_a_duration = self.a_duration

        # Process A-weighted 8-hour equivalent energy metric in accordance to MIL-STD 1474E B.5.4.1 EQ 3A and 3B

        self._liaeq8hr = self._liaeqT + 10.0 * np.log10(self.duration / 28800.0) - 1.5 * 10.0 * \
                         np.log10(self._corrected_a_duration / 2e-4)
        self._SELA = self._liaeq8hr + 10.0 * np.log10(28800.0 / 1.0)

        # Process noise dose with 3 db exchange rate, 85dBA limit for 8 hours from MIL-STD 1474E B.5.3.4.2 EQ 4
        self._noise_dose = 100.0 / (2 ** ((85 - self._liaeq8hr) / 3.0))

    def _process_mil_std_1474e_afrl_pref(self):
        # Process A-weighted equivalent energy metrics in accordance to MIL-STD 1474E B.5.3.2 EQ 1A
        # Sum and average energy across waveform for total recording time
        # Limit A-duration according to Notes 1-3 in MIL-STD-1474E B.5.4.1
        if self.a_duration < 2e-4:
            self._corrected_a_duration = 2e-4
        elif self.a_duration > 2.5e-3:
            self._corrected_a_duration = 2.5e-3
        else:
            self._corrected_a_duration = self.a_duration

        self._liaeqT = self.equivalent_level(
            weighting=WeightingFunctions.a_weighted,
            equivalent_duration=self.duration,
            leq_mode=LeqDurationMode.transient
        )
        self._liaeqT -= 1.5 * 10.0 * np.log10(self._corrected_a_duration / 2e-4)

        self._SELA = self._liaeqT + 10.0 * np.log10(self.duration / 1.0)

        self._liaeq100ms = self._liaeqT + 10.0 * np.log10(self.duration / 0.1)

        # Process A-weighted 8-hour equivalent energy metric in accordance to MIL-STD 1474E B.5.4.1 EQ 3A and 3B
        self._liaeq8hr = self._liaeqT + 10.0 * np.log10(self.duration / 28800.0)

        # Process noise dose with 3 db exchange rate, 85dBA limit for 8 hours from MIL-STD 1474E B.5.3.4.2 EQ 4
        self._noise_dose = 100.0 / (2 ** ((85 - self._liaeq8hr) / 3.0))

    def _process_no_a_duration_correction(self):
        self._corrected_a_duration = self.a_duration

        # Process A-weighted equivalent energy metrics in accordance to MIL-STD 1474E without a_duration corrections
        self._liaeqT = self.equivalent_level(
            weighting=WeightingFunctions.a_weighted,
            equivalent_duration=self.duration,
            leq_mode=LeqDurationMode.transient
        )

        self._SELA = self.equivalent_level(
            weighting=WeightingFunctions.a_weighted,
            equivalent_duration=1.0,
            leq_mode=LeqDurationMode.transient
        )

        self._liaeq100ms = self.equivalent_level(
            weighting=WeightingFunctions.a_weighted,
            equivalent_duration=0.1,
            leq_mode=LeqDurationMode.transient
        )

        self._liaeq8hr = self.equivalent_level(
            weighting=WeightingFunctions.a_weighted,
            equivalent_duration=8 * 60 * 60,
            leq_mode=LeqDurationMode.transient
        )

        # Process noise dose with 3 db exchange rate, 85dBA limit for 8 hours from MIL-STD 1474E B.5.3.4.2 EQ 4
        self._noise_dose = 100.0 / (2 ** ((85 - self._liaeq8hr) / 3.0))

    @property
    def liaeqT(self):
        #   TODO: Integration with continuous function
        if self.is_impulsive:
            if self._liaeqT is None:
                self._process_analysis()
            return self._liaeqT
        else:
            raise ValueError("This waveform is not impulsive")

    @property
    def liaeq100ms(self):
        #   TODO: Integration with continuous function
        if self.is_impulsive:
            if self._liaeq100ms is None:
                self._process_analysis()
            return self._liaeq100ms
        else:
            raise ValueError("This waveform is not impulsive")

    @property
    def liaeq8hr(self):
        #   TODO: Integration with continuous function
        if self.is_impulsive:
            if self._liaeq8hr is None:
                self._process_analysis()
            return self._liaeq8hr
        else:
            raise ValueError("This waveform is not impulsive")