# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 18:07:05 2018

@author: Denis
"""
import time
import numpy as np

def borders_m(data_cube, infos):
    print('%s : Creating borders masks - start' % time.asctime())
    masks = 0*data_cube
    nan_masks = np.isnan(masks)
    ag = infos.height
    bg = 1
    cg = infos.large
    dg = 1
    for i in range(infos.n_steps):
        a = 0
        ca = 1
        b = infos.height-1
        cb = 1
        c = 0
        cc = 1
        d = infos.large-1
        cd = 1
        cont = 1
        testnan = sum(sum(np.logical_not(nan_masks[i])))
        if testnan>0:
            while cont==1:
                if cc==1 and sum(np.logical_not(nan_masks[i,a:b,c]))==0:
                    c = c+1
                else:
                    cc = 0
                if cd==1 and sum(np.logical_not(nan_masks[i,a:b,d]))==0:
                    d = d-1
                else:
                    cd = 0
                if ca==1 and sum(np.logical_not(nan_masks[i,a,c:d]))==0:
                    a = a+1
                else:
                    ca = 0
                if cb==1 and sum(np.logical_not(nan_masks[i,b,c:d]))==0:
                    b = b-1
                else:
                    cb = 0
                if cc+cd+ca+cb==0:
                    cont = 0
            if a < ag:
                ag = a
            if b > bg:
                bg = b
            if c < cg:
                cg = c
            if d > dg:
                dg = d
            for j in range(a,b+1):
                u = c
                while nan_masks[i,j,u]==1:
                    u = u+1
                v = d
                while nan_masks[i,j,v]==1:
                    v = v-1
                for k in range(u,v+1):
                    masks[i,j,k] = 0
            for j in range(c,d+1):
                u = a
                while nan_masks[i,u,j]==1:
                    masks[i,u,j] = np.nan
                    u = u+1
                v = b
                while nan_masks[i,v,j]==1:
                    masks[i,v,j] = np.nan
                    v = v-1
    print('%s : Creating borders masks - end' % time.asctime())
    return masks, ag, bg, cg, dg
    