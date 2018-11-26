# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 15:21:27 2018

@author: Denis
"""

import os, errno

def fmake(dirm):
    try:
        os.makedirs(dirm)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise