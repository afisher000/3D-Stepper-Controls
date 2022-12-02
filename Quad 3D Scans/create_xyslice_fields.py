# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 19:08:42 2022

@author: afisher
"""

import pandas as pd
import numpy as np
# 

quad = 1
bx_file = f'Bx_q{quad}_2dscan_22-11-14.csv'
by_file = f'By_q{quad}_2dscan_22-11-14.csv'
bx_df = pd.read_csv(bx_file)
by_df = pd.read_csv(by_file)

bxy_df = bx_df.rename(columns={'field':'Bx'})
bxy_df['By'] = by_df.field
xyslice = bxy_df[bxy_df.z==0]
# xyslice.Bx = -1*xyslice.Bx
# xyslice.By = -1*xyslice.By
xyslice.to_csv(f'q{quad}_xyslice_fine.csv', index=False)





