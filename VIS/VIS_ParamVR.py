"""
Define all parameters which are needed to general things of the model. Many of them are hard coded.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import time
from datetime import date
import numpy as np

# Defining the model parameters as fields of a dictionary
ModelParam = {}

## Parameters Related to Loading pred-defined data and Saving the Results ##
# directory which contains all required data (Weight file, Target Pictures, etc.)
ModelParam['DataDir'] = '../VIS/Data/'

# Path for all kind of saved files as results
ModelParam['ResultDir'] = 'Results/Results_%s_%s/' % (date.today(), time.asctime(time.localtime(time.time())).split()[3])

# save all rates in mat files
ModelParam['Save_All_Values'] = False
if ModelParam['Save_All_Values']:
    for s in ['SaveValuesrV1C', 'SaveValuesPFC', 'SaveValuesHVA23', 'SaveValuesHVA4',
              'SaveValuesFEFv', 'SaveValuesFEFvm', 'SaveValuesFEFm']:
        ModelParam[s] = True
else:
    # Set what you want to save! Note that ModelParam['Save_All_Values'] should be False.
    ModelParam['SaveValuesrV1C'] = False
    ModelParam['SaveValuesPFC'] = False
    ModelParam['SaveValuesHVA23'] = False
    ModelParam['SaveValuesHVA4'] = False
    ModelParam['SaveValuesFEFv'] = False
    ModelParam['SaveValuesFEFvm'] = False
    ModelParam['SaveValuesFEFm'] = False

# Only HVA Layer 4 and HVA Layer 2/3 could be saved on separate files as image files
# If you  want to visualize other populations, set ModelParam['SaveImagesInOneFile'] or
# ModelParam['Make_Movie'] to True.
ModelParam['SaveImageHVA23'] = False
ModelParam['SaveImageHVA4'] = False
ModelParam['SaveImageV1C'] = False

# static images used for movie frames
#ModelParam['BG_Filename'] = 'forMovie/background_mc_R4c_small2.png'
ModelParam['BG_Filename'] = 'forMovie/conceptR3_Old.png'
ModelParam['Sacc_Sign_Filename'] = 'Sacc_Sign.png'
# make a movie after end of simulations based on saved images
ModelParam['Make_Movie'] = False
# global counter to count the frames for making movie
ModelParam['Movie_Frame'] = -1
# name of the movie file
ModelParam['Movie_Filename'] = 'Movie_'
# If you want to see the results of the simulation for all layers in one png files but do not want
# to create any movie, set this to True AND ModelParam['Make_Movie'] to False.
ModelParam['SaveImagesInOneFile'] = True
# ModelParam['OutputFileName'] = 'Results_withReset_'
ModelParam['OutputFileName'] = 'Results_NonReset_'

## Network  Parameters ##
ModelParam['Sim_Env'] = 'VR'    # VR means Virtual Reality
# resolution of input image (Visual Field) in [Width, Height, 3] for RGB images
ModelParam['resIm'] = [408, 308, 3]
# Size of the kernel for Gabor filter.
ModelParam['kernelSizes'] = np.asarray([9., 9.])
ModelParam['kernelSizesReal'] = np.asarray([9., 9.])
# size of Visual Field in pixels (added by juschu)
ModelParam['VF_px'] = np.asarray([(ModelParam['resIm'][0]-ModelParam['kernelSizes'][0]+1),
                                  (ModelParam['resIm'][1]-ModelParam['kernelSizes'][1]+1)])
# Pixel per Degree
ModelParam['PxperDeg'] = 4.
# size of Visual Field in degree (changed by beuth&juschu)
ModelParam['VF_Deg'] = ModelParam['VF_px'] / ModelParam['PxperDeg']

# Pooling Operation: No pooling (0), Max Pooling (1), Lanczos3 by Matlab (2), Bilinear (3),
# Lanczos3 by Amir (4)
ModelParam['enablePoolingV1'] = 4
# If ModelParam['enablePoolingV1'] != 0 then this parameter is used for Pooling function
ModelParam['poolFactor'] = 6
# type of Kernel for imresize function in Pooling
ModelParam['imresize_Kernel'] = 'Lanczos3'

# If True, the Neural Network will be reset after each saccade.
ModelParam['Net_Reset'] = False


ModelParam['SaccadeThreshold'] = 0.80

# Time of end of simulation
ModelParam['tEnd'] = 600
# Time of reseting the inputs
ModelParam['tReset'] = 0

ModelParam['LMSinput'] = 0
ModelParam['FastTest'] = 0
ModelParam['FilterBankV1'] = 1
ModelParam['N'] = 1
ModelParam['v1RFsizeDeg'] = 0.45
# This parameter is used to postpone the next Visual Field for some miliseconds.
ModelParam['FEFmDecayDelay'] = 100
# The time interval for updating the Visual Field during saccade.
ModelParam['NewVF_DuringSacc_Time'] = 100
# True means in Debug mode. I use this mode for comparing the model with the Matlab version.
ModelParam['Debug_Mode'] = False