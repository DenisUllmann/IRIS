# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 20:29:05 2018

@author: Denis

Inspired from Damian Garcia Matlab inpaintn.m 'Robust smoothing of gridded multidimensional data with missing values'
Different implementation for the nearest neighbor initial_guess (less memory
consuming, memorizing only the borders values), adapted to python.
"""

import numpy as np
from scipy import ndimage, fftpack
from scipy.interpolate import NearestNDInterpolator
from progressbar import ProgressBar, FormatLabel, Percentage, Bar, ETA
from copy import copy

# Find the "out-border" of the missing values regions
def miss_border(is_data, filter_size=3): #TO TEST (1,3,3)!!!!!
    return np.logical_xor(is_data,ndimage.minimum_filter(is_data,size=filter_size))

# Nearest neighbor interpolation for the missing data
def initial_guess(data, is_data):
    if np.sum(is_data)!=np.sum(np.ones(is_data.shape)):
        is_miss_border = miss_border(is_data)
        points = np.swapaxes(np.asarray(np.where(is_miss_border)),0,1)
        values = data[is_miss_border]
        f = NearestNDInterpolator(points, values)
        data[is_data==0] = f(np.swapaxes(np.asarray(np.where(is_data==0)),0,1))
    s0 = 3
    y = copy(data)
    data[np.logical_not(is_data)] = np.nan
    return y, s0

def generate_lambda(size_data):
    d = len(size_data)
    l = np.zeros(size_data) #lambda
    for i in range(d):
        size0 = np.ones(d).astype(int)
        nj = size_data[i]
        size0[i] = nj
        l += np.reshape(np.cos(np.array(range(nj))*np.pi/nj), tuple(size0), order="F")
    l = 4*np.power((l-d),2)
    return l

def inpaintn(data, n=100):
    w = data==data
    
    # The case of no missing data
    if np.sum(np.logical_not(w)) == 0:
        return data
    # Initial guessing for the missing data
    else:
        y,s0 = initial_guess(data, w)
    
    # Parameters for the inpainting
    if n==1:
        s = np.array([10**(-6)])
    else:
        s = np.logspace(s0, -6, n)
    l = generate_lambda(data.shape)
    data[np.logical_not(w)] = 0
    
    widgets = [FormatLabel('Processed: %(value)d (in: %(elapsed)s) '), Percentage(),' ',Bar(marker='0',left='[',right=']'),' ',ETA()]
    wait_bar = ProgressBar(widgets = widgets,maxval=n).start()
    for i in wait_bar((i for i in range(n))):
        #gamma = 1/(1+s[i]*l)
        y = 2*fftpack.idctn(1/(1+s[i]*l)*fftpack.dctn(w*(data-y)+y,norm='ortho'),norm='ortho') -y
        wait_bar.update(i)
    wait_bar.finish()
    
    data[np.logical_not(w)] = np.nan
    y[w] = data[w]
    return y

def partition_ind_to_position(p_ind):
    i = p_ind // 9
    j = (p_ind % 9) // 3
    k = (p_ind % 9) % 3
    return i,j,k

def partitioned_ind(p_ind, data_shape):
    n_steps, l, m = data_shape
    i, j, k = partition_ind_to_position(p_ind)
    t0 = (k*np.floor(n_steps/3)-10)*(k>0)
    t1 = ((k+1)*np.floor(n_steps/3)+10)*(k<2)+n_steps*(k==2)
    y0 = (i*np.floor(l/3)-10)*(i>0)
    y1 = ((i+1)*np.floor(l/3)+10)*(i<2)+l*(i==2)
    x0 = (j*np.floor(m/3)-10)*(j>0)
    x1 = ((j+1)*np.floor(m/3)+10)*(j<2)+m*(j==2)
    return slice(t0, t1, 1), slice(y0, y1, 1), slice(x0, x1, 1)

def combine_partitions(sji_inp_p, data_shape):
    sji_inp = np.zeros(data_shape)
    for p_ind in range(3**3):
        sji_inp[partitioned_ind(p_ind, data_shape)] += sji_inp_p[p_ind]
    sji_inp[:,np.floor(data_shape[1]/3)-11:np.np.floor(data_shape[1]/3)+9,:] /= 2
    sji_inp[:,2*np.floor(data_shape[1]/3)-11:2*np.floor(data_shape[1]/3)+9,:] /= 2
    sji_inp[:,:,np.floor(data_shape[2]/3)-11:np.floor(data_shape[2]/3)+9] /= 2
    sji_inp[:,:,2*np.floor(data_shape[2]/3)-11:2*np.floor(data_shape[2]/3)+9] /= 2
    sji_inp[np.floor(data_shape[0]/3)-11:np.floor(data_shape[0]/3)+9,:,:] /= 2
    sji_inp[2*np.floor(data_shape[0]/3)-11:2*np.floor(data_shape[0]/3)+9,:,:] /= 2
    return sji_inp