"""
A biologically inspired model of saccade generator is implemented in this program. This program has a couple of functions which only one of them
(SaccadeGenerator) should be imported in the main file (expVR.py).

   Functions:
   - SaccadeGenerator()
   - SaccadeGenerator2()

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

######################################################################################################################################################
#   A biologically inspired model of saccade generator is implemented in this program. This program has a couple of functions which only one of them
#   (SaccadeGenerator) should be imported in the main file (expVR.py).
#
#   ====================================================================================================
#   Functions:
#   - SaccadeGenerator()
#   - SaccadeGenerator2()
#   ====================================================================================================

import numpy as np
import math

######################################################################################################################################################
#   This function receives the start and stop point of the saccade and calculates the saccade trajectory points.
#   
#   Input Parameter(s):
#   - SaccStart: Coordinates of the start point of the saccade in visual fiels (in pixel).
#   - SaccStop : Coordinates of the stop  point of the saccade in visual fiels (in pixel).
#   - PxperDeg : Pixel per Degree.
#
#   Return Value(s):
#   - exePos   : A dictionary contains a list of time and corresponding coordinates of the saccade.
def SaccadeGenerator(SaccStart, SaccStop, PxperDeg, MinSpeed = 22, MinDistance = 0.05, saccadeEndBySpeed = False):

    # The statement 'saccadeEndBySpeed = False' means the end of saccade will be calculated by eye position
    # The statement 'saccadeEndBySpeed = True'  means the end of saccade will be calculated by eye speed

    eyePos = {}                                                         # Eye position over time during saccade

    eye0 = SaccStart / PxperDeg
    eye1 = SaccStop / PxperDeg
    
    SaccAmp = np.linalg.norm(eye1 - eye0)                               # Saccade Amplitude in degree

    # we use the extended model from WetterOpstal
    #vpk = 0.525                                                        # The original value used in WetterOpstal paper
    m0 = 7.0
    vpk = (750 * (1 - math.exp(-SaccAmp / 16)) + 50 ) / 1000.           # The value calculated by Alex and Frederik based on their own data
    print("vpk =", vpk)
    print("Saccade Amplitude =", SaccAmp)
    
    saccDur = 0
    sac_has_ended = False

    if(SaccAmp==0):
        # fixation point and saccade target are equal
        sac_has_ended = True
    else:
        direction = 1 / np.linalg.norm(eye1 - eye0) * (eye1 - eye0)     # The direction of saccade
        A = 1.0 / (1.0 - math.exp(-SaccAmp / m0))
    
    currentTimestep = 0
    currentEyepos = eye0
    eyePos[currentTimestep] = eye0
    
    while (not sac_has_ended):
    
        currentTimestep += 1    
        
        previousEyepos = currentEyepos
        currentEyepos = eye0 + direction*(m0 * math.log((A * math.exp(vpk * currentTimestep / m0)) / (1.0 + A * math.exp((vpk * currentTimestep - SaccAmp)/m0))))
        
        # detect saccade end       
        if saccadeEndBySpeed:
            # saccade end is calculated by eye speed
            current_eye_speed = np.linalg.norm(currentEyepos - previousEyepos)*1000      # one time step is one ms, so now "current_eye_speed" is in deg/sec
            if (current_eye_speed < MinSpeed):
                sac_has_ended = True
        else:
            # saccade end is calculated by position
            if (np.linalg.norm(currentEyepos - eye1) < MinDistance):
                sac_has_ended = True
                
        if(sac_has_ended):
            # saccade has ended
            eyePos[currentTimestep] = eye1
            saccDur = currentTimestep
        else:
            # saccade still ongoing
            eyePos[currentTimestep] = currentEyepos
            
    print("Saccade ended after", saccDur, "ms.")
    print("and goes from",eyePos[0],"to",eyePos[currentTimestep])
        
    return eyePos

######################################################################################################################################################
#   This function receives the start and stop point of the saccade and calculates the saccade trajectory points.
#   
#   Input Parameter(s):
#   - SaccStart: Coordinates of the start point of the saccade in visual fiels (in pixel).
#   - SaccStop : Coordinates of the stop  point of the saccade in visual fiels (in pixel).
#
#   Return Value(s):
#   - exePos   : A dictionary contains a list of time and corresponding coordinates of the saccade.
def SaccadeGenerator2(eye0, eye1, MinSpeed = 22, MinDistance = 0.05, saccadeEndBySpeed = False):

    # The statement 'saccadeEndBySpeed = False' means the end of saccade will be calculated by eye position
    # The statement 'saccadeEndBySpeed = True'  means the end of saccade will be calculated by eye speed

    eyePos = {}                                                         # Eye position over time during saccade
    
    SaccAmp = np.linalg.norm(eye1 - eye0)                               # Saccade Amplitude in degree

    # we use the extended model from WetterOpstal
    #vpk = 0.525                                                        # The original value used in WetterOpstal paper
    m0 = 7.0
    vpk = (750 * (1 - math.exp(-SaccAmp / 16)) + 50 ) / 1000.           # The value calculated by Alex and Frederik based on their own data
    print("vpk =", vpk)
    print("Saccade Amplitude =", SaccAmp)
    
    saccDur = 0
    sac_has_ended = False

    if(SaccAmp==0):
        # fixation point and saccade target are equal
        sac_has_ended = True
    else:
        direction = 1 / np.linalg.norm(eye1 - eye0) * (eye1 - eye0)     # The direction of saccade
        A = 1.0 / (1.0 - math.exp(-SaccAmp / m0))
    
    currentTimestep = 0
    currentEyepos = eye0
    eyePos[currentTimestep] = eye0
    
    while (not sac_has_ended):
    
        currentTimestep += 1    
        
        previousEyepos = currentEyepos
        currentEyepos = eye0 + direction*(m0 * math.log((A * math.exp(vpk * currentTimestep / m0)) / (1.0 + A * math.exp((vpk * currentTimestep - SaccAmp)/m0))))
        
        # detect saccade end       
        if saccadeEndBySpeed:
            # saccade end is calculated by eye speed
            current_eye_speed = np.linalg.norm(currentEyepos - previousEyepos)*1000      # one time step is one ms, so now "current_eye_speed" is in deg/sec
            if (current_eye_speed < MinSpeed):
                sac_has_ended = True
        else:
            # saccade end is calculated by position
            if (np.linalg.norm(currentEyepos - eye1) < MinDistance):
                sac_has_ended = True
                
        if(sac_has_ended):
            # saccade has ended
            eyePos[currentTimestep] = eye1
            saccDur = currentTimestep
        else:
            # saccade still ongoing
            eyePos[currentTimestep] = currentEyepos
            
    print("Saccade ended after", saccDur, "ms.")
    print("and goes from",eyePos[0],"deg to",eyePos[currentTimestep], "deg")
        
    return eyePos