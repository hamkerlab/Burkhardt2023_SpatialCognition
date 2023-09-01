"""
    Part of ANNarchy-SM

    This file contain implementation and comment of visualization.
    The resulting figures are stored in the subfolder *results*.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import os
import csv
import numpy as np
from numpy import round
from matplotlib import pylab as plt
from matplotlib import gridspec
from math import pi, floor, ceil
from mpl_toolkits.mplot3d import Axes3D

from ANNarchy import get_current_step
from imageio import imwrite
from cv2 import imread, cvtColor, COLOR_BGR2GRAY
from PIL import Image
from skimage import img_as_ubyte

from SM_parameters import ctrl_vars
from SM_helper_functions import pol2cart, radscaling
from SM_load_mat_files import load_grid_parameters

def compute_coords_BVC():
    """
    Compute cartesian coords for BVC-size population (currently 816 neurons)
    """
    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()

    NBVCR        = int(round((maxR)/polarDistRes))          # 16
    NBVCTheta    = int(floor((2*pi-0.01)/polarAngRes)+1)    # 51
    NGrid        = NBVCR*NBVCTheta # Num. grid neurons
    
    polarDist = radscaling(maxR) # added radial scaling (according to eLife code)
    
    polarAng = np.zeros(NBVCTheta)
    for i in range(NBVCTheta):
        polarAng[i] = i * polarAngRes * NBVCTheta / float(NBVCTheta - 1)
    
    (pDist, pAng) = np.meshgrid(polarDist, polarAng)
    (BVCX, BVCY)  = pol2cart(pAng, pDist)

    return BVCX, BVCY

def compute_coords_HD(nb_neurons_HD):
    """
    Compute cartesian coords for HD-size population (currently 100 neurons)
    """
    HDangles         = np.zeros(nb_neurons_HD)
    for i in range(nb_neurons_HD):
        HDangles[i] = i * (2.0 * pi / float(nb_neurons_HD - 1)) + pi/2.0

    (HDDist, HDAngle) = np.meshgrid([1, 1.5], HDangles)
    (HDX,HDY) = pol2cart(HDAngle,HDDist)

    return HDX, HDY

def compute_coords_HPC(nb_neurons_H):
    """
    Compute cartesian coords for HPC-size population (currently 1900 neurons)
    """

    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()
    NHx = round((int(maxX) - minX) / Hres)   #110
    NHy = round((int(maxY) - minY) / Hres)
    Hx = np.arange(minX + Hres/2.0, minX + (NHx - 0.5 + 1) * Hres, Hres)
    Hy = np.arange(minY + Hres/2.0, minY + (NHy - 0.5 + 1) * Hres, Hres)
    HX, HY = np.meshgrid(Hx,Hy)
    
    return HX, HY

def create_encoded_objects(encodedObjects):
    objIDs = np.arange(0,4)
    img = []

    for obj in objIDs:
        if(encodedObjects[obj] == 0):
            gray_scale = imread(ctrl_vars["images"]+"targets/Target0"+str(obj)+".png", 1)
            gray = cvtColor(gray_scale, COLOR_BGR2GRAY)
            tmp = np.zeros((gray_scale.shape[0], gray_scale.shape[1], 3))
            tmp[:,:,0] = gray
            tmp[:,:,1] = gray
            tmp[:,:,2] = gray
            img.append(tmp)
        else:
            img.append(imread(ctrl_vars["images"]+"targets/Target0"+str(obj)+".png"))

    mat = None

    init_1st_row = True
    for row in range(2):
        init_1st_col = True
        for col in range(2):
            if init_1st_col:
                row_data = img[row*2+col]
                init_1st_col = False
            else:
                row_data = np.concatenate((row_data,img[row*2+col]), axis=1)
        
        if init_1st_row:
            mat = row_data
            init_1st_row = False
        else:
            mat = np.concatenate((mat, row_data))

    return mat

def create_recalled_objects(obj2recall):
    objIDs = np.arange(0,4)
    img = []

    for obj in objIDs:
        if(obj != obj2recall):
            gray_scale = imread(ctrl_vars["images"]+"targets/Target0"+str(obj)+".png", 1)
            gray = cvtColor(gray_scale, COLOR_BGR2GRAY)
            tmp = np.zeros((gray_scale.shape[0], gray_scale.shape[1], 3))
            tmp[:,:,0] = gray
            tmp[:,:,1] = gray
            tmp[:,:,2] = gray
            img.append(tmp)
        else:
            img.append(imread(ctrl_vars['images']+'targets/Target0'+str(obj)+'.png'))

    mat = None

    init_1st_row = True
    for row in range(2):
        init_1st_col = True
        for col in range(2):
            if init_1st_col:
                row_data = img[row*3+col]
                init_1st_col = False
            else:
                row_data = np.concatenate((row_data,img[row*2+col]), axis=1)
        
        if init_1st_row:
            mat = row_data
            init_1st_row = False
        else:
            mat = np.concatenate((mat, row_data))

    return mat

def create_network_figure(SM_rates, VISLIP_rates, title, phase, vr_room, agent_view, folder, n=1):
    # figure size
    width = 6800
    height = 5000
    
    # SM indices
    nb_neurons_HD = SM_rates['HD'].shape[0]
    nb_neurons_H = SM_rates['PC'].shape[0]
    (HDX,HDY) = compute_coords_HD(nb_neurons_HD)
    (BVCX, BVCY)  = compute_coords_BVC()
    (HX, HY) = compute_coords_HPC(nb_neurons_H)

    # get grid for subplot
    wd = os.path.dirname(os.path.realpath(__file__))
    grid = {}    
    with open(f'{wd}/video/grid.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if row[0] != 'name':
                grid[row[0]] = row[1:]
                
    # background
    fn_bg_enc = f'{wd}/video/{phase}_template.png'

    ## Plotting
    fig = plt.figure(figsize=(width/100, height/100))
    fig.subplots_adjust(left=0.008, right=1, bottom=0, top=1, wspace=0, hspace=0)
    
    gs = gridspec.GridSpec(height, width)
    
    # VIS and LIP rates
    for name, r in VISLIP_rates.items():
        try:
            # print(name, grid[name])
            gs_slice = np.array(grid[name], dtype=int)
            fig.add_subplot(gs[gs_slice[1]:gs_slice[1]+gs_slice[3], gs_slice[0]:gs_slice[0]+gs_slice[2]])
            
            if name == 'AuxV1':
                r = np.average(np.average(r, axis=3), axis=2)
                plt.imshow(r.T)  
            elif name == 'V4':
                r = np.max(r, axis=2)
                plt.imshow(r.T, vmin=0.0, vmax=0.8)  
            elif name == 'PFC':
                r = np.ones((len(r), 1)) * r
                plt.imshow(r.T, vmin=0.0, vmax=1.0)
            elif name == 'FEF':
                plt.imshow(r.T, vmin=0.0, vmax=0.8)  
            elif name == 'Xh':
                if phase == "encoding" or phase == "encodingText":
                    plt.imshow(r.T, vmin=0.0, vmax=0.4)
                else:
                    plt.imshow(r.T, vmin=0.0, vmax=1.0)

            plt.axis('off')

        except KeyError:
            print(name, 'has no grid')
            
    # SM rates
    for name, r in SM_rates.items():
        try:
            # print(name, grid[name])
            gs_slice = np.array(grid[name], dtype=int)
            fig.add_subplot(gs[gs_slice[1]:gs_slice[1]+gs_slice[3], gs_slice[0]:gs_slice[0]+gs_slice[2]])
            
            if name == 'PRo':
                # Binarize rates for visualization
                r[r<0.5] = 0.1
                background_bars = [1, 1, 1]
                colors = [plt.cm.viridis((x - 0.1) / 0.6) if x > 0.1 else plt.cm.viridis(0) for x in r]
                plt.barh([2,1,0], background_bars, color='lightgray') # plot background bars
                plt.barh([2,1,0], r[:3], color=colors)
                plt.xlim(1, 0)
            elif name == 'HD':
                r = np.zeros((nb_neurons_HD, 2))
                r[:,0] = SM_rates['HD']
                r[:,1] = SM_rates['HD']
                plt.contourf(HDX, HDY, r, 20, vmin=0, vmax=1)
            elif name == 'PC':
                r = np.reshape(r, (HY.shape[0], HX.shape[1]))
                plt.contourf(HX, HY, r, 20, vmin=0, vmax=1)
            else:
                r = np.reshape(r, (BVCY.shape[0], BVCX.shape[1]))
                r[r < 0.1] = 0 # suppress small activations in plot
                plt.contourf(BVCX, BVCY, r, 20, vmin=0, vmax=1)

            plt.axis('off')
        except KeyError:
            print(name, 'has no grid')
            
    # visual field and top-down view of room
    gs_slice = np.array(grid['VF'], dtype=int)
    fig.add_subplot(gs[gs_slice[1]:gs_slice[1]+gs_slice[3], gs_slice[0]:gs_slice[0]+gs_slice[2]])
    plt.imshow(agent_view)
    plt.axis('off')

    gs_slice = np.array(grid['room'], dtype=int)
    fig.add_subplot(gs[gs_slice[1]:gs_slice[1]+gs_slice[3], gs_slice[0]:gs_slice[0]+gs_slice[2]])
    plt.imshow(vr_room)
    plt.axis('off')
            
    # background
    fig.add_subplot(gs[:, :])
    bg = plt.imread(fn_bg_enc)
    plt.imshow(bg)
    plt.axis('off')

    title_size = 100
    title_y_position = 0.99
    fig.subplots_adjust(top=0.95)
    plt.suptitle(title, fontsize=title_size, fontweight="bold", y=title_y_position)
    
    if n > 1:
        for i in range(n):
            fig.savefig(f"{folder}/{get_current_step()-1:06}_{i}.jpg", dpi=70)
    else:
        fig.savefig(f"{folder}/{get_current_step()-1:06}.jpg", dpi=70)
    plt.close()