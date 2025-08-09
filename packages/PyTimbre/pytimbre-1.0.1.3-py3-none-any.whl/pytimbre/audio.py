"""
| Description: This is a base class for the storage or information as a collection of samples, a number of samples
per second and the start time of these samples.
| Contributors: Drs. Frank Mobley and Alan Wall, Conner Campbell, Gregory Bowers
"""

import numpy as np
import datetime
import scipy.signal
from typing import Dict, Tuple
import numpy.typing as npt
from pytimbre.utilities.yin import yin
import warnings
from io import FileIO
import os.path
from pytimbre.utilities.audio_analysis_enumerations import TrimmingMethods, ScalingMethods
from pytimbre.utilities.audio_analysis_enumerations import WeightingFunctions, CorrelationModes
from pytimbre.utilities.audio_analysis_enumerations import LeqDurationMode, AnalysisMethod
from pytimbre.utilities.metadata import AudioMetaData


class Waveform:
    """
    |Description: This is a generic base class that contains the start time, samples and sample rate for a waveform.
    Some limited operations exist within this class for manipulation of the base data within the class.

    #   TODO: Add convolution function
    #   TODO: Add filter array function
    Remarks
    2022-05-11 - FSM - added the function to determine whether the waveform is a calibration signal or not.
    """

    def __init__(
            self,
            pressures,
            sample_rate,
            start_time,
            remove_dc_offset: bool = True,
            is_continuous_wfm: bool = True,
            is_steady_state: bool = True,
            header=None
    ):
        """
        Default constructor
        :param pressures:
            float, array-like - the list of pressure values
        :param sample_rate:
            float - the number of samples per second
        :param start_time:
            float or datetime - the time of the first sample
        :param remove_dc_offset:
            bool, default = True - remove a DC offset from the samples
        :param is_continuous_wfm:
            bool - flag to determine whether this waveform is continuous or impulsive in nature. Default is True
        :param is_steady_state:
            bool - flag to determine whether this waveform is steady-state or transient in nature. Default is True
        :param header:
            Dictionary - the collection of information regarding the StandardBinaryFile's properties.
        """
        warnings.filterwarnings('ignore')

        self._samples = pressures
        self.fs = sample_rate
        if isinstance(start_time, datetime.datetime):
            self.time0 = start_time
        else:
            self.time0 = float(start_time)
        if header is None:
            self._header = AudioMetaData()
        else:
            if isinstance(header, dict):
                self._header = AudioMetaData.from_header(header)
            else:
                self._header = header

        self._is_continuous = is_continuous_wfm
        self._is_steady_state = is_steady_state

        #   Run some checks on the data based on the information in the constructors
        if remove_dc_offset or self.is_impulsive:
            self._samples -= np.mean(self._samples)

        if self.is_impulsive and np.max(pressures) < -1.0 * np.min(pressures):
            pressures *= -1.0

    def __len__(self):
        return len(self.samples)

    # ---------------------- Collection of properties - this is both getters and setters -------------------------------

    @property
    def is_calibration(self):
        """
        This function examines the samples and determines whether the single contains a single pure tone.  If it does
        the function returns the approximate frequency of the tone.  This will examine every channel and determine
        whether each channel is a calibration tone

        :returns: bool - flag determining whether the signal was pure tone
                  float - the approximate frequency of the pure tone
        """
        from scipy.signal import find_peaks
        from pytimbre.utilities.audio_filtering import WaveformFilter

        calibration = None
        frequency = None

        #   Loop through the channels
        #   To remove high frequency transients, we pass the signal through a 2 kHz low pass filter
        wfm = WaveformFilter.apply_lowpass(self, 2000)

        if not wfm.is_mono:
            calibration = list()
            frequency = list()
            for ch in wfm.channels:
                calibration_flag, calibration_freq = ch.is_calibration
                frequency.append(calibration_freq)
                calibration.append(calibration_flag)
        else:
            peaks = find_peaks(wfm.samples, height=0.6 * np.max(wfm.samples))[0]

            if len(peaks) >= 2:
                calibration = False
                frequency = -1

                #   Determine the distance between any two adjacent peaks
                distance_sample = np.diff(peaks)

                #   Determine the distance between the samples in time
                distance_time = distance_sample / self.sample_rate

                #   Determine the frequencies
                frequencies = 1 / distance_time
                frequency = np.mean(frequencies)
                calibration = (abs(frequency - 1000) < 0.2 * 1000) or \
                              (abs(frequency - 250) < 0.1 * 250)

        return calibration, frequency

    @property
    def duration(self):
        """
        Determine the duration of the waveform by examining the number of samples and the sample rate
        :return: float - the total number of seconds within the waveform
        """
        return float(len(self._samples)) / self.fs

    @property
    def end_time(self):
        """
        Determine the end time - if the start time was a datetime, then this returns a datetime.  Otherwise a floating
        point value is returned
        :return: float or datetime - the end of the file
        """
        if isinstance(self.time0, datetime.datetime):
            return self.time0 + datetime.timedelta(seconds=self.duration)
        else:
            return self.time0 + self.duration

    @property
    def channel_count(self):
        if len(self.samples) == 1:
            return 1
        else:
            return self.samples.shape[1]

    @property
    def header(self) -> AudioMetaData:
        return self._header

    @header.setter
    def header(self, value: AudioMetaData):
        self._header = value

    @property
    def is_continuous(self):
        return self._is_continuous

    @is_continuous.setter
    def is_continuous(self, value):
        self._is_continuous = value

    @property
    def is_impulsive(self):
        return not self.is_continuous

    @is_impulsive.setter
    def is_impulsive(self, value):
        """
        Set to True to enable properties and methods tailored to impulsive acoustic signals.
        """
        self.is_continuous = not value

    @property
    def is_steady_state(self):
        return self._is_steady_state

    @is_steady_state.setter
    def is_steady_state(self, value):
        self._is_steady_state = value

    @property
    def is_transient(self):
        return not self.is_steady_state

    @is_transient.setter
    def is_transient(self, value):
        self.is_steady_state = not value

    @property
    def samples(self):
        """
        The actual pressure waveform
        :return: float, array-like - the collection of waveform data
        """
        return self._samples

    @samples.setter
    def samples(self, array):
        self._samples = array

    @property
    def sample_rate(self):
        """
        The number of samples per second to define the waveform.
        :return: float - the number of samples per second
        """
        return self.fs

    @sample_rate.setter
    def sample_rate(self, value):
        self.fs = value

    @property
    def start_time(self):
        """
        The time of the first sample
        :return: float or datetime - the time of the first sample
        """

        return self.time0

    @start_time.setter
    def start_time(self, value):
        self.time0 = value

    @property
    def times(self):
        """
        This determines the time past midnight for the start of the audio and returns a series of times for each sample
        :return: float, array-like - the sample times for each element of the samples array
        """

        if isinstance(self.start_time, datetime.datetime):
            t0 = (60 * (60 * self.start_time.hour + self.start_time.minute) + self.start_time.second +
                  self.start_time.microsecond * 1e-6)
        else:
            t0 = self.start_time

        return np.arange(0, len(self.samples)) / self.sample_rate + t0

    @property
    def is_mono(self):
        """
        This function examines the size of the samples array within the function. If there is a second dimension then
        this function returns false. It is true otherwise.
        """
        return len(self.samples.shape) == 1

    @property
    def is_clipped(self):
        """
        This function attempts to determine whether there is clipping in the acoustic data represented in this waveform.
        """
        _, total_clipped_samples = Waveform._detect_clipping(self.samples)

        return (total_clipped_samples / len(self.samples)) >= 0.01

    @property
    def is_reverberant(self):
        """
        This function classifies the audio file as either not sounding reverberant.

        This is based on the RT60 estimation algorithm documented in:
        Jan, T., and Wang, W., 2012: "Blind reverberation time estimation based on Laplace distribution",
        EUSIPCO. pp. 2050-2054, Bucharest, Romania.

        Version 0.4

        Copyright 2019 Andy Pearce, Institute of Sound Recording, University of Surrey, UK.

        Refactored from timbral_models.timbral_reverb function by Dr. Frank Mobley, 2023
        """
        from pytimbre.timbre_features.metrics.room_acoustics import RoomAcousticMetrics

        # check for mono file
        if self.is_mono:
            # it's a mono file
            mean_rt60 = RoomAcousticMetrics.from_waveform(self).reverb_time
        else:
            # the file has channels, estimate RT for the first two and take the mean
            reverb_time = list()
            for channel in self.channels:
                reverb_time.append(RoomAcousticMetrics.from_waveform(channel).reverb_time)

            mean_rt60 = np.mean(reverb_time)

        '''
          need to develop a logistic regression model to test this.
        '''
        # apply linear coefficients
        coefficients = [2.97126461]
        intercept = -1.45082989
        attributes = [mean_rt60]
        logit_model = np.sum(np.array(coefficients) * np.array(attributes)) + intercept

        # apply inverse of Logit function to obtain probability
        probability = np.exp(logit_model) / (1.0 + np.exp(logit_model))

        if probability < 0.5:
            return 0
        else:
            return 1

    @property
    def fundamental_frequency(self):
        return np.median(
            yin(
                self.samples,
                self.sample_rate,
                F_max=10000,
                F_min=10,
                N=int(np.floor(self.sample_rate / 10)),
                H=int(np.floor(self.sample_rate / 10 / 4))
            )[0]
        )

    @property
    def peak_pressure(self):
        return np.max(self.samples)

    @property
    def peak_level(self):
        return 20 * np.log10(self.peak_pressure / 20e-6)

    @property
    def peak_time(self):
        return self.times[np.argmax(self.samples)]

    @property
    def channels(self) -> np.ndarray:
        """
        This property creates a set of Waveform objects that represent the individual channels within the audio file.
        """

        array = np.empty((self.channel_count,), dtype=Waveform)
        for i in range(self.channel_count):
            array[i] = Waveform(
                pressures=self.samples[:, i],
                sample_rate=self.sample_rate,
                start_time=self.start_time,
                header=self.header
            )

        return array

    # ------------------ Static functions for the calculation of filter shapes and timbre features ---------------------
    @staticmethod
    def _detect_clipping(
            samples_array: npt.NDArray, max_threshold=0.995, min_threshold=0.995
    ) -> Tuple[Dict[str, int], int]:
        """
        Somewhat informed from https://www.sciencedirect.com/science/article/pii/S0167639321000832
        but without the sample-by-sample tagging. Intended to catch cases where clipped values have
        been normalized away.

        Returns the tagged clipped samples and the total number of clipped samples

        2023-04-06 - FSM - This function was extracted from the clipdetect project to minimize the dependency
        requirements of PyTimbre
        """
        if len(samples_array.shape) != 1:
            raise ValueError(
                "You must pass just the samples without any channel information"
            )
        max_sample = samples_array.max()
        min_sample = samples_array.min()
        max_threshold *= max_sample
        min_threshold *= min_sample
        clipping_sections = []
        total_clipped_samples = 0
        clip_end = 0
        for i, sample in enumerate(samples_array):
            if i > clip_end and sample in [max_sample, min_sample]:
                clipping_count = 0
                for new_sample in samples_array[i:]:
                    if new_sample >= max_threshold or new_sample <= min_threshold:
                        clipping_count += 1
                    else:
                        clipping_sections.append({"start": i, "end": i + clipping_count})
                        total_clipped_samples += clipping_count
                        clip_end = i + clipping_count
                        break
        return clipping_sections, total_clipped_samples

    @staticmethod
    def detect_local_extrema(input_v, lag_n):
        """
        This will detect the local maxima of the vector on the interval [n-lag_n:n+lag_n]

        Parameters
        ----------
        input_v : double array-like
            This is the input vector that we are examining to determine the local maxima
        lag_n : double, integer
            This is the number of samples that we are examining within the input_v to determine the local maximum

        Returns
        -------
        pos_max_v : double, array-like
            The locations of the local maxima
        """

        #   TODO: Does this belong with the cross-correlation?

        do_affiche = 0
        lag2_n = 4
        seuil = 0

        L_n = len(input_v)

        pos_cand_v = np.where(np.diff(np.sign(np.diff(input_v))) < 0)[0]
        pos_cand_v += 1

        pos_max_v = np.zeros((len(pos_cand_v),))

        for i in range(len(pos_cand_v)):
            pos = pos_cand_v[i]

            if (pos > lag_n) & (pos <= L_n - lag_n):
                tmp = input_v[pos - lag_n:pos + lag2_n]
                position = np.argmax(tmp)

                position = position + pos - lag_n - 1

                if (pos - lag2_n > 0) & (pos + lag2_n < L_n + 1):
                    tmp2 = input_v[pos - lag2_n:pos + lag2_n]

                    if (position == pos) & (input_v[position] > seuil * np.mean(tmp2)):
                        pos_max_v[i] = pos

        return pos_max_v

    # --------------------- Functions for reading the Wav File formatted files -----------------------------------------

    @staticmethod
    def from_wave_file(path: str, s0: int = None, s1: int = None):
        """
        This function employs the functions within this file to read the data and metadata from a Wav file object
        and returns it as a Waveform object.
        :param s1:
        :type s1:
        :param s0:
        :type s0:
        :param path: the location of the file to read
        :type path: str
        :return: The audio data from the Wave File
        :rtype: Waveform
        """

        #   Create an instance of the ChunkScanner that will assist in reading the file and determining the various
        #   chunks that exist within the file
        if not os.path.exists(path):
            raise ValueError("File Not Found")
        scanner = ChunkScanner(path)

        #   Now, open the file and read all the chunks, if the chunk does not exist within the scanner,
        #   then the function will ignore it.
        with open(path, 'rb') as fid:
            fmt = _read_format_chunk(scanner, fid)
            peak = _read_peak_chunk(scanner, fid, fmt)
            list, normalized, start_time = _read_list_chunk(scanner, fid)
            xml, xml_start_time = _read_xml_chunk(scanner, fid)
            fact = _read_fact_chunk(scanner, fid)
            data = _read_data_chunk(scanner, fid, peak, fmt, normalized, s0, s1)

            #   Now we need to construct the Waveform object by compiling the header information from the list and
            #   XML chunks and the data from the Data Chunk. The format chunk defines the sample rate.
            header = dict()
            header['format_chunk'] = fmt
            header['list_chunk'] = list
            header['xml_chunk'] = xml
            header['fact_chunk'] = fact
            header['peak_chunk'] = peak

            #   Now loop through all the fields of the list chunk and add them as specific fields within the
            #   dictionary that might not have been properly names within the meta data
            for field_key in list.__dict__.keys():
                if isinstance(list.__dict__[field_key], dict):
                    for key in list.__dict__[field_key].keys():
                        header[key] = list.__dict__[field_key][key]
                else:
                    if field_key[0] != '_':
                        header[field_key] = list.__dict__[field_key]

            if xml_start_time is not None and start_time is None:
                t0 = xml_start_time
            elif xml_start_time is None and start_time is not None:
                t0 = start_time
            else:
                t0 = 0.0

        return Waveform(
            pressures=data._samples,
            sample_rate=fmt.sample_rate,
            start_time=t0,
            header=AudioMetaData.from_header(header)
        )

    # ---------------------- Functions for reading the StandardBinaryFile formatted Files ------------------------------

    @staticmethod
    def from_standard_binary_file(
            path: str,
            sample_rate_key: str = 'SAMPLE RATE (HZ)',
            start_time_key: str = 'TIME (UTC ZULU)',
            sample_format_key: str = 'SAMPLE FORMAT',
            data_format_key: str = 'DATA FORMAT',
            sample_count_key: str = 'SAMPLES TOTAL',
            s0=None,
            s1=None,
            header_only: bool = False
    ):
        """
        This will create a waveform object from a Standard Binary File formatted file.
        :param s1: The end sample to read from the file. If it is None, then the last sample is read
        :type s1: int
        :param s0: The first or start sample to read from the file. If it is None, then the data is read from the first
        :type s0: int
        :param sample_count_key: The name of the header field that defines the sample count
        :type sample_count_key: string
        :param data_format_key: The name of the header field that defines the data format
        :type data_format_key: string
        :param sample_format_key: The name of the header field that defines the sample format
        :type sample_format_key: string
        :param start_time_key: The name of the header field that defines the start time of the first sample
        :type start_time_key: string
        :param sample_rate_key: The name of the header field that defines the number of samples per second
        :type sample_rate_key: string
        :param path: The full path to the file to read
        :type path: string
        :param header_only: Flag to return the header of the file without reading the remainder of the file
        :type header_only: bool
        :return: the contents of the file
        :rtype: Waveform
        """

        return read_standard_binary_file(
            path, sample_rate_key, start_time_key, sample_format_key, data_format_key,
            sample_count_key, s0, s1, header_only
            )

    # ---------------------------- Protected functions for feature calculation -----------------------------------------

    def _trim_by_samples(self, s0: int = None, s1: int = None):
        """
        This function will trim the waveform and return a subset of the current waveform based on sample indices within
        the 'samples' property within this class.

        Parameters
        __________
        :param s0: int - the start sample of the trimming. If s0 is None, then interface will use the first sample
        :param s1: int - the stop sample of the trimming. If s1 is None, then the interface uses the last sample

        Returns
        _______
        :returns: Waveform - a subset of the waveform samples
        """

        #   Handle the start/stop samples may be passed as None arguments
        if s0 is None:
            s0 = 0

        if s1 is None:
            s1 = self._samples.shape[0]

        #   Determine the new start time of the waveform
        if isinstance(self.start_time, datetime.datetime):
            t0 = self.start_time + datetime.timedelta(seconds=s0 / self.sample_rate)
        else:
            t0 = self.start_time + s0 / self.sample_rate

        #   Create the waveform based on the new time, and the subset of the samples
        wfm = Waveform(
            self.samples[np.arange(s0, s1)].copy(),
            self.sample_rate,
            t0,
            remove_dc_offset=False,
            header=self.header
        )

        #   Copy values that can be changed through properties, but are set in the constructor
        wfm.is_continuous = self.is_continuous
        wfm.is_steady_state = self.is_steady_state

        return wfm

    def _scale_waveform(self, scale_factor: float = 1.0, inplace: bool = False):
        """
        This function applies a scaling factor to the waveform's sample in a linear scale factor.

        Parameters
        __________
        :param scale_factor: float - the linear unit scale factor to change the amplitude of the sample values
        :param inplace: boolean - Whether to modify the samples within the current object, or return a new object

        Returns
        _______
        :returns: If inplace == True a new Waveform object with the sample magnitudes scaled, None otherwise
        """

        if inplace:
            self._samples *= scale_factor

            return None
        else:
            return Waveform(
                self._samples * scale_factor,
                self.sample_rate,
                self.start_time,
                remove_dc_offset=False,
                header=self.header
            )

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

    def _process_analysis(self):
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

    # -------------------- Public functions for operations on the samples within the Waveform --------------------------

    def determine_calibration_scale_factor(
            self, level: float = 114, frequency: float = 1000, frequency_tolerance:
            float = 25
    ):
        """
        This function will take the information within the current Waveform and determine the scaling factor that can be
        applied to this, or any other file, to ensure that the acoustic reference is obtained.

        Parameters
        ----------
        :param level: float
            default = 114 dB, this is the acoustic level at the specified frequency that we expect the calibration tone
            to generate
        :param frequency: float
            default = 1000 Hz, this is the acoustic frequency of the calibration device
        :param frequency_tolerance:
            The distance from the provided frequency that we are willing to go to ensure that this is a calibration tone
        """

        #   TODO: Create a CalibrateWaveform utility function/file and move the "calibrate" functions
        from pytimbre.utilities.fractional_octave_band import FractionalOctaveBandTools as fob
        from pytimbre.utilities.audio_filtering import WaveformFilter

        #   Now we need to calculate the scale factor required to adjust the level of the calibration Waveform to the
        #   desired magnitude.
        filtered_wfm = WaveformFilter.apply_bandpass(
            self,
            fob.lower_frequency(3, fob.exact_band_number(3, frequency)),
            fob.upper_frequency(3, fob.exact_band_number(3, frequency))
        )

        #   Now assuming that the data within the samples array is a pressure
        rms_level = 20 * np.log10(np.std(filtered_wfm.samples) / 20e-6)

        sens = level - rms_level
        sens /= 20
        sens *= -1
        sens = 10.0 ** sens

        return sens

    def scale_signal(
            self, factor: float = 1.0, inplace: bool = False,
            scale_type: ScalingMethods = ScalingMethods.linear
    ):
        """
        This method will call the sub-function to scale the values of the waveform in linear fashion. If the scale
        factor is provided in logarithmic form, it will be converted to a linear value and sent to the sub-function.

        Parameters
        ----------
        :param factor: float - the scale factor that needs to be passed to the scaling sub-function, which will be
            multiplied by the unscaled signal (e.g. 1 divided by the sensitivity of a microphone in V/Pa)
        :param inplace: bool - whether to manipulate the data within the current class, or return a new instance
        :param scale_type: scaling_method - how to apply the scaling to the signal

        Returns
        -------

        :returns: output of sub-function
        """

        scale_factor = factor

        if scale_type == ScalingMethods.logarithmic:
            scale_factor = 10 ** (scale_factor / 20)

        return self._scale_waveform(scale_factor, inplace)

    def trim(self, s0: float = 0.0, s1: float = None, method: TrimmingMethods = TrimmingMethods.samples):
        """
        This function will remove the samples before s0 and after s1 and adjust the start time
        :param s0: float - the sample index or time of the new beginning of the waveform
        :param s1: float - the sample index or time of the end of the new waveform
        :param method: trimming_methods - the method to trim the waveform
        :return: generic_time_waveform object
        """

        #   Determine whether to use the time or sample methods

        if method == TrimmingMethods.samples:
            if s1 is None:
                s1 = len(self.samples)
            return self._trim_by_samples(int(s0), int(s1))
        elif method == TrimmingMethods.times_absolute:
            t0 = s0
            t1 = s1

            if isinstance(self.start_time, datetime.datetime):
                start_seconds = 60 * (60 * self.start_time.hour + self.start_time.minute) + self.start_time.second + \
                                self.start_time.microsecond / 1e6
            else:
                start_seconds = self.start_time

            s0 = (t0 - start_seconds) * self.sample_rate
            ds = (t1 - t0) * self.sample_rate
            s1 = s0 + ds

            return self._trim_by_samples(int(s0), int(s1))

        elif method == TrimmingMethods.times_relative:
            t0 = s0
            t1 = s1

            s0 = t0 * self.sample_rate
            s1 = t1 * self.sample_rate

            return self._trim_by_samples(int(s0), int(s1))

    def pad(self, pad_size, pad_value):
        """
        This function will insert values into the sample array according to the information in the pad_size object.
        The value that is inserted is defined by the value in pad_value (default = 0). If pad_value is an integer, then
        all values are inserted at the front of the sample array. If pad_value is a list or an array, the first entry
        is the pad size for the front; the second entry is the pad value for the back of the array.

        Parameters
        ----------
        pad_size: int or list/np.ndarray of ints
            The number of elements to add to the sample array. If the value is an integer, the points are added to the
            front of the sample array. Otherwise, the first entry is the front pad size, and the second entry is the
            rear pad size.

        pad_value: float or list/np.ndarray of floats
            The value to insert into the sample array based on the pad_size object

        Returns
        -------
        A new waveform with the increased size.

        """

        new_samples = np.pad(self.samples, pad_size, mode='constant', constant_values=pad_value)
        if isinstance(pad_size, list) or isinstance(pad_size, np.ndarray):
            front_pad_length = pad_size[0]
        else:
            front_pad_length = pad_size

        if isinstance(self.start_time, datetime.datetime):
            t0 = self.start_time - datetime.timedelta(seconds=front_pad_length / self.sample_rate)
        else:
            t0 = self.start_time - float(front_pad_length / self.sample_rate)

        return Waveform(pressures=new_samples, sample_rate=self.sample_rate, start_time=t0, remove_dc_offset=False)

    def resample(self, new_sample_rate: int):
        """
        This function resamples the waveform and returns a new object with the correct sample rate and sample count.
        This function employs the resample function within scipy.signal to conduct the resampling.

        Parameters
        ----------
        new_sample_rate: int - the new sample rate that we want to create a signal for

        Returns
        -------
        Waveform - the new waveform object that contains the resampled data with the new sample rate.
        """

        #   Determine the ratio of the current sample rate to the new sample rate

        sr_ratio = new_sample_rate / self.sample_rate

        return Waveform(
            scipy.signal.resample(self.samples, int(np.floor(len(self.samples) * sr_ratio))),
            new_sample_rate,
            self.start_time,
            remove_dc_offset=False,
            header=self.header
        )

    def cross_correlation(self, b, mode=CorrelationModes.valid, lag_limit=None):
        """
        This function determines the cross correlation between the current waveform and the waveform passed to the
        function.

        Parameters
        ----------
        b: Waveform - the signal to compare to the current waveform's samples
        mode: correlation_mode - the mode of the correlation that we want to execute for the correlation methods
        lag_limit: - the limit of the correlation analysis

        Returns
        -------

        value of the maximum correlation
        sample lag of the maximum correlation

        Remarks
        2022-12-01 - FSM - Added completed enumeration usage for different correlation modes
        """

        #   TODO: Consider moving to temporal metrics
        # TODO - @Alan - we need a test for this function.

        if not isinstance(b, Waveform):
            raise ValueError("The first argument is required to be a Waveform object")

        sig = b.samples
        ref_sig = self.samples
        if len(sig) > len(ref_sig):
            sig, ref_sig = ref_sig, sig

        M = len(ref_sig)
        N = len(sig)

        if lag_limit is None:
            correlation_values = np.correlate(ref_sig, sig, mode.name)
            if mode == CorrelationModes.valid:
                lags = np.arange(0, max(M, N) - min(M, N) + 1)
            elif mode == CorrelationModes.full:
                lags = np.arange(-(N - 1), M)
            elif mode == CorrelationModes.same:
                lags = np.arange(-np.floor(N / 2), M - np.floor(N / 2))
        else:
            ref_sig_pad = np.pad(ref_sig.conj(), lag_limit, mode='constant')
            correlation_values = np.zeros(2 * lag_limit + 1)
            for i in range(0, 2 * lag_limit + 1):
                correlation_values[i] = sum(ref_sig_pad[i:len(sig) + i] * sig)
            lags = np.arange(-lag_limit, lag_limit + 1)

        return np.max(correlation_values), lags[np.argmax(correlation_values)]

    def concatenate(self, wfm):
        """
        This will create a new audio file that contains the data from the current Waveform and adds the samples from the
        new Waveform to the list and then returns a new object.

        Parameters
        ----------
        :param wfm: This is the Waveform that we want to concatenate with the current samples

        Returns
        -------
        A new waveform that contains the audio from the argument tacked onto the end of the samples from the current
        waveform.
        """

        new_samples = np.concatenate([self.samples, wfm.samples])
        return Waveform(new_samples, self.sample_rate, self.start_time, header=self.header)

    def split_by_time(self, frame_duration: float = 0.25):
        """
       This will create a numpy array of waveform objects that have been split into segments controlled by the time
       window.

       Parameters
       ----------
       :param frame_duration: The amount of time in each new waveform segment -  float, defaults to 0.25 seconds.

       Returns
       -------
       A new waveform numpy array of waveform objects broken into segments equal to the window size.
       """

        N = int(np.floor(self.duration / frame_duration))
        frames = np.empty(N, dtype=Waveform)
        sample_size = int(np.floor(frame_duration * self.sample_rate))

        #   Set the starting sample
        s0 = 0
        for n in range(N):
            # Get individual frame with trim and set in array
            frames[n] = self.trim(s0, s0 + sample_size, TrimmingMethods.samples)
            s0 += sample_size

        return frames

    def to_standard_binary_file(self, output_filename: str = ""):
        """
        This function writes the current data within the Waveform into a StandardBinaryFile.
        :param output_filename: the location to write the data to
        :type output_filename: str
        """
        import os.path
        import struct

        # Append sample format and encoding method if they don't exist to the header dict
        if not self.header.field_present("SAMPLE RATE (HZ)"):
            self.header.add_field('SAMPLE RATE (HZ)', int(np.floor(self.sample_rate)))

        if not self.header.field_present('SAMPLES TOTAL'):
            self.header.add_field('SAMPLES TOTAL', len(self.samples))
        else:
            self.header.add_field('SAMPLES TOTAL', len(self.samples))

        if isinstance(self.start_time, datetime.datetime) and not self.header.field_present('TIME (UTC ZULU)'):
            self.header.add_field('TIME (UTC ZULU)', self.start_time.strftime('%Y/%m/%d %H:%M:%S.%f'))
        elif isinstance(self.start_time, float) and not self.header.field_present('TIME (TPM)'):
            self.header.add_field('TIME (TPM)', self.start_time)

        if not self.header.field_present('SAMPLE FORMAT'):
            self.header.add_field('SAMPLE FORMAT', "LITTLE ENDIAN")

        if not self.header.field_present('DATA FORMAT'):
            self.header.add_field('DATA FORMAT', 'REAL*4')

        # Check to see if output path exist and open file if it doesn't exist
        if not os.path.exists(output_filename):
            with (open(output_filename, 'wb') as f):

                # Write header info from dict
                header_line = ';{}'.format("HEADER SIZE").ljust(41, '.') + \
                    ': {}\n'.format(len(self.header.data_keys) + 1)
                f.write(header_line.encode('utf-8'))

                for key in self.header.data_keys:
                    header_line = ';{}'.format(key.upper()).ljust(41, '.') + \
                                  ': {}\n'.format(self.header.get_field(key))
                    f.write(header_line.encode('utf-8'))

                # Write pressure data to end of file
                for i in range(len(self.samples)):
                    f.write(struct.pack('<f', self.samples[i]))

    def to_wav_file(self, path, normalize: bool = True):
        """
        This function will write the information from the Waveform into a properly formatted Wave file with
        associated information put into the List chunk for later retrieval.
        :param path: the location to write the file
        :type path: str
        :param normalize: whether to normalize the data and create a Peak chunk
        :type normalize: bool
        """

        import struct

        #   Put the information from the Waveform into the various structures to be able to write the Wavefile
        with open(path, "wb") as file:
            #   Write the header with a zero file size at this point, we will update this later
            file.write("RIFF".encode('utf-8'))
            file.write(struct.pack("<i", 0))
            file.write("WAVE".encode('utf-8'))

            #   Write the completed format chunk to the file
            FormatChunk.from_waveform(self).write_chunk(file)

            #   Normalize the audio levels with the PeakChunk
            PeakChunk.from_waveform(self).write_chunk(file)

            #   Next we place the DataChunk into the file
            DataChunk.from_waveform(self).write_chunk(file)

            #   Write the list chunk to the file and close the file.
            ListChunk.from_waveform(self).write_chunk(file)

            #   Update the file size
            file_size = file.tell()
            file.seek(4, 0)
            file.write(struct.pack("<i", file_size - 8))

    #   ----------------------------------------------- Operators ------------------------------------------------------

    def __add__(self, other):
        """
        This function will add the contents of one waveform to the other. This feature checks the sample rate to ensure
        that they both possess the same sample times. Also, if the data starts at different times, this function will
        create a new object that is the addition of the samples, with the new sample times.

        Parameters
        ----------
        :param other: Waveform - the new object to add to this class's data

        Returns
        -------
        :returns: - A new Waveform object that is the sum of the two
        """

        warnings.warn(
            message='waveform.add not yet tested. Use at your own risk.'
        )

        if not isinstance(other, Waveform):
            raise ValueError("You must provide a new Waveform object to add to this object.")

        if self.sample_rate != other.sample_rate:
            raise ValueError("At this time, the two waveforms must possess the same sample rate to add them together")

        s0 = int(other.start_time * other.sample_rate)
        s1 = s0 + len(other.samples)

        return Waveform(
            self.samples[s0:s1] + other.samples, self.sample_rate, self.start_time,
            remove_dc_offset=False, header=self.header
        )

    def __sub__(self, other):
        """
        This function subtracts another Waveform object from the current object and returns the value as a new
        Waveform. If the start times, durations, or sample rates are not equal then the function returns a ValueError

        """

        if self.start_time != other.start_time or self.duration != other.duration or self.sample_rate != \
                other.sample_rate:
            raise ValueError(
                "The meta-data of these two waveforms is inconsistent making it impossible to know how "
                "to subtract the information in the pressures."
            )

        return Waveform(
            self.samples - other._samples,
            self.sample_rate,
            self.start_time,
            False,
            header=self.header
        )


class ChunkScanner:
    """
    This class will scan the Wav file, assuming that there is a correctly formatted file, and collect all the various
    chunks that are available within the file.
    """

    def __init__(self, file_path: str):
        """
        This constructor will search through the file and determine the collection of data chunks that exist within the
        correctly formed audio file.
        """

        #   Open the file for reading
        file = open(file_path, 'rb')

        #   The canonical wave format possesses some very specific structure, but we can examine the data as a series
        #   of data chunks that can be parsed in a similar manner.

        #   The first chunk is required to be the RIFF chunk, with the file size minus 8.
        name = ChunkScanner.read_chunk_name(file)

        if name != "RIFF":
            raise ValueError(
                "A canonical file begins with the RIFF chunk.  This file does not, please provide a "
                "canonical file"
            )

        #   Since this is to be canonical, the RIFF size must be the file size minus 8, so let's determine what the file
        #   size actually is so that we can check this as we read the data
        file_size = ChunkScanner.read_chunk_size(file) + 8

        if ChunkScanner.read_chunk_name(file) != "WAVE":
            raise ValueError("Expected canonical wave format with WAVE as the next element, which was not found")

        #   The RIFF chunk is the beginning of the file.  Now we begin to parse the chunks
        current_location = file.tell()
        assert current_location == 12, "The file is not at the correct location"

        self.chunks = list()

        while file.tell() < file_size:
            #   Read the name and size of the chunk
            name = ChunkScanner.read_chunk_name(file)
            if name is None:
                break
            size = ChunkScanner.read_chunk_size(file)
            offset = file.tell()

            #   Add the chunk to the list
            self.chunks.append(ChunkInformation(name, size, offset))

            #   skip the chunk
            file.seek(size, 1)

        file.close()

    @staticmethod
    def read_chunk_size(file):
        """
        This function reads four bytes and formats them as an integer
        :param file: File - the binary file that is to be read
        :return: int - the size of the chunk
        """
        import struct

        return struct.unpack("<I", file.read(4))[0]

    @staticmethod
    def read_chunk_name(file):
        """
        This function reads the next four bytes from the file and returns the chunk name

        :param file: FILE - the binary file that contains the information
        :return: str - the name of the next chunk
        """

        b_name = file.read(4)
        try:
            name = b_name.decode()
            return name
        except:
            return None

    @property
    def available_chunks(self):
        return self.chunks

    @property
    def format_chunk(self):
        #   Now, every wav file will contain a format chunk so let's find that.

        fmt_chunk_info = None
        for chunk in self.chunks:
            if chunk.chunk_name == "fmt ":
                fmt_chunk_info = chunk
                break
        if fmt_chunk_info is None:
            raise ValueError("There is no format chunk with the description of the file")

        return fmt_chunk_info

    @property
    def peak_chunk(self):

        #   The peak chunk may not be present within the file, but if it is then we will also find that chunk

        peak_chunk_info = None
        for chunk in self.chunks:
            if chunk.chunk_name == "PEAK":
                peak_chunk_info = chunk
                break

        return peak_chunk_info

    @property
    def data_chunk(self):
        chunk_info = None
        for chunk in self.chunks:
            if chunk.chunk_name == "data":
                chunk_info = chunk
                break

        return chunk_info

    @property
    def list_chunk(self):
        chunk_info = None

        for chunk in self.chunks:
            if chunk.chunk_name == "LIST":
                chunk_info = chunk
                break

        return chunk_info

    @property
    def xml_chunk(self):
        chunk_info = None

        for chunk in self.chunks:
            if chunk.chunk_name == "iXML":
                chunk_info = chunk
                break

        return chunk_info

    @property
    def fact_chunk(self):
        chunk_info = None

        for chunk in self.chunks:
            if chunk.chunk_name == "fact":
                chunk_info = chunk
                break

        return chunk_info


class ChunkInformation:
    """
    This class contains simple information about the location of the various chunks within the wav file.
    """

    def __init__(self, name, size, offset=0):
        """
        Default constructor that inserts the information into the correct object so that the chunk can be discovered
        at a later time
        :param name: str - the name of the chunk
        :param size: int - the size in bytes of the chunk
        :param offset: int - the offset within the file of the first byte of this chunk - this is past the name and size
            elements of the chunk (i.e. the chunk start is actually offset - 16)
        """

        if not isinstance(name, str):
            raise ValueError("No valid name provided")
        if not isinstance(size, int):
            raise ValueError("No valid size provided")
        if not isinstance(offset, int):
            raise ValueError("The offset must be an integer")

        self._name = name
        self._size = size
        self._offset = offset

    @property
    def chunk_name(self):
        return self._name

    @property
    def chunk_size(self):
        return self._size

    @property
    def chunk_offset(self):
        return self._offset


class FactChunk(ChunkInformation):
    """
    The fact chunk provides some additional information regarding the interior data within the Wave File.
    """

    def __init__(
            self, reader: FileIO = None, chunk_offset: int = None, chunk_size: int = None, chunk_name: str = None
    ):
        """
        The constructor for the format chunk.  This will contain the ability to read the 16 and 40 byte formatted
        header
        :param reader: File - The binary reader that will represent the data file that we are reading
        :param chunk_offset: int - offset from the beginning of the file where the format chunk data begins
        :param chunk_size: int - the number of bytes to read that contain the data
        """

        import struct

        if reader is None:
            self._sample_count = 0

            return

        super().__init__(chunk_name, chunk_size, chunk_offset)

        reader.seek(chunk_offset, 0)

        self._sample_count = struct.unpack('<I', reader.read(4))[0]

    @property
    def sample_count(self):
        return self._sample_count


class FormatChunk(ChunkInformation):
    """
    The format chunk is a specialized data chunk found within the wav formatted files.
    """

    def __init__(
            self, reader: FileIO = None, chunk_offset: int = None, chunk_size: int = None, chunk_name: str = None
    ):
        """
        The constructor for the format chunk.  This will contain the ability to read the 16 and 40 byte formatted
        header
        :param reader: File - The binary reader that will represent the data file that we are reading
        :param chunk_offset: int - offset from the beginning of the file where the format chunk data begins
        :param chunk_size: int - the number of bytes to read that contain the data
        """

        import struct

        if reader is None:
            self.audio_format = 3
            self.num_channels = 1
            self.fs = 44100
            self.byte_rate = 0
            self.block_align = 0
            self.bits_per_sample = 32

            return

        super().__init__(chunk_name, chunk_size, chunk_offset)

        #   Seek the beginning of the format chunk's data, skipping the name and size
        reader.seek(chunk_offset, 0)

        #   Now read the collection of bytes and determine the elements that we need to represent within the format
        #   chunk class.
        if self.chunk_size == 16:
            #   Now we can parse the information from the format chunk
            self.audio_format = struct.unpack('<H', reader.read(2))[0]

            self.num_channels = struct.unpack('<H', reader.read(2))[0]

            self.fs = struct.unpack('<I', reader.read(4))[0]

            self.byte_rate = struct.unpack('<I', reader.read(4))[0]

            self.block_align = struct.unpack('<H', reader.read(2))[0]

            self.bits_per_sample = struct.unpack('<H', reader.read(2))[0]
        elif self.chunk_size == 40:
            self.audio_format = struct.unpack('<H', reader.read(2))[0]
            self.num_channels = struct.unpack('<H', reader.read(2))[0]
            self.fs = struct.unpack('<I', reader.read(4))[0]
            self.byte_rate = struct.unpack('<I', reader.read(4))[0]
            self.block_align = struct.unpack('<H', reader.read(2))[0]
            self.bits_per_sample = struct.unpack('<H', reader.read(2))[0]
        else:
            try:
                self.audio_format = struct.unpack('<H', reader.read(2))[0]
                self.num_channels = struct.unpack('<H', reader.read(2))[0]
                self.fs = struct.unpack('<I', reader.read(4))[0]
                self.byte_rate = struct.unpack('<I', reader.read(4))[0]
                self.block_align = struct.unpack('<H', reader.read(2))[0]
                self.bits_per_sample = struct.unpack('<H', reader.read(2))[0]
            except Exception as e:
                raise e

    @property
    def waveform_format(self):
        if self.audio_format == 1:
            return "PCM - Uncompressed"
        elif self.audio_format == 3:
            return "IEEE Floating Point"

    @property
    def channel_count(self):
        return self.num_channels

    @channel_count.setter
    def channel_count(self, value):
        self.num_channels = value

    @property
    def sample_rate(self):
        return self.fs

    @sample_rate.setter
    def sample_rate(self, value):
        self.fs = value

    @property
    def sample_bit_size(self):
        return self.bits_per_sample

    @sample_bit_size.setter
    def sample_bit_size(self, value):
        self.bits_per_sample = value

    def write_chunk(self, writer):
        """
        This function writes the contents of the chunk to the output file in the correct format for a canonical wav file
        :param writer: FileIO - the writer for the data - it is assumed that the data will be written to the current
            location of the writer
        :param sample_rate: int - the number of samples per seconds
        :param bits_per_sample: int - the number of bytes per sample
        :param channel_count: int - the number of channels
        """
        import struct

        block_align = int(np.floor(self.channel_count * (self.bits_per_sample / 8)))

        writer.write("fmt ".encode('utf-8'))
        writer.write(struct.pack("<i", 16))  # Format header size
        writer.write(struct.pack("<h", 3))  # format tag 1 = PCM, 3 = IEEE Float
        writer.write(struct.pack("<h", self.channel_count))  # channel count
        writer.write(struct.pack("<i", int(np.floor(self.sample_rate))))
        writer.write(struct.pack("<i", int(np.floor(self.sample_rate)) * block_align))
        writer.write(struct.pack("<h", block_align))
        writer.write(struct.pack("<h", self.bits_per_sample))

    @staticmethod
    def from_waveform(wfm: Waveform):
        """
        This creates an instance of the FormatChunk with the information from the waveform as the various properties
        of the FormatChunk class
        :param wfm: the audio data that is the foundation of the FormatChunk
        :type wfm: Waveform
        :return: The properly formatted FormatChunk object
        :rtype: FormatChunk
        """

        fmt = FormatChunk()
        if len(wfm.samples.shape) == 1:
            fmt.channel_count = 1
        else:
            fmt.channel_count = wfm.samples.shape[1]
        fmt.sample_rate = wfm.sample_rate
        fmt.bits_per_sample = 32

        return fmt


class PeakChunk(ChunkInformation):
    """
    This class contains the information about the peaks within each channel of the wave file
    """

    def __init__(
            self, reader: FileIO = None, offset: int = None, size: int = None, name: str = None,
            channel_count: int = 1
    ):
        """
        Constructor for the peak chunk.  This will read the peak from multiple channels
        :param reader: FileIO - the reader for the chunk data
        :param offset: int - the offset within the file of the actual data of the chunk
        :param size: int - the number of bytes within the chunk
        :param name: str - the name of the chunk
        :param channel_count: int - the number of channels within the wav file
        """
        import struct

        if reader is None:
            self.peak_value = 1.0
            return

        super().__init__(name, size, offset)

        #   Seek to the beginning of the data within the format chunk
        reader.seek(self.chunk_offset, 0)

        #   Read all the data from the file
        bytes = reader.read(size)

        #   Now we can parse the information from the format chunk
        self.version = struct.unpack("<i", bytes[:4])[0]  # struct.unpack("<i", reader.read(4))
        self.timestamp = struct.unpack("<i", bytes[4:8])[0]
        values = list()
        locations = list()

        s0 = 8
        for i in range(channel_count):
            values.append(struct.unpack("<f", bytes[s0:s0 + 4])[0])
            s0 += 4
            locations.append(struct.unpack("<i", bytes[s0:s0 + 4])[0])
            s0 += 4

        self.peak_value = np.asarray(values, dtype='float')
        self.peak_location = np.asarray(locations, dtype='int')

    @property
    def peak_amplitude(self):
        return self.peak_value

    @peak_amplitude.setter
    def peak_amplitude(self, value):
        self.peak_value = value

    @property
    def peak_sample(self):
        return self.peak_location

    @peak_sample.setter
    def peak_sample(self, values):
        self.peak_location = values

    def write_chunk(self, writer):
        """
        This function writes the contents of the chunk into the file at the current position of the FileIO object
        :param writer: FileIO - the writer that will put the data into the correct format at the current position
        """
        import struct

        writer.write("PEAK".encode('utf-8'))
        size_offset = writer.tell()
        writer.write(struct.pack("<i", 0))  # Size
        start_byte = writer.tell()
        writer.write(struct.pack("<i", 1))  # Version
        writer.write(struct.pack("<i", 0))  # Timestamp

        #   Now write the value and location of all the channel's peak values
        if isinstance(self.peak_value, float):
            writer.write(struct.pack("<f", self.peak_amplitude))
            writer.write(struct.pack("<i", self.peak_sample))
        else:
            if isinstance(self.peak_value, list):
                l = len(self.peak_value)
            elif isinstance(self.peak_value, np.ndarray):
                l = self.peak_value.shape[0]
            else:
                raise Exception("Error, unhandled peak type: {}".format(type(self.peak_value)))
            for i in range(l):
                if isinstance(self.peak_value[i], float):
                    writer.write(struct.pack("<f", self.peak_amplitude[i]))
                    writer.write(struct.pack("<i", self.peak_sample[i]))
                else:
                    for i in range(len(self.peak_value[i])):
                        writer.write(struct.pack("<f", self.peak_amplitude[i]))
                        writer.write(struct.pack("<i", self.peak_sample[i]))

        #   Update the size of the chunk

        chunk_size = writer.tell() - start_byte

        #   Go back and update the size of the chunk

        writer.seek(size_offset, 0)
        writer.write(struct.pack("<i", chunk_size))

        #   Return to the end of the chunk

        writer.seek(chunk_size, 1)

    @staticmethod
    def from_waveform(wfm: Waveform):
        """
        This function creates an instance of the PeakChunk from the data within a Waveform object
        :param wfm: The data to build the PeakChunk from
        :type wfm: Waveform
        :return: The properly formatted PeakChunk object
        :rtype: PeakChunk
        """

        pc = PeakChunk()
        pc.peak_amplitude = np.max(wfm.samples, axis=0)
        pc.peak_sample = np.argmax(wfm.samples, axis=0)

        return pc


class DataChunk(ChunkInformation):
    """
    This class understand the various types of data formats that exist within wav files
    """

    def __init__(
            self,
            reader: FileIO = None,
            offset: int = None,
            size: int = None,
            name: str = None,
            fmt: FormatChunk = None,
            peak: PeakChunk = None,
            s0: int = None,
            s1: int = None,
            normalized: bool = False
    ):
        """
        This constructor employs the Format_Chunk object to understand how to read the data from the wav file.
        :param reader: FileIO - The file object to read the data
        :param offset: int - the offset of the beginning of the data chunk's data
        :param size: int - the overall size of the data chunk's data
        :param name: str - the name of the chunk
        :param fmt: Format_Chunk - the object that understands how to format the waveform
        :param s0: int - the starting sample
        :param s1: int - the ending sample
        :param normalized: bool - a flag determining whether the contents of the data files were normalized to the peak
            values
        """
        import struct

        if name is None:
            name = "data"
        if size is None:
            size = 0
        if offset is None:
            offset = 0

        super().__init__(name, size, offset)

        if peak is None:
            peak = PeakChunk()

        if reader is not  None:
            #   Move to the beginning of the data chunk and read the number of bytes that this chunk contains
            reader.seek(self.chunk_offset, 0)

            #   Now we need to unpack the bytes using the correct format and the struct.unpack command.  The number of
            #   samples is the total size, in bytes, divided by the bytes per sample, divided by the number of channels.
            sample_count = int(np.floor(self.chunk_size / (fmt.bits_per_sample / 8) / fmt.channel_count))
            read_size = self.chunk_size

            #   Before we move through the reading of the samples, we need to enable the removal of data through the use of
            #   the s0 and s1 values.  This means that we want to remove the first s0 samples from all channels, and then
            #   we move the cursor this many bits past the current location.
            start_bits = 0
            if s0 is not None:
                #   First determine the number of bits to move if there is only a single channel
                start_bits = int(np.floor(s0 * fmt.sample_bit_size / 8))

                #   Now multiply by the number of channels
                start_bits *= fmt.channel_count
                reader.seek(start_bits, 1)

                #   Remove the beginning samples that we have moved over
                sample_count -= s0
                read_size -= start_bits

            if s1 is not None:
                if s0 is not None:
                    #   Determine the number of samples to read
                    sample_count = s1 - s0
                else:
                    #   This is if there is no s0 but an s1
                    sample_count = s1

                #   Now use this size to fix the number of bytes to read
                read_size = int(np.floor(sample_count * (fmt.sample_bit_size / 8) * fmt.channel_count))

            #   The size of the chunk includes all data, regardless of the number of channels within the file.  So we can
            #   just read all the bytes into an array that we will parse through sequentially.
            byte_array = reader.read(read_size)

            #   Now create the sample array, which is the number of samples in the first index, and the number of channels
            #   in the second index.  The format is floating point, so we will need to perform the conversion for each
            #   sample regardless of the type within the file.
            sample_count = int(np.floor(sample_count))
            samples = np.zeros((sample_count, fmt.channel_count), dtype='float')

            #   The order of the samples is channel 0 sample 0, channel 1 sample 0, ... channel N sample 0, channel 0
            #   sample 1...So we first loop through the samples, then the channels.  However, to keep track of where we are
            #   within the array that was read from the data there will be an index outside the loops.
            #
            #   Start by moving through the samples
            idx = 0
            sample_size = int(np.floor(fmt.bits_per_sample / 8))

            #   Now that we know the sample size, we have to compare that to the type of audio stored in the DataChunk.
            #   This is specified by the audio_format flag in the FormatChunk. If the flag is three, then the values are
            #   floating point and the sample_size better be 4. If not then there is an error that is raised.
            if sample_size == 4 and fmt.audio_format == 3:
                #   This is the IEEE Float and 32-bit, which is required for the floating point value
                samples = np.asarray(
                    struct.unpack(
                        "<{}f".format(int(np.floor(sample_count * fmt.channel_count))),
                        byte_array
                    ),
                    dtype='float'
                )
            elif sample_size != 4 and fmt.audio_format == 3:
                raise ValueError(
                    "There is a missmatch between the bit size of the samples and the sample representation. "
                    "You must use a 32-bit floating point value for PCM = 3 files."
                )

            #   If the sample size is 3, this means that there is a slight compression in the representation and the
            #   sample must be read as a three element byte array, then shifted to account for the remaining bit. Once
            #   the bit has been shifted, we convert the 4 byte value to a floating point and divide by the maximum
            #   value of a 32-bit integer.
            elif sample_size == 3:
                tmp = list([0, 0, 0, 0])

                samples = np.zeros((int(len(byte_array) / 3),), dtype=float)
                n = 0
                for i in range(0, len(byte_array), 3):
                    tmp[1] = byte_array[i]
                    tmp[2] = byte_array[i + 1]
                    tmp[3] = byte_array[i + 2]

                    samples[n] = struct.unpack("<i", bytearray(tmp))[0]
                    n += 1

                samples = np.asarray(samples, dtype=float)
                samples /= np.iinfo(np.int32).max
            #   If the audio_format flag is one, then the values in the file are represented as integers. However,
            #   there are multiple flavors of integers, so we need additional logic to determine how to read the integer
            #   values and convert them to floating point. We do this because we want to use floating point values to
            #   represent the pressure within the waveform.
            elif fmt.audio_format == 1:
                #   This is all the integer formatted data.
                if sample_size == 1:  # Character integer values
                    data = struct.unpack("<{}B".format(int(np.floor(sample_count * fmt.channel_count))), byte_array)
                    np_array = np.array(data, dtype=np.float64) - 127
                    samples = (np_array / np.iinfo(np.uint8).max) * 2
                elif sample_size == 2:  # short integer values
                    data = struct.unpack("<{}h".format(int(np.floor(sample_count * fmt.channel_count))), byte_array)
                    samples = np.asarray(data, dtype='float') / np.iinfo(np.int16).max
                elif sample_size == 4:  # integer values
                    data = struct.unpack("<{}i".format(int(np.floor(sample_count * fmt.channel_count))), byte_array)
                    samples = np.asarray(data, dtype='float') / np.iinfo(np.int32).max

            elif fmt.audio_format > 500:
                samples = np.asarray(
                    struct.unpack(
                        "<{}i".format(int(np.floor(sample_count * fmt.channel_count))),
                        byte_array
                    ),
                    dtype='float'
                ) / 2 ** 31

            #   Scale the samples by the peak levels

            #   Assign the data to the class's sample object

            self._samples = samples.reshape((sample_count, fmt.channel_count))

            if normalized:
                for i in range(fmt.channel_count):
                    self._samples[:, i] *= peak.peak_value[i]

            if fmt.channel_count == 1:
                self._samples = self._samples.reshape((-1,))

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, waveform):
        self._samples = waveform

        if len(self._samples.shape) > 1:
            for i in range(self.samples.shape[1]):
                self.samples[:, i] /= np.max(self.samples[:, i])
        else:
            self.samples[:] /= np.max(self.samples)

    @staticmethod
    def from_waveform(wfm: Waveform):
        """
        Create an instance of the DataChunk from the information within the Waveform object
        :param wfm: The audio data
        :type wfm: Waveform
        :return: Properly formatted DataChunk
        :rtype: DataChunk
        """

        dc = DataChunk()
        dc.samples = wfm.samples

        return dc

    def write_chunk(self, file):
        """
        Write the information within the chunk to the audio file in the correct manner
        :param file: the file object to write the chunk into
        :type file: FileIO
        """
        import struct

        file.write("data".encode('utf-8'))
        file.write(struct.pack("<i", 4 * np.prod(self.samples.shape)))
        samples_to_write = np.reshape(self.samples, (np.prod(self.samples.shape),))
        file.write(samples_to_write.astype("<f").tobytes())


class ListChunk(ChunkInformation):
    """
    This is an extra chunk that can provide metadata to the user through customizable fields.
    """

    def __init__(self,
                 reader: FileIO = None,
                 size: int = None,
                 offset: int = None,
                 name: str = None):
        """
        This will construct the information within the class and read the contents of the LIST chunk
        :param reader: FileIO - the binary reader that will be able to extract the information from the file
        :param size: int - the size of the data chunk
        :param offset: int - the offset of the chunk's data
        :param name: str - the name of the chunk

        https://www.recordingblogs.com/wiki/list-chunk-of-a-wave-file#:~:text=List%20chunk%20%28of%20a%20RIFF%20file
        %29%20%20,%20Depends%20on%20the%20list%20type%20ID%20
        """

        if reader is None:
            #   Create the dictionaries that will be used for the creation of the data

            self.time0 = datetime.datetime.fromtimestamp(0)
            self.meta_data = {
                'creation_date': self.time0
            }
            self.header = dict()
            return

        super().__init__(name, size, offset)

        #   Create the list of keys within the List Chunk and the associated names for the metadata dictionary
        command_keys = {"IARL": "archival_location",
                        "IART": "artist",
                        "ICMS": "commissioned_organization",
                        "ICOP": 'copyright',
                        "ICRD": 'creation_date',
                        "ICRP": 'cropping_information',
                        "IDIM": 'originating_object_dimensions',
                        "IDPI": 'dots_per_inch',
                        "IENG": 'engineer_name',
                        "IGNR": 'subject_genre',
                        "IKEY": 'key_words',
                        "ILGT": 'lightness_settings',
                        "IMED": 'originating_object_medium',
                        "INAM": 'title',
                        "IPLT": 'color_palette_count',
                        "IPRD": 'subject_name',
                        "ISBJ": 'description',
                        "ISFT": 'creation_software',
                        "ISRC": 'data_source',
                        "ISRF": 'original_form',
                        "ITCH": 'digitizing_engineer'}

        self.meta_data = dict()
        self.header = dict()

        #   Move to the offset within the file where the LIST chunk starts and read the data
        reader.seek(self.chunk_offset, 0)
        bytes = reader.read(self.chunk_size)

        #   The expected keyword should contain INFO for the description
        if bytes[:4] == b"INFO":
            #   Now we can begin parsing this information into elements that are important for the understanding
            #   of the audio file.

            offset = 4

            while offset < len(bytes):
                #   Get the command
                cmd = bytes[offset:offset + 4].decode()

                #   Get the size of the string
                size = int.from_bytes(bytes[offset + 4:offset + 8], 'little')

                #   Read the string
                data = bytes[offset + 8:offset + 8 + size].decode()

                #   Remove the null characters that exist at the end of the data
                if '\0' in data:
                    while data[-1] == '\0' and len(data) > 0:
                        data = data[:-1]
                        if len(data) <= 0:
                            break

                offset += 8 + size

                if cmd in command_keys:
                    self.meta_data[command_keys[cmd]] = data
                elif cmd == "ICMT":
                    self.meta_data["general_comments"] = data
                    self._parse_general_comments(data)
                elif cmd == "ITRK":
                    try:
                        self.meta_data['track_no'] = int(data)
                    except ValueError:
                        self.meta_data['track_no'] = data

    def _parse_general_comments(self, data: str):
        """
        The general comments within the ListChunk possess a free-form representation of information. We have used this
        for storing information associated with the new acoustic acquisition system and other elements that
        just do not fit within the structure of the other elements of the ListChunk. This function will attempt
        to parse this information.
        :param data: the collection of data in delimited string
        :type data: str
        """
        import json
        import dateutil.parser

        # Now we understand that the majority of the header does not actually fall within the
        # standard LIST elements.  So we created a comma delimited arrangement of header name and
        # we can now separate apart.
        if len(data) > 0:
            if "|" in data:
                sub_elements = data.split("|")

                for header_element in sub_elements:
                    cmd = header_element.split('=')[0]
                    data = header_element.split('=')[1]

                    self.header[cmd] = data
            if "{" in data and "}" in data:
                #   Define the keys and metadata names
                comment_data = {'sens_l': 'left_channel_sensor_sensitivity',
                                'sens_r':'right_channel_sensor_sensitivity',
                                'gain_l': 'left_channel_gain',
                                'gain_r': 'right_channel_gain',
                                'v_scale': 'vertical_scale',
                                'gps_lat': 'latitude',
                                'gps_lon': 'longitude',
                                'gpx_fix': 'gps_fix_quality',
                                'gps_sat': 'gps_satellite_count',
                                'gps_alt': 'gps_altitude',
                                'gps_spd': 'gps_ground_speed',
                                'gps_trk_ang': 'gps_track_heading_angle',
                                'gps_hor_dil': 'gps_horizontal_dilution',
                                'gps_ht_gd': 'gps_height_above_ground',
                                'gps_ts': 'gps_time_stamp',
                                'gps_ts_sub': 'gps_time_stamp'
                }

                #   This is likely a JSON formatted string, so we will attempt to use the JSON decoder to
                #   actually read the data from the string
                self.header['general_comments'] = json.loads(data)
                for key in self.header['general_comments'].keys():
                    self.header[comment_data[key]] = self.header['general_comments'][key]

                self.time0 = dateutil.parser.parse(self.meta_data['gps_time_stamp'])
            else:
                self.header['general_comments'] = data

    @staticmethod
    def from_waveform(wfm):
        """
        This function populates the data for the wave file from the information within the metadata
        class and a dictionary that may not be present within the metadata.
        :param meta_data: The class containing information from the file
        :type meta_data: AudioMetaData
        """

        lc = ListChunk()
        lc.meta_data["creation_date"] = wfm.start_time

        if isinstance(wfm.header, AudioMetaData):
            for key in wfm.header.data_keys:
                if not isinstance(wfm.header.get_field(key), ChunkInformation):
                    data = wfm.header.get_field(key)
                    if isinstance(data, dict):
                        values = list()
                        for key in data.keys():
                            values.append(data[key])
                        data = str.join("|", values)
                    elif isinstance(data, list):
                        data = str.join("|", data)

                    lc.meta_data[key] = data

        return lc


    @property
    def file_start_time(self) -> datetime.datetime:
        return self.time0

    @property
    def archival_location(self):
        if "archival_location" in self.meta_data.keys():
            return self.meta_data["archival_location"]
        else:
            return None

    @property
    def artist(self):
        if "artist" in self.meta_data.keys():
            return self.meta_data["artist"]
        else:
            return None

    @property
    def commissioned_organization(self):
        if "commissioned_organization" in self.meta_data.keys():
            return self.meta_data["commissioned_organization"]
        else:
            return None

    @property
    def general_comments(self):
        if "general_comments" in self.meta_data.keys():
            return self.meta_data["general_comments"]
        else:
            return None

    @property
    def copyright(self):
        if "copyright" in self.meta_data.keys():
            return self.meta_data["copyright"]
        else:
            return None

    @property
    def creation_date(self):
        if "creation_date" in self.meta_data.keys():
            return self.meta_data["creation_date"]
        else:
            return None

    @property
    def cropping_information(self):
        if "cropping_information" in self.meta_data.keys():
            return self.meta_data["cropping_information"]
        else:
            return None

    @property
    def originating_object_dimensions(self):
        if "originating_object_dimensions" in self.meta_data.keys():
            return self.meta_data["originating_object_dimensions"]
        else:
            return None

    @property
    def dots_per_inch(self):
        if "dots_per_inch" in self.meta_data.keys():
            return self.meta_data["dots_per_inch"]
        else:
            return None

    @property
    def engineer_name(self):
        if "engineer_name" in self.meta_data.keys():
            return self.meta_data["engineer_name"]
        else:
            return None

    @property
    def subject_genre(self):
        if "subject_genre" in self.meta_data.keys():
            return self.meta_data["subject_genre"]
        else:
            return None

    @property
    def key_words(self):
        if "key_words" in self.meta_data.keys():
            return self.meta_data["key_words"]
        else:
            return None

    @property
    def lightness_settings(self):
        if "lightness_settings" in self.meta_data.keys():
            return self.meta_data["lightness_settings"]
        else:
            return None

    @property
    def originating_object_medium(self):
        if "originating_object_medium" in self.meta_data.keys():
            return self.meta_data["originating_object_medium"]
        else:
            return None

    @property
    def title(self):
        if "title" in self.meta_data.keys():
            return self.meta_data["title"]
        else:
            return None

    @property
    def color_palette_count(self):
        if "color_palette_count" in self.meta_data.keys():
            return self.meta_data["color_palette_count"]
        else:
            return None

    @property
    def subject_name(self):
        if "subject_name" in self.meta_data.keys():
            return self.meta_data["subject_name"]
        else:
            return None

    @property
    def description(self):
        if "description" in self.meta_data.keys():
            return self.meta_data["description"]
        else:
            return None

    @property
    def creation_software(self):
        if "creation_software" in self.meta_data.keys():
            return self.meta_data["creation_software"]
        else:
            return None

    @property
    def data_source(self):
        if "data_source" in self.meta_data.keys():
            return self.meta_data["data_source"]
        else:
            return None

    @property
    def original_form(self):
        if "original_form" in self.meta_data.keys():
            return self.meta_data["original_form"]
        else:
            return None

    @property
    def digitizing_engineer(self):
        if "digitizing_engineer" in self.meta_data.keys():
            return self.meta_data["digitizing_engineer"]
        else:
            return None

    @property
    def track_number(self):
        if "track_no" in self.meta_data.keys():
            return self.meta_data["track_no"]
        else:
            return -1

    def write_chunk(self, writer):
        """
        This function writes the contents of this LIST chunk to the file at the current cursor location
        :param writer: FileIO - The object controlling how the data is written to the file
        """
        import struct

        #   Write the header command
        writer.write("LIST".encode('utf-8'))

        #   Get the position so that we know where to write the size of the chunk
        size_offset = writer.tell()

        #   At this point we do not know how big the chunk will be, so we will write a zero 4 byte value
        writer.write(struct.pack("<i", 0))

        #   Now store the location within the file so that we can calculate how big the chunk is
        start_byte = writer.tell()
        writer.write("INFO".encode('utf-8'))

        #   Specify the names that we want to use in the creation of the contents of the list chunk. This dictionary
        #   will contain the names of the objects in the metadata dictionary, and the data in the dictionary will be
        #   the LIST chunk command. This is in effort to simplify the structure of this function.
        list_commands = {"archival_location": "IARL",
                         "artist": "IART",
                         "commissioned_organization": "ICMS",
                         "general_comments": "ICMT",
                         "copyright": "ICOP",
                         "creation_date": "ICRD",
                         "cropping_information": "ICRP",
                         "originating_object_dimensions": "IDIM",
                         "dots_per_inch": "IDPI",
                         "engineer_name": "IENG",
                         "subject_genre": "IGNR",
                         "key_words": "IKEY",
                         "lightness_settings": "ILGT",
                         "originating_object_medium": "IMED",
                         "title": "INAM",
                         "color_palette_count": "IPLT",
                         "subject_name": "IPRD",
                         "description": "ISBJ",
                         "creation_software": "ISFT",
                         "data_source": "ISRC",
                         "original_form": "ISRF",
                         "digitizing_engineer": "ITCH",
                         "track_no": "ITRK"}

        for cmd_key in list_commands.keys():
            if cmd_key in self.meta_data.keys():
                ListChunk._write_list_chunk(writer, list_commands[cmd_key], self.meta_data[cmd_key])

        if self.header is not None:
            if isinstance(self.header, dict):
                elements = list()
                for key in self.header.keys():
                    elements.append("{}={}".format(key, self.header[key]))

                ListChunk._write_list_chunk(writer, "ICMT", "|".join(elements))
            else:
                ListChunk._write_list_chunk(writer, "ICMT", self.meta_data["general_comments"])

        #   Now that we have walked through each of the potential elements of the LIST chunk, we need to determine the
        #   size of the chunk
        chunk_size = writer.tell() - start_byte

        #   Update the size
        writer.seek(size_offset, 0)
        writer.write(struct.pack("<i", chunk_size))

        #   Now move back to the end of the file
        writer.seek(0, 2)

    @staticmethod
    def _write_list_chunk(writer: FileIO, id: str, contents):
        """
        This is a private helper function that assists in writing the data to the LIST chunk.
        :param writer: FileIO - the writer object
        :param id: str - the string identifier for the chunk that is within the accepted LIST commands
        :param contents: str - the data to write to the file
        """
        import struct
        if not isinstance(contents, str):
            contents = "{}".format(contents)

        byte_count = 0

        #   write the command
        writer.write(id.encode('utf-8'))

        #   post-pend the null character
        contents += '\0'

        #   Ensure that there is an even number of bytes
        if len(contents) % 2 != 0:
            contents += '\0'

        #   Write the length of the string in bytes
        writer.write(struct.pack("<i", len(contents)))
        byte_count += 8
        writer.write(contents.encode('utf-8'))
        byte_count += len(contents)

        return byte_count


class XMLChunk(ChunkInformation):
    """
    The SITH files are formatted in the broadcast wave file format.  This means there is a portion of the file that is
    formatted with an XML structure.  Within this structure is the start time of the audio file.  This will be used to
    override the start time that comes from anywhere else.

    see also: http://www.gallery.co.uk/ixml/
    """

    def __init__(self, reader: FileIO = None, size: int = None, offset: int = None, name: str = None):
        """
        This constructor will obtain the information from the file and insert it into the class
        """
        import dateutil.parser
        import xml.etree.ElementTree

        self.version = None
        self.scene = None
        self.take = None
        self.user_bits = None
        self.file_uid = None
        self.note = None
        self.speed_note = None
        self.speed_master_speed = None
        self.speed_current_speed = None
        self.speed_timecode_flag = None
        self.speed_timecode_rate = None
        self.speed_file_sample_rate = None
        self.speed_audio_bit_depth = None
        self.speed_digitizer_sample_rate = None
        self.speed_timestamp_sample_rate = None
        self.speed_timestamp_samples_since_midnight_hi = None
        self.speed_timestamp_samples_since_midnight_lo = None
        self.history = None
        self.file_set = None
        self.track_list = None
        self.bwf_originator = None
        self.bwf_date = None
        self.bwf_time = None
        self.bwf_time_ref_lo = None
        self.bwf_time_ref_hi = None
        self.bwf_verion = None
        self.bwf_id = None

        month = None
        day = None
        year = None

        #   Call the parent constructor
        super().__init__(name, size, offset)

        #   Move to the offset point within the file reader and read the data from the file
        if (reader is not None) and (offset is not None) and (size is not None):
            reader.seek(offset, 0)

            self.xml_string = reader.read(size).decode()

            #   Now use the built-in xml parser to extract information about the iXML data
            tree = xml.etree.ElementTree.fromstring(self.xml_string)

            #   Now loop through the child nodes of this root
            for child in tree:
                if child.tag == "IXML_VERSION":
                    self.version = float(child.text)
                elif child.tag == "PROJECT":
                    self.project = child.text
                elif child.tag == "SCENE":
                    self.scene = child.text
                elif child.tag == "TAKE":
                    self.take = child.text
                elif child.tag == "UBITS":
                    self.user_bits = child.text

                    #   Now use the user bits and timestamp values to build the start time
                    month = int(self.user_bits[:2])
                    day = int(self.user_bits[2:4])
                    year = int(self.user_bits[4:6]) + 2000
                elif child.tag == "FILE_UID":
                    self.file_uid = child.text
                elif child.tag == "NOTE":
                    self.note = child.text
                elif child.tag == "SPEED":
                    for node in child:
                        if node.tag == "NOTE":
                            self.speed_note = node.text
                        elif node.tag == "MASTER_SPEED":
                            self.speed_master_speed = node.text
                        elif node.tag == "CURRENT_SPEED":
                            self.speed_current_speed = node.text
                        elif node.tag == "TIMECODE_FLAG":
                            self.speed_timecode_flag = node.text
                        elif node.tag == "TIMECODE_RATE":
                            self.speed_timecode_rate = node.text
                        elif node.tag == "FILE_SAMPLE_RATE":
                            self.speed_file_sample_rate = float(node.text)
                        elif node.tag == "AUDIO_BIT_DEPTH":
                            self.speed_audio_bit_depth = float(node.text)
                        elif node.tag == "DIGITIZER_SAMPLE_RATE":
                            self.speed_digitizer_sample_rate = float(node.text)
                        elif node.tag == "TIMESTAMP_SAMPLE_RATE":
                            self.speed_timestamp_sample_rate = node.text
                        elif node.tag == "TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI":
                            self.speed_timestamp_samples_since_midnight_hi = int(node.text)
                        elif node.tag == "TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO":
                            self.speed_timestamp_samples_since_midnight_lo = int(node.text)
                elif child.tag == "HISTORY":
                    self.history = child.text
                elif child.tag == "FILE_SET":
                    self.file_set = child.text
                elif child.tag == "TRACK_LIST":
                    self.track_list = child.text
                elif child.tag == "BEXT":
                    for node in child:
                        if node.tag == "BWF_ORIGINATION_DATE":
                            dt = dateutil.parser.parse(node.text)
                            month = dt.month
                            day = dt.day
                            year = dt.year
                        elif node.tag == "BWF_ORIGINATOR":
                            self.bwf_originator = node.text
                        elif node.tag == "BWF_ORIGINATION_TIME":
                            self.bwf_time = node.text
                        elif node.tag == "BWF_TIME_REFERENCE_LOW":
                            self.bwf_time_ref_lo = int(node.text)
                        elif node.tag == "BWF_TIME_REFERENCE_HIGH":
                            self.bwf_time_ref_hi = int(node.text)
                        elif node.tag == "BWF_VERSION":
                            self.version = int(node.text)
                        elif node.tag == "BWF_ID":
                            self.bwf.id = node.text

            if month is None or day is None or year is None:
                raise ValueError("The iXML chunk was not formatted in a manner that is recognized by PyTimbre")

            if self.speed_timestamp_samples_since_midnight_hi is not None and \
                    self.speed_timestamp_samples_since_midnight_lo is not None and \
                    self.speed_file_sample_rate is not None:
                hi_bits = float(self.speed_timestamp_samples_since_midnight_hi) * 2 ** 32
                time_past_midnight = ((hi_bits + float(self.speed_timestamp_samples_since_midnight_lo)) /
                                      self.speed_file_sample_rate)

                self.start_time = datetime.datetime(year, month, day) + datetime.timedelta(seconds=time_past_midnight)
            elif self.bwf_time is not None:
                dt = dateutil.parser.parse(self.bwf_time)
                self.start_time = datetime.datetime(year, month, day, dt.hour, dt.minute, dt.second)


def _read_format_chunk(scanner: ChunkScanner, file):
    """
    To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

    :param file: The file reader that provides access to the file's contents
    :type file: BinaryIO
    :param scanner: The object that has looked into the file and determine whether different chunks exist within
    the file
    :type scanner: ChunkScanner
    :returns: the information from the chunk
    :type: FormatChunk
    """

    format_chunk = FormatChunk(
        file,
        scanner.format_chunk.chunk_offset,
        scanner.format_chunk.chunk_size,
        scanner.format_chunk.chunk_name
    )

    return format_chunk


def _read_peak_chunk(scanner: ChunkScanner, file, fmt: FormatChunk):
    """
    To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

    :param file: The file reader that provides access to the file's contents
    :type file: BinaryIO
    :param scanner: The object that has looked into the file and determine whether different chunks exist within
    the file
    :type scanner: ChunkScanner
    :param fmt: The format chunk read from the file in the first place
    :type fmt: FormatChunk
    :returns: PeakChunk
    """
    if scanner.peak_chunk is not None:
        peak_chunk = PeakChunk(
            file,
            scanner.peak_chunk.chunk_offset,
            scanner.peak_chunk.chunk_size,
            scanner.peak_chunk.chunk_name,
            fmt.channel_count
        )
    else:
        peak_chunk = None

    return peak_chunk


def _read_list_chunk(scanner: ChunkScanner, file):
    """
    To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

    :param file: The file reader that provides access to the file's contents
    :type file: FileIO
    :param scanner: The object that has looked into the file and determine whether different chunks exist within
    the file
    :type scanner: ChunkScanner
    :returns: tuple (ListChunk, normalized: bool, start_time: float/datetime.datetime)
    """
    import dateutil.parser

    if scanner.list_chunk is not None:
        list_chunk = ListChunk(
            file,
            scanner.list_chunk.chunk_size,
            scanner.list_chunk.chunk_offset,
            scanner.list_chunk.chunk_name
        )
        if list_chunk.cropping_information is not None:
            if list_chunk.cropping_information == "normalized":
                normalized = True
            else:
                normalized = False
        else:
            normalized = False

        if 'gps_time' in list_chunk.meta_data.keys():
            start_time = dateutil.parser.parse(list_chunk.meta_data['gps_time'])
        elif 'creation_date' in list_chunk.meta_data.keys():
            start_time = dateutil.parser.parse(list_chunk.meta_data['creation_date'])
            list_chunk.meta_data['creation_date'] = start_time
        else:
            start_time = None
    else:
        #   If there is no list chunk in the file, create one so that we can hold the start_time data for the
        #   waveform
        list_chunk = ListChunk()
        normalized = False
        start_time = None

    return list_chunk, normalized, start_time


def _read_xml_chunk(scanner: ChunkScanner, file):
    """
    To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

    :param file: The file reader that provides access to the file's contents
    :type file: FileIO
    :param scanner: The object that has looked into the file and determine whether different chunks exist within
    the file
    :type scanner: ChunkScanner
    """
    if scanner.xml_chunk is not None:
        xml_chunk = XMLChunk(
            file,
            scanner.xml_chunk.chunk_size,
            scanner.xml_chunk.chunk_offset,
            scanner.xml_chunk.chunk_name
        )

        #   You can store the start time in the XML chunk if using Broadcast Wave Format. So this should be
        #   called after the _read_list_chunk so that we can guarantee that there is a list chunk within the
        #   class and that the time is overwritten based on what was contained in the XML chunk
        start_time = xml_chunk.start_time
    else:
        xml_chunk = None
        start_time = None

    return xml_chunk, start_time


def _read_fact_chunk(scanner: ChunkScanner, file):
    """
    To further reduce the cognitive complexity of the functions, this will read the fact chunk from the file

    :param file: The file reader that provides access to the file's contents
    :type file: FileIO
    :param scanner: The object that has looked into the file and determine whether different chunks exist within
    the file
    :type scanner: ChunkScanner
    """
    if scanner.fact_chunk is not None:
        fact_chunk = FactChunk(
            file,
            scanner.format_chunk.chunk_offset,
            scanner.format_chunk.chunk_offset,
            scanner.format_chunk.chunk_name
        )
    else:
        fact_chunk = None

    return fact_chunk


def _read_data_chunk(
        scanner: ChunkScanner,
        file,
        peak: PeakChunk,
        fmt: FormatChunk,
        normalized: bool = False,
        s0: int = None,
        s1: int = None
):
    """
    To further reduce the cognitive complexity of the functions, this will read the format chunk from the file

    :param file: The file reader that provides access to the file's contents
    :type file: FileIO
    :param scanner: The object that has looked into the file and determine whether different chunks exist within
    the file
    :type scanner: ChunkScanner
    :param s0: The start sample for reading the data from the file
    :type s0: int
    :param s1: The end sample for reading the data from the file
    :type s1: int
    :param peak: The peak chunk that contains the maximum level that the data will be converted to after the reading
    :type peak: PeakChunk
    :param fmt: The format chunk that defines how to read the data
    :type fmt: FormatChunk
    :param normalized: Flag to determine whether the value was or needs to be normalized
    :type normalized: bool
    :returns:
    """
    return DataChunk(
        file,
        scanner.data_chunk.chunk_offset,
        scanner.data_chunk.chunk_size,
        scanner.data_chunk.chunk_name,
        fmt,
        peak,
        s0,
        s1,
        normalized
    )


def read_standard_binary_file(
        path: str,
        sample_rate_key: str = 'SAMPLE RATE (HZ)',
        start_time_key: str = 'TIME (UTC ZULU)',
        sample_format_key: str = 'SAMPLE FORMAT',
        data_format_key: str = 'DATA FORMAT',
        sample_count_key: str = 'SAMPLES TOTAL',
        s0=None,
        s1=None,
        header_only: bool = False
        ):
    """
    This will create a waveform object from a Standard Binary File formatted file.
    :param s1: The end sample to read from the file. If it is None, then the last sample is read
    :type s1: int
    :param s0: The first or start sample to read from the file. If it is None, then the data is read from the first
    :type s0: int
    :param sample_count_key: The name of the header field that defines the sample count
    :type sample_count_key: string
    :param data_format_key: The name of the header field that defines the data format
    :type data_format_key: string
    :param sample_format_key: The name of the header field that defines the sample format
    :type sample_format_key: string
    :param start_time_key: The name of the header field that defines the start time of the first sample
    :type start_time_key: string
    :param sample_rate_key: The name of the header field that defines the number of samples per second
    :type sample_rate_key: string
    :param path: The full path to the file to read
    :type path: string
    :param header_only: Flag to return the header of the file without reading the remainder of the file
    :type header_only: bool
    :return: the contents of the file
    :rtype: Waveform

    import struct
    """
    import struct

    try:
        header, f_in = AudioMetaData.from_standard_binary_file(path)
        if header_only:
            return header

        #   Now to effectively understand how to read the data from the binary portion, we must determine
        #   where specific data within the header exist. So look for the elements that were defined within
        #   the function prototype.
        #
        #   The sample rate
        fs = header.read_sample_rate(sample_rate_key)

        #   The start time of the audio file
        t0 = header.read_start_time(start_time_key)

        #   The number of samples in the waveform
        length = header.read_sample_count(sample_count_key)

        #   At this point there should be no reason for the data to be stored as anything other than REAL*4
        #   Little Endian, but we do not account for any other formats, so we must now examine what is in the
        #   header and exit if it is not what we expect.
        header.read_format(sample_format_key, data_format_key)

        if s0 is not None and s0 > 0:
            # At this point we should interrogate the header to determine the size of the data sample,
            # but we are only supporting floating point values, so we can just increment the current location
            # by four times the desired start sample. So let's move the counter from the current position.
            f_in.seek(s0 * 4, 1)

        #   Now we need to determine how many sample to read
        if s0 is not None and s1 is None:
            length -= s0
            if isinstance(t0, datetime.datetime):
                t0 += datetime.timedelta(seconds=s0 / fs)
            elif isinstance(t0, float):
                t0 += s0 / fs
        elif s0 is None and s1 is not None:
            length = s1
        elif s0 is not None and s1 is not None:
            length = s1 - s0
            if isinstance(t0, datetime.datetime):
                t0 += datetime.timedelta(seconds=s0 / fs)
            elif isinstance(t0, float):
                t0 += s0 / fs

        #   Read the data - At this point we only support 32-bit/4-byte data samples
        data = f_in.read(4 * length)

        #   Now unpack the data from the array of bytes into an array of floating point data
        samples = np.asarray(struct.unpack('f' * length, data))

        #   close the file
        f_in.close()

        return Waveform(
            pressures=samples,
            sample_rate=fs,
            start_time=t0,
            header=header
            )

    except IndexError:
        f_in.close()

        raise ValueError()
    except ValueError:
        f_in.close()

        raise ValueError()
