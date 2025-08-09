import numpy as np
from pytimbre.audio import Waveform, AudioMetaData
from pytimbre.utilities.audio_analysis_enumerations import NoiseColor
from pytimbre.timbre_features.metrics.level import LevelMetrics


def generate_tone(
        frequency: float = 100, sample_rate: float = 48000, duration: float = 1.0,
        amplitude_db: float = 94
):
    """
    This function generates a sine wave tone function with the specific frequency and duration specified in the
    argument list.

    Parameters
    ----------
    frequency: float, default: 100 - the linear frequency of the waveform
    sample_rate: float, default: 48000 - the number of samples per second
    duration: float, default: 1.0 - the total number of seconds in the waveform
    amplitude_db: float, default:94, this is the RMS amplitude of the waveform

    Returns
    -------
    A waveform this the generated data.
    """

    amplitude_rms = 10 ** (amplitude_db / 20) * 2e-5
    x = np.arange(0, duration, 1 / sample_rate)
    y = amplitude_rms * np.sqrt(2) * np.sin(2 * np.pi * frequency * x)

    return Waveform(y, sample_rate, 0, header=AudioMetaData())


def generate_noise(
        sample_rate: float = 48000,
        duration: float = 1.0,
        amplitude_db: float = 94,
        noise_color=NoiseColor.pink
):
    import colorednoise as cn
    from pytimbre.utilities.audio_analysis_enumerations import ScalingMethods
    samples = cn.powerlaw_psd_gaussian(noise_color.value, int(np.floor(duration * sample_rate)))

    wfm = Waveform(samples, sample_rate, 0, header= AudioMetaData())
    scaling = amplitude_db - LevelMetrics.from_waveform(wfm).overall_level
    wfm.scale_signal(scaling, True, ScalingMethods.logarithmic)

    return wfm


def generate_friedlander(
        peak_level: float = 165, a_duration: float = 0.005, duration: float = 3
        , sample_rate: float = 200e3, blast_time: float = 0.005 / 2.0, noise: bool = False
):
    """
    Generates a generic_time_waveform object containing a Friedlander waveform
    :param peak_level: float, defaults to 165dB.
    :param a_duration: float, defaults to 0.005s.
    :param duration: float, length of total waveform in s. Defaults to 3s.
    :param sample_rate: float, defaults to 200e3 Hz.
    :param blast_time: float, time when friedlander starts in signal. Defualts to half the default a_duration and
    must be less than the duration of the signal minus 2 * a_duration.
    :param noise: bool, if True adds +/-94dB random noise (1pa) to the signal.

    -20220325 - SCC - Created method.
    """
    # time array, sec.
    t0 = 0.0

    if blast_time >= duration - 2.0 * a_duration:
        raise ValueError("Blast time inout must be before the end of the duration of the signal!")

    else:

        t = np.arange(t0, duration + 1 / sample_rate, 1 / sample_rate)

        if noise is True:
            p = np.random.randint(-1, 1, size=(len(t) - 1,)) / 1.0

        else:
            p = np.zeros(len(t) - 1)

        t_fried = np.arange(t0 / sample_rate, duration - blast_time + 1 / sample_rate, 1 / sample_rate)

        p_fried = np.exp(-1.0 * t_fried / a_duration)
        p_fried = np.multiply(p_fried, (1.0 - t_fried / a_duration))
        p_fried = (10.0 ** (peak_level / 20.0) * 2e-5) * p_fried

        p[round(blast_time * sample_rate - 1):] = p_fried

        fried = Waveform(
            pressures=p, sample_rate=sample_rate, start_time=t0, is_continuous_wfm=False,
            is_steady_state=False
        )
        fried.is_impulsive = True

        return fried
