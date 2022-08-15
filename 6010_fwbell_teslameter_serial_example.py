# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 12:15:36 2022

@author: afish
"""

import serial
import time


with serial.Serial(port='COM5', baudrate=2400, timeout=1) as ser:
    time.sleep(1)
    for j in range(10):
        ser.write(b':measure:flux?\n')
        message = ser.read_until()
        meas = float(message.decode().strip('T;\n'))
        print(meas)
