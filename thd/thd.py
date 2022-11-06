#!/usr/bin/python3

from heapq import nsmallest
import sounddevice as sd
import numpy as np
from scipy import fftpack

from math import pi

from matplotlib import pyplot as plt
from scipy.io import wavfile
freqs = [1209, 1336, 1477, 1633,697, 770, 852, 941]


fig, axes = plt.subplots(nrows=int(np.ceil(len(freqs)/2)), ncols=2, figsize=(12, 8))

counter = 0
for F in freqs:
    Fs, samples = wavfile.read(f'{F}.wav')

    X = fftpack.fft(samples)
    fs = fftpack.fftfreq(len(samples)) * Fs
    X = np.abs(X)

    X2 = X[len(X)//2:]
    argmax = np.argmax(X2)
    X2 =X2[argmax:]

    thd = np.sqrt(np.sum(X2[2:]**2))/X2[0]*100

    print(f'THD {thd:.2f}%')

    row = counter//2
    col = counter % 2

    axes[row,col].set_title(f'{F} Hz')
    axes[row,col].stem(fs, X)
    axes[row,col].set_xlabel('Frequency [Hz]')
    axes[row,col].set_ylabel('Spectrum Magnitude')
    axes[row,col].set_xlim(-Fs / 2, Fs / 2)
    counter += 1

fig.tight_layout()
plt.show()


