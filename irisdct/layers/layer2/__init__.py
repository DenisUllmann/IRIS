# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 16:59:08 2018

@author: Denis
"""
import numpy as np
from scipy import fftpack
from copy import copy

def partition_ind_to_position(p_ind, hseq, lseq):
    t = p_ind // (hseq*lseq)
    h = (p_ind % (hseq*lseq)) // lseq
    l = (p_ind % (hseq*lseq)) % lseq
    return t, h, l

def partitioned_ind(p_ind, hseq, lseq, shape):
    t, h, l = partition_ind_to_position(p_ind, hseq, lseq)
    y0 = h*hseq
    y1 = min(y0+hseq, shape[1])
    x0 = l*lseq
    x1 = min(x0+lseq, shape[2])
    return t, slice(y0, y1, 1), slice(x0, x1, 1)

def partitioned_out(p_ind, hseq, lseq):
    return partition_ind_to_position(p_ind, hseq, lseq)

def layer_cv(data):
    
    return res

def combine_results(cv, hseq, lseq, cardhseq, cardlseq, shape):
    data = np.zeros((shape[0], cardhseq, cardlseq))
    data[:] = np.nan
    for p_ind in range(len(cv)):
        data[partitioned_out(p_ind, hseq, lseq)] = cv[p_ind]
    return data