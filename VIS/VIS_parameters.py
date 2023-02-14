"""
Loading Model Parameters

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import numpy as np
params = {}

# Weights
params['path_weightMat'] = '../VIS/Data/3obj_5rot_2size.mat'

# If you are using different weights, you can cange the layer size with the following 3 parameters:
params['objects'] = 3
params['sizes'] = 2
params['rotations'] = 5

## V1 Parameters
params['pV1C'] = 2.5

## V4L4 Parameters
params['vV1'] = 1.0
params['pE'] = 1
params['sigmaL4'] = 0.4
params['gHVA4'] = 1.066
params['vV24'] = 1.0
params['pV24'] = 1
params['vFEFvm'] = 4.0
params['vFEAT1'] = 3.0
params['pFEAT1'] = 3
params['vFEAT2'] = 2.0
params['pFEAT2'] = 2
params['vSP1'] = 0.85
params['pSP1'] = 1
params['vSP2'] = 1
params['pSP2'] = 1
params['vSUR1'] = 0
params['pSUR1'] = 1
params['vSUR2'] = 2
params['pSUR2'] = 2

## V4L23 Parameters
params['p1'] = 4
params['p2'] = 0.25
params['sigmaL23'] = 1.0
params['gHVA2'] = 1.55
params['vV42'] = 1.0
params['vPFC'] = 1.75
params['pV42'] = 0.25

params['vLIP'] = 1.0
params['vSSP'] = 1.5

params['vLIP1'] = 1.0
params['vLIP2'] = 0.1
params['vSSP1'] = 1.0
params['vSSP2'] = 0.1

## FEF Parameters
params['sigmaFEF'] = 0.1
params['cFEF'] = 6
params['vlow'] = 0.2
params['vEv'] = 0.6
params['vSv1'] = 0.6
params['tauFEFm'] = 65
params['vFEFvm_m'] = 1.0
params['vSvm'] = 0.3
params['vSFix'] = 3
params['vSv2'] = 0.35
params['dogScalingFactor_FEFvm'] = 0.93

### Universal Parameters
params['tau'] = 10
params['learnedWeightsMode'] = False
params['resImg'] = (408, 308)

## Numbers of Neurons in the different areas
params['resVisual'] = (66, 50)
params['PFC_shape'] = ( (params['objects'] * params['sizes'] * params['rotations']), )
params['V1_shape'] = params['resVisual'] + (3, 16)
params['V4L4_shape'] = params['resVisual'] + params['PFC_shape']
params['V4L23_shape'] = (33, 25) + params['PFC_shape']
params['FEF_shape'] = params['resVisual']
params['FEFvm_shape'] = params['resVisual'] + (6,)
params['RF_V1_V4L4'] = params['PFC_shape'] + (11, 11) + params['V1_shape'][-2:]

### Projection Parameters
params['viewfield'] = np.array([10.3, 7.8])
params['degPerCell_V4L4'] = params['viewfield'] / params['resVisual']
params['degPerCell_V4L23'] = params['viewfield'] / params['V4L23_shape'][:2]
params['rfsize_V4p'] = [5, 5] * (params['degPerCell_V4L4']
                                 / params['degPerCell_V4L23'])
params['sigma_RF_A_Feat'] = params['rfsize_V4p'] / 3

params['FBA_delay'] = 2
params['FEFv_delay'] = 7
params['RFsize4_23'] = [5, 5]
params['RFsigma4_23'] = [5. / 3, 5. / 3]

params['RFsizev_vm'] = [41, 31]
params['RFsigmav_vm'] = [4, 3]

# parameters of Amir's version
params['Input_V1C_Delay'] = 5.0 # Original value was 60, here set to 5 to speed things up.
params['Input_V1C_Weight'] = 1.0