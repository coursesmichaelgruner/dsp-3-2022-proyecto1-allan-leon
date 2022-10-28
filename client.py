#!/usr/bin/python3

import sounddevice as sd
import numpy as np
import sys
import tty
import termios
import re

fs = 44100  # sample rate
valid_keys = '123A456B789C*0#D'
cols_freqs = [1209, 1336, 1477, 1633]
rows_freqs = [697, 770, 852, 941]


def getch():
    '''
    This method returns a char read from the stdin
    '''
    # https://code.activestate.com/recipes/134892/
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def indexof(ch: str, string: str):
    '''
    This method searches a character in a string
    Parameters
        string: string in which the char ch is looked up
        ch: char to look up in string

    Returns
        -1 if ch is not found in string, otherwise the index of the char
    '''
    ch = ch.lower()
    string = string.lower()

    if ch not in string:
        return -1

    i = 0
    for key in string:
        if key == ch:
            return i
        i += 1

    return -1


def row_col(ch: str, string: str):
    '''
    This method a value in the DTMF matrix

    Returns
        None if the value is not present in the matrix, otherwise a tuple of row,col
    '''
    index = indexof(ch, string)
    if index == -1:
        return None

    return (index//4), (index % 4)


with sd.OutputStream(samplerate=fs, dtype='int16', latency='low', channels=1) as stream:
    while True:

        a = getch()

        if a == '\x03':  # ctrl-c
            break

        rc = row_col(a, valid_keys)

        if rc != None:
            row_freq = rows_freqs[rc[0]]
            col_freq = cols_freqs[rc[1]]
            print(f'{a}: {row_freq},{col_freq}')
