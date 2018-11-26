# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 13:57:55 2018

@author: Denis
"""

from .utils import infos_irisdates

class sji_frame_infos:
    def __init__(self, height, large, wavelength, year, month, day, hour, minute, second, millisecond, timestamp, xcenter, ycenter, xfov, yfov, xcenterslit, ycenterslit):
        self.height = height
        self.large = large
        self.wavelength = wavelength
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond
        self.timestamp = timestamp
        self.xcenter = xcenter
        self.ycenter = ycenter
        self.xfov = xfov
        self.yfov = yfov
        self.xcenterslit = xcenterslit
        self.ycenterslit = ycenterslit

def sji_frameinfos_loader(sji_data, i):
    (height, large) = sji_data.get_image_step(i).shape
    header = sji_data.headers[i]
    wavelength = int(header['TWAVE1'])
    (year, month, day, hour, minute, second, millisecond) = infos_irisdates(header['DATE_OBS'])
    timestamp = sji_data.get_timestamps()[i]
    xcenter = float(header['XCEN'])
    ycenter = float(header['YCEN'])
    xfov = float(header['FOVX'])
    yfov = float(header['FOVY'])
    xcenterslit = float(header['SLTPX1IX'])
    ycenterslit = float(header['SLTPX2IX'])
    return sji_frame_infos(height, large, wavelength, year, month, day, hour, minute, second, millisecond, timestamp, xcenter, ycenter, xfov, yfov, xcenterslit, ycenterslit)