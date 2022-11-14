# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 19:08:42 2022

@author: afisher
"""

import pandas as pd
import numpy as np
# 

quad = 1
bx_file = f'Bx_q{quad}_3dscan_22-11-09.csv'
by_file = f'By_q{quad}_3dscan_22-11-09.csv'
bx_df = pd.read_csv(bx_file)
by_df = pd.read_csv(by_file)

bxy_df = bx_df.rename(columns={'field':'Bx'})
bxy_df['By'] = by_df.field
xyslice = bxy_df[bxy_df.z==0]

xyslice.to_csv(f'q{quad}_xyslice.csv', index=False)





