#!/usr/bin/python3

from heapq import nsmallest
import sounddevice as sd
import numpy as np
from scipy import fftpack
from scipy import signal
from math import pi

from matplotlib import pyplot as plt
from scipy.io import wavfile
freqs = [1209, 1336, 1477, 1633,697, 770, 852, 941]


fig, axes = plt.subplots(nrows=int(np.ceil(len(freqs)/2)), ncols=2, figsize=(12, 8))

counter = 0
thd = 0.0
for F in freqs:
    Fs, samples = wavfile.read(f'{F}.wav')

    f, Pxx_den = signal.periodogram(samples, Fs)

    argmax = np.argmax(Pxx_den)

    this_thd = (np.sum(Pxx_den[argmax+1:])+np.sum(Pxx_den[:argmax-1]))/np.sum(Pxx_den)*100
    print(f'{F} Hz: THD {this_thd:.2f}%')

    thd += this_thd


    row = counter//2
    col = counter % 2

    axes[row,col].set_title(f'{F} Hz')
    axes[row,col].semilogy(f, Pxx_den)
    axes[row,col].set_xlabel('Frequency [Hz]')
    axes[row,col].set_ylabel('Spectrum Magnitude')
    axes[row,col].set_xlim(0, Fs / 2)
    counter += 1

thd = thd/len(freqs)
print(f'avg THD {thd:.2f}%')

fig.tight_layout()
plt.show()


