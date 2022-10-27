# %% -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 13:00:28 2022

@author: afish
"""
import serial
import time
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import os
import numpy as np


# TO IMPLEMENT:
    # Choose coordinate system and choose signs in code accordingly
    # There is slack in motors
    # Better error handing with field measurements
    
class Controller():
    def __init__(self, ard_port, gauss_port,
                 ard_baudrate=9600, gauss_baudrate=2400,
                 ard_timeout=10, gauss_timeout=2):
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
        self.reset_data()
        self.curpos = [0,0,0]
        if 'saved_pos.pkl' in os.listdir():
            self.curpos = pickle.load(open('saved_pos.pkl','rb'))

            
        time.sleep(2) #Wait for connections to be made
        self.get_measurement() # get measurement at first position
        return
    
    def reset_data(self):
        self.measurements= pd.DataFrame(columns=['x','y','z','field'])


    def get_measurement(self):
        ''' Read from 6010 FWBELL gaussmeter. Return measurement as tuple of
        z_step and field.'''

        field_reading = ''
        counter = 0
        while(field_reading==''):
            self.gauss.readline() #Emtpy buffer
            self.gauss.write(b':measure:flux?\n')
            message = self.gauss.readline()
            field_reading = message.decode().strip('T;\n')
            print(f'Field={field_reading} T')
            counter +=1
            if counter==5:
                raise ValueError('Gaussmeter did not return measurement')
        
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
        print(f'Writing to move: motor={motor}, steps={steps}')
        self.arduino.write(b'%i, %i' % (motor, steps))
        
        # Wait for stepper message
        message = self.arduino.read_until()
        if message.decode() != 'success\n':
           print(message.decode())
           raise ValueError
        
        # Update curpos and take measurement
        time.sleep(0.5)
        self.curpos[motor] += steps/self.motor_calibration[motor]
        if take_data:
            self.get_measurement()
        return
        
    def gradient_scan(self, motor=0, npoints=10, max_offset=1):
        self.reset_data()
        slop = 0.5
        conn.move(-max_offset-slop, motor=motor, take_data=False)
        conn.move(slop, motor=motor)
        for _ in range(npoints-1):
            conn.move(2*max_offset/(npoints-1), motor=motor)
        conn.move(-max_offset-slop, motor=motor, take_data=False)
        conn.move(slop, motor=motor)

        # Compute fit
        df = self.measurements
        polyfit = np.polyfit(df.x, df.field, 1)
        df['linearfit'] = np.polyval(polyfit, df.x)
        gradient = polyfit[0]*1000

        # Plot
        fig, ax = plt.subplots()
        coord = df.columns[motor]
        df.sort_values(by=coord)
        df.plot.scatter(x=coord, y='field', label='Data', ax=ax)
        df.plot(x=coord, y='linearfit', label=f'Fit: {gradient:.1f} T/m', ax=ax)
    
    def long_scan(self):
        self.reset_data()
        [self.move(2, motor=2) for _ in range(20)]
        [self.move(2, motor=2, take_data=False) for _ in range(35)]
        [self.move(2, motor=2) for _ in range(20)]

    def __exit__(self, *args):
        ''' Close connections on exit of with statement. Save curstep to 
        pickle file.'''
        self.arduino.close()
        self.gauss.close()
        self.measurements.to_csv('temp_data.csv', index=False)
        pickle.dump(self.curpos, open('saved_step.pkl','wb'))
        return

    def close(self):
        self.__exit__()
    
conn = Controller(ard_port='COM4', gauss_port='COM6')

#conn.gradient_scan(motor=0, npoints=10, max_offset=1)





# conn = Controller(ard_port='COM4', gauss_port='COM6')
# %%
