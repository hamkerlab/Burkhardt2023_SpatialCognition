"""
main function to execute VIS-LIP model

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

# If you don't want to see any kind of visualization, set this parameter to False.
Vis_Enable = False

# import standard libraries
import timeit
First_Start = timeit.default_timer()

import os
os.system('clear')

import time
import copy
import sys
import scipy.io
import numpy as np
import cv2
import pylab as plt
from PIL import Image, ImageFont, ImageDraw
import matplotlib.font_manager as fm
import matplotlib.colors as cs
import ANNarchy as ANN

# import files from somewhere else
sys.path.append('../VIS/')
from VIS_ParamVR import ModelParam
from VIS_parameters import params
from VIS_PreprocessingVR import stepV1
from VIS_InitializationVR import initV1
from VIS_VisualVR import Visualization, Highlight
from VIS_SaveResultsVR import SaveHVA23, SaveHVA4, SaveResults, SavePP, SaveVF, Prepare_Frames
from VIS_SaccGenVR import SaccadeGenerator, SaccadeGenerator2
from VIS_MainHelperVR import PFCObj, TargetName, SaccadeControl_new, CalculatePanTilt,\
                             ReadImageFromVR, waitTillExecuted, CheckWithMATLAB, ProgramEnd

sys.path.append('../LIP/')
from LIP_generateSignals import generateEPsignal, generateAttentionSignal
from LIP_parameters import defParams

sys.path.append('../SM/')
from SM_vr_functions import get_eye_pos


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
def drawPos(x_att, y_att, annarInterface, Step, att_sig=None, draw_att=0, alpha=None, vf=None, Experiment=None):
    '''
    draw stuff on result images (object location or attention pointer)
    '''

    if not annarInterface is None:
        #Read an image from the VR and save it
        vf = ReadImageFromVR(annarInterface)

    if draw_att == 1:
        plt.imsave(ModelParam['ResultDir'] + 'VisualField_pos.png', vf) # Draw position
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_pos.png')

    if draw_att == 11:
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_pos.png')

    if draw_att == 2:
        plt.imsave(ModelParam['ResultDir'] + 'VisualField_att.png', vf) # Draw attention
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_att.png')

    if draw_att == 3:
        if Experiment == 1:
            plt.imsave(ModelParam['ResultDir'] + 'VisualField_sacc_target.png', vf) # Draw saccade target
            img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_sacc_target.png')
        else:
            img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_att.png')

    if draw_att == 4:
        plt.imsave(ModelParam['ResultDir'] + 'VisualField_sacc.png', vf) # Draw saccade target
        img = cv2.imread(ModelParam['ResultDir'] + 'VisualField_sacc.png')

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

    if draw_att == 1:
        # draw max location of FEFm
        cv2.circle(img, (x_circle, y_circle), 7, (0,0,255), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_pos.png', img)

    if draw_att == 11:
        cv2.circle(img, (x_circle, y_circle), 7, (255,0,0), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_pos.png', img)

    if draw_att == 2 and x_att != None:
        plt.imsave(ModelParam['ResultDir'] + 'alpha.png', att_sig[1,:,:].T, vmin=0, vmax=0.2, cmap='gray')
        alpha = cv2.imread(ModelParam['ResultDir'] + 'alpha.png')
        alpha = cv2.resize(alpha, (408, 308))
        os.remove(ModelParam['ResultDir'] + 'alpha.png')

        img = img.astype(float)
        alpha = alpha.astype(float)/255
        alpha *= 1.5

        img2 = cv2.multiply(alpha, img)

        #Dark background
        img = cv2.addWeighted(img, 0.6, img2, 0.4, 0.0)

        #Save combined image
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_att.png', img)

    if draw_att == 3:
        cv2.circle(img, (x_circle, y_circle), 7, (0,0,255), -1)
        cv2.imwrite(ModelParam['ResultDir'] + 'VisualField_att.png', img)


####################################################################################################
def simulateNetwork(targetID, VisualField, populations, projections, searchOnly=False, AttPos_Deg=None, annarInterface=None, eyetilt=None, Experiment=None):
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
        elif pop.name == 'V4L4':
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

    Stop01 = timeit.default_timer()
    print("Precompile process has been finished in {0} seconds.".format(Stop01 - First_Start))

    # search for following target(s)
    TargetSequence = [targetID]

    # Starting the simulation
    FEFfix.r = 1.0

    VF_Counter = 100
    Sacc_Counter = 300

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

    # !!!!!!!!!!!!!!!!!!!!!!!!!!
    PrevSac = [ModelParam['VF_px'][0] / 2., ModelParam['VF_px'][1] / 2.]

    # eye position over time in pixel (width, height)
    eyepos_over_time_PxScene = {}
    # init with current fixation point
    for i in range(ModelParam['tEnd'] + 1):
        eyepos_over_time_PxScene[i] = PrevSac

    # init EP signal(s)
    # generateEPsignal(SaccStart, SaccTarget, SaccOnset, SaccDur, duration)
    # Attention: need coordinates in deg AND relative to head direction AND in (width,height)
    SaccStart_Deg = np.asarray([0.0, eyetilt])
    #SaccStart_Deg = np.asarray([0.0, 0.0])
    SaccTarget_Deg = SaccStart_Deg
    print("init EP signal at", SaccStart_Deg, "deg")
    ep_sig = generateEPsignal(SaccStart_Deg, SaccTarget_Deg, ModelParam['tEnd'] + 1, 0, ModelParam['tEnd'] + 1)
    
    if AttPos_Deg is not None:
        # init attention signal at top-down attention position, position needed in deg
        # AND in (width,height)
        # use position gathered from first phase
        # generateAttentionSignal(Attention, duration)
        # Attention = [{'name', 'position', 'starttime'},{...},...]
        print("top-down attention on:", AttPos_Deg, "[deg]")
        Attention = [{'name':'top-down attention', 'position':AttPos_Deg, 'starttime':0}]
        att_sig = generateAttentionSignal(Attention, ModelParam['tEnd']+1)
        
        AttPos_Deg_for_image = [AttPos_Deg[0], AttPos_Deg[1] - eyetilt]
        Attention_for_image = [{'name':'top-down attention', 'position':AttPos_Deg_for_image, 'starttime':0}]
        att_sig_for_image = generateAttentionSignal(Attention_for_image, ModelParam['tEnd']+1)
        drawPos(AttPos_Deg[0], AttPos_Deg[1] - eyetilt, annarInterface, None, att_sig_for_image, draw_att=2, vf=VisualField, Experiment=Experiment)

    else:
        Attention = []

    output = {'t_start': 0}
    
    for Step in range(ModelParam['tEnd'] + 1):
        # set EP signal as input to EP_Pop
        EP_Pop.baseline = ep_sig[Step]

        if AttPos_Deg is not None:
            # set attention signal as input to Xh_Pop
            Xh_Pop.baseline = att_sig[Step]

        # start VIS
        if (NewVisualField and FirstTime) or (NewVisualField and ShowSaccade and Step - SaccStep >= ModelParam['FEFmDecayDelay']):
            if not FirstTime:
                # Mark that the fixation cell should be changed in the future
                activateFixIn = 60

            if ModelParam['Net_Reset']:
                ANN.reset()
            CurSac = np.asarray([0, 0])
            NewVisualField = False
            FirstTime = False

            VF_Sacc = VisualField
            VF_Counter = SaveVF(VF_Counter, VF_Sacc, ModelParam)

            if Vis_Enable:
                subfolder = 'visualization/'
                if searchOnly:
                    subfolder += 'ObjSearch/'
                if AttPos_Deg is not None:
                    subfolder += 'topDownAtt/'
                Vis = Visualization(VisualField, ModelParam['ResultDir']+subfolder)
                Vis.Update(False, 0, 0)

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
            # juschu: switch width and height axes
            Input_Pop.r = np.swapaxes(rV1C, 0, 1)

            # Initializing the PFC
            if Experiment == 1 or Experiment == 3 or Experiment == 4:
                PFC_Pop.r = PFCObj(TargetSequence[TargetIndex])  # new: feature based attention for both localizations
            else:
                if searchOnly:
                    PFC_Pop.r = PFCObj(TargetSequence[TargetIndex])
                else:
                    print("!!!!!!! NO FEATURE_BASED ATTENTION !!!!!!!")

        if Step == 75:
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

            # saccade target in deg (height,width)
            # juschu: it's now in (width,height) !
            CurSac_Deg = [ModelParam['VF_Deg'][0]*(CurSac[0]/float(params['FEF_shape'][0]-1)-0.5),
                          ModelParam['VF_Deg'][1]*(CurSac[1]/float(params['FEF_shape'][1]-1)-0.5)]

            if Vis_Enable:
                Vis.Update(True, NewRow_Px, NewCol_Px)

            if searchOnly:
                # we only search for the object and do not want to execute a saccade to it
                # thus, we can stop here
                break

            # Logging
            setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
            setting_data.write("2nd localization: " + str(Step+1) + " steps\n")
            setting_data.close()

            SaccStart_Px = np.asarray(PrevSac)
            SaccStop_Px = np.asarray([NewRow_Px, NewCol_Px])

            EyePos_Deg = SaccadeGenerator2(np.asarray([0, 0]), np.asarray([CurSac_Deg[0], CurSac_Deg[1]]))
            Temp_Deg = SaccadeGenerator(SaccStart_Px, SaccStop_Px, ModelParam['PxperDeg'])

            EyePos_Px = copy.deepcopy(Temp_Deg)
            for i in EyePos_Px:
                EyePos_Px[i] = EyePos_Px[i] * ModelParam['PxperDeg']
                eyepos_over_time_PxScene[i+Step] = EyePos_Px[i]
            # now eyes are at a new fixation point
            for i in range(len(EyePos_Px)-1+Step, ModelParam['tEnd'] + 1):
                eyepos_over_time_PxScene[i] = EyePos_Px[len(EyePos_Px) - 1]

            # Preventing another saccade before finishing the current one
            FinishCounter = len(EyePos_Px)

            if 'sac_start' in output:
                output['sac_start'].append(Step)
                output['sac_end'].append(len(EyePos_Px)-1+Step)
            else:
                output['sac_start'] = [Step]
                output['sac_end'] = [len(EyePos_Px)-1+Step]

            # update EP signal(s)
            # generateEPsignal(SaccStart, SaccTarget, SaccOnset, SaccDur, duration)
            # Attention: need coordinates in deg AND relative to head direction AND in (width,height)
            SaccTarget_Deg = EyePos_Deg[len(EyePos_Deg) - 1]
            print("update EP signal from", SaccStart_Deg, "deg to", SaccTarget_Deg, "deg")
            ep_sig = generateEPsignal(SaccStart_Deg, SaccTarget_Deg, Step, len(EyePos_Px)-1, ModelParam['tEnd']+1)

            print("Object is at: ", SaccTarget_Deg)
            drawPos(SaccTarget_Deg[0], SaccTarget_Deg[1], annarInterface, Sacc_Counter, None,
                    draw_att=3, vf=VisualField, Experiment=Experiment)
            # new fixation point
            SaccStart_Deg = SaccTarget_Deg

            # update attention signal: attention on saccade target
            # generateAttentionSignal(Attention, duration)
            # Attention = [{'name', 'position', 'starttime'},{...},...]
            print("attention on saccade target:", SaccTarget_Deg, "[deg]")
            Attention.append({'name':'attention on saccade target', 'position':SaccTarget_Deg, 'starttime':Step, 'endtime':Step+len(EyePos_Px)})
            att_sig = generateAttentionSignal(Attention, ModelParam['tEnd']+1)

        if Step == (ModelParam['tEnd']):
            setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
            setting_data.write("2nd localization: " + str(Step+1) + " steps (timeout)\n")
            setting_data.close()

        
        if ShowSaccade:
            SaccIndex += 1
            if SaccIndex >= len(EyePos_Px):
                SaccIndex = len(EyePos_Px) - 1

            ### Run pre-processing for new VF during saccade.
            if not Enough_for_this_sacc:
                if (SaccIndex > 0 and SaccIndex % ModelParam['NewVF_DuringSacc_Time'] == 0) or \
                    (SaccIndex == len(EyePos_Px) - 1):
                    CR = int(round(EyePos_Px[SaccIndex][0]))
                    CC = int(round(EyePos_Px[SaccIndex][1]))
                    SaccStop_Px = np.asarray([CR, CC])
                    # juschu: SaccStart_Px and SaccStop_Px in (width,height)
                    Pan, Tilt = CalculatePanTilt(SaccStart_Px, SaccStop_Px)

                    if annarInterface:
                        # LG: Added to execute the saccade in the VR (10.3.16)
                        print("1: pan = ", Pan, " pan2 = ", Pan, " tilt = ", Tilt)
                        ID = annarInterface.sendEyeMovement(Pan, Pan, Tilt)
                        print("2: pan = ", Pan, " pan2 = ", Pan, " tilt = ", Tilt)
                        actionState = waitTillExecuted(annarInterface, ID, 2)
                        time.sleep(3.0)
                        VF_Sacc = ReadImageFromVR(annarInterface)
                        VF_Counter = SaveVF(VF_Counter, VF_Sacc, ModelParam)
                        drawPos(SaccTarget_Deg[0], SaccTarget_Deg[1], annarInterface, Sacc_Counter, HVA4_Pop.r, draw_att=4, vf=VisualField, Experiment=Experiment)
                        Sacc_Counter += 1

                    rV1C_Sacc, rV1S_Sacc = stepV1(VF_Sacc, objV1, ModelParam)
                    # Assigning the new pre-processed image to the input layer.
                    # HD, MB: switched width and height axes
                    Input_Pop.r = np.swapaxes(rV1C_Sacc, 0, 1)

                    print(Highlight('\nThe new Visual Field (during saccade) has been pre-processed' + ' and given to the input layer.', 'Cyan', Bold=True))
                    if SaccIndex == len(EyePos_Px) - 1:
                        # The last EyePos_Px is finished. Stop the pre-processing during saccade.
                        Enough_for_this_sacc = True
                    SaccStart_Px = SaccStop_Px

    # End for
    output['t_end'] = Step
    
    # Logging
    if searchOnly:
        setting_data = open(ModelParam['ResultDir'] + "setting_data.txt", "a")
        setting_data.write("1st localization: " + str(Step+1) + " steps\n")
        setting_data.close()
    
    return FEFm_Pop.r, Xh_Pop.r
    #return Xh_Pop.r

def getObjectPos(targetID, VisualField, populations, projections, annarInterface, Experiment):
    '''
    get position of object in head-centered coordinates
    '''
    if annarInterface == None:
        eyepos = [15.0, 213.0, 0, 0, 0, 0]
    else:
        eyepos = get_eye_pos(annarInterface) # gets eye position for LIP input

    rates_FEF, rates_Xh = simulateNetwork(targetID, VisualField, populations, projections, searchOnly=True, eyetilt=eyepos[0])


    # get maximum position in FEF
    # neuron with highest activity
    max_neuron = np.unravel_index(np.argmax(rates_FEF), rates_FEF.shape)
    # corresponding degrees (width)
    max_deg_w = idx2deg(max_neuron[0], rates_FEF.shape[0], [-defParams['v_w']/2.0, defParams['v_w']/2.0])
    # corresponding degrees (height)
    max_deg_h = idx2deg(max_neuron[1], rates_FEF.shape[1], [-defParams['v_h']/2.0, defParams['v_h']/2.0])

    drawPos(max_deg_w, max_deg_h, annarInterface, None, rates_FEF, draw_att=1, vf=VisualField, Experiment=Experiment)

    # Additional plot of Xh = head-centered coordinate in degree and [width,height]
    max_neuron = np.unravel_index(np.argmax(rates_Xh), rates_Xh.shape)
    max_deg_w = idx2deg(max_neuron[0], rates_Xh.shape[0], [-defParams['v_w']/2.0, defParams['v_w']/2.0])
    max_deg_h = idx2deg(max_neuron[1], rates_Xh.shape[1], [-defParams['v_h']/2.0, defParams['v_h']/2.0])
    drawPos(max_deg_w, max_deg_h - eyepos[0], annarInterface, None, None, draw_att=11, vf=VisualField, Experiment=Experiment)

    return [max_deg_w, max_deg_h]

def executeSaccade(targetID, VisualField, objPos_deg, populations, projections, vrInterface, Experiment):
    '''
    execute saccade to given object, supported by attention from LIP
    '''
    if vrInterface == None:
        eyepos = [15.0, 213.0, 0, 0, 0, 0]
    else:
        eyepos = get_eye_pos(vrInterface) # gets eye position for LIP input

    # Catch index error in case we don't find the object fast enough
    try:
        if Experiment == 1:
            simulateNetwork(targetID, VisualField, populations, projections, AttPos_Deg=None, annarInterface=vrInterface, eyetilt=eyepos[0], Experiment=Experiment)
        else:
            simulateNetwork(targetID, VisualField, populations, projections, AttPos_Deg=np.array(objPos_deg), annarInterface=vrInterface, eyetilt=eyepos[0], Experiment=Experiment)
    except:
        posImage = Image.open(ModelParam['ResultDir'] + "VisualField_pos.png")
        draw = ImageDraw.Draw(posImage)
        font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 20)
        draw.text((10,10), "Recall failed", font=font, fill=(0,0,0))
        posImage.save("Results_VIS/SaccTarget_" + ModelParam['ResultDir'][15:-1] + ".png")