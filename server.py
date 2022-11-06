#!/usr/bin/python3


from gtts import gTTS
from io import BytesIO
from pygame import mixer
import pyaudio
import math
import time
import numpy as np


text_language = 'es'
mixer.init()

pyaudio_iface = pyaudio.PyAudio()  # Create an interface to PortAudio
stream_mic = None

SAMPLE_RATE = 8000
WINDOW_SIZE = int(SAMPLE_RATE / 4)
CURR_PASS = "1234"

# Adjust according to the volume
threshold = 8000

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

def number_to_speech(num):
    char = str(num)
    text_to_speech(char, 0.75)

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
    
    # WE NEED TO CLOSE THE MIC
    stream_mic = pyaudio_iface.open(format=a_format,
            channels=channels,
            rate=SAMPLE_RATE,
            frames_per_buffer=WINDOW_SIZE,
            input=True)

def close_mic():
    global stream_mic
    stream_mic.stop_stream()
    stream_mic.close()

def get_sample():
    global WINDOW_SIZE
    divider = 1. / float(1 << 15)
    inputdata = stream_mic.read(WINDOW_SIZE)
    inputsample = np.frombuffer(inputdata, dtype=np.int16)
    sample = inputsample.astype(np.float32) * divider

    return sample

def get_row(freqs):
    row_freq = freqs[0]
    if row_freq < 750:
        return 0
    elif row_freq < 820:
        return 1
    elif row_freq < 900:
        return 2
    elif row_freq < 1000:
        return 3
    else:
        return None

def get_col(freqs):
    col_freq = freqs[len(freqs) - 1]
    if col_freq < 1100:
        return None
    if col_freq < 1300:
        return 0
    elif col_freq < 1400:
        return 1
    elif col_freq < 1500:
        return 2
    else:
        return 3

def get_digit(row, col):
    digits = '123A456B789C*0#D'
    return digits[row * 4 + col]

def tell_password(password):
    message = "La contraseña ingresada es"
    text_to_speech(message)
    for i in password:
        text_to_speech(i, delay=0.8)

def get_input(expected=1):
    global threshold
    open_mic()
    print("Listening...")
    digited = ""
    while (len(digited) < expected):
        sample = get_sample()
        freqs, results = analyse_sample(sample)
        processed = np.array(results)[:,2]

        maxval = processed.max()
        if (maxval > threshold):
            m = np.ma.masked_where(processed < threshold, freqs)
            read_freqs = m.compressed()

            row = get_row(read_freqs)
            col = get_col(read_freqs)

            if row is not None and col is not None:
                digit = get_digit(row, col)
                digited += digit
                print(digit)
    close_mic()
    return digited


if __name__ == "__main__":
    text_to_speech("Bienvenido al buzón de voz de Kolbi", 3)
    text_to_speech("Digite la contraseña para acceder al buzón de voz", 5)


    while(True):
        password = get_input(4)
        if password != CURR_PASS:
            text_to_speech("Contraseña incorrecta. Digite nuevamente", delay=5)    
        else:
            text_to_speech("Bienvenido", delay=2)
            break
    
    while(True):
        text_to_speech("Digite 0 si desea escuchar mensajes. 1 para cambiar la contraseña", delay=10)
        digited = get_input(1)
        if digited == '0':
            text_to_speech("No tiene mensajes nuevos. Hasta luego")
            exit(0)
        elif digited == '1':
            break
        else:
            text_to_speech("Opción inválida")
    
    while(True):
        text_to_speech("Digite la nueva contraseña")
        
        password = get_input(4)
        tell_password(password)

        text_to_speech("Digite 1 si es correcto. Otro para repetir")
        digited = get_input(1)

        if digited == '1':
            text_to_speech("Gracias. Hasta luego")
            break
        else:
            text_to_speech("Opción inválida")
