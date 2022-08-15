# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 13:00:28 2022

@author: afish
"""
import serial
import time
import pandas as pd


class Controller():
    def __init__(self, ard_port='COM4', gauss_port='COM3',
                 ard_baudrate=9600, gauss_baudrate=2400,
                 ard_timeout=10, gauss_timeout=10):
        '''Initialize connections to arduino and gaussmeter over serial. 
        Save measurements in DataFrame. '''
        self.arduino = serial.Serial(port = ard_port, baudrate=ard_baudrate,
                                     timeout=ard_timeout)
        self.gauss = serial.Serial(port = gauss_port, baudrate=gauss_baudrate,
                                   timeout=gauss_timeout)
        self.measurements= pd.DataFrame(columns=['step','field'])
        self.curstep = 0
        time.sleep(2) #Wait for connections to be made
        return
    
    def get_measurement(self):
        ''' Read from 6010 FWBELL gaussmeter. Return measurement as tuple of
        z_step and field.'''
        self.gauss.write(b':measure:flux?\n')
        message = self.gauss.read_until()
        print(message.decode().strip(';\n'))
        data = [self.curstep, float(message.decode().strip('T;\n'))]
        self.measurements.loc[len(self.measurements)] = data
        return
        
    def move_by_step(self, steps, take_data=True):
        ''' Moves motor and waits for success message to continue.
        Note arduino is only setup to use z-motor (motor=2). Default is to 
        take a measurment after a move. '''
        
        if steps>200*16*4:
            print('Steps moves toward quads more than a full turn.')
            raise ValueError
            
        if steps<-200*16*4:
            print('Steps move greater than two turns.')
            raise ValueError
            
        motor = 2
        self.arduino.write(b'%i, %i' % (motor, steps))
        message = self.arduino.read_until() #Wait for stepper to stop
        if message.decode() != 'success\n':
            print(message.decode())
            raise ValueError
        
        self.curstep += steps
        self.get_measurement()
        return
        
    def move_by_dist(self, dist, take_data=True):
        ''' Convert to steps for the user. Dist in mm.
        Conversion is 640 steps/mm. '''
        steps = dist*640
        self.move_by_step(steps, take_data=take_data)
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        ''' Close connections. '''
        self.arduino.close()
        self.gauss.close()
        return
    
#200*16 steps is 0.5 cm

with Controller() as conn:
    [conn.move_by_dist(1) for _ in range(10)]
    conn.move_by_dist(0.5)
    [conn.move_by_dist(-1) for _ in range(20)]
    conn.move_by_dist(-0.5)
    [conn.move_by_dist(1) for _ in range(10)]
    measurements = conn.measurements
