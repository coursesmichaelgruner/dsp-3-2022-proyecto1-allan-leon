#!/usr/bin/python3

import sounddevice as sd
import numpy as np
import sys, tty, termios

fs = 44100  # sample rate

def getch():
    #https://code.activestate.com/recipes/134892/
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

inp = sys.stdin
with sd.OutputStream(samplerate=fs, dtype='int16', latency='low', channels=1) as stream:
    while True:
        termios.ECHO
        a=getch()
        if a == '\x03':
            break
        print(f'{a}')