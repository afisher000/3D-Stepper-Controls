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
import seaborn as sns
from datetime import datetime


# TO IMPLEMENT:
# move to axis function
# Format curpos printing to .2f
    
class Controller():
    def __init__(self, ard_port='COM4', gauss_port='COM6',
                 ard_baudrate=9600, gauss_baudrate=2400,
                 ard_timeout=15, gauss_timeout=1):
        '''Initialize connections to arduino and gaussmeter over serial. 
        Save measurements in DataFrame. '''
        self.gauss_port = gauss_port
        self.gauss_baudrate = gauss_baudrate
        self.gauss_timeout = gauss_timeout
        self.arduino = serial.Serial(port = ard_port, baudrate=ard_baudrate,
                                     timeout=ard_timeout)
        self.gauss = serial.Serial(port = gauss_port, baudrate=self.gauss_baudrate,
                                   timeout=self.gauss_timeout)

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
        self.get_measurement() # get initial measurement
        return
    
    def reset_data(self):
        # Reset measurements dataframe
        self.measurements= pd.DataFrame(columns=['x','y','z','field'])


    def get_measurement(self):
        ''' Read from 6010 FWBELL gaussmeter. Return measurement as tuple of
        z_step and field. While loop ensures that measurements is tried until sucessful'''

        try:
            while True:
                # print('take measurement') #for troubleshooting
                self.gauss.write(b':measure:flux?\n')
                message = self.gauss.read_until()
                if message:
                    break
        except:
            # Error in writing or reading to gaussmeter. Disconnect and reconnect
            self.gauss.__exit__()
            time.sleep(1)
            self.gauss = serial.Serial(port = self.gauss_port, baudrate=self.gauss_baudrate,
                                    timeout=self.gauss_timeout)
        
        field_reading = message.decode().split('T')[0]
        print(f'Field: {field_reading} T at {[round(x,2) for x in self.curpos]}')

        data = [*self.curpos, float(field_reading)]
        self.measurements.loc[len(self.measurements)] = data
        return

        
    def move(self, dist, take_data=True, motor=2):
        '''To elimate slop measurement errors, always approach desired location from the 
        negative direction and only take measurement when at desired location. Positive direction
        is movement away from motor.'''
        
        slop = 0.5
        max_move = 4
        if abs(dist)<=5: # Short moves
            if dist>=0:
                self.raw_move(dist, take_data=take_data, motor=motor)
            else:
                self.raw_move(dist-slop, take_data=False, motor=motor)
                self.raw_move(slop, take_data=take_data, motor=motor)
        elif motor!=2:
            print('Cannot move motors x,y move than 5mm!')
        else: # Long moves
            if dist>=0:
                n_moves = np.ceil((dist)/max_move).astype('int')
                for _ in range(n_moves):
                    self.raw_move((dist)/n_moves, take_data=False, motor=motor)
                if take_data:
                    self.get_measurement()
            else:
                n_moves = np.ceil(abs(dist-slop)/max_move).astype('int')
                for _ in range(n_moves):
                    self.raw_move((dist-slop)/n_moves, take_data=False, motor=motor)
                self.raw_move(slop, take_data=take_data, motor=motor) 


    def raw_move(self, dist, take_data=True, motor=2):
        ''' Moves select motor a distance "dist" and waits for success message 
        to continue. Default is to take a measurement after a move. '''

        # Move motor correct steps
        steps = round(dist*self.motor_calibration[motor])
        #print(f'Writing to move: motor={motor}, steps={steps}, (dist={dist:.2f})') # for troubleshooting
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
        
    def scan_3D(self, reset=True, save=True,
        x_npoints=5, x_max_offset=0.75, 
        y_npoints=5, y_max_offset=0.75,
        z_range=np.linspace(-30,30,41)
    ):
        ''' Perform a three dimensional scan with the specified resolution.'''
        if reset:
            self.reset_data()

        for z in z_range:
            self.move(z-self.curpos[2], motor=2, take_data=False)
            self.scan_2D(x_npoints=x_npoints, x_max_offset=x_max_offset, 
                y_npoints=y_npoints, y_max_offset=y_max_offset,
                reset=False, save=False
            )
        
        timestamp = datetime.today().strftime('%H:%M')
        print(f'3D Completed at {timestamp}')
        if save:
            self.measurements.to_csv('scan_3D data.csv', index=False)

    def scan_2D(self, reset=True, save=True,
        x_npoints=21, x_max_offset=0.75, 
        y_npoints=21, y_max_offset=0.75
    ):
        ''' Scan the transverse plane with the specified resolution.'''
        if reset:
            self.reset_data()

        self.move(-x_max_offset, motor=0, take_data=False)
        for _ in range(x_npoints-1):
            self.scan_1D(motor=1, npoints=y_npoints, max_offset=y_max_offset, reset=False, save=False)
            self.move(2*x_max_offset/(x_npoints-1), motor=0, take_data=False)
        self.scan_1D(motor=1, npoints=y_npoints, max_offset=y_max_offset, reset=False, save=False)
        self.move(-x_max_offset, motor=0, take_data=False)

        timestamp = datetime.today().strftime('%H:%M')
        print(f'2D Completed at {timestamp}')
        if save:
            self.measurements.to_csv('scan_2D data.csv', index=False)

    def scan_1D(self, motor, npoints=10, max_offset=1, reset=False, save=False):
        ''' Scan a single dimension with the specified resolution.'''
        if reset:
            self.reset_data()

        self.move(-max_offset, motor=motor)
        for _ in range(npoints-1):
            self.move(2*max_offset/(npoints-1), motor=motor)
        self.move(-max_offset, motor=motor, take_data=False)

        print('1D Completed')
        if save:
            self.measurements.to_csv('scan_1D data.csv', index=False)

    def gradient_scan(self, motor, npoints=10, max_offset=1):
        # Take gradient measurement of npoints for a range of max_offset*[-1,1]. 
        if motor==2:
            print('Invalid use of z-motor for gradient scan')

        self.scan_1D(motor=motor, npoints=npoints, max_offset=max_offset, reset=True, save=True)

        # Compute fit
        df = self.measurements
        coord = df.columns[motor]
        polyfit = np.polyfit(df[coord], df.field, 1)
        df['linearfit'] = np.polyval(polyfit, df[coord])
        gradient = polyfit[0]*1000

        # Plot
        fig, ax = plt.subplots()
        df.sort_values(by=coord)
        df.plot.scatter(x=coord, y='field', label='Data', ax=ax)
        df.plot(x=coord, y='linearfit', label=f'Fit: {gradient:.1f} T/m', ax=ax)
    
    def __exit__(self, *args):
        ''' Close connections on exit of with statement. Save curstep to 
        pickle file.'''
        self.arduino.close()
        self.gauss.close()
        self.measurements.to_csv('temp_data.csv', index=False)
        pickle.dump(self.curpos, open('saved_pos.pkl','wb'))
        return

    def close(self):
        self.__exit__()
    
conn = Controller(ard_port='COM4', gauss_port='COM6')


# %%
