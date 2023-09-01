"""
Network definition of the Visual Attention Model

It is an ANNarchy-Python version of the original model and has been adapted for Spacecog. The original model is published in:
Beuth, F. (2019). Visual attention in primates and for machines - neuronal mechanisms. Doctoral dissertation, Technische Universität Chemnitz, Germany. Chapter 4.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

from scipy.io import loadmat
import numpy as np

from ANNarchy import Neuron, Population, Projection, CSR
from ANNarchy.extensions.convolution import Pooling, Convolution
from VIS_parameters import params
from VIS_functions import rangeX, Gaussian2D, positive
from VIS_Connections import one_to_dim, con_scale


##########################################
##########  NEURON DEFINITION   ##########
##########################################

## Neuron of V1 population: Applies the power rule to the given baseline input
# See Eq 4.29
AuxV1_Neuron = Neuron(
    name='AuxV1_Neuron',
    parameters="""
        pV1C = 'pV1C' : population
    """,
    equations="""
        r = pow(sum(exc), pV1C)
    """,
    extra_values=params
)

## Neuron of Layer 4 in Area V4: Receives Input from V1, V4L23, and FEFvm
# See Eq 4.30-4.32 / 4.35-4.37 / 4.41
V4L4_Neuron = Neuron(
    name='V4L4_Neuron',
    parameters="""
        sigmaL4 = 'sigmaL4' : population
        gHVA4 = 'gHVA4' : population
        tau = 'tau' : population
        vV1 = 'vV1' : population
        vFEFvm = 'vFEFvm' : population
        vV24 = 'vV24' : population
        pV24 = 'pV24' : population
        vLIP = 'vLIP' : population
        vF1 = 'vFEAT1' : population
        pF1 = 'pFEAT1' : population
        pE = 'pE' : population
        vSP1 = 'vSP1' : population
        vSUR1 = 'vSUR1' : population
    """,
    equations="""
        E = pow(vV1*clip(sum(exc), 0, 1), pE)
        ASP = vFEFvm*sum(A_SP)
        AFEAT = vV24*pow(sum(A_FEAT), pV24)
        ALIP = vLIP*(sum(LIP))
        A = 1 + ASP + AFEAT + ALIP
        SFEAT = pow(vF1*clip(sum(S_FEAT), 0, 1), pF1)
        SSP = vSP1*sum(S_SP)
        SSUR = vSUR1*sum(S_SUR)
        S = E*(A+SFEAT+SSP+SSUR)
        EA = E * A
        A_S = A / (sigmaL4 + S)
        EA_S = E * A / (sigmaL4 + S)
        tau * dr /dt = -r + gHVA4 * E * A / (sigmaL4 + S)
    """,
    extra_values=params
)

## Neuron of Layer 2/3 in Area V4: Receives Input from V4L4, and PFC
# See Eq 4.48-4.50
V4L23_Neuron = Neuron(
    name='V4L23_Neuron',
    parameters="""
        sigmaL23 = 'sigmaL23' : population
        gHVA2 = 'gHVA2' : population
        tau = 'tau' : population
        pV42 = 'pV42' : population
        vV42 = 'vV42' : population
        vPFC = 'vPFC' : population
        vLIP = 'vLIP' : population
        vLIP1 = 'vLIP1' : population
        vLIP2 = 'vLIP2' : population
        vSSP = 'vSSP' : population
    """,
    equations="""
        ALIP = vLIP1*sum(LIP1) + vLIP2*sum(LIP2)
        A = pow(vV42*sum(exc), pV42) * (1 + vPFC*sum(A_PFC) + vLIP*ALIP)
        S = pow(vV42*sum(exc), pV42) * (1 + vPFC*sum(A_PFC) + vLIP*ALIP + vSSP*sum(SSP))
        tau * dr /dt = -r + gHVA2 * A / (sigmaL23 + S) : max = 1.0
    """,
    extra_values=params
)

## Neuron of visual Layer in FEF: Receives Input from V4L23
# See Eq 4.53-4.60
FEFv_Neuron = Neuron(
    name='FEFv_Neuron',
    parameters="""
        tau = 'tau' : population
        sigmaFEF = 'sigmaFEF' : population
        c = 'cFEF' : population
        vExc = 0.55 : population
        vLIP1 = 0.75 : population
        vLIP2 = 0.1 : population
    """,
    equations="""
        ALIP = vLIP1*sum(LIP1) + vLIP2*sum(LIP2)
        AFEAT = vExc*sum(exc)
        E = vExc*sum(exc) + ALIP
        q = (E * (1 + sigmaFEF) / (E + sigmaFEF))
        tau * dr /dt = -r + pos(q * (1 + c) - c)
    """,
    extra_values=params
)

## Neuron of visuo-motoric Layer in FEF: Receives Input from FEFv and FEFm
# See Eq 4.61-4.64
FEFvm_Neuron = Neuron(
    name='FEFvm_Neuron',
    parameters="""
        tau = 'tau' : population
        vlow = 'vlow' : population
        vEv = 'vEv' : population
        vSv1 = 'vSv1' : population
        vFEFv = 1.0
    """,
    equations="""
        ES = clip(vEv*sum(E_v)-vSv1*sum(S_v),0,1)
        E = vlow * pos(vEv*sum(E_v)) + (1-vlow) * ES
        tau * dr /dt = -r + vFEFv * E + (1-vFEFv) * sum(E_m)
    """,
    extra_values=params
)

## Neuron of motoric Layer in FEF: Receives Input from FEFvm and FEFfix
# See Eq 4.68-4.71
FEFm_Neuron = Neuron(
    name='FEFm_Neuron',
    parameters="""
        tau = 'tauFEFm' : population
        vFEFvm = 'vFEFvm_m' : population
        vSvm = 'vSvm' : population
        vSFix = 'vSFix' : population
    """,
    equations="""
        svm = sum(vm)
        tau * dr /dt = -r + vFEFvm*sum(vm) - vSvm*max(svm) - vSFix*sum(fix): min=0.0
    """,
    extra_values=params
)

## Input Neuron: Has to be set to value. Does not change over time.
Inp_Neuron = Neuron(name='Input_Neuron', parameters="r = 0.0")

## Basic Auxillary Neuron is transmitting an unmodified input
Aux_Neuron = Neuron(name='Aux_Neuron', equations="""r = sum(exc)""")

##########################################
######### POPULATION DEFINITION  #########
##########################################
# juschu: Input Population of Amir's version
V1 = Population(params['V1_shape'], Inp_Neuron, name='V1')
AuxV1 = Population(params['V1_shape'], AuxV1_Neuron, name='AuxV1')
V4L4 = Population(params['V4L4_shape'], V4L4_Neuron, name='V4L4')
V4L23 = Population(params['V4L23_shape'], V4L23_Neuron, name='V4L23')
FEFv = Population(params['FEF_shape'], FEFv_Neuron, name='FEFv')
FEFvm = Population(params['FEFvm_shape'], FEFvm_Neuron, name='FEFvm')
FEFm = Population(params['FEF_shape'], FEFm_Neuron, name='FEFm')
PFC = Population(params['PFC_shape'], Inp_Neuron, name='PFC')
AuxA = Population(params['resVisual'], Aux_Neuron, name='AuxA')
AuxE = Population(params['V4L23_shape'][:2], Aux_Neuron, name='AuxE')
FEFfix = Population(name='FEFfix', geometry=1, neuron=Inp_Neuron)

##########################################
######### CONNECTION DEFINITION  #########
##########################################
## Connection for V1 (V1 -> AuxV1) 
# juschu: connection of Amir's version
# V1 contains the beforehand-calculated LGN/V1 responses and the connection is used to applying delay and non-linearity.
V1_Proj = Projection(pre=V1, post=AuxV1, target='exc')
V1_Proj.connect_one_to_one(weights=params['Input_V1C_Weight'], delays=params['Input_V1C_Delay'])

## Connection of V1 -> V4/IT L4
# load the pretrained weights and transform it into a 4D Bank of Filters
weightData = loadmat(params['path_weightMat'])
W = np.array(weightData['W'], dtype='float32')
FilterBank = np.swapaxes(np.reshape(W, params['RF_V1_V4L4'], order='F'), 1, 2)

ssList14 = []
Center = [(n - 1) // 2 for n in params['V1_shape'][-2:]]
for Row, Col in rangeX(params['V4L4_shape'][:2]):
    ssList14.append([Row, Col] + Center)
# create the convolution Projection
# juschu: use delay and padding of Amir's version
V1_V4L4 = Convolution(AuxV1, V4L4, target='exc')
V1_V4L4.connect_filters(weights=FilterBank, delays=5.0,# padding='border',
                        subsampling=ssList14)

## Connection of the V4/IT Populations, L4 => L2/3 (excitatory)
# The weight is a 3x3 Gaussian with maximum 1, width (sigma) 1
w42 = Gaussian2D(1.0, params['RFsize4_23'], params['RFsigma4_23'])[:, :, None]
w42 /= w42.sum()
pspText = 'w*pow(pre.r, {p1})'.format(**params)
ssList42 = []
for Row, Col, Plane in rangeX(params['V4L23_shape']):
    ssList42.append([Row * 2 + 1, Col * 2 + 1, Plane])
V4L4_V4L23 = Convolution(V4L4, V4L23, target='exc', psp=pspText)
V4L4_V4L23.connect_filter(weights=w42, keep_last_dimension=True,
                          subsampling=ssList42)

## Connection of the V4/IT Populations, L2/3 => L4 (feature-based amplification)
# The weight is a 3x3 Gaussian with maximum 1, width (sigma) 0.6
w24 = Gaussian2D(1.0, [3, 3], params['sigma_RF_A_Feat'])[:, :, None]
ssList24 = []
for Row, Col, Plane in rangeX(params['V4L4_shape']):
    ssList24.append([Row // 2, Col // 2, Plane])
V4L23_V4L4A = Convolution(V4L23, V4L4, target='A_FEAT', operation='max')
V4L23_V4L4A.connect_filter(weights=w24, delays=params['FBA_delay'],
                           keep_last_dimension=True, subsampling=ssList24)

## Connection of the V4/IT Populations, L2/3 => L4 (feature-based suppression)
# The previous weights are used, but calculating another post-synaptic
# potential. See Eq 4.39-4.41
pspText = 'pow(w*({vFEAT2}*pre.r), {pFEAT2})'.format(**params)

if 'AH' in weightData.keys():
    # Use the trained AH-Matrix, if it exists.
    AH = weightData['AH']
elif 'OM' in weightData.keys():
    # generate AH from OM if its not existing (as in previous models)
    OM = np.array(weightData['OM'], dtype='float32')
    # Inhibition for all cells that do not code the object. If multple cells
    # encode the same object divide by their number.
    with np.errstate(divide='ignore', invalid='ignore'):
        AH = np.tile(1.0 / OM.sum(axis=0), [params['V4L23_shape'][-1], 1])
    AH[AH == np.inf] = 0.0
    # Prevent inhibition of same object cells (& self-inhibition)
    for o in OM:
        os = np.argwhere(o).flatten()
        AH[np.ix_(os, os)] = 0.0
AH = AH[:, None, None, :]
lid = params['V4L4_shape'][-1]
V4L23_V4L4SFE = Convolution(V4L23, V4L4, target='S_FEAT', psp=pspText)
V4L23_V4L4SFE.connect_filters(weights=AH, subsampling=ssList24[(lid-1)//2::lid])

## Connection of the V4/IT Populations, L2/3 => L4 (spatial supp.)
# A difference of Gaussians is used as weight
wPos = Gaussian2D(1.0, [13, 13], [3, 3])
wNeg = Gaussian2D(2.0, [13, 13], [1.5, 1.5])
wDoG = (positive(wPos - wNeg) / np.sum(positive(wPos - wNeg)))[:, :, None]
V4L23_V4L4SUR = Convolution(V4L23, V4L4, target='S_SUR')
V4L23_V4L4SUR.connect_filter(weights=wDoG, keep_last_dimension=True,
                             subsampling=ssList24)

## Connection from V4/IT L2/3 to FEF visual (excitatory)
# The auxiliary population is used to pool the down-sampled V4L23 Population.
# Afterwards it could be up-sampled again. The combination of the two is
# currently not possible in ANNarchy
# juschu: removed delay
ssList2v = ssList24[9::params['V4L4_shape'][-1]]
V4L23_AuxE = Pooling(V4L23, AuxE, target='exc', operation='max')
V4L23_AuxE.connect_pooling(extent=(1, 1) + params['PFC_shape'])
AuxE_FEFv = Projection(AuxE, FEFv, target='exc')
AuxE_FEFv.connect_with_func(con_scale, factor=2)#, delays=params['FEFv_delay'])

## Connections from FEF visual to FEF visuo-motoric (exc and supp)
# A lowered Gaussian is used to simulate the combined responses
G = Gaussian2D(1.0, params['RFsizev_vm'], params['RFsigmav_vm'])
wvvm = np.tile((G - params['vSv2'])[None, :, :],
               (params['FEFvm_shape'][-1], 1, 1))
wvvm *= params['dogScalingFactor_FEFvm']**np.arange(6)[:, None, None]
# The plus sign(+) is needed, so that wvvm will not be overwritten
FEFv_FEFvmE = Convolution(FEFv, FEFvm, target='E_v')
FEFv_FEFvmE.connect_filters(weights=positive(+wvvm))
FEFv_FEFvmS = Convolution(FEFv, FEFvm, target='S_v')
FEFv_FEFvmS.connect_filters(weights=positive(-wvvm))

## Connection from FEF visuo-motoric to V4/IT L2/3 (amplification)
# The auxiliary population is used to pool FEFvm activities over different
# layers. Then a one to many connectivity is used. This combination is
# currently not possible in one step
FEFvm_AuxA = Pooling(FEFvm, AuxA, target='exc', operation='mean')
FEFvm_AuxA.connect_pooling(extent=(1, 1, params['FEFvm_shape'][-1]))
otmV4 = np.ones(params['V4L4_shape'][-1])[:, None, None]
AuxA_V4L4A = Convolution(AuxA, V4L4, target='A_SP')
AuxA_V4L4A.connect_filters(weights=otmV4)

## Connection of the V4/IT Populations, L2/3 => L4 (spatial suppression)
# A rectified inverse Gaussian is used as weight
G = Gaussian2D(1.0, [11, 9], [4, 3])
wSP = np.tile(positive(1 - G**0.125)[None, :, :], params['PFC_shape'] + (1, 1))
AuxA_V4L4S = Convolution(AuxA, V4L4, target='S_SP')
AuxA_V4L4S.connect_filters(weights=wSP)

## Connection from FEF visuo-motoric to FEF motoric (mean pooling)
FEFvm_FEFm = Pooling(FEFvm, FEFm, target='vm', operation='mean')
FEFvm_FEFm.connect_pooling(extent=(1, 1, params['FEFvm_shape'][-1]))

## Connection from FEF motoric to FEF visuo-motoric, distributing the activity
otmFEF = np.ones(params['FEFvm_shape'][-1])[:, None, None]
FEFm_FEFvm = Convolution(FEFm, FEFvm, target='E_m')
FEFm_FEFvm.connect_filters(weights=otmFEF)

## Connection from prefrontal Cortex to V4/IT L2/3 (layerwise amplification)
PFC_V4L23 = Projection(PFC, V4L23, target='A_PFC')
PFC_V4L23.connect_with_func(one_to_dim, postDim=2)

## Connection from FEFfix to FEF motoric
FEFfix_FEFm = Projection(FEFfix, FEFm, target='fix')
FEFfix_FEFm.connect_all_to_all(weights=1.0)