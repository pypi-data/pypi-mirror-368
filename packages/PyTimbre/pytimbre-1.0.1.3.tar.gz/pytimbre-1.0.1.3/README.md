![PyTimbre Logo](pytimbre_bing_gen_a.png " ") 

# PyTimbre
__PyTimbre is a Python conversion of the Matlab package Timbre Toolbox, found here:
(https://github.com/VincentPerreault0/timbretoolbox).__

This package was created in association with work conducted at the United States Air Force Research Laboratory on human 
perception of sound. Generally, models of perception have focused on sound pressure level spectra, and time histories of 
sound pressure. But auditory detection, identification/classification, and localization may be described better by 
attributes of the sound that are more based on perceptual studies of signals.

The concept of Timbre has been used in music perception research for many years. In 2011, Geoffroy Peeters compiled a 
collection of spectro-temporal attributes (features calculated on a frequency spectrum, that varies with time), and 
temporal attributes (features calculated on the waveform, or waveform's envelop). This paper forms the basis for the 
Matlab toolbox referenced above.

Though the Matlab coding functioned, it was cumbersome as Matlab is not a true object-oriented language. This conversion
has sought to integrate the calculation of the various timbre auditory features with the structure of classes and 
provides a more robust method for extension of these ideas and concepts than was available within the Matlab version.

In addition, a generic time waveform object (Waveform) was provided to represent the time signal. From this class, a 
child class is derived to read wave files. This derived class permits the reading of multiple types of wav files (
canonical, and non-canonical) with bit rates from 8-, 16-, 24-, and 32-bit. Also included are interface methods for
reading and adding meta-data that is similar to the MP3 tagging and assists in organizing the audio files by more than 
name or date.

Over the course of research at the United States Air Force Research Laboratory a number of other features were 
determined to be of interest for the use of the PyTimbre toolbox. In effort to unify these different extraction methods
with the data that PyTimbre represents, the tool kits were added to the requirements list and added as properties of the
various classes. 

Initially the sound quality metrics found in Mosqito project (https://github.com/Eomys/MoSQITo) were integrated into the 
interface. However, these functions became less stable across the variety of signals of interest to the Air Force 
researchers. The timbral_models (https://pypi.org/project/timbral_models/) were integrated into PyTimbre to replace the
roughness, sharpness, and loudness calculations. In addition, these codes added a number of other metrics. But, the 
original code relied on a number of libraries that were available, but cumbersome for off-line installation like 
soundfile and librosa. As a result the code was integrated into the PyTimbre interface as many of the features within 
these libraries were already available within PyTimbre.

In addition to this code, PyTimbre has taken the code from libf0 (https://github.com/groupmm/libf0) that assists with 
the computation of the fundamental frequency. There are a number of methods that exist within the libf0 module, but the
package contains a number of dependencies that are not required for the other calculations and computations within
PyTimbre. To facilitate the calculation of the fundamental frequency, the swipe class and associated functions were
extracted and placed into PyTimbre. The code was extracted from the 1.0.2 version of the code on 1 April 2023. This is 
based on the report: __*Justin Salamon and Emilia Gomez: Melody Extraction From Polyphonic Music Signals Using Pitch 
Contour Characteristics, IEEE Transactions on Audio, Speech, and Language Processing, vol. 20, no. 6, pp. 1759–1770, 
2012.*__ Unfortunately, this method became unstable with further development and required the use of librosa. Due to 
these limitations, the yin function replaced the swipe function to determine the fundamental frequency.


Additionally, this version of PyTimbre included the code for the determination of waveform clipping taken from 
clipdetect (https://pypi.org/project/clipdetect/#description). In similar manner as libf0, there were dependencies that
were required by this package that increased the load of the PyTimbre installation. This code is incorporated within the
Waveform class to make it available to all Waveform children classes. Usage of this code can be referenced this paper:
__*Hansen, John H. L., Allen Stauffer, and Wei Xia. Nonlinear Waveform Distortion: Assessment and Detection of Clipping
on Speech Data and Systems. Speech Communication 134 (2021): 20–31.*__

The code within this package has been used in a variety of research publications. These range from loading and saving 
audio data, to using the features extracted from the spectral time histories to model classification and detection of
aircraft.

# Usage Example
## 1. Defining a waveform from an array of values

    from pytimbre.waveform import Waveform

    fs = 48000
    w = 2 * np.pi * f
    t = np.arange(0, 10, 1/fs)

    wfm = Waveform(0.75 * np.sin(w*t), fs, 0.0)

## 2. Define a waveform from a wav file

    from pytimbre.audio_files.wavefile import WaveFile
    wfm = wave_file(filename)

## 3. Obtain global temporal attributes

    from pytimbre.audio_files.wavefile import WaveFile

    wfm = WaveFile(filename)
    print(wfm.amplitude_modulation)

## 4. Create single spectrogram and get a feature

    from pytimbre.audio_files.wavefile import WaveFile
    from pytimbre.spectra import SpectrumByFFT

    wfm = wave_file(filename)
    spectrum = SpectrumByFFT(wfm)
    print(spectrum.spectral_roll_off)

# Clearance review and publication permission

This software was developed in conjunction with research into the human perception of sound at the 711th Human 
Performance Wing, Airman Systems Directorate.  

It is approved for Distribution A, 88ABW-2020-2147.

A series of audio files employed in classification research within the wing are provided for testing and examples of how 
to use the interface.