#!/usr/bin/python3

from heapq import nsmallest
import sounddevice as sd
import numpy as np
import sys
import tty
import termios
from math import pi

import time

Fs = 8000  # sample rate
freqs = [1209, 1336, 1477, 1633,697, 770, 852, 941]



n_samples = int(Fs)
x = np.arange(0, n_samples,dtype=np.float32)

def generate_triangle(x,n_samples:int):
    y = np.zeros(n_samples,dtype=np.float32)

    y[0:len(x)//2]=x[0:len(x)//2]/(len(x)//2)

    m=-1/(x[-1]-x[len(x)//2])
    b=-m*x[-1]
    y[len(x)//2:]=x[len(x)//2:]*m+b

    return y

def generate_tone(F1):
    f1 = F1/Fs


    samples = np.sin(2*pi*f1*x, dtype=np.float32) 

    return samples*generate_triangle(x,n_samples)


with sd.OutputStream(samplerate=Fs, dtype='float32', latency='low', channels=1) as stream:
    for f in freqs:

        stream.write(generate_tone(f))
        time.sleep(0.1)
