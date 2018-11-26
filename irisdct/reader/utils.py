# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 13:32:03 2018

@author: Denis
"""

import sys
sys.path.append("..")
import numpy as np
from copy import copy
from inpaint.inpaintn import miss_border

def infos_irisdates(date_obs):
    date = date_obs.split('T')
    time = date[1].split(':')
    date = date[0].split('-')
    (year, month, day) = date
    (hour, minute) = time[0:2]
    (second, millisecond) = time[2].split('.')
    return int(year), int(month), int(day), int(hour), int(minute), int(second), int(millisecond)
    
def miss_to_nan(data_cube, inframe_add=1):
    nan_cube = copy(data_cube)
    nan_cube[data_cube<=0] = np.nan
    if inframe_add>0:  #add to nan the borders in-frame of inframe_add size
        nan_cube[miss_border(nan_cube==nan_cube, filter_size=(1,2*inframe_add+1,2*inframe_add+1))] = np.nan
    return nan_cube