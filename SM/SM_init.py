"""
    part of ANNarchy-SM
    This script contains necessary initialization of the model.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import sys

sys.path.append('../SM/')
from SM_helper_functions import CueHDActivity, CueGridActivityMultiseg
from SM_vr_functions import get_agent_pos
from SM_load_mat_files import load_room_data_for_perception_drive, load_object_attributes

from SM_network import *
from SM_parameters import ctrl_vars
from SM_PdrivePW_withObj import SM_PdrivePW_withObj

import scipy.io as sio

import time

def initialize_combined(vr_interface, vr_data):
    """
    Initialize variables, load external data for the integrated version of the SM model

    *parameters*

    vr_interface: interface to the VR library    
    """
           
    # update initial positions with VR coordinates
    if vr_interface:
        Xag, Yag, HDag = get_agent_pos(vr_interface)
    else:
        Xag, Yag, HDag = vr_data

    ctrl_vars['Xag'] = Xag
    ctrl_vars['Yag'] = Yag
    ctrl_vars['HDag'] = HDag
    print("Initial position: ", Xag, Yag)

    # initialize PW cuing / perceptual drive
    ctrl_vars['BndryPtX'], \
    ctrl_vars['BndryPtY'], \
    ctrl_vars['dir'], \
    ctrl_vars['line'], \
    ctrl_vars['r0'] = load_room_data_for_perception_drive()    

    # determine cue for entire field of view, do this also during navi
    (ctrl_vars['egocues'], \
    ctrl_vars['VBX_rt'], \
    ctrl_vars['VBY_rt'], \
    ctrl_vars['L_r'],
    ctrl_vars['BX'],
    ctrl_vars['BY'],
    ctrl_vars['TX'],
    ctrl_vars['TY']) = SM_PdrivePW_withObj(ctrl_vars['r0'], \
                                     ctrl_vars['dir'], \
                                     ctrl_vars['line'], \
                                     ctrl_vars['BndryPtX'], \
                                     ctrl_vars['BndryPtY'], \
                                     ctrl_vars['Xag'], \
                                     ctrl_vars['Yag'], \
                                     ctrl_vars['HDag'], 0, 0)

    # load attributes for object cueing  
    if vr_interface:
        ctrl_vars['ObjPtX'], \
        ctrl_vars['ObjPtY'], \
        ctrl_vars['ObjCenX'], \
        ctrl_vars['ObjCenY'] = load_object_attributes(vr_interface)
    else:
        ctrl_vars['ObjPtX'], \
        ctrl_vars['ObjPtY'], \
        ctrl_vars['ObjCenX'], \
        ctrl_vars['ObjCenY'] = load_object_attributes(None)

    ctrl_vars['ObjEncoded'] = np.zeros(ctrl_vars['Nobj'])   # NEW: keeping track of which object has been encoded. We only encode an object once (this more realistic), 
                                                            # but if for some reason we want to re-encode it (e.g. if it changed position becasue we carried it across the room) 
                                                            # we can simply set the flag in of this object in the present array to 0 and the SM will reencode it.

    (ctrl_vars['OBJcues'], \
    ctrl_vars['VBX_rt'], \
    ctrl_vars['VBY_rt'], \
    ctrl_vars['L_r'],
    ctrl_vars['BX'],
    ctrl_vars['BY'],
    ctrl_vars['TX'],
    ctrl_vars['TY']) = SM_PdrivePW_withObj(ctrl_vars['r0'], \
                                     ctrl_vars['dir'], \
                                     ctrl_vars['line'], \
                                     ctrl_vars['ObjPtX'], \
                                     ctrl_vars['ObjPtY'], \
                                     ctrl_vars['Xag'], \
                                     ctrl_vars['Yag'], \
                                     ctrl_vars['HDag'], 0, 1)


    # calculate the current to be injected into the various neuron populations
    # (EgoCue for PW, HDcue for HDCs, PRcue for perirhinal)
    # see the "helper_functions.py" for the comments
    PW.use_ego_cue = True # (ctrl_vars['DWELL'] > step)
    PW.ego_cue = 40 * CueGridActivityMultiseg(0.5, ctrl_vars['egocues'], nb_neurons_BVC)
    
    HD.cue = 0
    HD.cue_init = 40 * CueHDActivity(ctrl_vars['HDag'], nb_neurons_HD)
    
    oPW.ObjCue_percep = 0
    H.I_comp = 0.0

    HD.CWturn = 0                                                      # clockwise or
    HD.CCWturn= 0                                                      # counterclockwise

    # disable "inputs"
    H.use_syninput = False
    BVC.use_syninput = False
    PR.use_syninput = False
    oPR.use_syninput = False
    PW.use_syninput = False
    TR.use_syninput = False
    oPW.use_syninput = False
    OVC.use_syninput = False
    oTR.use_syninput = False