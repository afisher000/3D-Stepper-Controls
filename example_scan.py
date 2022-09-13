# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 13:00:28 2022

@author: afish
"""
import serial
import time
import pandas as pd
import pickle
import matplotlib
import os


# TO IMPLEMENT:
    # Choose coordinate system and choose signs in code accordingly
    
    
class Controller():
    def __init__(self, ard_port, gauss_port,
                 ard_baudrate=9600, gauss_baudrate=2400,
                 ard_timeout=10, gauss_timeout=10):
        '''Initialize connections to arduino and gaussmeter over serial. 
        Save measurements in DataFrame. '''
        self.arduino = serial.Serial(port = ard_port, baudrate=ard_baudrate,
                                     timeout=ard_timeout)
        self.gauss = serial.Serial(port = gauss_port, baudrate=gauss_baudrate,
                                   timeout=gauss_timeout)

        # Motor calibrations (arduino steps per mm)
        # Additional info: 1 arduino step is 1/16 of motor step. All motors are 
        # 200 steps per revolution. Single turn travels are 2.0, 2.5, 5.0mm for 
        # x, y, z motors respectively. 
        self.motor_calibration = (1600, 1280, 640)
        
        # Create measurements table, read in curstep
        self.measurements= pd.DataFrame(columns=['step','field'])
        self.curpos = [0,0,0]
        if 'saved_pos.pkl' in os.listdir():
            self.curpos = pickle.load(open('saved_pos.pkl','rb'))

            
        time.sleep(2) #Wait for connections to be made
        self.get_measurement() # get measurement at first position
        return
    
    def get_measurement(self):
        ''' Read from 6010 FWBELL gaussmeter. Return measurement as tuple of
        z_step and field.'''
        self.gauss.write(b':measure:flux?\n')
        message = self.gauss.read_until()
        field_reading = message.decode().strip(';\n')
        print(field_reading)
        data = [*self.curpos, float(field_reading)]
        self.measurements.loc[len(self.measurements)] = data
        return

        
    def move(self, dist, take_data=True, motor=2, safety=True):
        ''' Moves select motor a distance "dist" and waits for success message 
        to continue. Default is to take a measurement after a move. '''
        # Safety measure
        if safety and abs(dist)>5:
            print('Trying to move motor >5mm. If sure you want to proceed, add argument safety=False')
        
        # Move motor correct steps
        steps = round(dist*self.motor_calibration[motor])
        self.arduino.write(b'%i, %i' % (motor, steps))
        
        # Wait for stepper message
        message = self.arduino.read_until()
        if message.decode() != 'success\n':
            print(message.decode())
            raise ValueError
        
        # Update curpos and take measurement
        self.curpos[motor] += steps/self.motor_calibration[motor]
        self.get_measurement()
        return
        
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        ''' Close connections on exit of with statement. Save curstep to 
        pickle file.'''
        self.arduino.close()
        self.gauss.close()
        self.measurements['z'] = self.measurements.step/self.z_motor_calibration
        self.measurements.to_csv('temp_data.csv', index=False)
        pickle.dump(self.curstep, open('saved_step.pkl','wb'))
        return

if "__init__"=="__main__":
    
    # Enter correct COM ports for the stepper arduino and gauss meter.
    with Controller(ard_port='COM6', gauss_port='COM7') as conn:
        # Move the motor once
        conn.move(-1, motor=2)
        
        # Use a loop to take a series of measurements
        [conn.move(-1, motor=2) for _ in range(10)] 
        
        # Save conn.measurements before end of with to keep in workspace
        measurements = conn.measurements 


