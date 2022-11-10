# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 10:12:05 2022

@author: afisher
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.close('all')
# filename = 'Bx_q1_3dscan_22-11-09.csv'
# filename = 'Bx_q2_3dscan_22-11-08.csv'
# filename = 'By_q1_3dscan_22-11-09.csv'
filename = 'By_q2_3dscan_22-11-09.csv'


if 'bx' in filename.lower():
    xymaj, xymin, field = 'y', 'x', 'Bx'
else:
    xymaj, xymin, field = 'x', 'y', 'By'
   
# Read data (round machine precision)
data = pd.read_csv(filename).rename(columns={'field':field}).round(10)
cmap = plt.get_cmap('coolwarm')

# Figures
data.plot.scatter('z', field, c=xymaj, cmap=cmap)
data.plot.scatter('z', field, c=xymin, cmap=cmap)

# Measure gradients from z=10,10
grad_data = data[(data[xymin]==0) & (data.z.abs()<=10)].drop(columns=[xymin])


gradients = pd.DataFrame(columns=['grad'])
for group in grad_data.groupby(by='z'):
    df = group[1]
    grad = np.polyfit(df[xymaj], df[field], 1)[0]*1000 # T/m
    gradients.loc[group[0]] = grad
gradients = gradients.rename_axis('z').reset_index()
gradients.plot.scatter('z', 'grad')
    
    
    