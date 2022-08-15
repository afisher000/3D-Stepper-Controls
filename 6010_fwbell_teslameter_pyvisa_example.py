# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 12:15:36 2022

@author: afish
"""

import serial
import time
import pyvisa

scope_id = 'ASRL5::INSTR'
rm = pyvisa.ResourceManager()
scope = rm.open_resource(scope_id)

scope.timeout= 5000 
scope.baud_rate = 2400
meas = float(scope.query(':measure:flux?\n').strip('T;\n'))
