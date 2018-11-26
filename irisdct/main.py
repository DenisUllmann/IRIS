# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 20:29:28 2018

@author: Denis
"""

import numpy as np
import math
from config import config as cfg
import folders
import reader
from reader.utils import miss_to_nan
import masks
import time
from joblib import Parallel, delayed
import multiprocessing
from inpaint.inpaintn import inpaintn, partitioned_ind, combine_partitions
from scipy.misc import toimage
import layers.layer1 as layer1
from layer1 import layer_dct3
import layers.layer2 as layer2
from layer2 import layer_cv

source = folders.source # path to fits images
source_children_pathes = folders.source_children # pathes to all fits images

for source_child_path in source_children_pathes:
    
    # make folders integrated in the tree for analysis of this video
    child_folders_make = folders.source_child_foldermaker(source_child_path,source)
    
    # read data, get parameters
    sji_original, sji_infos = reader.sji_cube_loader(source_child_path)
    n_steps = sji_infos.n_steps
    height = sji_infos.height
    large = sji_infos.large
    
    # in case of downsizing before anayzing
    if cfg.downsize:
        height = math.floor(height*cfg.ds_ratio)
        large = math.floor(large*cfg.ds_ratio)
        sji_original = np.resize(sji_original,(n_steps, height, large))
    
    # analyse parameters from config and infered
    hmargin = cfg.hmargin
    lmargin = cfg.lmargin
    timeseq = int(cfg.timeseq)
    cardtimeseq = math.ceil(n_steps/timeseq)
    hseq = int(cfg.hseq)
    cardhseq = math.ceil((height-2*hmargin)/hseq)
    lseq = int(cfg.lseq)
    cardlseq = math.ceil((large-2*lmargin)/lseq)
    
    # put all negative values and their requested neighbors to nan
    nan_cube = miss_to_nan(sji_original)
    
    # BORDER MASKS ------------------------------------------------------------
    # get the mask for borders missing values only, ag, bg, cg & dg are the
    # top, bottom, left, right maximum values for cropping and keeping all
    # theinformation
    if not(cfg.loadm and (cfg.doInp or cfg.loadInp)):
        masks, ag, bg, cg, dg = masks.borders.borders_m(nan_cube,sji_infos)
        np.savez(folders.name_saving(source_child_path, source, 'masks'),masks=masks, ag=ag, bg=bg, cg=cg, dg=dg)
    elif cfg.loadm and (cfg.doInp or cfg.loadInp):
        print('%s : Loading borders masks - start' % time.asctime())
        masks = np.load(folders.name_saving(source_child_path, source, 'masks.npz'))['masks']
        ag = np.load(folders.name_saving(source_child_path, source, 'masks.npz'))['ag']
        bg = np.load(folders.name_saving(source_child_path, source, 'masks.npz'))['bg']
        cg = np.load(folders.name_saving(source_child_path, source, 'masks.npz'))['cg']
        dg = np.load(folders.name_saving(source_child_path, source, 'masks.npz'))['dg']
        print('%s : Loading borders masks - end' % time.asctime())
    
    # INPAINTING --------------------------------------------------------------
    # parallel inpaint the missing data
    if not(cfg.loadInp) and cfg.doInp:
        sji_for_inp = sji_original[:,ag:bg,cg:dg]
        # Partition in 27 overlapping subblocks for faster inpainting
        num_cores = multiprocessing.cpu_count()
        
        sji_inp_p = Parallel(n_jobs=num_cores)(delayed(inpaintn)(
                sji_for_inp[partitioned_ind(p_ind, sji_for_inp.shape)]
                ) for p_ind in range(3**3))
        
        sji_inp_p = combine_partitions(sji_inp_p, sji_for_inp.shape)
        
        sji_inp = np.zeros(sji_original.shape)
        sji_inp[:] = np.nan
        sji_inp[:,ag:bg,cg:dg] = sji_inp_p
        np.savez(folders.name_saving(source_child_path, source, 'InpSJI'),sji_inp=sji_inp)
    elif cfg.loadInp:
        print('%s : Loading inpainted images - start' % time.asctime())
        sji_inp = np.load(folders.name_saving(source_child_path, source, 'InpSJI.npz'))['sji_inp']
        print('%s : Loading inpainted images - end' % time.asctime())
    
    # IMAGES SAVE -------------------------------------------------------------
    maxo = np.max(sji_original)
    sji_inp_m = sji_inp
    sji_inp_m[masks==np.nan] = np.nan
    
    if cfg.writeImH:
        print('%s : Saving images - start' % time.asctime())
        for i in range(n_steps):
            toimage(np.log(sji_original[i,:,:])/np.log(maxo), cmin=0.0, cmax=1.0).save(folders.pathname_image(source_child_path, source,'Original%i.png' % i))
            toimage(np.log(sji_inp[i,:,:])/np.log(maxo), cmin=0.0, cmax=1.0).save(folders.pathname_image(source_child_path, source,'Inpaint%i.png' % i))
            toimage(np.log(sji_inp_m[i,:,:])/np.log(maxo), cmin=0.0, cmax=1.0).save(folders.pathname_image(source_child_path, source,'MInpaint%i.png' % i))
        print('%s : Saving images - end' % time.asctime())
    
    # 1ST LAYER - 3D DCT + LOGVARS --------------------------------------------
    if not(cfg.loadDCTCV):
        # Read and apply 2D DCT
        print('%s : Parallel 3D analyse - 1st Layer - start' % time.asctime())
        num_cores = multiprocessing.cpu_count()
        
        dct3 = Parallel(n_jobs=num_cores)(delayed(layer_dct3)(
                sji_original[layer1.partitioned_ind(p_ind, timeseq, hseq, lseq, sji_original.shape)]
                ) for p_ind in range((2*cardtimeseq-1)*cardhseq*cardlseq))
        
        dct3 = layer1.combine_results(dct3, timeseq, hseq, lseq, sji_original.shape)
        
        if cfg.doInp or cfg.loadInp:
            dct3_inp = Parallel(n_jobs=num_cores)(delayed(layer_dct3)(
                    sji_inp[layer1.partitioned_ind(p_ind, timeseq, hseq, lseq, sji_original.shape)]
                    ) for p_ind in range((2*cardtimeseq-1)*cardhseq*cardlseq))
            
            dct3_inp = layer1.combine_results(dct3_inp, timeseq, hseq, lseq, sji_original.shape)
        print('%s : Parallel 3D analyse - 1st Layer - end' % time.asctime())
    
    # 1ST LAYER - 3D DCT + LOGVARS --------------------------------------------
    if not(cfg.loadDCT3):
        # Read and apply 2D DCT
        print('%s : Parallel 3D analyse - 1st Layer - start' % time.asctime())
        num_cores = multiprocessing.cpu_count()
        
        dct3 = Parallel(n_jobs=num_cores)(delayed(layer_dct3)(
                sji_original[layer1.partitioned_ind(p_ind, timeseq, hseq, lseq, sji_original.shape)]
                ) for p_ind in range((2*cardtimeseq-1)*cardhseq*cardlseq))
        
        dct3 = layer1.combine_results(dct3, timeseq, hseq, lseq, sji_original.shape)
        
        if cfg.doInp or cfg.loadInp:
            dct3_inp = Parallel(n_jobs=num_cores)(delayed(layer_dct3)(
                    sji_inp[layer1.partitioned_ind(p_ind, timeseq, hseq, lseq, sji_inp.shape)]
                    ) for p_ind in range((2*cardtimeseq-1)*cardhseq*cardlseq))
            
            dct3_inp = layer1.combine_results(dct3_inp, timeseq, hseq, lseq, sji_inp.shape)
        print('%s : Parallel 3D analyse - 1st Layer - end' % time.asctime())
        np.savez(folders.name_saving(source_child_path, source, 'DCT3'),dct3=dct3)
        if cfg.doInp or cfg.loadInp:
            np.savez(folders.name_saving(source_child_path, source, 'InpDCT3'),dct3_inp=dct3_inp)
    else:
        print('%s : Loading 3d-dct analysis - start' % time.asctime())
        dct3 = np.load(folders.name_saving(source_child_path, source, 'DCT3.npz'))['dct3']
        if cfg.doInp or cfg.loadInp:
            dct3_inp = np.load(folders.name_saving(source_child_path, source, 'InpDCT3.npz'))['dct3_inp']
        print('%s : Loading 3d-dct analysis - end' % time.asctime())
    
    # 2ND LAYER - SUBVARIANCES ------------------------------------------------
    if not(cfg.loadDCTCV):
        # Apply the selected part subvariances
        print('%s : Parallel partials subvariances - 2nd Layer - start' % time.asctime())
        num_cores = multiprocessing.cpu_count()
        
        cv = Parallel(n_jobs=num_cores)(delayed(layer_cv)(
                dct3[layer2.partitioned_ind(p_ind, timeseq, hseq, lseq, sji_original.shape)]
                ) for p_ind in range((2*cardtimeseq-1)*cardhseq*cardlseq))
        
        cv = layer2.combine_results(cv, timeseq, hseq, lseq, dct3.shape)
        
        if cfg.doInp or cfg.loadInp:
            cv_inp = Parallel(n_jobs=num_cores)(delayed(layer_cv)(
                    dct3_inp[layer2.partitioned_ind(p_ind, timeseq, hseq, lseq, sji_original.shape)]
                    ) for p_ind in range((2*cardtimeseq-1)*cardhseq*cardlseq))
            
            cv_inp = layer2.combine_results(cv_inp, hseq, cardlseq, cardhseq, lseq, dct3_inp.shape)
        print('%s : Parallel partials subvariances - 2nd Layer - end' % time.asctime())
        np.savez(folders.name_saving(source_child_path, source, 'CV'),cv=cv)
        if cfg.doInp or cfg.loadInp:
            np.savez(folders.name_saving(source_child_path, source, 'InpCV'),cv_inp=cv_inp)
    else:
        print('%s : Loading partials subvariances - start' % time.asctime())
        cv = np.load(folders.name_saving(source_child_path, source, 'CV.npz'))['cv']
        if cfg.doInp or cfg.loadInp:
            cv_inp = np.load(folders.name_saving(source_child_path, source, 'InpCV.npz'))['cv']
        print('%s : Loading partials subvariances - end' % time.asctime())
