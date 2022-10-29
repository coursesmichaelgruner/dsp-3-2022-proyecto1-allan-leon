#!/usr/bin/python3


from gtts import gTTS
from io import BytesIO
from pygame import mixer
import pyaudio
import math
import time
import numpy as np
import matplotlib.pyplot as plt

text_language = 'es'
mixer.init()

pyaudio_iface = pyaudio.PyAudio()  # Create an interface to PortAudio
stream_mic = None

SAMPLE_RATE = 8000
WINDOW_SIZE = 1024

def goertzel(samples, sample_rate, *freqs):
    """
    Implementation of the Goertzel algorithm, useful for calculating individual
    terms of a discrete Fourier transform.
    `samples` is a windowed one-dimensional signal originally sampled at `sample_rate`.
    The function returns 2 arrays, one containing the actual frequencies calculated,
    the second the coefficients `(real part, imag part, power)` for each of those frequencies.
    For simple spectral analysis, the power is usually enough.
    Example of usage :
        
        freqs, results = goertzel(some_samples, 8000, (400, 500), (1000, 1100))
    """
    window_size = len(samples)
    f_step = sample_rate / float(window_size)
    f_step_normalized = 1.0 / window_size

    # Calculate all the DFT bins we have to compute to include frequencies
    # in `freqs`.
    bins = set()
    for f_range in freqs:
        f_start, f_end = f_range
        k_start = int(math.floor(f_start / f_step))
        k_end = int(math.ceil(f_end / f_step))

        if k_end > window_size - 1: raise ValueError('frequency out of range %s' % k_end)
        bins = bins.union(range(k_start, k_end))

    # For all the bins, calculate the DFT term
    n_range = range(0, window_size)
    freqs = []
    results = []
    for k in bins:

        # Bin frequency and coefficients for the computation
        f = k * f_step_normalized
        w_real = 2.0 * math.cos(2.0 * math.pi * f)
        w_imag = math.sin(2.0 * math.pi * f)

        # Doing the calculation on the whole sample
        d1, d2 = 0.0, 0.0
        for n in n_range:
            y  = samples[n] + w_real * d1 - d2
            d2, d1 = d1, y

        # Storing results `(real part, imag part, power)`
        results.append((
            0.5 * w_real * d1 - d2, w_imag * d1,
            d2**2 + d1**2 - w_real * d1 * d2)
        )
        freqs.append(f * sample_rate)
    return freqs, results

def text_to_speech(text, delay=5):
    global text_language

    # Synthesise text
    tts = gTTS(text=text, lang=text_language, slow=False)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)

    # Reproduce
    mp3_fp.seek(0)
    mixer.music.load(mp3_fp, "mp3")
    mixer.music.play()

    # Wait until reproduction
    time.sleep(delay)
    while(mixer.get_busy()):
        continue

def welcome_message():
    welcome = "Bienvenido al buzón de voz de Kolbi"
    text_to_speech(welcome, 3)

def password_request():
    message = "Digite la contraseña para acceder al buzón de voz"
    text_to_speech(message)

def number_to_speech(num):
    char = str(num)
    text_to_speech(char, 0.75)

def plot_frequencies(samples, freqs, results):
    plt.subplot(2, 1, 1)
    plt.title('(1) Sine wave 440Hz + 1020Hz')
    plt.plot(samples)

    plt.subplot(2, 1, 2)
    plt.title('(1) Goertzel Algo, freqency ranges : [400, 500] and [1000, 1100]')
    plt.plot(freqs, np.array(results)[:,2], 'o')
    plt.ylim([0,100000])
    plt.draw()

def analyse_sample(sample):
    global SAMPLE_RATE
    freqs, results = goertzel(sample, SAMPLE_RATE, (500, 1000),  (1200, 1700))
    return freqs, results

def open_mic():
    global pyaudio_iface
    global SAMPLE_RATE
    global WINDOW_SIZE
    global stream_mic
    channels = 1
    a_format = pyaudio.paInt16
    
    stream_mic = pyaudio_iface.open(format=a_format,
            channels=channels,
            rate=SAMPLE_RATE,
            frames_per_buffer=WINDOW_SIZE,
            input=True)


def get_sample():
    global stream_mic
    global WINDOW_SIZE
    divider = 1. / float(1 << 15)
    inputdata = stream_mic.read(WINDOW_SIZE)
    inputsample = np.frombuffer(inputdata, dtype=np.int16)
    sample = inputsample.astype(np.float32) * divider
    return sample

if __name__ == "__main__":
    th = 10000
    #welcome_message()
    #password_request()
    #number_to_speech(1)
    #number_to_speech(2)

    # Start capturing
    open_mic()
    plt.show()
    while (True):
        sample = get_sample()
        freqs, results = analyse_sample(sample)
        processed = np.array(results)[:,2]
        #plot_frequencies(sample, freqs, results)
        
        maxval = processed.max()
        if (maxval > th):
            print("Freqs")
            for i in freqs:
                print(i)
            print("Procs")
            for i in processed:
                print(i)
            
        else:
            print("NS")
    