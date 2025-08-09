from scipy import interpolate
import numpy as np
# import librosa
import scipy.signal
from .spectra import Spectrum

"""
| Description: libf0 SWIPE implementation
| Contributors: Sebastian Rosenzweig, Vojtěch Pešek, Simon Schwär, Meinard Müller
| License: The MIT license, https://opensource.org/licenses/MIT
| This file is part of libf0.
"""
"""
This file was downloaded on 1 April 2023, from https://github.com/groupmm/libf0. This swipe.py file was integrated into
the structure of the PyTimbre module to facilitate the calculation of the fundamental frequency. However, there are a
number of dependencies that were not required by PyTimbre. 

2023_04_01 - FSM - Function arguments were normalized to the standard Python rules.
2023-04-06 - FSM - Updated the swipe function to use the SciPy.Signal.STFT function rather than librosa
2023-04-06 - FSM - Removed all functions that rely on librosa
"""


def swipe_spectral_estimation(x: Spectrum, hop_size: float = 256, minimum_frequency: float = 10.0,
                              maximum_frequency: float = 10000, pitch_resolution: float = 1 / 100,
                              erb_resolution: float = 0.1,
                              strength_threshold: float = 0):
    if x.waveform is None:
        raise ValueError("At this point, you must provide a Spectrum object that has been created from a waveform")
    t = x.time

    # Compute pitch candidates
    pc = 2 ** np.arange(np.log2(minimum_frequency), np.log2(maximum_frequency), pitch_resolution)

    # Pitch strength matrix
    S = np.zeros((len(pc),))

    # Determine P2-WSs [max, min]
    log_ws = np.round(np.log2(np.divide(8 * x.waveform.sample_rate, [minimum_frequency, maximum_frequency])))

    # P2-WSs - window sizes in samples
    ws = len(x.frequencies)

    # Determine window sizes used by each pitch candidate
    log2pc = np.arange(np.log2(minimum_frequency), np.log2(maximum_frequency), pitch_resolution)
    d = log2pc - np.log2(np.divide(8 * x.waveform.sample_rate, ws))

    # Create ERBs spaced frequencies (in Hertz)
    f_erbs = erbs2hz(np.arange(hz2erbs(pc[0] / 4), hz2erbs(x.waveform.sample_rate / 2), erb_resolution))

    #   Resample the frequency spectrum to the ERB frequencies
    loudness = interpolate.splev(f_erbs, interpolate.splrep(x.frequencies, x.pressures_pascals ** 2))
    # loudness = np.sqrt(magnitude)

    pc_to_compute = pc

    # Normalize loudness
    normalization_loudness = np.full_like(loudness, np.sqrt(np.sum(loudness * loudness, axis=0)))
    with np.errstate(divide='ignore', invalid='ignore'):
        loudness = loudness / normalization_loudness

    # Create pitch salience matrix
    S = np.zeros((len(pc_to_compute),))

    for j in range(0, len(pc_to_compute)):
        S[j] = pitch_strength_one(f_erbs, loudness, pc_to_compute[j])

    # pitch_strength = pitch_strength_all_candidates(f_erbs, loudness, pc_to_compute)

    pitches, strength = parabolic_interpolation(S, strength_threshold, pc)

    if np.isnan(pitches):
        pitches = 0  # avoid NaN output

    return pitches, t, strength


def swipe(samples, sample_rate: float = 22050, hop_size: float = 256, minimum_frequency: float = 55.0,
          maximum_frequency: float = 1760.0, pitch_resolution: float = 1 / 96, erb_resolution: float = 0.1,
          strength_threshold: float = 0):
    """
    Implementation of a sawtooth waveform inspired pitch estimator (SWIPE).
    This version of the algorithm follows the original implementation, see `swipe_slim` for a more efficient
    alternative.

    .. [#] Arturo Camacho and John G. Harris,
       "A sawtooth waveform inspired pitch estimator for speech and music."
       The Journal of the Acoustical Society of America, vol. 124, no. 3, pp. 1638–1652, Sep. 2008

    Parameters
    ----------
    samples : ndarray
        Audio signal
    sample_rate : int
        Sampling rate
    hop_size : int
        Hop size
    minimum_frequency : float or int
        Minimal frequency
    maximum_frequency : float or int
        Maximal frequency
    pitch_resolution : float
        resolution of the pitch candidate bins in octaves (default value = 1/96 -> 96 bins per octave)
    erb_resolution : float
        resolution of the ERB bands (default value = 0.1)
    strength_threshold : float
        confidence threshold [0, 1] for the pitch detection (default value = 0)

    Returns
    -------
    f0 : ndarray
        Estimated F0-trajectory
    t : ndarray
        Time axis
    strength : ndarray
        Confidence/Pitch Strength

    Remarks/Development
    2023-04-01 - FSM - updated the argument names, and put the parameter helpers into the list
    """

    t = np.arange(0, len(samples), hop_size) / sample_rate  # Times

    # Compute pitch candidates
    pc = 2 ** np.arange(np.log2(minimum_frequency), np.log2(maximum_frequency), pitch_resolution)

    # Pitch strength matrix
    S = np.zeros((len(pc), len(t)))

    # Determine P2-WSs [max, min]
    log_ws = np.round(np.log2(np.divide(8 * sample_rate, [minimum_frequency, maximum_frequency])))

    # P2-WSs - window sizes in samples
    ws = 2 ** np.arange(log_ws[0], log_ws[1] - 1, -1, dtype=np.int32)

    # Determine window sizes used by each pitch candidate
    log2pc = np.arange(np.log2(minimum_frequency), np.log2(maximum_frequency), pitch_resolution)
    d = log2pc - np.log2(np.divide(8 * sample_rate, ws[0]))

    # Create ERBs spaced frequencies (in Hertz)
    f_erbs = erbs2hz(np.arange(hz2erbs(pc[0] / 4), hz2erbs(sample_rate / 2), erb_resolution))

    for i in range(0, len(ws)):
        N = ws[i]
        hop_size = int(N / 2)

        x_zero_padded = np.concatenate([samples, np.zeros(N)])

        f, ti, x = scipy.signal.stft(x_zero_padded,
                                     fs=sample_rate,
                                     nperseg=hop_size,
                                     nfft=N,
                                     scaling='psd',
                                     boundary='zeros',
                                     padded=True)

        ti = np.insert(ti, 0, 0)
        ti = np.delete(ti, -1)

        spectrum = np.abs(x)
        magnitude = resample_ferbs(spectrum, f, f_erbs)
        loudness = np.sqrt(magnitude)

        # Select candidates that use this window size
        # First window
        if i == 0:
            j = np.argwhere(d < 1).flatten()
            k = np.argwhere(d[j] > 0).flatten()
        # Last Window
        elif i == len(ws) - 1:
            j = np.argwhere(d - i > -1).flatten()
            k = np.argwhere(d[j] - i < 0).flatten()
        else:
            j = np.argwhere(np.abs(d - i) < 1).flatten()
            k = np.arange(0, len(j))

        pc_to_compute = pc[j]

        pitch_strength = pitch_strength_all_candidates(f_erbs, loudness, pc_to_compute)

        resampled_pitch_strength = resample_time(pitch_strength, t, ti)

        lambda_ = d[j[k]] - i
        mu = np.ones(len(j))
        mu[k] = 1 - np.abs(lambda_)

        S[j, :] = S[j, :] + np.multiply(
            np.ones(resampled_pitch_strength.shape) * mu.reshape((mu.shape[0], 1)),
            resampled_pitch_strength
        )

    # Fine-tune the pitch using parabolic interpolation
    pitches, strength = parabolic_int(S, strength_threshold, pc)

    pitches[np.where(np.isnan(pitches))] = 0  # avoid NaN output

    return pitches, t, strength


def nyquist(sample_rate):
    """Nyquist Frequency"""
    return sample_rate / 2


def frequency_coefficients(k, fft_size, sample_rate):
    """Physical frequency of STFT coefficients"""
    return (k * sample_rate) / fft_size


def time_values(m, hop_size, sample_rate):
    """Physical time of STFT coefficients"""
    return m * hop_size / sample_rate


def hz2erbs(hz):
    """Convert Hz to ERB scale"""
    return 21.4 * np.log10(1 + hz / 229)


def erbs2hz(erbs):
    """Convert ERB to Hz"""
    return (10 ** np.divide(erbs, 21.4) - 1) * 229


def pitch_strength_all_candidates(ferbs, loudness, pitch_candidates):
    """Compute pitch strength for all pitch candidates"""
    # Normalize loudness
    normalization_loudness = np.full_like(loudness, np.sqrt(np.sum(loudness * loudness, axis=0)))
    with np.errstate(divide='ignore', invalid='ignore'):
        loudness = loudness / normalization_loudness

    # Create pitch salience matrix
    S = np.zeros((len(pitch_candidates), loudness.shape[1]))

    for j in range(0, len(pitch_candidates)):
        S[j, :] = pitch_strength_one(ferbs, loudness, pitch_candidates[j])
    return S


def pitch_strength_one(erbs_frequencies, normalized_loudness, pitch_candidate):
    """Compute pitch strength for one pitch candidate"""
    number_of_harmonics = np.floor(erbs_frequencies[-1] / pitch_candidate - 0.75).astype(np.int32)
    k = np.zeros(erbs_frequencies.shape)

    # f_prime / f
    q = erbs_frequencies / pitch_candidate

    for i in np.concatenate(([1], primes(number_of_harmonics))):
        a = np.abs(q - i)
        p = a < 0.25
        k[p] = np.cos(np.dot(2 * np.pi, q[p]))
        v = np.logical_and(0.25 < a, a < 0.75)
        k[v] = k[v] + np.cos(np.dot(2 * np.pi, q[v])) / 2

    # Apply envelope
    k = np.multiply(k, np.sqrt(1.0 / erbs_frequencies))

    # K+-normalize kernel
    k = k / np.linalg.norm(k[k > 0])

    # Compute pitch strength
    S = np.dot(k, normalized_loudness)
    return S


def resample_ferbs(spectrum, f, ferbs):
    """Resample to ERB scale"""

    magnitude = np.zeros((len(ferbs), spectrum.shape[1]))

    for t in range(spectrum.shape[1]):
        spl = interpolate.splrep(f, spectrum[:, t])
        interpolate.splev(ferbs, spl)

        magnitude[:, t] = interpolate.splev(ferbs, spl)

    return np.maximum(magnitude, 0)


def resample_time(pitch_strength, resampled_time, ti):
    """Resample time axis"""
    if pitch_strength.shape[1] > 0:
        pitch_strength = interpolate_one_candidate(pitch_strength, ti, resampled_time)
    else:
        pitch_strength = np.kron(np.ones((len(pitch_strength), len(resampled_time))), np.nan)
    return pitch_strength


def interpolate_one_candidate(pitch_strength, ti, resampled_time):
    """Interpolate time axis"""
    pitch_strength_interpolated = np.zeros((pitch_strength.shape[0], len(resampled_time)))

    for s in range(pitch_strength.shape[0]):
        t_i = interpolate.interp1d(ti, pitch_strength[s, :], 'linear', bounds_error=True)
        pitch_strength_interpolated[s, :] = t_i(resampled_time)

    return pitch_strength_interpolated


def parabolic_int(pitch_strength, strength_threshold, pc):
    """Parabolic interpolation between pitch candidates using pitch strength"""
    p = np.full((pitch_strength.shape[1],), np.nan)
    s = np.full((pitch_strength.shape[1],), np.nan)

    for j in range(pitch_strength.shape[1]):
        i = np.argmax(pitch_strength[:, j])
        s[j] = pitch_strength[i, j]

        if s[j] < strength_threshold:
            continue

        if i == 0:
            p[j] = pc[0]
        elif i == len(pc) - 1:
            p[j] = pc[0]
        else:
            I = np.arange(i - 1, i + 2)
            tc = 1 / pc[I]
            ntc = np.dot((tc / tc[1] - 1), 2 * np.pi)
            if np.any(np.isnan(pitch_strength[I, j])):
                s[j] = np.nan
                p[j] = np.nan
            else:
                c = np.polyfit(ntc, pitch_strength[I, j], 2)
                ftc = 1 / 2 ** np.arange(np.log2(pc[I[0]]), np.log2(pc[I[2]]), 1 / 12 / 64)
                nftc = np.dot((ftc / tc[1] - 1), 2 * np.pi)
                poly = np.polyval(c, nftc)
                k = np.argmax(poly)
                s[j] = poly[k]
                p[j] = 2 ** (np.log2(pc[I[0]]) + k / 12 / 64)
    return p, s


def parabolic_interpolation(pitch_strength, strength_threshold, pc):
    """Parabolic interpolation between pitch candidates using pitch strength"""

    i = np.argmax(pitch_strength)
    strength = pitch_strength[i]

    if strength < strength_threshold:
        return np.nan, np.nan

    if i == 0:
        return pc[0], pitch_strength[0]
    elif i == len(pc) - 1:
        return pc[-1], pitch_strength[-1]
    else:
        I = np.arange(i - 1, i + 2)
        tc = 1 / pc[I]
        ntc = np.dot((tc / tc[1] - 1), 2 * np.pi)
        if np.any(np.isnan(pitch_strength[I])):
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


def primes(n):
    """Returns a set of n prime numbers"""
    small_primes = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89,
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
