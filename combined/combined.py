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

from combinedHelper import read_positions, read_objects, label_VFs, load_ExpData, make_video
from combinedVIS_LIP import getObjectPos, executeSaccade

sys.path.append('../LIP/')
from LIP_parameters import defParams

if defParams['save_connections']:
    from combinedNet import *
else:
    from combinedNet_loadConn import *

sys.path.append('../SM/')
from SM_init import initialize_combined
from SM_integrated import SM_1st_step, move_to_pos_and_cue_PW, cue_object_and_encode, recall_object, random_coords, reset_learned_weights
import SM_network

sys.path.append('../VIS/')
from VIS_MainHelperVR import ReadImageFromVR, ProgramEnd
from VIS_VisualVR import Highlight
from VIS_ParamVR import ModelParam

First_Start = timeit.default_timer()

# Initialize parameters from config (see the config.yaml for details)
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

Remote_Desktop =   config['RemoteDesktop']

VR_IP_ADDRESS =    config['VR_IP_ADDRESS']
VR_UNITY_PORT =    config['VR_UNITY_PORT']
VR_AGENT_NO =      config['VR_AGENT_NO']

record_encoding =  config['record_encoding']
record_recall =    config['record_recall']
record_SM =        config['record_SM']
create_video =     config['create_video']
create_report =    config['create_report']

replicate_sim =    config['replication_sim']
replicate_exp =    config['replication_exp']
replicate_num =    config['replication_num']

Experiment =       config['Experiment']
N_simulations =    config['N_simulations']

# Run all simulations?
if Experiment == 0:
    Experiment = [11,12,13,21,22,23]
else: 
    Experiment = [Experiment]

# Replicate an existing simulation?
if replicate_sim:
    Experiment = [replicate_exp]
    N_simulations = 1

# When creating a video: update the visual field in every time step during the saccade 
if create_video:
    ModelParam['NewVF_DuringSacc_Time'] = 1

# Get data for the simulations from the paper
obj_list, pos_list = load_ExpData()

# Import network interface
if Remote_Desktop:
    sys.path.append('../UnityVR/newAgentBrain/')
    import newAnn4Interface



############################
####    Main program    ####
############################
if __name__ == "__main__":
    ANN.compile() # Compile network
    
    # Create model description report (as .tex file)
    if create_report:
        ANN.report(filename="model_description.tex") 

    # If we calculated new projections, we save them for future simulations
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
        print("Start Vision and Memory scenario")
        annarInterface.sendEnvironmentReset(3)
    else:
        annarInterface = None
        print("No VR interface, only replicatio simulations are possible")
        assert replicate_sim, "config['replication_sim'] needs to be True if config['RemoteDesktop'] is False"

    ####################################
    ####    MAIN SIMULATION LOOP    ####
    ####################################
    for sim in range(N_simulations):
        for exp in Experiment:
            # Create result directories
            ModelParam['ResultDir'] = f'Results/Exp{exp}/Simulation_{sim+1}/'
            ModelParam['ResultDir'] = f'Results/Results_{date.today()}_{time.asctime(time.localtime(time.time())).split()[3]}/'
            
            if not os.path.isdir(ModelParam['ResultDir']):
                os.makedirs(ModelParam['ResultDir'])

            # We either replicate an existing simulation or make a custom one
            if config['replication_sim']:
                replication_path = f"Results/Exp{config['replication_exp']}/Simulation_{config['replication_num']}/"
                targetID = obj_list[replicate_num-1]
                target_position = pos_list[replicate_num-1]
            else:
                replication_path = None 
                # Custom simulation
                if config['SET_TASK']:
                    targetID = config['TARGET']
                    target_position = config['POSITION']
                # Visual neglect has a pre-defined scenario which overwrites the custom data
                elif exp == 3:
                    print("Left side neglect in Xh!")
                    annarInterface.sendEnvironmentReset(5)
                    targetID = 1
                    target_position = [8.3, 5.0, 213, -15]
                # We neither have custom settings nor visual neglect: Perform random simulation
                else:
                    targetID = randint(0,2)
                    target_position = random_coords()   

            # Print simulation data
            vr_objects = {
            0 : "yellow crane",
            1 : "green crane",
            2 : "green racecar"
            }

            print(f"Starting Experiment {exp}, simulation {sim+1}")
            print("Target object:", targetID, vr_objects[targetID])
            print("Target position:", target_position)
            
            # Log setting data in a settings file
            # Clear settings file in the results folder if it already exists
            file_path = f"{ModelParam['ResultDir']}setting_data.txt"
            if os.path.exists(file_path): 
                open(file_path, "w").close()

            # Save the target in the settings file
            setting_data = open(file_path, "a")
            setting_data.write("Encoding: " + str(targetID) + ", " + str(vr_objects[targetID]) + "\n")
            setting_data.close()

            # Reset learned BB weights in case we have previously performed a simulation
            reset_learned_weights(popSM, projSM)

            ##################################
            #### 1. Walk to target object ####
            ##################################
            img_count = 0
            print(Highlight('STEP 1: walk to target object', 'Yellow', Bold=True))

            # Video: Disable the LIP network during walking
            if create_video:
                deactivatedPop = ''
                for pop in popLIP_Net:
                    deactivatedPop += pop.name + '   '
                    pop.disable()

                deactivatedProj = ''
                for proj in projLIP_Net | projLIP_VIS:
                    deactivatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
                    proj.transmission = False
            # No video: Disable VIS and LIP as we only need SM for walking
            else:
                deactivatedPop = ''
                for pop in popLIP_Net | popVISNet:
                    deactivatedPop += pop.name + '   '
                    pop.disable()

                deactivatedProj = ''
                for proj in projLIP_Net | projVISNet | projLIP_VIS:
                    deactivatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
                    proj.transmission = False

            # Initializations for SM
            if not Remote_Desktop:
                start_position = [8.0,17.0,np.pi] # starting position of the agent when VR is not used
            else: 
                start_position = None    
            
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

            # First SM step, then move to the object and cue the PW
            img_count = SM_1st_step(popSM, projSM, annarInterface, start_position, target_position, img_count, replication_path, ModelParam['ResultDir'], popVISNet, popLIP_Net, create_video=create_video)
            img_count = move_to_pos_and_cue_PW(popSM, annarInterface, targetID, target_position, img_count, ModelParam['ResultDir'], popVISNet, popLIP_Net, create_video=create_video)

            ##########################################
            #### 2. get position of target object ####
            ##########################################
            print(Highlight('STEP 2: get position of target object', 'Yellow', Bold=True))
            
            # Activate VIS and LIP, deactvate SM
            if create_video:
                activatedPop = ''
                for pop in popLIP_Net:
                    activatedPop += pop.name + '   '
                    pop.enable()

                activatedProj = ''
                for proj in projLIP_Net | projLIP_VIS:
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

            else:
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

            # Record firing rates
            if record_encoding:
                monitors = {
                        'V1': ANN.Monitor(VIS.AuxV1, 'r'),
                        'HVA4': ANN.Monitor(VIS.V4L4, 'r'),
                        'HVA23': ANN.Monitor(VIS.V4L23, 'r'),
                        'FEFv': ANN.Monitor(VIS.FEFv, ['r', 'ALIP']),
                        'FEFm': ANN.Monitor(VIS.FEFm, 'r'),
                        'Xh': ANN.Monitor(LIP_.Xh_Pop, 'r'),
                        'LIP_EP': ANN.Monitor(LIP_.LIP_EP_Pop, 'r'),
                        'LIP_CD': ANN.Monitor(LIP_.LIP_CD_Pop, 'r')
                        }

            # Get visual field to be passed into the visual model and also save it for evaluation purposes
            if Remote_Desktop:
                VisualField = ReadImageFromVR(annarInterface)
                VisualField = VisualField / VisualField.max()
                plt.imsave(ModelParam['ResultDir'] + "VisualField_encoding.png", VisualField)
                plt.imsave(ModelParam['ResultDir'] + "VisualField_pos.png", VisualField)
            else:
                Img = Image.open(replication_path + "/VisualField_encoding.png")
                Img_arr = np.asarray(Img) / 255.
                VisualField = Img_arr[:,:,:3] / Img_arr.max()
                plt.imsave(ModelParam['ResultDir'] + "VisualField_encoding.png", VisualField)
                plt.imsave(ModelParam['ResultDir'] + "VisualField_pos.png", VisualField)

            # Check if VF has the correct dimensions
            if VisualField.shape[0] != ModelParam['resIm'][1] or VisualField.shape[1] != ModelParam['resIm'][0] or VisualField.shape[2] != ModelParam['resIm'][2]:
                print(Highlight('\nError: The resolution of the VISual field should be ' + str(ModelParam['resIm']), 'Red', Bold=True))
                exit(1)
            
            # Perform object localization
            ModelParam['OutputFileName'] += 'encode_'
            objPos_deg = getObjectPos(targetID, VisualField, popLIP_Net | popVISNet, projLIP_Net | projVISNet | projLIP_VIS, annarInterface, exp, ModelParam['ResultDir'], popSM, popVISNet, popLIP_Net, create_video=create_video)
            print("Target object at", objPos_deg, "[deg] (care: head centered coordinates!)")
            
            # Put labels on the images for manual evaluation
            label_VFs(ModelParam['ResultDir'], vr_objects[targetID], exp, "encoding") # label for visual inspection 
            
            # Save firing rates
            if record_encoding:
                print("save firing rates as mat file")
                recorded_rates = {}
                for layer in monitors:
                    recorded_rates[layer] = monitors[layer].get(['r'], reshape=True)

                recorded_rates['FEFv_ALIP'] = monitors['FEFv'].get('ALIP', reshape=True)

                savemat(ModelParam['ResultDir'] + 'rates_encoding.mat', recorded_rates)
                #make_video(ModelParam['ResultDir'], exp, vr_objects[targetID], 0, -1)

            #################################
            #### 3. encode target object ####
            #################################
            print(Highlight('STEP 3: encode target object', 'Yellow', Bold=True))
            
            # activate SM, deactivate VIS/LIP
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
            
            # cue object and encode it into memory
            img_count = cue_object_and_encode(popSM, projSM, annarInterface, targetID, objPos_deg, target_position, img_count, replication_path, ModelParam['ResultDir'], popVISNet, popLIP_Net, create_video=create_video)

            #######################################
            #### 4. walk to different position ####
            #######################################
            print(Highlight('STEP 4: walk to different position', 'Yellow', Bold=True))
            
            # for video: set Xh to 0, activate VIS
            if create_video:
                # Set Xh to 0 before walking, as the LIP is disabled during navigation
                for pop in popLIP_Net:
                    if pop.name == "Xh":
                        pop.r = 0

                # Activate VIS populations during navigation
                activatedPop = ''
                for pop in popVISNet:
                    activatedPop += pop.name + '   '
                    pop.enable()

                activatedProj = ''
                for proj in projVISNet:
                    activatedProj += proj.pre.name + '-' + proj.post.name + '-' + proj.target + '   '
                    proj.transmission = True

            walkToID = 5 # originally was the position of the red pencil, now hardcoded to be the sofa in SM_integrated
            img_count = move_to_pos_and_cue_PW(popSM, annarInterface, walkToID, target_position, img_count, ModelParam['ResultDir'], popVISNet, popLIP_Net, create_video=create_video, objPos_deg=objPos_deg)

            # For cluttered recall: When away from the tesk, move some objects in front of the previous target objects
            if annarInterface and (exp == 21 or exp == 22 or exp == 23):
                print("Cluttering the table")
                annarInterface.sendEnvironmentReset(4)

            #################################
            #### 5. recall target object ####
            #################################
            print(Highlight('STEP 5: recall and walk to target object', 'Yellow', Bold=True))
            # involved networks: SM

            walkTo_position = [14.5, 10.0, 70, target_position[3]] # position of couch, we need to add original head tilt, as it can't be decoded from PW
            img_count, Xag_imag, Yag_imag, HDestim, THobj_imag_oPW_VRdeg = recall_object(popSM, projSM, annarInterface, targetID, walkTo_position, objPos_deg, img_count, replication_path,  ModelParam['ResultDir'], popVISNet, popLIP_Net, create_video=create_video)
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


            #############################################################
            #### 6. re-localise and perform saccade to target object ####
            #############################################################
            print(Highlight('STEP 6: re-localise and perform saccade to target object', 'Yellow', Bold=True))
            if Remote_Desktop:
                annarInterface.saccFlag(True) # linear saccade steps (instead of VanOpstal)

            # involved networks: VIS, LIP
            # --> reactivate LIP, VIS  and connection between them
            # --> deactivate SM
            if create_video:
                activatedPop = ''
                for pop in popLIP_Net:
                    activatedPop += pop.name + '   '
                    pop.enable()

                activatedProj = ''
                for proj in projLIP_Net | projLIP_VIS:
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
            
            else:
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
                        'V1': ANN.Monitor(VIS.AuxV1, 'r'),
                        'HVA4': ANN.Monitor(VIS.V4L4, 'r'),
                        'HVA23': ANN.Monitor(VIS.V4L23, 'r'),
                        'FEFv': ANN.Monitor(VIS.FEFv, ['r', 'ALIP', 'AFEAT']),
                        'FEFm': ANN.Monitor(VIS.FEFm, 'r'),
                        'Xh': ANN.Monitor(LIP_.Xh_Pop, 'r'),
                        'LIP_EP': ANN.Monitor(LIP_.LIP_EP_Pop, 'r'),
                        'LIP_CD': ANN.Monitor(LIP_.LIP_CD_Pop, 'r')
                        }

            # get Visual field
            if Remote_Desktop:
                VisualField = ReadImageFromVR(annarInterface)
                VisualField = VisualField / VisualField.max()
                plt.imsave(ModelParam['ResultDir'] + "VisualField_recall.png", VisualField)
                plt.imsave(ModelParam['ResultDir'] + "VisualField_att.png", VisualField)
            else:
                Img = Image.open(replication_path + "/VisualField_recall.png")
                Img_arr = np.asarray(Img) / 255.
                VisualField = Img_arr[:,:,:3] / Img_arr.max()    
                plt.imsave(ModelParam['ResultDir'] + "VisualField_recall.png", VisualField)
                plt.imsave(ModelParam['ResultDir'] + "VisualField_att.png", VisualField)
            
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
                executeSaccade(targetID, VisualField, objPos_deg_recall, popLIP_Net | popVISNet, projLIP_Net | projVISNet | projLIP_VIS, annarInterface, exp, ModelParam['ResultDir'], popSM, popVISNet, popLIP_Net, create_video=create_video)
            else:
                print("NO REMOTE DESKTOP")
                executeSaccade(targetID, VisualField, objPos_deg_recall, popLIP_Net | popVISNet, projLIP_Net | projVISNet | projLIP_VIS, annarInterface, exp, ModelParam['ResultDir'], popSM, popVISNet, popLIP_Net, create_video=create_video)
            # Put labels on the images
            label_VFs(ModelParam['ResultDir'], vr_objects[targetID], exp, "recall") # label for visual inspection
            
            # save firing rates
            if record_recall:
                recorded_rates = {}
                for layer in monitors:
                    recorded_rates[layer] = monitors[layer].get('r', reshape=True)

                recorded_rates['FEFv_ALIP'] = monitors['FEFv'].get('ALIP', reshape=True)
                recorded_rates['FEFv_exc'] = monitors['FEFv'].get('AFEAT', reshape=True)

                print("save recall rates as mat file")
                savemat(ModelParam['ResultDir'] + 'rates_recall.mat', recorded_rates)
                        
                # get steps for 2nd localization for colorbar scaling in video
                with open (str(ModelParam['ResultDir'] + 'setting_data.txt'), 'rt') as data_file: 
                    content = data_file.readlines()    
                if Remote_Desktop:
                    saccade_step = int(content[4][18:21])
                else:
                    saccade_step = int(content[2][18:21])

                #make_video(ModelParam['ResultDir'], exp, vr_objects[targetID], 1, saccade_step)

            # Reinit SM (check if this can be removed)
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

            # Final resets
            ANN.reset()  # Reset network
            if Remote_Desktop:
                annarInterface.sendEnvironmentReset(3) # Reset VR
        
    if Remote_Desktop:
        annarInterface.stop(True) # Stop VR interface