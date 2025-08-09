from enum import Enum


class WindowingMethods(Enum):
    """
    The available windowing methods for the waveform
    """

    hanning = 1
    hamming = 2
    tukey = 3
    rectangular = 4


class TrimmingMethods(Enum):
    """
    Trimming can be accomplished with either the samples or times. This enumeration defines whether to use the time to
    calculate the sample or just provide the samples.
    """

    samples = 1
    times_absolute = 2
    times_relative = 3


class ScalingMethods(Enum):
    """
    In scaling the waveform we can apply the level changes in either decibels or linear values. This will determine how
    the interface scales the signal when manipulating the sample magnitudes.
    """

    linear = 1
    logarithmic = 2


class WeightingFunctions(Enum):
    """
    This class provides the options on how to weight the calculation of the overall level values
    """

    unweighted = 0
    a_weighted = 1
    c_weighted = 2


class CorrelationModes(Enum):
    """
    This class defines the various modes for the cross-correlation function.
    """

    valid = 0
    full = 1
    same = 2


class NoiseColor(Enum):
    white = 0
    pink = 1
    brown = 2


class LeqDurationMode(Enum):
    """
    The available types of time scaling for conversion of a signal to equivalent levels
    """

    steady_state = 0
    transient = 1


class AnalysisMethod(Enum):
    """
    |Description: Method for processing impulse metrics.
    """

    NONE = 0
    MIL_STD_1474E = 1
    MIL_STD_1474E_AFRL_PREF = 2
    NO_A_DURATION_CORRECTIONS = 3