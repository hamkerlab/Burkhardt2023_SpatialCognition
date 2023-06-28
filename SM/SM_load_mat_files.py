"""
    Part of ANNarchy-SM
    This file contain all codes needed to load .mat files and store data in matrices used by network.py

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import sys
import scipy.io
import numpy as np
from SM_parameters import ctrl_vars
from SM_roomGridPositions import load_attributes

def load_weights():
    """
    Load pre-trained connection weights and apply scaling factors.

    Returns:

        * dictionary containing all loaded matrices, as key-value pairs.
    """
    weights = {}

    #
    # load precalculated weight matrices
    # (externally supplied for now, will need to be recalculated for the VR room)

    # Weights_VR_MTL.mat
    # ====================================
    weights['BVC2BVC'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['BVC2BVCwts']
    weights['BVC2H']   = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['BVC2Hwts']
    weights['BVC2PR']  = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['BVC2PRwts']
    weights['H2BVC']   = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['H2BVCwts']
    weights['H2H']     = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['H2Hwts']
    weights['H2PR']    = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['H2PRwts']
    weights['PR2BVC']  = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['PR2BVCwts']
    weights['PR2H']    = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['PR2Hwts']
    weights['PR2PR']   = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['PR2PRwts']

    '''#
    weights['OVC2BVC'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['OVC2BVCwts']
    weights['BVC2OVC'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['BVC2OVCwts']
    weights['OVC2H']   = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['OVC2Hwts']
    weights['H2OVC']   = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['H2OVCwts']
    weights['OVC2oPR']  = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['OVC2oPRwts']
    weights['oPR2OVC']  = scipy.io.loadmat(ctrl_vars['data_from_training']+'Weights_VR_MTL.mat')['oPR2OVCwts']
    '''

    # TRWeights_original.mat
    # ====================================
    weights['HD2TR'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['HD2TRwts']
    weights['BVC2TR'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['BVC2TRwts'].transpose()
    weights['TR2BVC'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2BVCwts'].transpose()

    # from_sparse_matrix() connector requires pre-ordererd pairs
    weights['PW2TR1'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts1'].transpose()
    weights['PW2TR2'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts2'].transpose()
    weights['PW2TR3'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts3'].transpose()
    weights['PW2TR4'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts4'].transpose()
    weights['PW2TR5'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts5'].transpose()
    weights['PW2TR6'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts6'].transpose()
    weights['PW2TR7'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts7'].transpose()
    weights['PW2TR8'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts8'].transpose()
    weights['PW2TR9'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts9'].transpose()
    weights['PW2TR10'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts10'].transpose()
    weights['PW2TR11'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts11'].transpose()
    weights['PW2TR12'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts12'].transpose()
    weights['PW2TR13'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts13'].transpose()
    weights['PW2TR14'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts14'].transpose()
    weights['PW2TR15'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts15'].transpose()
    weights['PW2TR16'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts16'].transpose()
    weights['PW2TR17'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts17'].transpose()
    weights['PW2TR18'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts18'].transpose()
    weights['PW2TR19'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts19'].transpose()
    weights['PW2TR20'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['PW2TRwts20'].transpose()

    # from_sparse_matrix() connector requires pre-ordererd pairs
    weights['TR2PW1'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts1'].transpose()
    weights['TR2PW2'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts2'].transpose()
    weights['TR2PW3'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts3'].transpose()
    weights['TR2PW4'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts4'].transpose()
    weights['TR2PW5'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts5'].transpose()
    weights['TR2PW6'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts6'].transpose()
    weights['TR2PW7'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts7'].transpose()
    weights['TR2PW8'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts8'].transpose()
    weights['TR2PW9'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts9'].transpose()
    weights['TR2PW10'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts10'].transpose()
    weights['TR2PW11'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts11'].transpose()
    weights['TR2PW12'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts12'].transpose()
    weights['TR2PW13'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts13'].transpose()
    weights['TR2PW14'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts14'].transpose()
    weights['TR2PW15'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts15'].transpose()
    weights['TR2PW16'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts16'].transpose()
    weights['TR2PW17'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts17'].transpose()
    weights['TR2PW18'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts18'].transpose()
    weights['TR2PW19'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts19'].transpose()
    weights['TR2PW20'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'TRWeights_original.mat')['TR2PWwts20'].transpose()

    # RotIntWeights
    weights['Rotwts'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'RotIntWeights.mat')['Rotwts']

    # HDWeights.mat
    weights['HD2HD'] = scipy.io.loadmat(ctrl_vars['data_from_training']+'HDWeights.mat')['HD2HDwts']

    # scale values
    H_inhib_phi   = 0.4 # Will be multiplied with Hphi
    BVC_inhib_phi = 0.2
    PR_inhib_phi  = 9.0
    HD_inhib_phi  = 0.4 # Will be multiplied with Hphi
    TR_inhib_phi  = 0.075
    oTR_inhib_phi = 0.1
    PW_inhib_phi  = 0.165
    PR_inhib_phi  = 9.0
    OVC_inhib_phi = 0.7
    oPW_inhib_phi = 0.2
    oPR_inhib_phi = 1.0
    OVC2oPR_inhib_phi = 0.0

    # rescale weights with inhibition
    weights['H2H'] = weights['H2H'] - H_inhib_phi
    weights['BVC2BVC'] = weights['BVC2BVC'] - BVC_inhib_phi
    weights['PR2PR'] = weights['PR2PR'] - PR_inhib_phi
    weights['HD2HD'] = weights['HD2HD'] - HD_inhib_phi 

    return weights

def print_shapes(weight_dict):
    """
    Helper function, shows for all dictionary entries: name and shape.
    """
    for key, value in weight_dict.items():
        print(key, ':', value.shape)

def load_grid_parameters():
    """
    Load scenario parameters.

    Used by:
    
    * visualize.py
    """
    Texture = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['Texture']
    TrainingLoc = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['TrainingLoc']
    VisX = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['VisX']
    VisY = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['VisY']
    maxTrainX = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['maxTrainX']
    maxTrainY = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['maxTrainY']
    minTrainX = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['minTrainX']
    minTrainY = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['minTrainY']
    nTextures = scipy.io.loadmat(ctrl_vars['data_from_training']+'TrainingData_VR_Room_WallsOnly.mat')['nTextures']

    Hres = 0.5
    maxR = 16
    maxX = maxTrainX
    maxY = maxTrainY
    minX = 0
    minY = 0
    polarDistRes = 1.0
    polarAngRes = 2 * np.pi / 51.0
    

    return Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes # Texture, TrainingLoc, VisX, VisY, maxTrainX, maxTrainY, minTrainX, minTrainY, nTextures, 

def load_room_data_for_perception_drive():
    """
    Load room data for perception drive from matlab file.
    """
    BndryPtX = scipy.io.loadmat(ctrl_vars['data_from_training']+'VRroomdataforperceptiondrive.mat')['BndryPtX']
    BndryPtY = scipy.io.loadmat(ctrl_vars['data_from_training']+'VRroomdataforperceptiondrive.mat')['BndryPtY']
    dir = scipy.io.loadmat(ctrl_vars['data_from_training']+'VRroomdataforperceptiondrive.mat')['dir']
    line = scipy.io.loadmat(ctrl_vars['data_from_training']+'VRroomdataforperceptiondrive.mat')['line'][0][0]
    r0 = scipy.io.loadmat(ctrl_vars['data_from_training']+'VRroomdataforperceptiondrive.mat')['r0']

    return BndryPtX, BndryPtY, dir, line, r0

def load_object_attributes(annarInterface):
    """
    Load VR object data from matlab file.
    """
    ObjectAttributes = load_attributes(annarInterface)

    Nobj = 9 #  9 objects in SpaceCog VR but numbering starts with 0, seei-1 below, you C-people ...
    ObjPtX = np.zeros([Nobj, 7])
    ObjPtY = np.zeros([Nobj, 7])
    ObjCenX = np.zeros(Nobj)
    ObjCenY = np.zeros(Nobj)

    for i in range(Nobj):
        CoordsTMP = ObjectAttributes[i]['Coords3D']
        CoordsTMP[0] = CoordsTMP[0] # Using Coords3D

        ObjPtX[i, :] = np.arange(CoordsTMP[0] - 0.3, CoordsTMP[0] + 0.35, 0.1) # make sure the upper end is "... + 0.3"
        ObjCenX[i] = CoordsTMP[0]
        ObjPtY[i, :] = np.arange(CoordsTMP[2] - 0.3, CoordsTMP[2] + 0.35, 0.1) # Using Coords3D
        ObjCenY[i] = CoordsTMP[2]
        #print("DEBUG: Object", i, "is at", CoordsTMP)

    return ObjPtX, ObjPtY, ObjCenX, ObjCenY


def load_obj_data(annarInterface):

    ObjectAttributes = load_attributes(annarInterface)
    data = []

    for i_obj in range(len(ObjectAttributes)):
        obj_dict = dict()

        obj_dict['name'] = ObjectAttributes[i_obj]['name']        
        obj_dict['grid_coords'] = ObjectAttributes[i_obj]['Coords2D']
        obj_dict['coords'] = ObjectAttributes[i_obj]['Coords3D']


        data.append(obj_dict)

    return data