"""
main function to execute VIS-LIP model

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import timeit
First_Start = timeit.default_timer()

import os
os.system('clear')

import time
import timeit
import copy
import sys
import scipy.io
import numpy as np
import cv2
import pylab as plt
from PIL import Image, ImageFont, ImageDraw
import matplotlib.font_manager as fm
import matplotlib.colors as cs
from matplotlib import pyplot as plt
import ANNarchy as ANN

# import files from somewhere else
sys.path.append('../VIS/')
from VIS_ParamVR import ModelParam
from VIS_parameters import params
from VIS_PreprocessingVR import stepV1
from VIS_InitializationVR import initV1
from VIS_VisualVR import Visualization, Highlight
from VIS_SaveResultsVR import SaveHVA23, SaveHVA4, SaveResults, SavePP, SaveVF, Prepare_Frames
from VIS_SaccGenVR import SaccadeGenerator, SaccadeGenerator2, spherical_to_linear
from VIS_MainHelperVR import PFCObj, TargetName, SaccadeControl_new, CalculatePanTilt,\
                             ReadImageFromVR, waitTillExecuted, CheckWithMATLAB, ProgramEnd

sys.path.append('../LIP/')
from LIP_generateSignals import generateEPsignal, generateAttentionSignal
from LIP_parameters import defParams

sys.path.append('../SM/')
from SM_vr_functions import get_eye_pos, get_image, get_image2
from SM_visualize import create_network_figure

####################################################################################################
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

def get_VISLIP_rates(popVIS, popLIP):
    for pop in popVIS:
        if pop.name == 'V1':
            V1 = pop
        if pop.name == 'V4L23':
            V4L23 = pop
        if pop.name == 'FEFm':
            FEFm = pop
        if pop.name == 'PFC':
            PFC = pop

    for pop in popLIP:
        if pop.name == 'Xh':
            Xh = pop
    
    VISLIP_rates = {
        'V1' : V1.r,
        'V4' : V4L23.r,
        'FEF': FEFm.r,
        'PFC': PFC.r,
        'Xh' : Xh.r
    }

    return VISLIP_rates

####################################################################################################
def idx2deg(idx, max_idx, plotrange):
    '''
    transform degree in visual space to corresponding index of neuron
    '''

    if max_idx in [16, 21, 31, 41]:
        max_idx -= 1
    d = idx / float(max_idx)
    d = d * (plotrange[1]-plotrange[0])
    d = d + plotrange[0]

    return d

####################################################################################################
def drawPos(draw, x_att, y_att, annarInterface, att_sig=None, alpha=None, vf=None, Experiment=None):
    '''
    draw stuff on result images (object location or attention pointer)
    '''
    if not annarInterface is None:
        #Read an image from the VR and save it
        vf = ReadImageFromVR(annarInterface)

    if draw == "encoding_FEF":
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_pos.png')

    if draw == "encoding_Xh":
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_pos.png')

    if draw == "attention_signal":
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_att.png')

    if draw == "recall_FEF":
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_att.png')

    fov_horizontal = 102.0    # defined in Unity APPconfig
    fov_vertical = 77.0       # defined in Unity APPconfig

    height, width, channels = img.shape  # dimensions of the image

    # center of the image
    x_center = width/2
    y_center = height/2

    # pixels per degree of the fov
    pix_per_x = width/fov_horizontal
    pix_per_y = height/fov_vertical

    # center of the circle of attention
    x_circle = int(x_center - pix_per_x * -x_att)
    y_circle = int(y_center - pix_per_y * -y_att)

    if draw == "encoding_FEF":
        cv2.circle(img, (x_circle, y_circle), 9, (0,0,255), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_pos.png', img)

        cv2.circle(img, (x_circle, y_circle), 11, (0,0,255), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_pos_plot.png', img)

    if draw == "encoding_Xh":
        cv2.circle(img, (x_circle, y_circle), 9, (255,0,0), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_pos.png', img)

    if draw == "attention_signal" and x_att != None:
        plt.imsave(ModelParam['ResultDir'] + 'alpha.png', att_sig[1,:,:].T, vmin=0, vmax=0.2, cmap='gray')
        alpha = cv2.imread(ModelParam['ResultDir'] + 'alpha.png')
        alpha = cv2.resize(alpha, (408, 308))
        os.remove(ModelParam['ResultDir'] + 'alpha.png')

        img = img.astype(float)
        alpha = alpha.astype(float)/255
        alpha *= 1.5

        img2 = cv2.multiply(alpha, img)
        img = cv2.addWeighted(img, 0.6, img2, 0.4, 0.0) #Dark background
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_att.png', img)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_att_plot.png', img)

    if draw == "recall_FEF":
        # recall: draw max location of FEFm
        cv2.circle(img, (x_circle, y_circle), 9, (0,0,255), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_att.png', img)

        cv2.circle(img, (x_circle, y_circle), 11, (0,0,255), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_att_plot.png', img)

####################################################################################################
def simulateNetwork(targetID, VisualField, populations, projections, searchOnly=False, AttPos_Deg=None, annarInterface=None, eyetilt=None, Experiment=None, folder='results', popSM=None, popVIS=None, popLIP=None, create_video=False):
    '''
    simulate the combined network of LIP and VIS
    '''

    # get needed populations and projections
    # of VIS
    for pop in populations:
        if pop.name == 'Input':
            Input_Pop = pop
        elif pop.name == 'PFC':
            PFC_Pop = pop
        elif pop.name == 'V1':
            V1_Pop = pop
        elif pop.name == 'V4L23':
            HVA4_Pop = pop
        elif pop.name == 'FEFm':
            FEFm_Pop = pop
        elif pop.name == 'FEFv':
            FEFv = pop
        elif pop.name == 'FEFfix':
            FEFfix = pop
    # of LIP
    for pop in populations:
        if pop.name == 'Xh':
            Xh_Pop = pop
        if pop.name == 'EP':
            EP_Pop = pop
    
    # Defining the preprocessing parameters as fields of a class (objV1):
    objV1 = initV1(ModelParam)

    # search for following target(s)
    TargetSequence = [targetID]

    # Starting the simulation
    FEFfix.r = 1.0

    VF_Counter = 100

    # The Saccade Sign should not be located in the first frames of output movie.
    TargetIndex = 0
    SaccStep = 0
    # Used for saccade control
    FinishCounter = -1
    ShowSaccade = False
    NewVisualField = True
    FirstTime = True
    activateFixIn = -1
    SStep = 0
    first_time = True
    showedSacc = False

    # !!!!!!!!!!!!!!!!!!!!!!!!!!
    PrevSac = [ModelParam['VF_px'][0] / 2., ModelParam['VF_px'][1] / 2.]

    # init EP signal(s)
    # generateEPsignal(SaccStart, SaccTarget, SaccOnset, SaccDur, duration)
    # Attention: need coordinates in deg AND relative to head direction AND in (width,height)
    SaccStart_Deg = np.asarray([0.0, eyetilt])
    #SaccStart_Deg = np.asarray([0.0, 0.0])
    SaccTarget_Deg = SaccStart_Deg
    print("init EP signal at", SaccStart_Deg, "deg")
    ep_sig = generateEPsignal(SaccStart_Deg, SaccTarget_Deg, ModelParam['tEnd'] + 1, 0, ModelParam['tEnd'] + 1)

    if AttPos_Deg is not None:
        print("top-down attention on:", AttPos_Deg, "[deg]")
        Attention = [{'name':'top-down attention', 'position':AttPos_Deg, 'starttime':0}]
        att_sig = generateAttentionSignal(Attention, ModelParam['tEnd']+1)
        
        AttPos_Deg_for_image = [AttPos_Deg[0], AttPos_Deg[1] - eyetilt]
        Attention_for_image = [{'name':'top-down attention', 'position':AttPos_Deg_for_image, 'starttime':0}]
        att_sig_for_image = generateAttentionSignal(Attention_for_image, ModelParam['tEnd']+1)
        drawPos("attention_signal", AttPos_Deg_for_image[0], AttPos_Deg_for_image[1], annarInterface, att_sig_for_image, vf=VisualField, Experiment=Experiment)

    else:
        Attention = []

    #Video creation
    if create_video:
        SM_rates = get_SM_rates(popSM)
        VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
        ObjEncoded = np.zeros(9)
        agent_view = get_image(annarInterface)
        main_view = get_image2(annarInterface)
        vr_objects = {0 : "yellow crane",
                    1 : "green crane",
                    2 : "green racecar"}
        title = f"Arrived at the {vr_objects[targetID]}"
        phase = "encoding"
        create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)
    
    for Step in range(ModelParam['tEnd'] + 1):
        # set EP signal as input to EP_Pop
        EP_Pop.baseline = ep_sig[Step]

        if AttPos_Deg is not None:
            # set attention signal as input to Xh_Pop
            Xh_Pop.baseline = att_sig[Step]

        # start VIS
        if (NewVisualField and FirstTime) or (NewVisualField and ShowSaccade and Step - SaccStep >= ModelParam['FEFmDecayDelay']):
            if not FirstTime:
                activateFixIn = 60 # Mark that the fixation cell should be changed in the future

            if ModelParam['Net_Reset']:
                ANN.reset()
            CurSac = np.asarray([0, 0])
            NewVisualField = False
            FirstTime = False

            if TargetIndex >= len(TargetSequence):
                ProgramEnd(First_Start)
                break

            TargetNo = TargetSequence[TargetIndex]
            print(Highlight('-------------------------------------------------------------------------', 'Yellow', Bold=True))
            print("The Visual Field number", TargetIndex + 1, "from", len(TargetSequence), end=' ')
            print("is showing in the transparent rectangle on Figure 1.")
            print("Search for", Highlight(TargetName(TargetSequence[TargetIndex]), 'Cyan', Bold=True))

            print("Preprocessing the visual field ...")
            PreProcessTime1 = timeit.default_timer()
            rV1C, rV1S = stepV1(VisualField, objV1, ModelParam)
            SavePP(ModelParam, params, rV1C)
            PreProcessTime2 = timeit.default_timer()
            print("OK")
            if ModelParam['Debug_Mode']:
                CheckWithMATLAB(rV1C)
            print("\nPre-processing phase has been finished in {0} seconds.".format(PreProcessTime2-PreProcessTime1))

            # Assigning the pre-processed image to the input layer.
            Input_Pop.r = np.swapaxes(rV1C, 0, 1)

            # Initializing the PFC
            if Experiment == 11 or Experiment == 13 or Experiment == 21 or Experiment == 23 or Experiment == 3:
                PFC_Pop.r = PFCObj(TargetSequence[TargetIndex])
            else:
                if searchOnly:
                    PFC_Pop.r = PFCObj(TargetSequence[TargetIndex])
                else:
                    print("!!!!!!! NO FEATURE_BASED ATTENTION !!!!!!!")

        # FEF is now able to activate
        if Step == 75:
            FEFfix.r = 0.0

        # When creating a video we allow for earlier FEF activation as V4 information is already established
        if create_video and Step == 25:
            FEFfix.r = 0.0

        # Planning of a saccade is allowed
        if activateFixIn == 0:
            print('Fixation cell is deactivated again at t=' + str(Step) + ' !')
            FEFfix.r = 0.0
            activateFixIn = -1
        if activateFixIn > 0:
            print("activate fixation in", activateFixIn)
            activateFixIn -= 1

        sys.stdout.write("\rThe Step %d has been completed." % Step)
        sys.stdout.flush()

        ANN.simulate(1.0)

        NewSac = False
        FinishCounter, NewSac, TempSac = SaccadeControl_new(FEFm_Pop.r, FEFfix, FinishCounter, Step)

        #Video creation
        if create_video:
            SM_rates = get_SM_rates(popSM)
            VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
            ObjEncoded = np.zeros(9)
            agent_view = get_image(annarInterface) if searchOnly else plt.imread(folder + "VisualField_att_plot.png")
            main_view = get_image2(annarInterface)
            vr_objects = {0 : "yellow crane",
                        1 : "green crane",
                        2 : "green racecar"}
            title = f"Localise the {vr_objects[targetID]} with feature-based attention" if searchOnly else f"Re-localise the {vr_objects[targetID]} with spatial attention"
            phase = "encodingText" if searchOnly else "recallAtt"
            create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)
        
        if NewSac:
            # To show saccade sign in the related frames.
            SaccStep = Step
            NewVisualField = True
            TargetIndex += 1

            ShowSaccade = True
            # True means stop pre-processing during saccade. False means pre-processing during
            # saccade is allowed.
            Enough_for_this_sacc = False
            SaccIndex = 0
            if CurSac[0] == 0 and CurSac[1] == 0:
                CurSac = copy.deepcopy(TempSac)

            NewRow_Px = round((CurSac[0]+1) / params['V1_shape'][0] * ModelParam['resIm'][0])
            NewCol_Px = round((CurSac[1]+1) / params['V1_shape'][1] * ModelParam['resIm'][1])

            print("The coordinates of center of the circle is: Row = {0}, Col = {1}".format(NewRow_Px, NewCol_Px))

            # saccade target in deg (width,height)
            CurSac_Deg = [ModelParam['VF_Deg'][0]*(CurSac[0]/float(params['FEF_shape'][0]-1)-0.5),
                          ModelParam['VF_Deg'][1]*(CurSac[1]/float(params['FEF_shape'][1]-1)-0.5)]

            if searchOnly:
                # encoding does not require saccade, stop here
                break

            # Logging
            setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
            setting_data.write("2nd localization: " + str(Step+1) + " steps\n")
            setting_data.close()

            SaccStart_Px = np.asarray(PrevSac)
            SaccStop_Px = np.asarray([NewRow_Px, NewCol_Px])

            EyePos_Deg = SaccadeGenerator2(np.asarray([0, 0]), np.asarray([CurSac_Deg[0], CurSac_Deg[1]]))
            Temp_Deg = SaccadeGenerator(SaccStart_Px, SaccStop_Px, ModelParam['PxperDeg'])
            
            # Approximation to transform the spherical space back into linear so the actual VR saccade does not overshoot the target
            Pan_Deg, Tilt_Deg = spherical_to_linear(CalculatePanTilt(SaccStart_Px, SaccStop_Px))
            VR_Deg = SaccadeGenerator2(np.asarray([0, 0]), np.asarray([Pan_Deg, Tilt_Deg]))

            EyePos_Px = Temp_Deg
            for i in EyePos_Px:
                EyePos_Px[i] = EyePos_Px[i] * ModelParam['PxperDeg']

            # Preventing another saccade before finishing the current one
            FinishCounter = len(EyePos_Px)

            # update EP signal(s)
            # generateEPsignal(SaccStart, SaccTarget, SaccOnset, SaccDur, duration)
            # Attention: need coordinates in deg AND relative to head direction AND in (width,height)
            SaccTarget_Deg = EyePos_Deg[len(EyePos_Deg) - 1]
            print("update EP signal from", SaccStart_Deg, "deg to", SaccTarget_Deg, "deg")
            ep_sig = generateEPsignal(SaccStart_Deg, SaccTarget_Deg, Step, len(EyePos_Px)-1, ModelParam['tEnd']+1)

            print("Object is at: ", SaccTarget_Deg)
            drawPos("recall_FEF", SaccTarget_Deg[0], SaccTarget_Deg[1], annarInterface, None, vf=VisualField, Experiment=Experiment) 
            SaccStart_Deg = SaccTarget_Deg # new fixation point

            # update attention signal: attention on saccade target
            # generateAttentionSignal(Attention, duration)
            # Attention = [{'name', 'position', 'starttime'},{...},...]
            print("attention on saccade target:", SaccTarget_Deg, "[deg]")
            Attention.append({'name':'attention on saccade target', 'position':SaccTarget_Deg, 'starttime':Step, 'endtime':Step+len(EyePos_Px)})
            att_sig = generateAttentionSignal(Attention, ModelParam['tEnd']+1)

            # Re-calculate for saccade with spherical projection

        # timeout during encoding
        if Step == (ModelParam['tEnd']) and searchOnly == True:
            # Write settings data
            setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
            setting_data.write("1st localization: " + str(Step+1) + " steps (timeout)\n")
            setting_data.close()

            # Higlight maximally firing FEF neuron on the VF
            rates_FEF = FEFm_Pop.r 
            max_neuron = np.unravel_index(np.argmax(rates_FEF), rates_FEF.shape)
            max_deg_w = idx2deg(max_neuron[0], rates_FEF.shape[0], [-defParams['v_w']/2.0, defParams['v_w']/2.0])
            max_deg_h = idx2deg(max_neuron[1], rates_FEF.shape[1], [-defParams['v_h']/2.0, defParams['v_h']/2.0])

            if np.argmax(FEFm_Pop.r) > 0:
                drawPos("encoding_FEF", max_deg_w, max_deg_h - eyetilt, annarInterface, None, vf=VisualField, Experiment=Experiment)
                text = "Timeout (FEFm < threshold)"
            else:
                text = "Timeout (no FEFm activity)"

            # Write the error message on the results VF
            posImage = Image.open(ModelParam['ResultDir'] + "VisualField_pos.png")
            posImage = posImage.convert("RGBA")
            overlay = Image.new('RGBA', posImage.size, (255, 255, 255, 0))

            draw = ImageDraw.Draw(overlay)
            font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 20)

            margin = 4
            x = 11
            y = 38
            opacity = 165
            
            bbox = draw.textbbox((x,y), text, font=font)
            draw.rectangle([(bbox[0] - margin, bbox[1] - margin), (bbox[2] + margin, bbox[3] + margin)], fill=(255,255,255,opacity))
            draw.text((x, y), text, font=font, fill=(0,0,0))
            combined = Image.alpha_composite(posImage, overlay)
            combined.save(ModelParam['ResultDir'] + "VisualField_pos.png")  

        # timeout during recall
        if Step == (ModelParam['tEnd']) and searchOnly == False:
            # Write setting data
            setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
            setting_data.write("2nd localization: " + str(Step+1) + " steps (timeout)\n")
            setting_data.close()

            # Higlight maximally firing FEF neuron on the VF
            rates_FEF = FEFm_Pop.r 
            max_neuron = np.unravel_index(np.argmax(rates_FEF), rates_FEF.shape)
            max_deg_w = idx2deg(max_neuron[0], rates_FEF.shape[0], [-defParams['v_w']/2.0, defParams['v_w']/2.0])
            max_deg_h = idx2deg(max_neuron[1], rates_FEF.shape[1], [-defParams['v_h']/2.0, defParams['v_h']/2.0])


            if np.argmax(FEFm_Pop.r) > 0:
                drawPos("recall_FEF", max_deg_w, max_deg_h - eyetilt, annarInterface, None, vf=VisualField, Experiment=Experiment)
                text = "Timeout (FEFm < threshold)"
            else:
                text = "Timeout (no FEFm activity)"
            
            # Write the error message on the results VF
            posImage = Image.open(ModelParam['ResultDir'] + "VisualField_att.png")
            posImage = posImage.convert("RGBA")
            overlay = Image.new('RGBA', posImage.size, (255, 255, 255, 0))

            draw = ImageDraw.Draw(overlay)
            font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 20)

            margin = 4
            x = 11
            y = 38
            opacity = 165
            
            bbox = draw.textbbox((x,y), text, font=font)
            draw.rectangle([(bbox[0] - margin, bbox[1] - margin), (bbox[2] + margin, bbox[3] + margin)], fill=(255,255,255,opacity))
            draw.text((x, y), text, font=font, fill=(0,0,0))
            combined = Image.alpha_composite(posImage, overlay)
            combined.save(ModelParam['ResultDir'] + "VisualField_att.png")  
        
        # FEFm threshold is successfuly reached and a saccade is performed
        if ShowSaccade:
            if first_time:
                SM_rates = get_SM_rates(popSM)
                VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
                agent_view = plt.imread(folder + "VisualField_att_plot.png")
                main_view = get_image2(annarInterface) if create_video else plt.imread(folder + "rep_main_view_recall.jpg")
                vr_objects = {0 : "yellow crane",
                                1 : "green crane",
                                2 : "green racecar"}
                title = f"Re-localised the {vr_objects[targetID]}"
                phase = "recall"
                
                if create_video:
                    create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder, n=60)
                else:
                    create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)
                first_time = False

            else:
                if create_video:
                    SM_rates = get_SM_rates(popSM)
                    VISLIP_rates = get_VISLIP_rates(popVIS, popLIP)
                    agent_view = get_image(annarInterface)
                    main_view = get_image2(annarInterface)
                    vr_objects = {0 : "yellow crane",
                                1 : "green crane",
                                2 : "green racecar"}
                    title = f"Fixate the {vr_objects[targetID]}"
                    phase = "recall"
                    create_network_figure(SM_rates, VISLIP_rates, title, phase, main_view, agent_view, folder)
                else:
                    pass
            
            SaccIndex += 1
            if SaccIndex >= len(VR_Deg):
                SaccIndex = len(VR_Deg) - 1

            ### Perform saccade
            if annarInterface and not Enough_for_this_sacc:
                if (SaccIndex > 0 and SaccIndex % ModelParam['NewVF_DuringSacc_Time'] == 0) or (SaccIndex == len(VR_Deg) - 1):
                    # Calculate pan and tilt for the eyes
                    prevIndex = 0 if ModelParam['NewVF_DuringSacc_Time'] > (len(VR_Deg) - 1) else SaccIndex - ModelParam['NewVF_DuringSacc_Time']
                    Pan, Tilt = VR_Deg[SaccIndex] - VR_Deg[prevIndex]

                    # Execute the saccade in the VR
                    ID = annarInterface.sendEyeMovement(Pan, Pan, Tilt)
                    print(f"pan = {Pan}, tilt = {Tilt}")
                    actionState = waitTillExecuted(annarInterface, ID, 2)
                    time.sleep(1.0)
                    
                    VF_Sacc = ReadImageFromVR(annarInterface)
                    VF_Counter = SaveVF(VF_Counter, VF_Sacc, ModelParam)
                    rV1C_Sacc, rV1S_Sacc = stepV1(VF_Sacc, objV1, ModelParam)
                    Input_Pop.r = np.swapaxes(rV1C_Sacc, 0, 1) # Assigning the new pre-processed image to the input layer.

                    print(Highlight('\nThe new Visual Field (during saccade) has been pre-processed' + ' and given to the input layer.', 'Cyan', Bold=True))
                    if SaccIndex == len(VR_Deg) - 1:
                        Enough_for_this_sacc = True # The last EyePos_Px is finished. Stop the pre-processing during saccade.
                    showedSacc = True

    # Save duration of first localization
    if searchOnly and (Step < ModelParam['tEnd']):
        setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
        setting_data.write("1st localization: " + str(Step+1) + " steps\n")
        setting_data.close()

    return FEFm_Pop.r, Xh_Pop.r

def getObjectPos(targetID, VisualField, populations, projections, annarInterface, Experiment, folder='results', popSM=None, popVIS=None, popLIP=None, create_video=False):
    '''
    get position of object in head-centered coordinates
    '''
    if annarInterface == None:
        eyepos = [15.0, 213.0, 0, 0, 0, 0]
    else:
        eyepos = get_eye_pos(annarInterface) # gets eye position for LIP input

    rates_FEF, rates_Xh = simulateNetwork(targetID, VisualField, populations, projections, annarInterface=annarInterface, searchOnly=True, eyetilt=eyepos[0], folder=folder, popSM=popSM, popVIS=popVIS, popLIP=popLIP,  create_video=create_video)

    # get neuron with highest activation in FEF
    max_neuron = np.unravel_index(np.argmax(rates_FEF), rates_FEF.shape)
    # corresponding degrees (width, height)
    max_deg_w = idx2deg(max_neuron[0], rates_FEF.shape[0], [-defParams['v_w']/2.0, defParams['v_w']/2.0])
    max_deg_h = idx2deg(max_neuron[1], rates_FEF.shape[1], [-defParams['v_h']/2.0, defParams['v_h']/2.0])
    drawPos("encoding_FEF", max_deg_w, max_deg_h, annarInterface, rates_FEF, vf=VisualField, Experiment=Experiment)

    # Additional plot of Xh = head-centered coordinate in degree and [width,height]
    max_neuron = np.unravel_index(np.argmax(rates_Xh), rates_Xh.shape)
    max_deg_w = idx2deg(max_neuron[0], rates_Xh.shape[0], [-defParams['v_w']/2.0, defParams['v_w']/2.0])
    max_deg_h = idx2deg(max_neuron[1], rates_Xh.shape[1], [-defParams['v_h']/2.0, defParams['v_h']/2.0])
    drawPos("encoding_Xh", max_deg_w, max_deg_h - eyepos[0], annarInterface, None, vf=VisualField, Experiment=Experiment)

    return [max_deg_w, max_deg_h]

def executeSaccade(targetID, VisualField, objPos_deg, populations, projections, vrInterface, Experiment, folder='results', popSM=None, popVIS=None, popLIP=None, create_video=False):
    '''
    execute saccade to given object, supported by attention from LIP
    '''
    if vrInterface == None:
        eyepos = [15.0, 213.0, 0, 0, 0, 0]
    else:
        eyepos = get_eye_pos(vrInterface) # eye position for LIP input

    if Experiment == 11 or Experiment == 21:
        simulateNetwork(targetID, VisualField, populations, projections, AttPos_Deg=None, annarInterface=vrInterface, eyetilt=eyepos[0], Experiment=Experiment, folder=folder, popSM=popSM, popVIS=popVIS, popLIP=popLIP, create_video=create_video)
    else:
        simulateNetwork(targetID, VisualField, populations, projections, AttPos_Deg=np.array(objPos_deg), annarInterface=vrInterface, eyetilt=eyepos[0], Experiment=Experiment, folder=folder, popSM=popSM, popVIS=popVIS, popLIP=popLIP, create_video=create_video)
