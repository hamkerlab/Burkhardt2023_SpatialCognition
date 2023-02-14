# -*- coding: utf-8 -*-
"""
helper functions for the main file of the model, which are not belonging to any other modul

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

# import standard libraries
import timeit
import time
import os
import math
import numpy as np
from PIL import Image
from scipy.io import loadmat

from VIS_parameters import params
from VIS_ParamVR import ModelParam
from VIS_VisualVR import Highlight


def CalculatePanTilt(SaccStart_Px, SaccStop_Px):
    '''
    Calculate Pan and Tilt for agent's saccade in VR.

    params: SaccStart_Px -- numpy array with coordinates of Saccade's start point in pixel
            SaccStop_Px  -- numpy array with coordinates of Saccade's stop point in pixel

    return: Pan          -- scalar value with amount of Pan in Degree
            Tilt         -- scalar value with amount of Tilt in Degree
    '''

    Alpha_Deg = 102. / 2.
    Alpha_Rad = Alpha_Deg * math.pi / 180.
    Half_Width = ModelParam['resIm'][0] / 2.
    Eye_VF_Distance = Half_Width / math.tan(Alpha_Rad)

    Pan_AlphaT_Rad = math.atan((SaccStop_Px[0] - SaccStart_Px[0]) / Eye_VF_Distance)
    Pan_AlphaT_Deg = Pan_AlphaT_Rad * 180. / math.pi
    Pan = Pan_AlphaT_Deg # round(Pan_AlphaT_Deg)

    Alpha_Deg = 77. / 2.
    Alpha_Rad = Alpha_Deg * math.pi / 180.
    Half_Width = ModelParam['resIm'][1] / 2.
    Eye_VF_Distance = Half_Width / math.tan(Alpha_Rad)

    Tilt_AlphaT_Rad = math.atan((SaccStart_Px[1] - SaccStop_Px[1]) / Eye_VF_Distance)
    Tilt_AlphaT_Deg = Tilt_AlphaT_Rad * 180. / math.pi
    Tilt = Tilt_AlphaT_Deg # round(Tilt_AlphaT_Deg)

    return Pan, Tilt


def CheckWithMATLAB(rV1C):
    '''
    In debug mode (ModelParam['Debug_Mode'] = True) one can use this function to compare the result
    of preprocessing of Python and Matlab.

    params: rV1C -- numpy array containing rate of V1-Complex neutons (pre-processed image)
    '''

    MATLAB_rV1C = loadmat(ModelParam['DataDir'] + 'rV1CS.mat')['rV1C']

    if np.max(np.abs(rV1C-MATLAB_rV1C)) > 0.0001:
        print("\n", Highlight('Warning: Matlab and Python make different results in pre-processing phase.',
                              'Yellow', Bold = True))
    else:
        print("\n", Highlight('Matlab and Python make same results in pre-processing phase.',
                              'Green', Bold = True))


def CoG(A):
    '''
    calculate Center of Gravity (CoG) of an array

    params: A -- array

    return: Centers -- numpy array with coordinates of Center of Gravity
    '''

    rc, cc = np.mgrid[0:A.shape[0], 0:A.shape[1]]
    Mt = sum(sum(A))
    Centers = np.zeros(2)
    Centers[0] = sum(sum(A * rc)) / Mt
    Centers[1] = sum(sum(A * cc)) / Mt

    return Centers


def MakeMovie(ShowMovie=False, DeleteFrames=True):
    '''
    After completion of the simulation and if ModelParam['Make_Movie'] is True, some numbered
    png files (e.g. 0000.png, 0001.png, 0002.png, ...) should be generated as single frames of a
    movie. This function, first makes such single frames based on saved images and then, uses a
    Linux instruction (ffmpeg) to make a movie from these single frames.

    params: ShowMovie    -- show the Movie immediately after simulation
                            default: False
            DeleteFrames -- delete genereted (remaned) png files
                            default: True
    '''

    # Change the current directory to the results directory.
    CurrentDir = os.getcwd()
    os.chdir(ModelParam['ResultDir'])

    # The following for loop makes frames based on saved image files.
    # It's basically a renaming
    for entry in os.scandir('./'):
        StFilename = entry.path
        if ModelParam['OutputFileName'] in StFilename:
            step = int(StFilename.split('_')[-1][:-4])
            FrFilename = "{:>04d}.png".format(step)
            Frame = Image.open(StFilename)
            Frame.save(FrFilename)

    # Delete the old probable movie with the same filename.
    MovFilename = ModelParam['Movie_Filename'] + ModelParam['OutputFileName'].split('_')[-2] + '.mp4'
    Movie_File = open(MovFilename, 'w')
    Movie_File.close()
    St = 'rm ' + MovFilename
    os.system(St)

    St = 'ffmpeg -framerate 2 -i %04d.png -r 30 -pix_fmt yuv420p ' + MovFilename
    os.system(St)

    # Delete the frames after making the movie file (by default).
    if DeleteFrames:
        os.system('rm 0*.*')

    # Delete the saved graphical results.
    if not ModelParam['SaveImagesInOneFile']:
        St = 'rm ' + ModelParam['OutputFileName'] + '*.png'
        os.system(St)

    # Show the movie on demand.
    if ShowMovie:
        St = 'ffplay ' + MovFilename
        os.system(St)

    os.chdir(CurrentDir)    # Back to the previous directory.


def PFCObj(ObjNo):
    '''
    return proper value of PFC based on what is already saved in Object Memory (OM).
    OM is a matrix which is saved in a *.mat file.

    params: ObjNo -- integer number in [0, 14] interval

    return: OBJ   -- vector which retrieved from Object Memory and should be assigned to the PFC
    '''

    OBJ = loadmat(params['path_weightMat'])['OM'][ObjNo].astype(float)
    print(Highlight('The PFC is:', 'Yellow', Bold = True))
    print(OBJ)
    print(Highlight('----------------------------------------------------------------------------------------------------', 'Yellow', Bold = True))
    return OBJ


def ProgramEnd(First_Start):
    '''
    Generate message about whole time consumed during simulation and then ends the program safely

    params: First_Start -- start time of simulation
    '''
    Last_Stop = timeit.default_timer()
    if ModelParam['Make_Movie']:
        MakeMovie()
    print(Highlight('\n----------------------------------------------------------------------------------------------------', 'Red', Bold = True))
    print(Highlight('The whole simulation has been finished in %f seconds.' % (Last_Stop-First_Start),
                    'Green', Bold=True))
    print(Highlight('Press Enter to quit.', 'Red', Bold=True))


def ReadImageFromVR(annarInterface):
    '''
    Read an image from VR agent's left eye

    params: annarInterface -- ANNarchy Interface

    return: LImage         -- numpy array of shape (height, width, 3) with values from 0 to 1
                              containing Left Image received from VR
    '''

    ret = False
    while not ret:
        ret = annarInterface.checkImages()

    Tmp = annarInterface.getImageLeft()
    LImage = np.array(Tmp) / 255.
    LImage = LImage / LImage.max()

    return LImage

def SaccadeControl_new(rFEFm, FEFfix, FinishCounter, Step):
    '''
    Determining if the saccade should be run or not based on the rates of neurons in FEFm layer.
    If maximum value of FEFm neurons is bigger than a threshold, the new saccade coordinates will be
    calculated.

    params: rFEFm -- current firing rates of FEF Movement Layer
    '''

    CurSac = np.asarray([0, 0])
    NewSac = False
    LowResponse = 0.8
    if FinishCounter == -1:
        Max_Row, Max_Col = np.unravel_index(rFEFm.argmax(), rFEFm.shape)
        MaxFEFm = rFEFm[Max_Row, Max_Col]

        if MaxFEFm > ModelParam['SaccadeThreshold']:
            print(Highlight('\nAfter step ' + str(Step + 1) + ' Max(FEFm) = ' + str(MaxFEFm),
                            'Green', Bold=True))
            St = 'Max_Row = ' + str(Max_Row) + '\tMax_Col = ' + str(Max_Col)
            print(Highlight(St, 'Green', Bold=True))
            rFEFm[rFEFm < LowResponse * ModelParam['SaccadeThreshold']] = 0
            CurSac = CoG(rFEFm)
            print("Eye position should be on: ", np.round(CurSac + 1, 2))
            NewSac = True
            #FinishCounter = 20
            FEFfix.r = 1.0
    else:
        FinishCounter -= 1
    return FinishCounter, NewSac, CurSac


def TargetName(TNo):
    '''
    return proper name based on what already saved in object memory

    params: TNo -- integer of Target Number

    return: string containing corresponding name
    '''

    namePerNo = {0: "Yellow Crane", 1: "Green Crane", 2: "Green Race Car", 3: "Blue Book",
                 4: "Yellow Duck", 5: "Red Pencil", 6: "Blue Pencil", 7: "Green Pencil",
                 8: "Dummy", 9: "Painting", 10: "Red Car", 11: "Green Car", 12: "Teddy Bear",
                 13: "Yellow Truck", 14: "Green Ball"}

    return namePerNo[TNo]


def waitTillExecuted(annarInterface, ID, timeout = -1):
    '''
    wait until one action in VR would be executed

    params: annarInterface -- ANNarchy Interface
            ID             -- action ID
            timeout        -- default: -1 (function waits for the Action State. could be infinity!)

    return: actionState    -- Action State
    '''

    ret = False
    actionState = 0

    if timeout == -1:

        while actionState == 0:
            ret = annarInterface.checkActionExecState(ID)
            if ret:
                actionState = annarInterface.getActionExecState()
        return actionState

    # else
    start_time = time.time()
    dur = 0
    while (actionState == 0) and dur < timeout:
        dur = time.time() - start_time
        ret = annarInterface.checkActionExecState(ID)
        if ret:
            actionState = annarInterface.getActionExecState()

    if dur >= timeout:
        print("Timeout")

    return actionState