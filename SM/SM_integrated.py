"""
    Part of ANNarchy-SM
    Main script for the integrated SM-model

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

from ANNarchy import *
import sys
from matplotlib import pyplot as plt
from math import fmod, pi, sin, cos, sqrt
from astropy.stats import circmean
from imageio import imread
import time
import timeit
import pickle
import numpy as np
import random
import math
import yaml

sys.path.append('../SM/')
from SM_parameters import ctrl_vars
from SM_PdrivePW_withObj import SM_PdrivePW_withObj
from SM_BoundaryCueing import SM_BoundaryCueing
from SM_updateWTS2 import SM_updateWTS2
from SM_load_mat_files import load_obj_data, load_grid_parameters, print_shapes
from SM_helper_functions import CueHDActivity, CueGridActivityMultiseg
from SM_visualize import compute_coords_HPC, compute_coords_BVC, create_network_figure
from SM_vr_functions import get_agent_pos,  get_image, get_image2, wait_for_finished_walk, wait_for_finished_turn, wait_for_finished_eye_movement, get_and_store_image, transform_SM_to_VR

sys.path.append('../VIS/')
from VIS_ParamVR import ModelParam
from VIS_parameters import params
from VIS_PreprocessingVR import stepV1
from VIS_InitializationVR import initV1

def updateVision(agent_view, popVIS, popLIP):
    # Visual Network
    V1, AuxV1, V4, PFC, FEF, Xh = get_VISLIP_populations(popVIS, popLIP)
    VisualField = agent_view / agent_view.max()
    objV1 = initV1(ModelParam)
    rV1C_Sacc, rV1S_Sacc = stepV1(VisualField, objV1, ModelParam)
    V1.r = np.swapaxes(rV1C_Sacc, 0, 1)

def cueObject(vr_interface, target_coords, target_obj_ID, objPos_deg):
    # agent position
    if vr_interface:
        Xag, Yag, HDag = get_agent_pos(vr_interface, False)
    else:
        Xag, Yag, HDag = target_coords[:3]
        HDag = 2*np.pi - HDag/180*np.pi     
    
    line = ctrl_vars['line']
    r0 = ctrl_vars['r0']
    ObjPtX, ObjPtY = ctrl_vars['ObjPtX'], ctrl_vars['ObjPtY']
    ObjCenX, ObjCenY = ctrl_vars['ObjCenX'], ctrl_vars['ObjCenY']

    CurrObjAllX = np.zeros([7, 1])
    CurrObjAllY = np.zeros([7, 1])

    CurrObjCenX = ObjCenX[target_obj_ID] # center of the object
    CurrObjCenY = ObjCenY[target_obj_ID]
    
    CurrObjDist = np.sqrt((Xag - CurrObjCenX)**2 + (Yag - CurrObjCenY)**2) # use distance from VR coordinates
    CurrObjDist *= 1.5  # Artificially increase distance to make firing rates look nicer in plots

    obj_angle_allo_math = (HDag+ctrl_vars['angle_offset_OVCvsHD']) - (objPos_deg[0] / 180.0 * np.pi)  ### For HDag, "rightwards" is a positive angle; in the visual field, "right" is a negative angle
    ObjCenX_fromModel = Xag + CurrObjDist * np.cos(obj_angle_allo_math)
    ObjCenY_fromModel = Yag + CurrObjDist * np.sin(obj_angle_allo_math)

    CurrObjCenX = ObjCenX_fromModel # Replacing the VR coordinates by the ones from the model
    CurrObjCenY = ObjCenY_fromModel

    CurrObjAllX[:, 0] = np.arange(CurrObjCenX - 0.3, CurrObjCenX + 0.35, 0.1) # extended object
    CurrObjAllY[:, 0] = np.arange(CurrObjCenY - 0.3, CurrObjCenY + 0.35, 0.1) # ensure upper limit reaches ... + 0.3

    # OBJcues is empty if object not in visual field, i.e. it has dropped out
    return SM_PdrivePW_withObj(r0, ctrl_vars['dir'], line, CurrObjAllX, CurrObjAllY,  Xag, Yag, HDag, 0, 1)

def random_coords():
    # Calculate random position within a circle
    circle_r = 1.0
    circle_x = 8.5
    circle_y = 5.0

    alpha = 2 * pi * random.random()
    r = circle_r * sqrt(random.random())
    x = round(r * cos(alpha) + circle_x, 1)
    y = round(r * sin(alpha) + circle_y, 1)
    hd = random.randrange(211, 216) if x > 8.0 else 210
    tilt = -20 if y < 4.5 else -15 # Adjust tilt to ensure objects are in the visual field
    
    coords = [x, y, hd, tilt]

    return coords

def get_SM_populations(populations):
    for pop in populations:
        if pop.name == 'HD':
            HD = pop
        elif pop.name == 'BVC':
            BVC = pop
        elif pop.name == 'PR':
            PR = pop
        elif pop.name == 'oPR':
            oPR = pop
        elif pop.name == 'PW':
            PW = pop
        elif pop.name == 'H':
            H = pop
        elif pop.name == 'TR':
            TR = pop
        elif pop.name == 'IP':
            IP = pop
        elif pop.name == 'oPW':
            oPW = pop
        elif pop.name == 'OVC':
            OVC = pop
        elif pop.name == 'oTR':
            oTR = pop

    return HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR 

def get_VISLIP_populations(popVIS, popLIP):
    for pop in popVIS:
        if pop.name == 'V1':
            V1 = pop
        if pop.name == 'AuxV1':
            AuxV1 = pop
        if pop.name == 'V4L23':
            V4L23 = pop
        if pop.name == 'FEFm':
            FEFm = pop
        if pop.name == 'PFC':
            PFC = pop

    for pop in popLIP:
        if pop.name == 'Xh':
            Xh = pop

    return V1, AuxV1, V4L23, PFC, FEFm, Xh

def get_SM_rates(populations):
    for pop in populations:
        if pop.name == 'HD':
            HD = pop
        elif pop.name == 'BVC':
            BVC = pop
        elif pop.name == 'oPR':
            oPR = pop
        elif pop.name == 'PW':
            PW = pop
        elif pop.name == 'H':
            H = pop
        elif pop.name == 'oPW':
            oPW = pop
        elif pop.name == 'OVC':
            OVC = pop
    
    SM_rates = {
        'PWb': PW.r,
        'PWo': oPW.r,
        'BVC': BVC.r,
        'OVC': OVC.r,
        'HD' : HD.r,
        'PC' : H.r,
        'PRo': oPR.r
    }
    
    return SM_rates

def get_VISLIP_rates(popVIS, popLIP, reset=False):
    for pop in popVIS:
        if pop.name == 'AuxV1':
            AuxV1 = pop
        if pop.name == 'V4L23':
            V4L23 = pop
        if pop.name == 'FEFm':
            FEFm = pop
        if pop.name == 'PFC':
            PFC = pop

    for pop in popLIP:
        if pop.name == 'Xh':
            Xh = pop

    if reset:
        AuxV1.r = 0.0
        V4L23.r = 0.0
        FEFm.r = 0.0
        PFC.r = 0.0
        Xh.r = 0.0
    
    VISLIP_rates = {
        'V1' : AuxV1.r,
        'V4' : V4L23.r,
        'FEF': FEFm.r,
        'PFC': PFC.r,
        'Xh' : Xh.r
    }

    return VISLIP_rates

def get_SM_projections(populations, projections):
    """
    Select the SM-related projections from a list of projections provided in *projections*
    """
    # filter out SM-related populations
    HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR = get_SM_populations(populations)
    # our search targets
    OVC2H = None
    BVC2OVC = None
    oPR2OVC = None
    OVC2oPR = None
    oPR2H = None
    oPR2HD = None
    H2OVC = None
    OVC2BVC = None
    H2oPR = None
    # filter all projections to find targets
    for proj in projections:
        if proj.pre == OVC and proj.post == H:
            OVC2H = proj
        elif proj.pre == BVC and proj.post == OVC:
            BVC2OVC = proj
        elif proj.pre == oPR and proj.post == OVC:
            oPR2OVC = proj
        elif proj.pre == OVC and proj.post == oPR:
            OVC2oPR = proj
        elif proj.pre == oPR and proj.post == H:
            oPR2H = proj
        elif proj.pre == oPR and proj.post == HD:
            oPR2HD = proj
        elif proj.pre == H and proj.post == OVC:
            H2OVC = proj
        elif proj.pre == OVC and proj.post == BVC:
            OVC2BVC = proj
        elif proj.pre == H and proj.post == oPR:
            H2oPR = proj
    return OVC2H, BVC2OVC, oPR2OVC, OVC2oPR, oPR2H, oPR2HD, H2OVC, OVC2BVC, H2oPR

def reset_learned_weights(populations, projections):
    HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR = get_SM_populations(populations) 

    nb_neurons_H    = 1936
    nb_neurons_HD   = 100
    nb_neurons_BVC  = 816
    nb_neurons_oPW  = 816
    nb_neurons_OVC  = 816
    nb_neurons_PR   = 4
    nb_neurons_oPR  = 9

    print("Resetting learned weights!")
    for proj in projections:
        if proj.pre == OVC and proj.post == H:
            proj.w = np.zeros([nb_neurons_H, nb_neurons_OVC]) 
        elif proj.pre == OVC and proj.post == oPR:  
            proj.w = np.zeros([nb_neurons_oPR, nb_neurons_OVC])
        elif proj.pre == oPR and proj.post == H:
            proj.w = np.zeros([nb_neurons_H, nb_neurons_oPR])
        elif proj.pre == oPR and proj.post == HD:
            proj.w = np.zeros([nb_neurons_HD, nb_neurons_oPR])
        elif proj.pre == BVC and proj.post == OVC:
            proj.w = np.zeros([nb_neurons_OVC, nb_neurons_BVC])
        elif proj.pre == H and proj.post == OVC:
            proj.w = np.zeros([nb_neurons_OVC, nb_neurons_H])
        elif proj.pre == oPR and proj.post == OVC:
            proj.w = np.zeros([nb_neurons_OVC, nb_neurons_oPR]) 
        elif proj.pre == H and proj.post == oPR:
            proj.w = np.zeros([nb_neurons_oPR, nb_neurons_H])
        elif proj.pre == HD and proj.post == oPR:
            proj.w = np.zeros([nb_neurons_oPR, nb_neurons_HD])
        elif proj.pre == OVC and proj.post == BVC:
            proj.w = np.zeros([nb_neurons_BVC, nb_neurons_OVC])

    return
   
def SM_1st_step(popSM, projSM, vr_interface, start_position, coords, img_count, replication_path, folder='results', popVIS=None, popLIP=None, create_video=False):
    print("SM_1st_step running ...")
    HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR = get_SM_populations(popSM) 
    
    simulate(core.Global.config['dt'])     

    # enable signals   
    H.use_syninput = True
    BVC.use_syninput = True
    PR.use_syninput = True
    oPR.use_syninput = True
    PW.use_syninput = True
    TR.use_syninput = True
    oPW.use_syninput = True
    OVC.use_syninput = True
    oTR.use_syninput = True

    # get population sizes
    nb_neurons_H = H.size
    nb_neurons_HD = HD.size
    nb_neurons_BVC = BVC.size

    # other veriables
    line = ctrl_vars['line']
    r0 = ctrl_vars['r0']
    ObjPtX, ObjPtY = ctrl_vars['ObjPtX'], ctrl_vars['ObjPtY']
    ObjCenX, ObjCenY = ctrl_vars['ObjCenX'], ctrl_vars['ObjCenY']
    VBX_rt, VBY_rt = ctrl_vars['VBX_rt'], ctrl_vars['VBY_rt']
    BndryPtX, BndryPtY = ctrl_vars['BndryPtX'], ctrl_vars['BndryPtY']
    ObjAttThresh = ctrl_vars['ObjAttThresh']
    ObjEncThresh = ctrl_vars['ObjEncThresh']
    (HX, HY) = compute_coords_HPC(nb_neurons_H) # used for estimating agent & object location
    (BVCX, BVCY) = compute_coords_BVC()
    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()

    if vr_interface:
        Xag, Yag, HDag = get_agent_pos(vr_interface)
        obj_data = load_obj_data(vr_interface)
    else:
        Xag, Yag, HDag = start_position
        obj_data = load_obj_data(None)

    # cue neural activities for start position:
    PW.use_ego_cue_percep = True                 
    (egocues, VBX_rt, VBY_rt, L_r, BX, BY, TX, TY) = SM_PdrivePW_withObj(r0, ctrl_vars['dir'], line, BndryPtX, BndryPtY, Xag, Yag, -HDag, get_current_step(), 0)
    
    PR.cue_percep = SM_BoundaryCueing(VBX_rt, VBY_rt, HDag, Xag, Yag)
    PW.ego_cue_percep = 30 * CueGridActivityMultiseg(0.5, egocues, nb_neurons_BVC)
    HD.cue_init = 40 * CueHDActivity(HDag, nb_neurons_HD)

    if vr_interface:
        agent_view = get_image(vr_interface)
        main_view = get_image2(vr_interface)
        plt.imsave(folder + "rep_main_view.jpg", main_view)
        plt.imsave(folder + "rep_agent_view.jpg", agent_view)
    else:
        agent_view = plt.imread(replication_path + "rep_agent_view.jpg")
        main_view = plt.imread(replication_path + "rep_main_view.jpg")
        plt.imsave(folder + "rep_main_view.jpg", main_view)
        plt.imsave(folder + "rep_agent_view.jpg", agent_view)

    start = timeit.default_timer()
    
    for i in range(1, 601):
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = BVC.Pmod + 0.01
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = min(BVC.Pmod, 1.0)
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = BVC.Imod - 0.01
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = max(BVC.Imod, 0.05)

        simulate(1)

        if i%100 == 0:
            print("Simulating 100 steps took " + str((timeit.default_timer() - start)/(i/100)) + " seconds")
        
        if create_video:
            if (i < 100 and i%2 == 0) or (i > 100 and i < 200 and i%5 == 0) or (i > 200 and i%10 == 0):
                SM_rates = get_SM_rates(popSM)
                VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
                updateVision(agent_view, popVIS, popLIP)
                title = "Initialization phase"
                phase = "encoding"
                create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)

    # Estimate location of agent and object
    (HX, HY) = compute_coords_HPC(nb_neurons_H)
    H_tmp = np.reshape(H.r, (HX.shape[0], HX.shape[1])) 
    X_tmp = np.sum(H_tmp, 0)
    Y_tmp = np.sum(H_tmp, 1)
    
    Xag_imag = (np.where(X_tmp==np.amax(X_tmp))[0][0] * Hres) + 0.25    # Added offset of 0.25 since the H-cells start at (0.25, 0.25)
    Yag_imag = (np.where(Y_tmp==np.amax(Y_tmp))[0][0] * Hres) + 0.25    # Added offset of 0.25 since the H-cells start at (0.25, 0.25)
    
    print("Agent position in the VR: (x,y) = ", Xag, Yag)
    print("Perceived position (amax): (x,y) = ", Xag_imag, Yag_imag)
    
    setting_data = open(folder + "setting_data.txt", "a")
    setting_data.write("1st position: " + str(coords) + "\n")
    setting_data.close()

    print("SM_1st_step done")
    return img_count

def move_to_pos(vr_interface, target_coords):
    """
    walk & turn towards specified coordinates
    """
    print("move to object near", target_coords)

    id = vr_interface.sendAgentMoveTo(target_coords[0], 0.0, target_coords[1], 1)
    wait_for_finished_walk(vr_interface, id, True)
    time.sleep(1)

    agent_pos = get_agent_pos(vr_interface, True)
    Xag, Yag, HDag = get_agent_pos(vr_interface, False)
    print('stopped at:', Xag, Yag, (ctrl_vars['angle_offset_VRvs4B'] - HDag) / np.pi*180)
    
    # Check and wait until Felice is facing in the correct direction (+-1 as a precausion)
    # This should act as a workaround for seldom cases in which she doesn't turn correctly on the first try
    while (agent_pos[4] < (target_coords[2] - 1)) or (agent_pos[4] > (target_coords[2] + 1)):
        delta_angle_deg = target_coords[2] - agent_pos[4]
        if abs(delta_angle_deg) > 180:
            delta_angle_deg = fmod(360 - abs(delta_angle_deg), 360) * (-1)*np.sign(delta_angle_deg)

        id = vr_interface.sendAgentTurn(delta_angle_deg)
        wait_for_finished_turn(vr_interface, id, True)
        time.sleep(3)
        agent_pos = get_agent_pos(vr_interface, True)

def move_to_pos_sync(popSM, vr_interface, target_coords, target_obj_ID, folder, recall_walk=False, objPos_deg=None, popVIS=None, popLIP=None):
    """
    walk & turn towards specified coordinates
    """

    HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR = get_SM_populations(popSM)
    V1, AuxV1, V4, PFC, FEF, Xh = get_VISLIP_populations(popVIS, popLIP)
    
    nb_neurons_H = H.size
    nb_neurons_HD = HD.size
    nb_neurons_BVC = BVC.size
    r0 = ctrl_vars['r0']
    line = ctrl_vars['line']
    VBX_rt, VBY_rt = ctrl_vars['VBX_rt'], ctrl_vars['VBY_rt']
    BndryPtX, BndryPtY = ctrl_vars['BndryPtX'], ctrl_vars['BndryPtY']
    
    phase = "encoding"
    title = "Walking to the target object"
    if target_obj_ID == 5:
        title = "Walking to a different position"
    elif recall_walk:
        title = "Walking back to the recalled position of the green crane"
        phase = "recall"

    print("Move to object near:", target_coords)
    id = vr_interface.sendAgentMoveTo( target_coords[0], 0.0, target_coords[1], 1)

    # Walk a tiny step and then simulate the network and create plot
    simulation_steps = 30
    while True:
        vr_interface.videoSync(True) # This tells the VR to walk a step and then wait until we arrive here in the next iteration of the loop

        avail = vr_interface.checkActionExecState(id)
        while not avail:
            avail = vr_interface.checkActionExecState(id)
        state = vr_interface.getActionExecState()

        if state == 1: # Walk has finished
            break

        Xag, Yag, HDag = get_agent_pos(vr_interface, False)
        print("Xag, Yag, HDag = ", Xag, Yag, HDag)
        agent_view = get_image(vr_interface)
        main_view = get_image2(vr_interface)
        updateVision(agent_view, popVIS, popLIP)
        
        PW.use_ego_cue = False
        PW.use_ego_cue_percep = True
        HD.cue = 60 * CueHDActivity(HDag, nb_neurons_HD)                                  # recalculate correct HD activities
        (egocues, VBX_rt, VBY_rt, L_r, BX, BY, TX, TY) = SM_PdrivePW_withObj(r0, ctrl_vars['dir'], line, BndryPtX, BndryPtY, Xag, Yag, -HDag, get_current_step(), 0)
        PR.cue_percep = SM_BoundaryCueing(VBX_rt, VBY_rt, HDag, Xag, Yag)
        PW.ego_cue_percep = 30 * CueGridActivityMultiseg(0.5, egocues, nb_neurons_BVC)
        
        # TODO Why is this not working when walking to the couch?
        #if recall_walk or target_obj_ID == 5:
        if recall_walk:
            # When we have previously encoded an object, we constantly cue it during locomotion
            [OBJcues, oVBX_rt, oVBY_rt, oL_r, oBX, oBY, oTX, oTY] = cueObject(vr_interface, target_coords, target_obj_ID, objPos_deg)

            if len(OBJcues) > 0:
                oPR.r = oPR.r * 0.0
                oPR[target_obj_ID].r = 1.0
            else:
                oPR.r = oPR.r * 0.0

            oPW.ObjCue_percep = 100 * CueGridActivityMultiseg(0.5, OBJcues, nb_neurons_BVC)
            oPR.oPR_drive = np.ones(9)

        for i in range(simulation_steps):
            oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = BVC.Pmod + 0.01
            oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = min(BVC.Pmod, 1.0)
            oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = BVC.Imod - 0.01
            oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = max(BVC.Imod, 0.05)
            simulate(1)

        if target_obj_ID == 5:
            oPW.r = 0
            OVC.r = 0
        
        SM_rates = get_SM_rates(popSM)
        VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)

    Xag, Yag, HDag = get_agent_pos(vr_interface, False)
    print('stopped at:', Xag, Yag, (ctrl_vars['angle_offset_VRvs4B'] - HDag) / np.pi*180)
    time.sleep(2)
    
    # Send agent turn in steps of 1 degrees for video creation
    agent_pos = get_agent_pos(vr_interface, True)
    delta_angle_deg = target_coords[2] - agent_pos[4]
    if abs(delta_angle_deg) > 180:
        delta_angle_deg = fmod(360 - abs(delta_angle_deg), 360) * (-1)*np.sign(delta_angle_deg)
    
    while abs(delta_angle_deg) > 1:
        id = vr_interface.sendAgentTurn( np.sign(delta_angle_deg) * min(2.0, abs(delta_angle_deg)) )
        wait_for_finished_turn(vr_interface, id, True)

        Xag, Yag, HDag = get_agent_pos(vr_interface, False)
        PW.use_ego_cue = False
        PW.use_ego_cue_percep = True                 

        (egocues, VBX_rt, VBY_rt, L_r, BX, BY, TX, TY) = SM_PdrivePW_withObj(r0, ctrl_vars['dir'], line, BndryPtX, BndryPtY, Xag, Yag, -HDag, get_current_step(), 0)

        PR.cue_percep = SM_BoundaryCueing(VBX_rt, VBY_rt, HDag, Xag, Yag)
        PW.ego_cue_percep = 30 * CueGridActivityMultiseg(0.5, egocues, nb_neurons_BVC)
        HD.cue = 60 * CueHDActivity(HDag, nb_neurons_HD) 

        agent_view = get_image(vr_interface)
        main_view = get_image2(vr_interface)
        updateVision(agent_view, popVIS, popLIP)
        simulate(simulation_steps)
        
        SM_rates = get_SM_rates(popSM)
        VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)

        agent_pos = get_agent_pos(vr_interface, True)
        delta_angle_deg = target_coords[2] - agent_pos[4]
        if abs(delta_angle_deg) > 180:
            delta_angle_deg = fmod(360 - abs(delta_angle_deg), 360) * (-1)*np.sign(delta_angle_deg)

    if abs(target_coords[3]) > 0:
        sacc_sign = int(np.sign(target_coords[3]))
        for i_sacc_step in range(int(abs(target_coords[3]))):
            print("sacc_angle [deg] = ", sacc_sign)
            id = vr_interface.sendEyeMovement( 0, 0, sacc_sign)
            wait_for_finished_eye_movement(vr_interface, id, True)
            
            agent_view = get_image(vr_interface)
            main_view = get_image2(vr_interface)
            updateVision(agent_view, popVIS, popLIP)

            simulate(simulation_steps)
            
            SM_rates = get_SM_rates(popSM)
            VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
            create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)

    # Done turning, update position
    simulate(200)
            
def move_to_pos_and_cue_PW(popSM, vr_interface, target_obj_ID, coords, img_count, folder='results', popVIS=None, popLIP=None, create_video=False, objPos_deg=None):
    print("SM: move to object and cue PW ...")
    HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR = get_SM_populations(popSM) 
    nb_neurons_HD = HD.size
    nb_neurons_BVC = BVC.size     

    if target_obj_ID == 5:
        target_coords = [14.5, 10.0, 70, 0] 
    else:
        target_coords = coords       

    if vr_interface:
        if create_video:
            move_to_pos_sync(popSM, vr_interface, target_coords, target_obj_ID, folder, objPos_deg=objPos_deg, popVIS=popVIS, popLIP=popLIP)
        else:
            move_to_pos(vr_interface, target_coords)

            id = vr_interface.sendEyeMovement( 0, 0, target_coords[3] )
            wait_for_finished_eye_movement(vr_interface, id, True)
            time.sleep(1)
        
        Xag, Yag, HDag = get_agent_pos(vr_interface, False)
        print('stopped at:', Xag, Yag, (ctrl_vars['angle_offset_VRvs4B'] - HDag) / np.pi*180)

    else:
        Xag, Yag, HDag = target_coords[:3]
        HDag = 2*np.pi - HDag/180*np.pi 

    # cue neural activities & start encoding here:
    PW.use_ego_cue_percep = True
    (egocues, VBX_rt, VBY_rt, L_r, BX, BY, TX, TY) = SM_PdrivePW_withObj(ctrl_vars['r0'], ctrl_vars['dir'], ctrl_vars['line'], ctrl_vars['BndryPtX'], ctrl_vars['BndryPtY'], Xag, Yag, -HDag, get_current_step(), 0)
            
    PR.cue_percep = SM_BoundaryCueing(VBX_rt, VBY_rt, HDag, Xag, Yag)
    PW.ego_cue_percep = 30 * CueGridActivityMultiseg(0.5, egocues, nb_neurons_BVC)
    HD.cue = 40 * CueHDActivity(HDag, nb_neurons_HD) 
    HD.cue_init = 0

    return img_count

def cue_object_and_encode(popSM, projSM, vr_interface, target_obj_ID, objPos_deg, target_coords, img_count, replication_path, folder='results', popVIS=None, popLIP=None, create_video=False):
    HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR = get_SM_populations(popSM)
    OVC2H, BVC2OVC, oPR2OVC, OVC2oPR, oPR2H, oPR2HD, H2OVC, OVC2BVC, H2oPR = get_SM_projections(popSM, projSM)

    nb_neurons_OVC = OVC.size
    nb_neurons_H = H.size
    nb_neurons_BVC = BVC.size

    # agent position
    if vr_interface:
        Xag, Yag, HDag = get_agent_pos(vr_interface, False)
    else:
        Xag, Yag, HDag = target_coords[:3]
        HDag = 2*np.pi - HDag/180*np.pi     

    # Cue the object
    ObjEncoded = ctrl_vars['ObjEncoded']
    [OBJcues, oVBX_rt, oVBY_rt, oL_r, oBX, oBY, oTX, oTY] = cueObject(vr_interface, target_coords, target_obj_ID, objPos_deg)
    
    if len(OBJcues) > 0:
        oPR.r = oPR.r * 0.0
        oPR[target_obj_ID].r = 1.0
    else:
        oPR.r = oPR.r * 0.0

    oPW.ObjCue_percep = 100 * CueGridActivityMultiseg(0.5, OBJcues, nb_neurons_BVC)
    oPR.oPR_drive = np.ones(9)

    if vr_interface:
        agent_view = get_image(vr_interface)
        main_view = get_image2(vr_interface)
        plt.imsave(folder + "rep_main_view_encoding.jpg", main_view)
        plt.imsave(folder + "rep_agent_view_encoding.jpg", agent_view)
    else:
        # TODO: Has to be loaded from individual simulation data
        agent_view = plt.imread(replication_path + "rep_agent_view_encoding.jpg")
        main_view = plt.imread(replication_path + "rep_main_view_encoding.jpg")
        plt.imsave(folder + "rep_main_view_encoding.jpg", main_view)
        plt.imsave(folder + "rep_agent_view_encoding.jpg", agent_view)

    start = timeit.default_timer()
    for i in range(1, 601):
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = BVC.Pmod + 0.01
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = min(BVC.Pmod, 1.0)
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = BVC.Imod - 0.01
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = max(BVC.Imod, 0.05)

        if i == 300:
            HD.cue = 0
        
        simulate(1)

        if i%100 == 0:
            print("Simulating 100 steps took " + str((timeit.default_timer() - start)/(i/100)) + " seconds")
        if (create_video and ((i < 100 and i%2 == 0) or (i > 100 and i < 200 and i%5 == 0) or (i > 200 and i%10 == 0))) or (not create_video and i%600 == 0):
            SM_rates = get_SM_rates(popSM)
            VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
            vr_objects = {0 : "yellow crane",
                          1 : "green crane",
                          2 : "green racecar"}
            title = f"Found the {vr_objects[target_obj_ID]}, encode it into memory"
            phase = "encodingText"
            agent_view = plt.imread(folder + "VisualField_pos_plot.png")
            create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)
        
    if create_video:
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)

    # weight update:
    oPR[target_obj_ID].r = 1.0       # object recognition at end of cylce
    if ObjEncoded[target_obj_ID]==0:
        SM_updateWTS2(HD.r, OVC.r, H.r, BVC.r, oPR.r, H2OVC, OVC2H, OVC2BVC, BVC2OVC, oPR2OVC, OVC2oPR, oPR2H, oPR2HD, H2oPR, get_current_step(), 1.0)
        ObjEncoded[target_obj_ID] = 1

    # Saving agent & object position to file:
    (BVCX, BVCY) = compute_coords_BVC()
    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()

    oPW_tmp = np.reshape(oPW.r, (BVCX.shape[0], BVCX.shape[1]))
    R_tmp_oPW = np.sum(oPW_tmp, 0)
    TH_tmp_oPW = np.sum(oPW_tmp, 1)
    Robj_oPW = np.where(R_tmp_oPW==np.amax(R_tmp_oPW))[0][0] * polarDistRes
    THobj_oPW = ctrl_vars['angle_offset_VRvs4B']  - (np.where(TH_tmp_oPW==np.amax(TH_tmp_oPW))[0][0] * polarAngRes - ctrl_vars['angle_offset_OVCvsHD'])
    
    THobj_oPW_VRdeg = fmod(THobj_oPW / pi * 180.0, 360.0)
    THobj_oPW_VRdeg2 = np.average(np.arange(0, 51, 1), weights = TH_tmp_oPW)  #Testing weighted average solution

    # Estimate location of agent and object
    (HX, HY) = compute_coords_HPC(nb_neurons_H)
    H_tmp = np.reshape(H.r, (HX.shape[0], HX.shape[1])) 
    X_tmp = np.sum(H_tmp, 0)
    Y_tmp = np.sum(H_tmp, 1)
    
    # Weighted average to calculate the position of the agent instead of a hard max of a single H-cell 
    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()
    NHx = round((float(maxX) - float(minX)) / float(Hres))
    NHy = round((float(maxY) - float(minY)) / float(Hres))
    
    Xag_imag_weighted = np.average(np.arange(minX + Hres/2.0, minX + (NHx - 0.5 + 1) * Hres, Hres), weights = X_tmp) # Added offset of 0.25 since the H-cells start at (0.25, 0.25)
    Yag_imag_weighted = np.average(np.arange(minX + Hres/2.0, minX + (NHy - 0.5 + 1) * Hres, Hres), weights = Y_tmp) # Added offset of 0.25 since the H-cells start at (0.25, 0.25)
    print("Perceived pos: (x,y) = ", Xag_imag_weighted, Yag_imag_weighted)

    # !!!!!!! Attention 
    # at the end of the trial, we need to "reset" eyes
    if vr_interface:
        id = vr_interface.sendEyeMovement( 0, 0, -target_coords[3] )
        wait_for_finished_eye_movement(vr_interface, id, True)
        time.sleep(1)

        V1, AuxV1, V4, PFC, FEF, Xh = get_VISLIP_populations(popVIS, popLIP)
        PFC.r = 0
        oPR.percep_flag = 0
        oPW.r = 0
        OVC.r = 0

    return img_count

def recall_object(popSM, projSM, vr_interface, target_obj_ID, target_coords, objPos_deg, img_count, replication_path, folder='results', popVIS=None, popLIP=None, create_video=False):
    HD, BVC, PR, oPR, PW, H, TR, IP, oPW, OVC, oTR = get_SM_populations(popSM)

    nb_neurons_H = H.size
    nb_neurons_HD = HD.size
    nb_neurons_BVC = BVC.size

    (HX, HY) = compute_coords_HPC(nb_neurons_H) # used for estimating agent & object location
    (BVCX, BVCY) = compute_coords_BVC()
    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()

    # Encode current position before recall, without cueing and oPR
    oPR.r    = oPR.r * 0.0
    oPW.ObjCue_percep = 0.0 * oPW.ObjCue_percep

    if vr_interface:
        agent_view = get_image(vr_interface)
        main_view = get_image2(vr_interface)
        plt.imsave(folder + "rep_main_view_remote.jpg", main_view)
        plt.imsave(folder + "rep_agent_view_remote.jpg", agent_view)
    else:
        agent_view = plt.imread(replication_path + "rep_agent_view_remote.jpg")
        main_view = plt.imread(replication_path + "rep_main_view_remote.jpg")
        plt.imsave(folder + "rep_main_view_remote.jpg", main_view)
        plt.imsave(folder + "rep_agent_view_remote.jpg", agent_view)

    start = timeit.default_timer()
    for i in range(1, 601):  
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = BVC.Pmod + 0.01
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = min(BVC.Pmod, 1.0)
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = BVC.Imod - 0.01
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = max(BVC.Imod, 0.05)

        if i == 300:
            HD.cue = 0

        simulate(1)

        if i%100 == 0:
            print("Simulating 100 steps took " + str((timeit.default_timer() - start)/(i/100)) + " seconds")
        if create_video and i == 600:
            SM_rates = get_SM_rates(popSM)
            VISLIP_rates = get_VISLIP_rates(popVIS, popLIP, reset=True)      
            title = "Arrived at a different position"
            phase = "encoding"
            create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)

    print('\nrecall object', target_obj_ID)

    if vr_interface:
        Xag, Yag, HDag = get_agent_pos(vr_interface, False)
    else:
        Xag, Yag, HDag, tilt = target_coords
        HDag = 2*np.pi - HDag/180*np.pi  
    
    old_HD = HDag # remember HD for reset later

    PW.use_ego_cue_percep = False
    HD.percep_flag = 0
    HD.imag_flag = 1
    
    oPR.recallobj = 1

    ObjInd = target_obj_ID # for current use with "single" objects

    oPR.Cue = np.zeros(9)
    oPR[ObjInd].Cue = 160.0

    # For the plot
    vr_objects = {0 : "yellow crane",
                          1 : "green crane",
                          2 : "green racecar"}
    title = f"Recall target: Where is my {vr_objects[target_obj_ID]}?"
    phase = "recallText"
    if create_video:
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)

    # Generate recall network activity
    start = timeit.default_timer()
    for i in range(1, 601):
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = BVC.Imod + 0.01
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = min(BVC.Imod, 1.0)
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = BVC.Pmod - 0.01
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = max(BVC.Pmod, 0.05)

        simulate(1)

        if i%100 == 0:
            print("Simulating 100 steps took " + str((timeit.default_timer() - start)/(i/100)) + " seconds")
        
        if (create_video and ((i < 100 and i%2 == 0) or (i > 100 and i%5 == 0))) or (not create_video and i%600 == 0):
            SM_rates = get_SM_rates(popSM)
            VISLIP_rates = get_VISLIP_rates(popVIS, popLIP, reset=True)
            create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)
    
    if create_video:
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)
    
    # estimate HD from population
    popmax = np.where(HD.r==np.amax(HD.r))[0][0] # np.where returns a list of indices
    HDestim = fmod(float(popmax + 1) * 2.0 * pi / 100.0, 2.0 * pi)  # "+ 1" for consistency with Matlab indexing
    
    # Estimate agent location and object location
    H_tmp = np.reshape(H.r, (HX.shape[0], HX.shape[1])) 
    X_tmp = np.sum(H_tmp, 0)
    Y_tmp = np.sum(H_tmp, 1)
    
    # Weighted average to calculate the position of the agent instead of a hard max of a single H-cell, needs further testing (maybe just take some neurons around max?)
    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()
    NHx = round((float(maxX) - float(minX)) / float(Hres))
    NHy = round((float(maxY) - float(minY)) / float(Hres))
    
    Xag_imag_weighted = np.average(np.arange(minX + Hres/2.0, minX + (NHx - 0.5 + 1) * Hres, Hres), weights = X_tmp)
    Yag_imag_weighted = np.average(np.arange(minX + Hres/2.0, minX + (NHy - 0.5 + 1) * Hres, Hres), weights = Y_tmp)

    oPW_tmp = np.reshape(oPW.r, (BVCX.shape[0], BVCX.shape[1]))
    Robj = np.sum(oPW_tmp, 0)
    TH_tmp_oPW = np.sum(oPW_tmp, 1)
    
    Robj_imag_average = np.average(np.arange(0, 16, 1), weights = Robj)
    Obj_average = math.degrees(circmean(np.arange(1, 52, 1)*7.2/180*np.pi, weights=TH_tmp_oPW))
    THobj_imag_average = 90 - Obj_average

    print("Estimateed agent pos: (x,y) = ", Xag_imag_weighted, Yag_imag_weighted)
    print("Estimated agent head direction in deg. [0 = N, 90 = E]: HD = ", (ctrl_vars['angle_offset_VRvs4B'] - HDestim) / np.pi * 180)
    print("Estimated egocentric object position (from oPW) (distance, angle) = ", Robj_imag_average, THobj_imag_average) 
     
    # Re-establish perceptual mode
    print("re-establish perceptual mode")

    PW.use_ego_cue_percep = True
    HD.percep_flag = 1
    HD.imag_flag = 0
 
    oPR.recallobj = 0
    oPR.Cue = 0 * oPR.Cue
    HDag = old_HD                                      # reinstate old HD
    HD.cue = 60 * CueHDActivity(old_HD, nb_neurons_HD) # recalculate correct HD activities

    # Cue boundaries
    (egocues, VBX_rt, VBY_rt, L_r, BX, BY, TX, TY) = SM_PdrivePW_withObj(ctrl_vars['r0'], ctrl_vars['dir'], ctrl_vars['line'], ctrl_vars['BndryPtX'], ctrl_vars['BndryPtY'], Xag, Yag, -HDag, get_current_step(), 0)
    PR.cue_percep = SM_BoundaryCueing(VBX_rt, VBY_rt, HDag, Xag, Yag)
    PW.ego_cue_percep = 30 * CueGridActivityMultiseg(0.5, egocues, nb_neurons_BVC)

    # For the plot
    title = "Re-establish bottom-up representation based on perception"
    phase = "recall"
    if create_video:
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)
    
    # Simulate network
    start = timeit.default_timer()
    for i in range(1, 601):     
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = BVC.Pmod + 0.01
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = min(BVC.Pmod, 1.0)
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = BVC.Imod - 0.01
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = max(BVC.Imod, 0.05)

        if i == 300:
            HD.cue = 0.0

        simulate(1)

        if i%100 == 0:
            print("Simulating 100 steps took " + str((timeit.default_timer() - start)/(i/100)) + " seconds")
        if create_video and ((i < 100 and i%2 == 0) or (i > 100 and i%5 == 0)):
            SM_rates = get_SM_rates(popSM)
            VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
            create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)
    
    if create_video:
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)
    
    target_x, target_y = transform_SM_to_VR(Xag_imag_weighted, Yag_imag_weighted)
    target_VRangle_deg = (ctrl_vars['angle_offset_VRvs4B'] - HDestim) / np.pi * 180
    target_coords_recall = [target_x, target_y, target_VRangle_deg, target_coords[3]]  # target_coords[3] is head tilt, which is hardcoded
    
    # Logging
    setting_data = open(folder + "setting_data.txt", "a")
    setting_data.write("2nd position: " + str(target_coords_recall) + "\n")
    setting_data.close()

    # Move back to the table
    if vr_interface:
        if create_video:
            move_to_pos_sync(popSM, vr_interface, target_coords_recall, target_obj_ID, folder, recall_walk =True, objPos_deg=objPos_deg, popVIS=popVIS, popLIP=popLIP)
        else:
            move_to_pos(vr_interface, target_coords_recall)

            id = vr_interface.sendEyeMovement( 0, 0, target_coords[3] )
            wait_for_finished_eye_movement(vr_interface, id, True)
            time.sleep(1)
    
    if vr_interface:
        Xag, Yag, HDag = get_agent_pos(vr_interface, False)
    else:
        Xag, Yag, HDag = target_coords_recall[:3]
        HDag = 2*np.pi - HDag/180*np.pi  
    
    # Cue boundaries
    (egocues, VBX_rt, VBY_rt, L_r, BX, BY, TX, TY) = SM_PdrivePW_withObj(ctrl_vars['r0'], ctrl_vars['dir'], ctrl_vars['line'], ctrl_vars['BndryPtX'], ctrl_vars['BndryPtY'], Xag, Yag, -HDag, get_current_step(), 0)
    PR.cue_percep = SM_BoundaryCueing(VBX_rt, VBY_rt, HDag, Xag, Yag)
    PW.ego_cue_percep = 30 * CueGridActivityMultiseg(0.5, egocues, nb_neurons_BVC)
    HD.cue = 40 * CueHDActivity(HDag, nb_neurons_HD) 

    # Cue object
    [OBJcues, oVBX_rt, oVBY_rt, oL_r, oBX, oBY, oTX, oTY] = cueObject(vr_interface, target_coords_recall, target_obj_ID, objPos_deg)

    if len(OBJcues) > 0:
        oPR.r = oPR.r * 0.0
        oPR[target_obj_ID].r = 1.0
    else:
        oPR.r = oPR.r * 0.0

    oPW.ObjCue_percep = 100 * CueGridActivityMultiseg(0.5, OBJcues, nb_neurons_BVC)
    oPR.oPR_drive = np.ones(9)
    
    # Get visual data
    if vr_interface:
        agent_view = get_image(vr_interface)
        main_view = get_image2(vr_interface)
        plt.imsave(folder + "rep_main_view_recall.jpg", main_view)
        plt.imsave(folder + "rep_agent_view_recall.jpg", agent_view)
    else:
        agent_view = plt.imread(replication_path + "rep_agent_view_recall.jpg")
        main_view = plt.imread(replication_path + "rep_main_view_recall.jpg")
        plt.imsave(folder + "rep_main_view_recall.jpg", main_view)
        plt.imsave(folder + "rep_agent_view_recall.jpg", agent_view)
  
    # Simulate the network
    start = timeit.default_timer()
    for i in range(1, 601):
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = BVC.Pmod + 0.01
        oTR.Pmod = OVC.Pmod = oPW.Pmod = PW.Pmod = TR.Pmod = PR.Pmod = H.Pmod = BVC.Pmod = min(BVC.Pmod, 1.0)
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = BVC.Imod - 0.01
        oTR.Imod = OVC.Imod = oPW.Imod = PW.Imod = TR.Imod = PR.Imod = H.Imod = BVC.Imod = max(BVC.Imod, 0.05)

        if i == 300:
            HD.cue = 0.0

        simulate(1)

        if create_video and i%600 == 0:
            print("Simulating 100 steps took " + str((timeit.default_timer() - start)/(i/100)) + " seconds")

            SM_rates = get_SM_rates(popSM)
            VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
            vr_objects = {0 : "yellow crane",
                          1 : "green crane",
                          2 : "green racecar"}
            title = f"Returned to the {vr_objects[target_obj_ID]}"
            phase = "recall"
            create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)
    
    return img_count, Xag_imag_weighted, Yag_imag_weighted, HDestim, THobj_imag_average