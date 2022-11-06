#!/usr/bin/python3

from heapq import nsmallest
import sounddevice as sd
import numpy as np
from scipy import fftpack

from math import pi

from matplotlib import pyplot as plt
from scipy.io import wavfile


Fs, samples = wavfile.read("1336.wav")

X = fftpack.fft(samples)
fs = fftpack.fftfreq(len(samples)) * Fs
X = np.abs(X)

X2 = X[len(X)//2:]
argmax = np.argmax(X2)
X2 =X2[argmax:]

thd = np.sqrt(np.sum(X2[2:]**2))/X2[0]*100

print(f'THD {thd:.2f}%')

fig, ax = plt.subplots()

ax.stem(fs, X)
ax.set_xlabel('Frequency in Hertz [Hz]')
ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
ax.set_xlim(-Fs / 2, Fs / 2)

plt.show()


