import pandas as pd
import numpy as np
import warnings
import datetime
from pytimbre.audio import Waveform
from pytimbre.spectral.spectral_frame_builder import FrameBuilder
from pytimbre.spectral.spectra import Spectrum
from pytimbre.utilities.metadata import AudioMetaData


class SpectralTimeHistory:
    """
    This class wraps the ability of the analysis to contain multiple spectrum objects and create a variation across
    time.

    Remarks
    2022-12-13 - FSM - added a function to collect the sound quality metrics from each of the spectra
    2022-12-13 - FSM - added a function to collect the times past midnight from the spectra objects
    """

    def __init__(self):
        """
        Constructor - this will build a class object for the TimeHistory and instantiate all properties and protected
        elements.

        Parameters
        ----------
        :param a: This is the waveform object that we want to process into a TimeHistory object
        :param integration_time: float - the size of the independent waveforms that will be processed into a series of
            Spectrum objects
        """

        self._spectra = None
        self._times = None
        self._waveform = None
        self._header = None
        self._frame_builder = None
        self._explicit_duration = None

    def __len__(self):
        return len(self._spectra)

    def _write_header(self, file):
        """
        This function writes the header to the output file
        :param file: The FileIO object that was opened to store the data
        :type file: FileIO
        """
        from pytimbre.utilities.metadata import AudioMetaData

        #   If the header dictionary is present, write it to the output file
        if self.header is not None:
            header_line = ';{},{}\n'.format("HEADER SIZE", len(self.header) + 1)
            file.write(header_line)
            unwanted_strs = [',']

            if isinstance(self.header, AudioMetaData):
                for key in self.header.data_keys:
                    new_key = key
                    for str in unwanted_strs:
                        new_key = key.replace(str, "_")
                    header_line = ';{},{}\n'.format(new_key.upper(), self.header.get_field(key))
                    file.write(header_line)
            elif isinstance(self.header, dict):
                for key in self.header.keys():
                    new_key = key
                    for str in unwanted_strs:
                        new_key = key.replace(str, "_")
                    header_line = ';{},{}\n'.format(new_key.upper(), self.header[key])
                    file.write(header_line)

        #   Now write the last header row which will have the time and frequency array
        header_line = ';{}'.format('year').ljust(7, ' ')
        header_line += ',{}'.format('month').ljust(7, ' ')
        header_line += ',{}'.format('day').ljust(7, ' ')
        header_line += ',{}'.format('hour').ljust(7, ' ')
        header_line += ',{}'.format('minute').ljust(7, ' ')
        header_line += ',{}'.format('second').ljust(7, ' ')

        for f in self.frequencies:
            header_line += ',{:6.2f}'.format(f).ljust(10, ' ')

        header_line += '\n'
        file.write(header_line)

    def concatenate(self, b=None, inplace: bool = False, normalize_time: bool = False):
        """
        This function will concatenate the TimeHistory that is passed as an argument to the current element. If the
        inplace argument is True, the data is concatenated to the current object, otherwise it is returned as a new
        object.

        Parameters
        ----------
        :param b: TimeHistory
            This is the object to concatenate with the current object
        :param inplace: bool
            Default = False - When False, this function will return a new TimeHistory Object, otherwise it returns a
            new TimeHistory object
        :param normalize_time: bool
            Default = False - This will normalize the time to a zero for the first spectra.
        """
        if not isinstance(b, SpectralTimeHistory):
            raise ValueError("The first argument is required to be a TimeHistory object.")
        if not np.array_equal(self.frequencies, b.frequencies):
            raise ValueError("Two TimeHistory objects must have same frequency content.")
        if np.round(self.integration_time, decimals=3) != np.round(b.integration_time, decimals=3):
            raise AttributeError("Two TimeHistory objects must have same integration time.")
        warnings.warn(
            'Concatenated TimeHistory object currently returns the header equal to the header of the first '
            'TimeHistory object only.'
        )

        if not inplace:
            #   Create the TimeHistory object without any data
            th = SpectralTimeHistory()
            th._header = self._header
            th._spectra = np.empty(len(self.times) + len(b.times), dtype=Spectrum)
            n = 0

            #   Loop through the current object and copy the contents of the spectra to the new object
            for i in range(len(self.times)):
                th._spectra[n] = self.spectra[i]
                if normalize_time:
                    th._spectra[n]._time0 = n * self.integration_time
                n += 1

            for i in range(len(b.times)):
                th._spectra[n] = b.spectra[i]
                if normalize_time:
                    th._spectra[n]._time0 = n * self.integration_time
                n += 1

            th.duration = self.duration + b.duration
            return th

        else:
            raise NotImplementedError("inplace concatenation not yet implemented.")

    def to_dataframe(self):
        """
        This function converts the information within the time history object into a Pandas.DataFrame
        :return: The data organized with the header as part of every row within a data frame
        :rtype: Pandas.DataFrame
        """
        #   Build the names of the columns for the DataFrame
        names = list(self.header.data_keys)
        names.append('tpm')
        for f in self.frequencies:
            names.append('F{:05.0f}Hz'.format(f))

        dataset = pd.DataFrame(columns=names, index=np.arange(len(self.times)))
        i = len(self.header.data_keys)
        dataset.iloc[:, i] = self.times_past_midnight
        dataset.iloc[:, i + 3:] = self.spectrogram_array_decibels

        for key in self.header.data_keys:
            dataset[key] = self.header.get_field(key)

        return dataset

    def to_fractional_octave_band(self, bandwidth: int = 3, f0: float = 10, f1: float = 10000):
        """
        This creates a new TimeHistory object where the spectral objects are representations of the fractional octave
        bandwidths rather than the narrowband. This will check the contents of the current class and determine
        whether the conversion is appropriate (i.e. this is a narrowband spectral representation). If not a warning
        is thrown.
        :param bandwidth: The desired output fractional octave bandwidth
        :type bandwidth: int
        :param f0: the desired output lower limit frequency
        :type f0: float
        :param f1: the desired output upper limit frequency
        :type f1: float
        :return: The new fractional octave resolution time history object
        :rtype: SpectralTimeHistory
        """

        t = SpectralTimeHistory()

        t._waveform = self.waveform
        t._spectra = np.empty(len(self.spectra), dtype=Spectrum)
        t._header = self.header

        for i in range(len(self.spectra)):
            t._spectra[i] = self.spectra[i].to_fractional_octave_band(bandwidth=bandwidth, f0=f0, f1=f1)

        return t

    def save(self, filename: str):
        import datetime

        """
        This function saves the data from the waveform's header and the spectral information to a file 

        Parameters:
        -----------
        :param filename: string - the fill path to the output file
        
        Remarks
        -------
        20230221 - FSM - Updated the constructor to assign the header to the time history object if there is a header 
            within the Waveform object passed to the constructor.
        """

        #   open the output file
        file = open(filename, 'wt')
        self._write_header(file)

        #   Now loop through the data
        for time_idx in range(len(self.spectra)):
            if isinstance(self.spectra[time_idx].time, datetime.datetime):
                data_line = '{:04.0f}'.format(self.spectra[time_idx].time.year).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(self.spectra[time_idx].time.month).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(self.spectra[time_idx].time.day).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(self.spectra[time_idx].time.hour).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(self.spectra[time_idx].time.minute).ljust(7, ' ')
                data_line += ',{:02.3f}'.format(
                    self.spectra[time_idx].time.second +
                    self.spectra[time_idx].time.microsecond * 1e-6
                ).ljust(7, ' ')
            else:
                hour = np.floor(self.spectra[time_idx].time / 3600)
                minute = np.floor((self.spectra[time_idx].time - hour * 3600) / 60)
                second = self.spectra[time_idx].time - 60 * (60 * hour + minute)

                data_line = '{:04.0f}'.format(0).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(0).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(0).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(hour).ljust(7, ' ')
                data_line += ',{:02.0f}'.format(minute).ljust(7, ' ')
                data_line += ',{:02.3f}'.format(second).ljust(7, ' ')

            #   Add the decibel data to the data_line object

            for j in range(len(self.frequencies)):
                data_line += ',{:03.2f}'.format(
                    self.spectra[time_idx].pressures_decibels[j]
                ).ljust(10, ' ')

            data_line += '\n'
            file.write(data_line)

        file.close()

    def trim(self, start_time=None, end_time=None, inplace: bool = False):
        """
        This function creates a subset of the existing data that is between the start_time and end_time objects. If the
        start_time is None then no elements are eliminated from the beginning; if the end_time is None then no elements
        are eliminated from the end.
        :param start_time:
            The start time of the subset. This can be either represented as a datetime object or a float. If the
            value is None, then the start time of the system is used.
        :param end_time:
            The stop time of the subset. This can be either represented as a datetime object or a float. If the
            value is None, then the stop time of the system is used.
        :param inplace:
            This parameter determines whether the data will be stored in the current object, loosing any values that
            were excluded based on the start_time and end_time. If True the data is lost, otherwise the subset is
            returned as a new object.
        """

        #   Determine the start of the subset
        if start_time is None:
            t0 = self.times_past_midnight[0]
        else:
            if isinstance(start_time, datetime.datetime):
                t0 = float(60 * (60 * start_time.hour + start_time.minute) + start_time.second) + float(
                    start_time.microsecond
                ) / 1e-6
            else:
                t0 = start_time

        #   Determine the end of the subset
        if end_time is None:
            t1 = self.times_past_midnight[-1]
        else:
            if isinstance(end_time, datetime.datetime):
                t1 = float(60 * (60 * end_time.hour + end_time.minute) + end_time.second) + float(
                    end_time.microsecond
                ) / 1e-6
            else:
                t1 = end_time

        #   obtain the indices for the subset based on the time past midnight estimation of the times
        idx = np.nonzero((self.times_past_midnight >= t0) & (self.times_past_midnight <= t1))[0]

        #   Determine whether we will eliminate the data from this object or return a new object
        if inplace:
            self._times = self.times[idx]
            self._spectra = self.spectra[idx]
        else:
            spectra = SpectralTimeHistory()
            spectra._spectra = self.spectra[idx]
            spectra._times = self.times[idx]
            spectra._integration_time = np.mean(np.diff(spectra._times))
            spectra._header = self.header

            return spectra

    @property
    def waveform(self):
        if self._waveform is None:
            warnings.warn('No Waveform object has been passed to this TimeHistory object.')
        return self._waveform

    @property
    def signal(self):
        return self.waveform.samples

    @property
    def waveform_sample_rate(self):
        return self.waveform.sample_rate

    @property
    def time_history_sample_rate(self):
        """
        The number of samples per second of evey TimeHistory metric.
        """
        return 1.0 / self.integration_time

    @property
    def integration_time(self):
        return np.diff(self.times_past_midnight)[0]

    @property
    def duration(self):
        if self._waveform is not None:
            return self._waveform.duration
        elif self.frame_builder is not None:
            return self.times[-1] - self.times[0] + self.frame_builder.frame_length_seconds
        else:
            return self._explicit_duration

    @duration.setter
    def duration(self, value):
        self._explicit_duration = value

    @property
    def times(self):
        if self.spectra[0].time_past_midnight is not None:
            t = np.zeros((len(self._spectra),), dtype=datetime.datetime)
        else:
            t = np.zeros((len(self._spectra),))

        for i in range(len(self.spectra)):
            if self.spectra[i]._waveform is not None:
                t[i] = self.spectra[i].time
            else:
                t[i] = self.spectra[i].time_past_midnight

        return t

    @property
    def waveform_sample_size(self):
        return int(np.floor(self.integration_time * self._waveform.sample_rate))

    @property
    def frequencies(self):
        return self._spectra[0].frequencies

    @property
    def spectra(self):
        return self._spectra

    @property
    def spectrogram_array_decibels(self):
        spectrogram = np.zeros([len(self._spectra), len(self._spectra[0].frequencies)])
        for i in range(len(self._spectra)):
            spectrogram[i, :] = self._spectra[i].pressures_decibels

        return spectrogram

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        self._header = value

    @property
    def times_past_midnight(self):
        tpm = np.zeros((len(self.spectra),))

        for i in range(len(tpm)):
            tpm[i] = self.spectra[i].time_past_midnight

        return tpm

    @property
    def fft_size(self):
        return self.spectra[0].fft_size

    @property
    def is_narrowband_resolution(self):
        is_nb = True
        for spec in self.spectra:
            is_nb &= spec.is_narrowband_resolution

        return is_nb

    @property
    def is_fractional_octave_resolution(self):
        return not self.is_narrowband_resolution

    @property
    def fractional_octave_bandwidth(self):
        bw = list()
        for spec in self.spectra:
            bw.append(spec.fractional_octave_bandwidth)

        return np.mean(bw)

    @property
    def frame_builder(self) -> FrameBuilder:
        return self._frame_builder

    @staticmethod
    def from_data(levels, frequencies, times, levels_as_pressure: bool = False):
        """
        This function constructs the Spectrogram object from information obtained from the users and sets up an object
        that can be compared with external data without concern for differences in the methods to calculate the
        spectrogram data.

        :param levels: array-like - the 2-D levels with shape = [len(times), len(frequencies)]
        :param frequencies: array-like - the collection of frequencies that define one dimension of the levels matrix
        :param times: array-like - the collection of times within the spectrogram that define the second dimension
        :param levels_as_pressure: boolean - if True the levels matrix is assumed to be a pressure matrix,
        otherwise the levels are converted to a pressure matrix
        :returns: Spectrogram object
        """

        s = SpectralTimeHistory()
        s._spectra = np.empty((len(times),), dtype=Spectrum)

        if levels_as_pressure:
            p = levels
        else:
            p = 20e-6 * 10 ** (levels / 20)

        for i in range(len(times)):
            spec = Spectrum()
            spec._time_past_midnight = times[i]
            spec._time0 = times[i]
            spec.frequencies = frequencies
            spec.pressures_pascals = p[i, :]

            s._spectra[i] = spec

        return s

    @staticmethod
    def load(filename: str):
        """
        This function loads the information from a file into the class object
        :param filename: the path to the file to be loaded
        :type filename: str
        :return: The contents of the file
        :rtype: SpectralTimeHistory
        """
        import os.path

        if not os.path.exists(filename):
            raise ValueError("The filename must exist")

        file = open(filename, "rt")
        contents = file.readlines()
        file.close()

        th = SpectralTimeHistory()

        if contents[0][0] == ';':
            th._header = dict()

            n = 0

            while contents[n][0] == ';' and not (contents[n][:5] == ";year"):
                #   Split the data apart based on the comma
                elements = contents[n].split(',')
                if len(elements) == 2:
                    th._header[elements[0][1:]] = elements[1][:-1]
                else:
                    value = elements[-1][:-1]
                    name = ','.join(elements[:-1])
                    th._header[name[1:]] = value

                #   increment the line
                n += 1

                if contents[n] == "\n":
                    n += 1

            elements = contents[n].split(',')
            f = list()
            for freq_index in range(6, len(elements)):
                f.append(float(elements[freq_index]))

            frequencies = np.asarray(f)
            n += 1

            th._spectra = np.empty((len(contents) - n,), dtype=Spectrum)

            for line_index in range(n, len(contents)):
                elements = contents[line_index].split(',')

                if int(elements[0]) == int(elements[1]) == int(elements[2]) == 0:
                    time = 60 * (60 * float(elements[3]) + float(elements[4])) + float(elements[5])
                else:
                    year = int(elements[0])
                    month = int(elements[1])
                    day = int(elements[2])
                    hour = int(elements[3])
                    minute = int(elements[4])
                    seconds = float(elements[5])
                    second = int(np.floor(seconds))
                    microsecond = int(np.floor(1e6 * (seconds - second)))
                    time = datetime.datetime(year, month, day, hour, minute, second, microsecond)

                spl = np.zeros((len(frequencies),))
                for spl_idx in range(6, len(elements)):
                    spl[spl_idx - 6] = float(elements[spl_idx])

                th._spectra[line_index - n] = Spectrum()
                th._spectra[line_index - n]._frequencies = frequencies
                th._spectra[line_index - n]._acoustic_pressures_pascals = 20e-6 * 10 ** (spl / 20)
                th._spectra[line_index - n]._time0 = time

            #   Set the integration time as the difference between the first and second times
            th._integration_time = th.times[1] - th.times[0]
            th.duration = th.times[-1] - th.times[0] + th.integration_time
            return th

    @staticmethod
    def from_fourier_transform(wfm: Waveform, fb: FrameBuilder, fft_size: int = None):
        """
        This function creates a series of Spectrum objects using the FFT methods that exist within the Spectrum object.
        The waveform for each frame are defined by the FrameBuilder object.
        :param wfm: The audio to process
        :type wfm: Waveform
        :param fft_size: The number of frequency bins
        :type fft_size: int
        :param fb: The class that partitions the waveform for each frame
        :type fb: FrameBuilder
        :return: The spectral time history object
        :rtype: SpectralTimeHistory
        """

        n = fb.complete_frame_count
        s = SpectralTimeHistory()
        s._waveform = wfm
        s._spectra = np.empty((n,), dtype=Spectrum)
        for i in range(n):
            s._spectra[i] = Spectrum.from_fourier_transform(fb.get_next_waveform_subset(wfm), fft_size=fft_size)

        s.header = wfm.header
        s._waveform = wfm
        s._frame_builder = fb

        return s

    @staticmethod
    def from_digital_filters(
            wfm: Waveform,
            fb: FrameBuilder,
            frequency_resolution: int = 3,
            f0: float = 10.,
            f1: float = 10000
    ):
        """
        This constructs the individual Spectrum objects with digital filters.
        :param wfm: The audio data
        :type wfm: Waveform
        :param fb: the class that partitions the waveform for each frame
        :type fb: FrameBuilder
        :param frequency_resolution: The fractional octave frequency resolution
        :type frequency_resolution: int
        :param f0: The desired start frequency
        :type f0: float
        :param f1: The desired stop frequency
        :type f1: float
        :return: The spectral time history developed from fractional octave digital filters
        :rtype: SpectralTimeHistory
        """
        n = fb.complete_frame_count
        s = SpectralTimeHistory()
        s._waveform = wfm
        s._spectra = np.empty((n,), dtype=Spectrum)
        for i in range(n):
            s._spectra[i] = Spectrum.from_digital_filters(
                fb.get_next_waveform_subset(wfm),
                frequency_resolution,
                f0,
                f1
            )

        s.header = wfm.header
        s._frame_builder = fb

        return s


class OverallLevelTimeHistory:
    """
    This class defines the collection of overall levels as a dictionary. As additional levels are defined and added to
    the LevelMetrics class they will be added to the dictionary. This object contains a list of times and a dictionary
    that contains a list of levels.
    """

    def __init__(self):
        """
        Initialize the data within the class
        """

        self._metrics = dict()
        self._times = list()
        self._waveform = None
        self._header = None
        self._frame_builder = None
        self._explicit_duration = None

    @property
    def times(self) -> list:
        return self._times

    @times.setter
    def times(self, times: list):
        self._times = times

    @property
    def metrics(self) -> dict:
        return self._metrics

    @metrics.setter
    def metrics(self, metrics: dict):
        self._metrics = metrics

    @property
    def header(self) -> AudioMetaData:
        return self._header

    @header.setter
    def header(self, header: AudioMetaData):
        self._header = header

    @property
    def frame_builder(self) -> FrameBuilder:
        return self._frame_builder

    @property
    def duration(self):
        if self._waveform is not None:
            return self._waveform.duration
        elif self._frame_builder is not None:
            return self.times[-1] - self.times[0] + self.frame_builder.frame_length_seconds
        else:
            return self._explicit_duration

    @duration.setter
    def duration(self, duration: float):
        self._explicit_duration = duration

    @property
    def integration_time(self):
        return np.diff(self.times)[0]

    @property
    def time_history_sample_rate(self):
        """
        The number of samples per second of evey TimeHistory metric.
        """
        return 1.0 / self.integration_time

    @property
    def times_past_midnight(self)->list:
        if isinstance(self.times[0], float):
            return self.times
        elif isinstance(self.times[0], datetime.datetime):
            tpm = list()
            for time in self.times:
                tpm.append(60 * (60 * time.hour + time.minute) + time.second + time.microsecond / 1e6)

            return tpm

    @staticmethod
    def from_SpectralTimeHistory(sth: SpectralTimeHistory):
        """
        This function extracts the data from the spectral time history and builds the data for the class with the
        LevelMetrics class.
        :param sth: The spectral data over time
        :type sth: SpectralTimeHistory
        :return: The collection of levels that were calculated from the spectrum objects at each time frame
        :rtype: OverallLevelTimeHistory
        """
        from pytimbre.timbre_features.metrics.level import LevelMetrics as lm

        levels = lm.from_time_history(sth)

        oth = OverallLevelTimeHistory()
        if sth.waveform is not None:
            oth._waveform = sth.waveform

        if sth.header is not None:
            oth._header = sth.header

        oth.times = levels.time_history.times
        oth.metrics['la'] = levels.overall_a_weighted_level
        oth.metrics['lz'] = levels.overall_level
        oth.metrics['lc'] = levels.overall_c_weighted_level
        if sth.is_fractional_octave_resolution:
            oth.metrics['pnl'] = levels.perceived_noise_level

        return oth

    def to_dataframe(self)->pd.DataFrame:
        names = ['times']
        for key in self.metrics.keys():
            names.append(key)

        df = pd.DataFrame(columns=names, index=np.arange(len(self.times)))

        df['times'] = self.times
        for key in self.metrics.keys():
            df[key] = self._metrics[key]

        return df