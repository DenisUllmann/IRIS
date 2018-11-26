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

def partitioned_ind(p_ind, timeseq, hseq, lseq, shape):
    t, h, l = partition_ind_to_position(p_ind, hseq, lseq)
    t0 = t*(timeseq // 2)
    t1 = min(t0+timeseq, shape[0])
    y0 = h*hseq
    y1 = min(y0+hseq, shape[1])
    x0 = l*lseq
    x1 = min(x0+lseq, shape[2])
    return slice(t0, t1, 1), slice(y0, y1, 1), slice(x0, x1, 1)

def partitioned_out(p_ind, hseq, lseq, shape):
    t, h, l = partition_ind_to_position(p_ind, hseq, lseq)
    y0 = h*hseq
    y1 = min(y0+hseq, shape[1])
    x0 = l*lseq
    x1 = min(x0+lseq, shape[2])
    return t, slice(y0, y1, 1), slice(x0, x1, 1)

def layer_dct3(data):
    shape = data.shape
    res = copy(data)
    # Normalize data
    res /= np.linalg.norm(res)
    # apply 2D-DCT for all frames
    for i in range(shape[0]):
        res[i,:,:] = fftpack.dctn(data[i,:,:], norm='ortho')
    # apply 1D-DCT on the time component
    for i in range(shape[1]*shape[2]):
        res[:, i // shape[1], i % shape[1]] = fftpack.dct(res[:, i // shape[1], i % shape[1]], norm='ortho')
    # get variances on the time component
    res = np.log(np.var(res, axis=0)+1)
    return res

def combine_results(dct3, cardtimeseq, hseq, lseq, shape):
    data = np.zeros((2*cardtimeseq-1,shape[1],shape[2]))
    data[:] = np.nan
    for p_ind in range(len(dct3)):
        data[partitioned_out(p_ind, hseq, lseq, shape)] = dct3[p_ind]
    return data