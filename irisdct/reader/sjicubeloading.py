# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 18:55:44 2018

@author: Denis
"""

from irisreader import sji_cube
from .utils import infos_irisdates

class sji_cube_infos:
    def __init__(self,n_steps, height, large, name, wavelength, year_init, month_init, day_init, hour_init, minute_init, second_init, millisecond_init, year_end, month_end, day_end, hour_end, minute_end, second_end, millisecond_end, obsid):
        self.n_steps = n_steps
        self.height = height
        self.large = large
        self.name = name
        self.wavelength = wavelength
        self.year_init = year_init
        self.month_init = month_init
        self.day_init = day_init
        self.hour_init = hour_init
        self.minute_init = minute_init
        self.second_init = second_init
        self.millisecond_init = millisecond_init
        self.year_end = year_end
        self.month_end = month_end
        self.day_end = day_end
        self.hour_end = hour_end
        self.minute_end = minute_end
        self.second_end = second_end
        self.millisecond_end = millisecond_end
        self.obsid = obsid

def sji_cube_loader(sji_path):
    sji_data = sji_cube( str(sji_path) )
    data = sji_data[:,:,:]
    n_steps = sji_data.n_steps
    (height, large) = sji_data.get_image_step(1).shape
    name = sji_path
    wavelength = int(sji_data.line_info.split(' ')[2])
    (year_init, month_init, day_init, hour_init, minute_init, second_init, millisecond_init) = infos_irisdates(sji_data.primary_headers['DATE_OBS'])
    (year_end, month_end, day_end, hour_end, minute_end, second_end, millisecond_end) = infos_irisdates(sji_data.primary_headers['DATE_END'])
    obsid = int(sji_data.primary_headers['OBSID'])
    return data, sji_cube_infos(n_steps, height, large, name, wavelength, year_init, month_init, day_init, hour_init, minute_init, second_init, millisecond_init, year_end, month_end, day_end, hour_end, minute_end, second_end, millisecond_end, obsid)