# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import math
import sys
import ANNarchy as ANN

# network of LIP
sys.path.append('../LIP/')
from LIP_connectionPattern import gaussian2dTo4d_h, gaussian4dTo2d_h
import LIP_network as LIP_
from LIP_parameters import defParams
projLIP_Net = set(ANN.projections())
popLIP_Net = set(ANN.populations())

# network of VIS
sys.path.append('../VIS/')
import VIS_Network as VIS
projVISNet = set(ANN.projections()).difference(projLIP_Net)
popVISNet = set(ANN.populations()).difference(popLIP_Net)

# network of SM
sys.path.append('../SM/')
import SM_network as SM
projSM = set(ANN.projections()).difference(projVISNet).difference(projLIP_Net)
popSM = set(ANN.populations()).difference(popVISNet).difference(popLIP_Net)


print("create connections between LIP and VIS")
projLIP_VIS = set()

# Connect FEFm (66*50) with X_FEF (21*16*21*16) as eye-centered CD signal
FEFm_X_FEF = ANN.Projection(
    pre=VIS.FEFm,
    post=LIP_.X_FEF_Pop,
    target='CD'
).connect_with_func(method=gaussian2dTo4d_h, mv=defParams['K_FEFm_X_FEF'],
                    radius=defParams['sigma_FEFm_X_FEF']/float(defParams['v_w']), delay=5)
projLIP_VIS.add(FEFm_X_FEF)


# Connect FEFm (66*50) with LIP (21*16*21*16) with gaussian pattern as spatial attention on ST
FEFm_LIP_EP = ANN.Projection(
    pre=VIS.FEFm,
    post=LIP_.LIP_EP_Pop,
    target='FEF'
).connect_with_func(method=gaussian2dTo4d_h, mv=defParams['K_FEFm_LIP_EP'],
                    radius=defParams['sigma_FEFm_LIP_EP']/float(defParams['v_w']), delay=5)
projLIP_VIS.add(FEFm_LIP_EP)

FEFm_LIP_CD = ANN.Projection(
    pre=VIS.FEFm,
    post=LIP_.LIP_CD_Pop,
    target='FEF'
).connect_with_func(method=gaussian2dTo4d_h, mv=defParams['K_FEFm_LIP_CD'],
                    radius=defParams['sigma_FEFm_LIP_CD']/float(defParams['v_w']), delay=5)
projLIP_VIS.add(FEFm_LIP_CD)


# Connect LIP (21*16*21*16) with FEFv (66*50) with gaussian pattern as spatial attention
LIP_EP_FEFv = ANN.Projection(
    pre=LIP_.LIP_EP_Pop,
    post=VIS.FEFv,
    target='LIP1'
).connect_with_func(method=gaussian4dTo2d_h, mv=0.1, radius=1.0/20, delay=5)
projLIP_VIS.add(LIP_EP_FEFv)

LIP_CD_FEFv = ANN.Projection(
    pre=LIP_.LIP_CD_Pop,
    post=VIS.FEFv,
    target='LIP2'
).connect_with_func(method=gaussian4dTo2d_h, mv=0.1, radius=1.0/20, delay=5)
projLIP_VIS.add(LIP_CD_FEFv)


# Connect first two dimensions of V4L23 (33*25*x) with first two dimension of LIP (21*16*21*16)
# with gaussian pattern via AuxE Population
AuxE_LIP_EP = ANN.Projection(
    pre=VIS.AuxE,
    post=LIP_.LIP_EP_Pop,
    target='V4'
).connect_with_func(method=gaussian2dTo4d_h, mv=0.5, radius=0.5/32, delay=5)
projLIP_VIS.add(AuxE_LIP_EP)

AuxE_LIP_CD = ANN.Projection(
    pre=VIS.AuxE,
    post=LIP_.LIP_CD_Pop,
    target='V4'
).connect_with_func(method=gaussian2dTo4d_h, mv=0.5, radius=0.5/32, delay=5)
projLIP_VIS.add(AuxE_LIP_CD)