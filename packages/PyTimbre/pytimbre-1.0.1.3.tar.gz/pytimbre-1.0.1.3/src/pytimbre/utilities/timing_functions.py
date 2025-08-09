import numpy as np
import datetime


def irig_converter(signal):
    """
    Compute the time of the signal using the IRIG-B format as reference.

    Parameters
    ----------
    signal : double, array-like

    Returns
    -------
    datetime object for the start of the sample
    """

    irig = signal * 30.0 / np.max(signal)
    si = np.sign(irig - np.mean(irig))

    dsi = np.diff(si)

    rise = np.where(dsi == 2)[0]
    fall = np.where(dsi == -2)[0]

    if np.min(fall) < np.min(rise):
        fall = fall[1:]

    if np.max(rise) > np.max(fall):
        rise = rise[:-1]

    rf = np.stack([rise, fall]).transpose()

    index = np.round(np.mean(rf, axis=1, dtype='int'))
    top = irig[index]
    top2 = (top > 20) * 30 + (top < 20) * 10 - 10

    p0pr = np.array([30, 30, 30, 30, 30, 30, 30, 30, 10, 10, 30, 30, 30, 30, 30, 30, 30, 30]) - 10

    #   Locate this sequence in the top2 array

    pr = list()
    for i in range(len(top2) - len(p0pr)):
        located = True
        for j in range(len(p0pr)):
            if top2[i + j] != p0pr[j]:
                located = False
                break
        if located:
            pr.append(i + 10)

    prrise = rise[pr]
    sps = np.mean(np.diff(prrise))

    carr = np.mean(np.diff(pr))

    seconds = np.zeros((len(pr) - 1,))
    minutes = np.zeros((len(pr) - 1,))
    hours = np.zeros((len(pr) - 1,))
    day_of_year = np.zeros((len(pr) - 1,))
    dt = np.zeros((len(pr) - 1,))

    for j in range(len(pr) - 1):

        start_index = int(pr[j] + 0.01 * carr)
        stop_index = int(pr[j] + 0.01 * 2 * carr)

        values = np.array([1, 2, 4, 8, 0, 10, 20, 40])
        mask = np.zeros((len(values),))

        for i in range(len(mask)):
            if np.sum(top2[start_index:stop_index]) > 70:
                mask[i] = 1

            start_index += 10
            stop_index += 10

        seconds[j] = np.sum(values * mask)

        start_index = int(pr[j] + 0.01 * carr * 10)
        stop_index = int(pr[j] + 0.01 * 11 * carr)

        values = np.array([1, 2, 4, 8, 0, 10, 20, 40])
        mask = np.zeros((len(values),))

        for i in range(len(mask)):
            if np.sum(top2[start_index:stop_index]) > 70:
                mask[i] = 1

            start_index += 10
            stop_index += 10

        minutes[j] = np.sum(values * mask)

        start_index = int(pr[j] + 0.01 * carr * 20)
        stop_index = int(pr[j] + 0.01 * 21 * carr)

        values = np.array([1, 2, 4, 8, 0, 10, 20])
        mask = np.zeros((len(values),))

        for i in range(len(mask)):
            if np.sum(top2[start_index:stop_index]) > 70:
                mask[i] = 1

            start_index += 10
            stop_index += 10

        hours[j] = np.sum(values * mask)

        start_index = int(pr[j] + 0.01 * carr * 30)
        stop_index = int(pr[j] + 0.01 * 31 * carr)

        values = np.array([1, 2, 4, 8, 0, 10, 20, 40, 80, 0, 100, 200])
        mask = np.zeros((len(values),))

        for i in range(len(mask)):
            if np.sum(top2[start_index:stop_index]) > 70:
                mask[i] = 1

            start_index += 10
            stop_index += 10

        day_of_year[j] = np.sum(values * mask)

        #   Determine the linear adjustment for the zero cross over not occurring right on the sample

        dt[j] = (np.interp(0, [irig[prrise[j]], irig[prrise[j] + 1]], [prrise[j], prrise[j] + 1]) - prrise[j]) / sps

    #   Compute the time past midnight

    times = 60 * (60 * hours + minutes) + seconds - dt

    day_of_year = np.mean(day_of_year)

    index = np.arange(0, len(irig))
    timevector = times[0] + (index - prrise[0]) / sps

    return times[0] - prrise[0] / sps, day_of_year

def irig_converter_for_arc(data, fs):
    """
    The timecode generators present at the Aeroacoustic Research Complex (ARC) produce the signal that defines
    the IRIG-
    B timecode differently. The previous methods do not return the correct information for the ARC data.


    """
    #   Find the index of the first minimum - which is assumed to occur within the first second of the waveform

    index = np.where(data[:fs] == np.min(data[:fs]))[0][0]

    #   The IRIG-B waveform is an amplitude modulated 1 kHz sine wave.  So we need to know the number of samples
    #   for a single period of the waveform

    frequency = 1000
    period = 1 / frequency
    period_samples = period * fs

    #   Now we can get the first set of signals and determine the amplitude for the minima

    amplitudes = np.zeros((3000,))

    for i in range(3000):
        amplitudes[i] = data[int(index + i * period_samples)]

        if index + (i + 1) * period_samples >= len(data):
            break

    maximum_index = i

    #   Scale by the smallest value in this array

    amplitudes /= np.min(amplitudes)

    #   Convert this to a binary array that will be used for the determination of the bit-wise elements of the
    #   signal

    binary_array = np.zeros((maximum_index,))

    for i in range(maximum_index):
        if amplitudes[i] >= 0.8:
            binary_array[i] = 1

    #   Now the start of a signal must be with a signal that is 8, so we need to locate the first 8 within the
    #   summation of the binary signal.

    first_eight = -1
    for i in range(3000):
        elements = binary_array[i:i + 10]

        if np.sum(elements) == 8 and binary_array[i] == 1 and binary_array[i + 9] == 0:
            first_eight = i
            break

    if first_eight < 0:
        return None, None

    #   Now that we have determined the location of the first 8, we can begin to sum the binary array in
    #   sections of 10 elements at a time

    summed_array = np.zeros((250,))

    for i in range(250):
        idx = first_eight + i * 10
        summed_array[i] = np.sum(binary_array[idx:idx + 10])

    #   Now we must find the first double-8 as this marks the beginning of the time code definition

    first_double_eight = -1
    for i in range(250):
        if summed_array[i] == 8 and summed_array[i + 1] == 8:
            first_double_eight = i + 1
            break

    if first_double_eight < 0:
        return None, None

    #   Now from this we need to extract the various parts of the time code

    timecode_elements = summed_array[first_double_eight:first_double_eight + 100]

    #   Get the hours

    hour_elements = timecode_elements[20:30]
    hour_elements[np.where(hour_elements < 5)[0]] = 0
    hour_elements[np.where(hour_elements >= 5)[0]] = 1

    weights = np.array([1, 2, 4, 8, 0, 10, 20, 0, 0, 0])

    hour = np.sum(hour_elements * weights)

    #   Get the minutes

    minute_elements = timecode_elements[10:20]
    minute_elements[np.where(minute_elements < 5)[0]] = 0
    minute_elements[np.where(minute_elements == 5)[0]] = 1
    weights = np.array([1, 2, 4, 8, 0, 10, 20, 40, 0, 0])

    minutes = np.sum(minute_elements * weights)

    #   Next the seconds

    seconds_elements = timecode_elements[:10]
    seconds_elements[np.where(seconds_elements < 5)[0]] = 0
    seconds_elements[np.where(seconds_elements == 5)[0]] = 1
    weights = np.array([0, 1, 2, 4, 8, 0, 10, 20, 40, 0])

    seconds = np.sum(seconds_elements * weights)

    #   And finally we get the julian date of the time code

    date_elements = timecode_elements[30:42]
    date_elements[np.where(date_elements != 5)[0]] = 0
    date_elements[np.where(date_elements == 5)[0]] = 1
    weights = np.array([1, 2, 4, 8, 0, 10, 20, 40, 80, 0, 100, 200])

    julian_date = np.sum(weights * date_elements)

    #   Now we know that the time code was not at the very beginning of the signal, so let's go ahead and
    #   determine the time offset to the beginning of the file.

    tpm = 60 * (60 * hour + minutes) + seconds

    file_start_adjustment = (((first_double_eight + 1) * 10 + first_eight) * (fs / 1000) + index) / fs

    tpm -= file_start_adjustment

    return tpm, julian_date