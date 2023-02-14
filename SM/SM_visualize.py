"""
    Part of ANNarchy-SM

    This file contain implementation and comment of visualization.
    The resulting figures are stored in the subfolder *results*.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

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

def create_figure_3_withVR(HD_rate, BVC_rate, PR_rate, H_rate, OVC_rate, ObjEncoded, plt_ttl_flag, load_flag, imag_flag, vr_room, agent_view, folder, Obj2Recall=-1):
    """
    New visualization of the SM-model in VR
    """
    
    #figure setup
    fig = plt.figure(figsize=(24,16))

    title_size = 50     # overall title size
    plt_ttl_size = 16   # subplot title size
    plt_lbl_size = 12   # subplot label size
    
    gs0 = gridspec.GridSpec(1, 2)
    gs0.update(top=.90, hspace=.4, wspace=.35, left=0.05, right=0.95, bottom=0.025)
    gs00 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[0])
    gs01 = gridspec.GridSpecFromSubplotSpec(3, 2, subplot_spec=gs0[1])
    
    
    # compute indices
    nb_neurons_HD = HD_rate.shape[0]
    nb_neurons_H = H_rate.shape[0]
    (HDX,HDY) = compute_coords_HD(nb_neurons_HD)
    (BVCX, BVCY)  = compute_coords_BVC()
    (HX, HY) = compute_coords_HPC(nb_neurons_H)
    
    
    #VR images
    ax1 = fig.add_subplot(gs00[0, :])
    ax1.set_title('Agent View', fontsize = plt_ttl_size)
    ax1.imshow(agent_view)
    ax1.set_xticks([])
    ax1.set_yticks([])
    
    
    ax2 = fig.add_subplot(gs00[1, :])
    ax2.set_title('VR Room', fontsize = plt_ttl_size)
    ax2.imshow(vr_room)
    ax2.set_xticks([])
    ax2.set_yticks([])
    
    #############
    #firing rates
    #############
    
    #HPC activity
    ax3 = fig.add_subplot(gs01[0, 0])
    ax3.set_xticks([])
    ax3.set_yticks([])
    
    ax3.set_title("PC rates\n", fontsize = plt_ttl_size)
    ax3.text( 11.0, 22.1, "North", verticalalignment="bottom", horizontalalignment="center", fontsize = plt_lbl_size)
    ax3.text( 22.1, 11.0, "East", verticalalignment="center", horizontalalignment="left", rotation=270.0, fontsize = plt_lbl_size)
    ax3.text( 11.0, -0.1, "South", verticalalignment="top", horizontalalignment="center", fontsize = plt_lbl_size)
    ax3.text( -0.1, 11.0, "West", verticalalignment="center", horizontalalignment="right", rotation=90.0, fontsize = plt_lbl_size)
   
    data = np.zeros( (nb_neurons_H, 2) )
    data = np.reshape(H_rate, (HX.shape[0], HY.shape[1]))
    
    ax3.contourf(HX, HY, data, 20)

    #BVC activity
    ax4 = fig.add_subplot(gs01[0, 1])
    ax4.set_xticks([])
    ax4.set_yticks([])
    
    ax4.set_title("BVC rates\n", fontsize = plt_ttl_size)
    ax4.text(  0.0, 16.1, "North", verticalalignment="bottom", horizontalalignment="center", fontsize = plt_lbl_size)
    ax4.text( 16.1,  0.0, "East", verticalalignment="center", horizontalalignment="left", rotation=270.0, fontsize = plt_lbl_size)
    ax4.text(  0.0,-16.1, "South", verticalalignment="top", horizontalalignment="center", fontsize = plt_lbl_size)
    ax4.text(-16.1,  0.0, "West", verticalalignment="center", horizontalalignment="right", rotation=90.0, fontsize = plt_lbl_size)
    
    data = np.reshape(BVC_rate, (BVCY.shape[0], BVCX.shape[1]))
    ax4.contourf(BVCX, BVCY, data, 20)
    

    #HD activity
    ax5 = fig.add_subplot(gs01[1, 0])
    ax5.set_xticks([])
    ax5.set_yticks([])
    
    data = np.zeros( (nb_neurons_HD, 2) )
    data[:,0] = HD_rate
    data[:,1] = HD_rate
    
    ax5.set_title("HD rates\n", fontsize = plt_ttl_size)
    ax5.text( 0.0, 1.55, "North", verticalalignment="bottom", horizontalalignment="center", fontsize = plt_lbl_size)
    ax5.text( 1.55, 0.0, "East", verticalalignment="center", horizontalalignment="left", rotation=270.0, fontsize = plt_lbl_size)
    ax5.text(  0, -1.55, "South", verticalalignment="top", horizontalalignment="center", fontsize = plt_lbl_size)
    ax5.text(-1.55, 0.0, "West", verticalalignment="center", horizontalalignment="right", rotation=90.0, fontsize = plt_lbl_size)
    
    ax5.contourf(HDX, HDY, data, 20)
    
    
    #OVC activity
    ax6 = fig.add_subplot(gs01[1, 1])
    ax6.set_xticks([])
    ax6.set_yticks([])
    
    ax6.set_title("OVC rates\n", fontsize = plt_ttl_size)
    ax6.text(  0.0, 16.1, "North", verticalalignment="bottom", horizontalalignment="center", fontsize = plt_lbl_size)
    ax6.text( 16.1,  0.0, "East", verticalalignment="center", horizontalalignment="left", rotation=270.0, fontsize = plt_lbl_size)
    ax6.text(  0.0,-16.1, "South", verticalalignment="top", horizontalalignment="center", fontsize = plt_lbl_size)
    ax6.text(-16.1,  0.0, "West", verticalalignment="center", horizontalalignment="right", rotation=90.0, fontsize = plt_lbl_size)
    
    data = np.reshape(OVC_rate, (BVCY.shape[0], BVCX.shape[1]))
    data[data < 0.05] = 0
    ax6.contourf( BVCX, BVCY, data, 20, vmax = max(0.05, data.max())) # Added to suppress display of "almost zero" rates
    
    #PR activity
    ax7 = fig.add_subplot(gs01[2, 0])
    ax7.set_xticks([])
    ax7.set_yticks([])
    
    ax7.bar(list(range(PR_rate.shape[0])), PR_rate)
    ax7.set_title("PR rates\n", fontsize = plt_ttl_size)
    ax7.set_xticks([0, 1, 2, 3])
    ax7.set_xticklabels(['N', 'W', 'S', 'E'])
    ax7.set_ylim([0, 1]) 
    
    
    #Encoded objects
    ax8 = fig.add_subplot(gs01[2, 1])
    ax8.set_xticks([])
    ax8.set_yticks([])
    if imag_flag:
        ax8.set_title("Object to Recall\n", fontsize = plt_ttl_size)
    else:
        ax8.set_title("Object Encoded\n", fontsize = plt_ttl_size)
    enc_obj = create_encoded_objects(ObjEncoded)
    # need to store in intermediate file, otherwise imshow does some strange stuff visualizing enc_obj directly
    enc_obj = enc_obj.astype(np.uint8) #colorspace conversion to suppress warning when saving
    imwrite(ctrl_vars['images']+'targets/tmp.png', enc_obj)  
    ax8.imshow(imread(ctrl_vars['images']+'targets/tmp.png'))
    ax8.set_xticks([])
    ax8.set_yticks([])
    
    #Printing the title    
    if plt_ttl_flag == 1:
        plt.suptitle('Encoding current position of the agent', fontsize=title_size)
    elif plt_ttl_flag == 2:
        plt.suptitle('Imagery engaged: Where is my green crane?', fontsize=title_size)
    elif plt_ttl_flag == 3:
        plt.suptitle('Re-establish bottom-up representation based on perception', fontsize=title_size)
    elif plt_ttl_flag == 4:
        plt.suptitle('Object encountered, encoding', fontsize=title_size)
    elif plt_ttl_flag == 5:
        plt.suptitle('Imagination phase', fontsize=title_size)
    elif plt_ttl_flag == 6:  
        plt.suptitle(' ', fontsize=title_size)
    elif plt_ttl_flag == 7:  
        plt.suptitle('Walking to a new position', fontsize=title_size)
    elif plt_ttl_flag == 8:  
        plt.suptitle('Executing a saccade to the target object', fontsize=title_size)
    elif plt_ttl_flag == 9:  
        plt.suptitle('Applying spatial attention on the expected target position', fontsize=title_size)
    elif plt_ttl_flag == 10:  
        plt.suptitle('Located target object', fontsize=title_size)
    elif plt_ttl_flag == 11:  
        plt.suptitle('Searching for the target object (green crane)', fontsize=title_size)
    elif plt_ttl_flag == 12:  
        plt.suptitle('Walking back to the target object', fontsize=title_size)
    # the step count was already incremented.
    try:
        if load_flag:
            fig.savefig(folder + "/load_figure1_%06i.jpg" %(get_current_step()-1) )
        else:
            fig.savefig(folder + "/SM_%06i.jpg" %(get_current_step()-1) )
        plt.close()
        
    except IOError:
        # Folder 'results' was not existing.
        pass