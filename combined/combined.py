# -*- coding: utf-8 -*-
"""
This script contains the main function to run the model.
It combines the ANNarchy-Python models of LIP, VIS, and SM as defined in:
    - LIP/LIP_network.py
    - VIS/VIS_Network.py
    - SM/SM_neuron_model.py

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import sys
import os
import time
import timeit
import yaml
import numpy as np
import linecache
import ANNarchy as ANN
import matplotlib.font_manager as fm
from PIL import Image, ImageFont, ImageDraw
from datetime import date
from scipy.io import savemat
from PIL import Image
from random import randint
from matplotlib import pyplot as plt

from combinedHelper import read_positions, read_objects, create_video, label_VFs
from combinedVIS_LIP import getObjectPos, executeSaccade

sys.path.append('../LIP/')
from LIP_parameters import defParams

if defParams['save_connections']:
    from combinedNet import *
else:
    from combinedNet_loadConn import *

sys.path.append('../SM/')
from SM_init import initialize_combined
from SM_integrated import SM_1st_step, move_to_pos_and_cue_PW, cue_object_and_encode, recall_object, show_saccade_in_VR, calculate_coords, reset_learned_weights

sys.path.append('../VIS/')
from VIS_MainHelperVR import ReadImageFromVR, ProgramEnd
from VIS_VisualVR import Highlight
from VIS_ParamVR import ModelParam

First_Start = timeit.default_timer()

# Initialize parameters from config (see the config.yaml for details)
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

Remote_Desktop =  config['RemoteDesktop']
record_encoding = config['record_encoding']
record_recall =   config['record_recall']
record_SM =       config['record_SM']

Experiment =      config['Experiment']
N_simulations =   config['N_simulations']

VR_IP_ADDRESS =   config['VR_IP_ADDRESS']
VR_UNITY_PORT =   config['VR_UNITY_PORT']
VR_AGENT_NO =     config['VR_AGENT_NO']

if Remote_Desktop:
    sys.path.append('../UnityVR/newAgentBrain/')
    import newAnn4Interface


####################################################################################################
####################################################################################################
# Main program
if __name__ == "__main__":
    
    import SM_network
    ANN.compile() # compile network
    #ANN.report(filename="model_description.tex") # create model description report (as .tex file)

    # if we calculated new projections, we save them for future simulations
    if defParams['save_connections']:
        print("save connections")
        saveDirConn = defParams['saveConnAt'] + '/'
        if not os.path.exists(saveDirConn):
            os.makedirs(saveDirConn)
        for proj in projLIP_Net.union(projLIP_VIS):
            projName = proj.pre.name + '-' + proj.post.name + '-' + proj.target
            print(" - save", projName)
            proj.save_connectivity(filename=saveDirConn+projName+'.data')

    # Network interface setup
    if Remote_Desktop:
        annarInterface = newAnn4Interface.Annar4Interface(VR_IP_ADDRESS, VR_UNITY_PORT, 0, False)
        annarInterface.start()
        annarInterface.sendEnvironmentReset(3)
    else:
        annarInterface = None

    # Main simuation loop
    for sim in range(N_simulations):
        # Create result directories
        ModelParam['ResultDir'] = 'Results/Results_%s_%s/' % (date.today(), time.asctime(time.localtime(time.time())).split()[3])
        
        if not os.path.isdir(ModelParam['ResultDir']):
            os.makedirs(ModelParam['ResultDir'])

        # VR scenario data
        vr_objects = {
        0 : "yellow crane",
        1 : "green crane",
        2 : "green racecar"
        }

        if config['SET_TARGET']:
            targetID = config['TARGET']
        else:
            targetID = randint(0,2)
        
        # Get position to walk to
        target_position = calculate_coords()   

        # Simulation with left side neglect
        if defParams['neglect']:
            print("Left side neglect in Xh!")
            targetID = 1

        # If we do not use Unity, we need to get data from pre-saved simulations
        if not Remote_Desktop:
            print("Replicate simulation", config['replication_number'], "- Experiment", config['replication_experiment'])
            Experiment = config['replication_experiment']
            replication_path = "Results/Exp" + str(config['replication_experiment']) + "/Simulation_" + str(config['replication_number'])
            targetID = int(linecache.getline(replication_path + '/setting_data.txt', 1)[10:11])
            
            target_position = linecache.getline(replication_path + '/setting_data.txt', 2)[15:-2].split(", ")
            target_position = [float(i) for i in target_position]
        else:
            replication_path = None

        print("Target object:", vr_objects[targetID])

        setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
        setting_data.write("Encoding: " + str(targetID) + ", " + str(vr_objects[targetID]) + "\n")
        setting_data.close()

        ##################################
        ####    START of simulation   ####
        ################################## 
        
        #### 1. walk to target object ####
        img_count = 0
        print(Highlight('STEP 1: walk to target object', 'Yellow', Bold=True))
        # involved networks: SM
        # --> deactivate LIP, VIS  and connection between them
        deactivatedPop = ''
        for pop in popLIP_Net | popVISNet:
            deactivatedPop += pop.name + '   '
            pop.disable()

        deactivatedProj = ''
        for proj in projLIP_Net | projVISNet | projLIP_VIS:
            deactivatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
            proj.transmission = False

        # Initializations for SM
        start_position = [8.0,17.0,np.pi] # starting position of the agent (only used when simulating without VR). if you cange this, it needs to be changed in the VR aswell!
        initialize_combined(annarInterface, start_position)
        
        # record firing rates
        if record_SM:
            monitors_SM = {'HD': ANN.Monitor(SM.HD, 'r'),
                        'IP': ANN.Monitor(SM.IP, 'r'),
                        'H': ANN.Monitor(SM.H, 'r'),
                        'BVC': ANN.Monitor(SM.BVC, 'r'),
                        'PR': ANN.Monitor(SM.PR, 'r'),
                        'oPR': ANN.Monitor(SM.oPR, 'r'),
                        'PW': ANN.Monitor(SM.PW, 'r'),
                        'oPW': ANN.Monitor(SM.oPW, 'r'),
                        'OVC': ANN.Monitor(SM.OVC, 'r'),
                        'TR': ANN.Monitor(SM.TR, 'r'),
                        'oTR': ANN.Monitor(SM.oTR, 'r')
                        }

        # Reset learned weights if we have previously performed a simulation
        if sim > 0:
            reset_learned_weights(popSM, projSM)

        # First SM step, then move to the object and cue the PW
        img_count = SM_1st_step(popSM, projSM, annarInterface, start_position, target_position, img_count, replication_path, ModelParam['ResultDir'])
        img_count = move_to_pos_and_cue_PW(popSM, annarInterface, targetID, target_position, img_count)

        #### 2. get position of target object ####
        print(Highlight('STEP 2: get position of target object', 'Yellow', Bold=True))
        # involved networks: VIS , LIP
        # --> activate LIP, VIS  and connection between them
        # --> deactivate SM
        activatedPop = ''
        for pop in popLIP_Net | popVISNet:
            activatedPop += pop.name + '   '
            pop.enable()

        activatedProj = ''
        for proj in projLIP_Net | projVISNet | projLIP_VIS:
            activatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
            proj.transmission = True

        deactivatedPop = ''
        for pop in popSM:
            deactivatedPop += pop.name + '   '
            pop.disable()

        deactivatedProj = ''
        for proj in projSM:
            deactivatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
            proj.transmission = False

        # record firing rates
        if record_encoding:
            monitors = {
                    'V1': ANN.Monitor(VIS.V1, 'r'),
                    'HVA4': ANN.Monitor(VIS.V4L4, 'r'),
                    'HVA23': ANN.Monitor(VIS.V4L23, 'r'),
                    'FEFv': ANN.Monitor(VIS.FEFv, ['r', 'ALIP']),
                    'FEFm': ANN.Monitor(VIS.FEFm, 'r'),
                    'Xh': ANN.Monitor(LIP_.Xh_Pop, 'r'),
                    'LIP_EP': ANN.Monitor(LIP_.LIP_EP_Pop, 'r'),
                    'LIP_CD': ANN.Monitor(LIP_.LIP_CD_Pop, 'r')
                    }

        # get VISual field
        if Remote_Desktop:
            VisualField = ReadImageFromVR(annarInterface)
            VisualField = VisualField / VisualField.max()
            plt.imsave(ModelParam['ResultDir'] + "VisualField_encoding.png", VisualField)
        else:
            Img = Image.open(replication_path + "/VisualField_encoding.png")
            Img_arr = np.asarray(Img) / 255.
            VisualField = Img_arr[:,:,:3] / Img_arr.max()
            plt.imsave(ModelParam['ResultDir'] + "VisualField_encoding.png", VisualField)

        if VisualField.shape[0] != ModelParam['resIm'][1] or VisualField.shape[1] != ModelParam['resIm'][0] or VisualField.shape[2] != ModelParam['resIm'][2]:
            print(Highlight('\nError: The resolution of the VISual field should be ' + str(ModelParam['resIm']), 'Red', Bold=True))
            ModelParam['Make_Movie'] = False # Don't make a movie in ProgramEnd()
            ProgramEnd(First_Start)
            exit(1)

        # get head-centered object position in degree and (width, height)
        ModelParam['OutputFileName'] += 'encode_'
        objPos_deg = getObjectPos(targetID, VisualField, popLIP_Net | popVISNet, projLIP_Net | projVISNet | projLIP_VIS, annarInterface, Experiment)
        print("Target object at", objPos_deg, "[deg] (care: head centered coordinates!)")

        # save firing rates
        if record_encoding:
            print("save firing rates as mat file")
            recorded_rates = {}
            for layer in monitors:
                recorded_rates[layer] = monitors[layer].get(['r'], reshape=True)

            recorded_rates['FEFv_ALIP'] = monitors['FEFv'].get('ALIP', reshape=True)

            savemat(ModelParam['ResultDir'] + 'rates_encoding.mat', recorded_rates)
            create_video(ModelParam['ResultDir'], Experiment, vr_objects[targetID], 0, -1)

        if Experiment == 4:
            print("Simulation with neglect, quit after encoding")
            if Remote_Desktop:
                annarInterface.stop(True)
            quit() 
        
        #### 3. encode target object ####
        print(Highlight('STEP 3: encode target object', 'Yellow', Bold=True))
        # involved networks: SM
        # --> reactivate SM
        # --> deactivate LIP, VIS  and connection between them
        activatedPop = ''
        for pop in popSM:
            activatedPop += pop.name + '   '
            pop.enable()

        activatedProj = ''
        for proj in projSM:
            activatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
            proj.transmission = True

        deactivatedPop = ''
        for pop in popLIP_Net | popVISNet:
            deactivatedPop += pop.name + '   '
            pop.disable()

        deactivatedProj = ''
        for proj in projLIP_Net | projVISNet | projLIP_VIS:
            deactivatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
            proj.transmission = False
        
        img_count = cue_object_and_encode(popSM, projSM, annarInterface, targetID, objPos_deg, target_position, img_count, replication_path, ModelParam['ResultDir'])

        #### 4. walk to different position (door, ...) ####
        print(Highlight('STEP 4: walk to different position', 'Yellow', Bold=True))
        # involved networks: SM

        walkToID = 5 # originally was the position of the red pencil, now hardcoded to be the sofa in SM_integrated
        img_count = move_to_pos_and_cue_PW(popSM, annarInterface, walkToID, target_position, img_count)

        #### 5. recall target object ####
        print(Highlight('STEP 5: recall and walk to target object', 'Yellow', Bold=True))
        # involved networks: SM

        walkTo_position = [14.5, 10.0, 70, target_position[3]] # position of couch, we need to add original head tilt, as it can't be decoded from PW
        img_count, Xag_imag, Yag_imag, HDestim, THobj_imag_oPW_VRdeg = recall_object(popSM, projSM, annarInterface, targetID, walkTo_position, img_count, replication_path,  ModelParam['ResultDir'])
        print('Recall: ', HDestim, THobj_imag_oPW_VRdeg)

        # We only take the decoded horizontal information from the SM model, as it does not include vertical information
        if THobj_imag_oPW_VRdeg > 50.0:
            counter_angle = -(360.0-THobj_imag_oPW_VRdeg)
            if counter_angle < -50.0:
                print('The angle exceeded FoV -50. .. 50.0')
                objPos_deg_recall = objPos_deg
            objPos_deg_recall = [counter_angle, objPos_deg[1]]
        elif THobj_imag_oPW_VRdeg > -50.0:
            # [ -50 .. 50 ] everything is fine
            objPos_deg_recall = [THobj_imag_oPW_VRdeg, objPos_deg[1]]
        else:
            print('TODO:')
            objPos_deg_recall = [THobj_imag_oPW_VRdeg, objPos_deg[1]]

        if record_SM:
            print("save SM firing rates as mat file:")
            recorded_rates = {}
            for layer in monitors_SM:
                recorded_rates[layer] = monitors_SM[layer].get('r', reshape=True)
            savemat(ModelParam['ResultDir'] + 'rates_SM.mat', recorded_rates)

        print('Top-Down Attention:', objPos_deg_recall)

        #### 6. execute saccade to target object ####
        print(Highlight('STEP 6: execute saccade to target object', 'Yellow', Bold=True))
        if Remote_Desktop:
            annarInterface.saccFlag(True) # linear saccade steps (instead of VanOpstal)

        # involved networks: VIS , LIP
        # --> reactivate LIP, VIS  and connection between them
        # --> deactivate SM
        activatedPop = ''
        for pop in popLIP_Net | popVISNet:
            activatedPop += pop.name + '   '
            pop.enable()

        activatedProj = ''
        for proj in projLIP_Net | projVISNet | projLIP_VIS:
            activatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
            proj.transmission = True

        deactivatedPop = ''
        for pop in popSM:
            deactivatedPop += pop.name + '   '
            pop.disable()

        deactivatedProj = ''
        for proj in projSM:
            deactivatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
            proj.transmission = False

        # reset network
        #reset() # LG: Performs a global reset, including simulation time step and SM activities
        for pop in popLIP_Net | popVISNet:
            pop.reset()
        for proj in projLIP_Net | projVISNet | projLIP_VIS:
            proj.reset()

        # record firing rates
        if record_recall:
            monitors = {
                    #'Input': ANN.Monitor(VIS.Input_Pop, 'r'),
                    'V1': ANN.Monitor(VIS.V1, 'r'),
                    'HVA4': ANN.Monitor(VIS.V4L4, 'r'),
                    'HVA23': ANN.Monitor(VIS.V4L23, 'r'),
                    'FEFv': ANN.Monitor(VIS.FEFv, ['r', 'ALIP']),
                    'FEFm': ANN.Monitor(VIS.FEFm, 'r'),
                    'Xh': ANN.Monitor(LIP_.Xh_Pop, 'r'),
                    'LIP_EP': ANN.Monitor(LIP_.LIP_EP_Pop, 'r'),
                    'LIP_CD': ANN.Monitor(LIP_.LIP_CD_Pop, 'r')
                    }

        # get VISual field
        if Remote_Desktop:
            VisualField = ReadImageFromVR(annarInterface)
            VisualField = VisualField / VisualField.max()
            plt.imsave(ModelParam['ResultDir'] + "VisualField_recall.png", VisualField)
        else:
            Img = Image.open(replication_path + "/VisualField_recall.png")
            Img_arr = np.asarray(Img) / 255.
            VisualField = Img_arr[:,:,:3] / Img_arr.max()
            plt.imsave(ModelParam['ResultDir'] + "VisualField_recall.png", VisualField)

        if VisualField.shape[0] != ModelParam['resIm'][1] or VisualField.shape[1] != ModelParam['resIm'][0] or VisualField.shape[2] != ModelParam['resIm'][2]:
            print(Highlight('\nError: The resolution of the VISual field should be ' + str(ModelParam['resIm']),
                            'Red', Bold=True))
            # Because otherwise in ProgramEnd() it tries to make a movie:
            ModelParam['Make_Movie'] = False
            ProgramEnd(First_Start)
            exit(1)

        # Execute saccade to target object
        # Object localization with additional spatial attention
        ModelParam['OutputFileName'] = ModelParam['OutputFileName'].replace('encode', 'recall')
        if Remote_Desktop:
            print("Obj_pos_deg_recall for spatial att.: ", objPos_deg_recall)
            executeSaccade(targetID, VisualField, objPos_deg_recall, popLIP_Net | popVISNet,
                        projLIP_Net | projVISNet | projLIP_VIS, annarInterface, Experiment)

        else:
            print("NO REMOTE DESKTOP")
            executeSaccade(targetID, VisualField, objPos_deg_recall, popLIP_Net | popVISNet,
                        projLIP_Net | projVISNet | projLIP_VIS, annarInterface, Experiment)

        # Put labels on VFs in Results folder for easy inspection
        label_VFs(ModelParam['ResultDir'], vr_objects[targetID])
        
        # save firing rates
        if record_recall:
            recorded_rates = {}
            for layer in monitors:
                recorded_rates[layer] = monitors[layer].get('r', reshape=True)

            recorded_rates['FEFv_ALIP'] = monitors['FEFv'].get('ALIP', reshape=True)

            print("save recall rates as mat file")
            savemat(ModelParam['ResultDir'] + 'rates_recall.mat', recorded_rates)
                    
            # get steps for 2nd localization for colorbar scaling in video
            with open (str(ModelParam['ResultDir'] + 'setting_data.txt'), 'rt') as data_file: 
                content = data_file.readlines()    
            if Remote_Desktop:
                saccade_step = int(content[4][-10:-6])
            else:
                saccade_step = int(content[2][-10:-6])

            create_video(ModelParam['ResultDir'], Experiment, vr_objects[targetID], 1, saccade_step)

        # Reinit SM after network reset
        # involved networks: SM
        # --> reactivate SM
        # --> deactivate LIP, VIS  and connection between them
        if Remote_Desktop:
            activatedPop = ''
            for pop in popSM:
                activatedPop += pop.name + '   '
                pop.enable()

            activatedProj = ''
            for proj in projSM:
                activatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
                proj.transmission = True

            deactivatedPop = ''
            for pop in popLIP_Net | popVISNet:
                deactivatedPop += pop.name + '   '
                pop.disable()

            deactivatedProj = ''
            for proj in projLIP_Net | projVISNet | projLIP_VIS:
                deactivatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
                proj.transmission = False

            # Create SM plot after saccade
            img_count = show_saccade_in_VR(img_count, annarInterface, targetID, popSM, [0, 0], ModelParam['ResultDir']) # objPos_deg_recall: "zero degree saccade"

        print("Simulation", sim+1, "has finished")
        ANN.reset()                                 # Reset network
        
        if Remote_Desktop:
            annarInterface.sendEnvironmentReset(3)  # Reset VR
        
    if Remote_Desktop:
        annarInterface.stop(True)