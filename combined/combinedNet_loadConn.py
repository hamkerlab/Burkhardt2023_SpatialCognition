# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import sys
import ANNarchy as ANN

# first import LIP, then VIS 
# important for loading connections!

# network of LIP
sys.path.append('../LIP/')
import LIP_network_loadConn as LIP_
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

# Loading connections
print("load connections between LIP and VIS ")
projLIP_VIS = set()

# load connections from file
saveDirConn = defParams['saveConnAt'] + '/'

# Connect FEFm (66*50) with X_FEF (21*16*21*16) as eye-centered CD signal
FEFm_X_FEF = ANN.Projection(
    pre=VIS.FEFm,
    post=LIP_.X_FEF_Pop,
    target='CD'
)
projName = FEFm_X_FEF.pre.name + '-' + FEFm_X_FEF.post.name + '-' + FEFm_X_FEF.target
print(" - load", projName)
FEFm_X_FEF.connect_from_file(filename=saveDirConn+projName+'.data')
projLIP_VIS.add(FEFm_X_FEF)


# Connect FEFm (66*50) with LIP (21*16*21*16) as spatial attention on ST
FEFm_LIP_EP = ANN.Projection(
    pre=VIS.FEFm,
    post=LIP_.LIP_EP_Pop,
    target='FEF'
)
projName = FEFm_LIP_EP.pre.name + '-' + FEFm_LIP_EP.post.name + '-' + FEFm_LIP_EP.target
print(" - load", projName)
FEFm_LIP_EP.connect_from_file(filename=saveDirConn+projName+'.data')
projLIP_VIS.add(FEFm_LIP_EP)

FEFm_LIP_CD = ANN.Projection(
    pre=VIS.FEFm,
    post=LIP_.LIP_CD_Pop,
    target='FEF'
)
projName = FEFm_LIP_CD.pre.name + '-' + FEFm_LIP_CD.post.name + '-' + FEFm_LIP_CD.target
print(" - load", projName)
FEFm_LIP_CD.connect_from_file(filename=saveDirConn+projName+'.data')
projLIP_VIS.add(FEFm_LIP_CD)


# Connect LIP (21*16*21*16) with FEFv (66*50) as spatial attention
LIP_EP_FEFv = ANN.Projection(
    pre=LIP_.LIP_EP_Pop,
    post=VIS.FEFv,
    target='LIP1'
)
projName = LIP_EP_FEFv.pre.name + '-' + LIP_EP_FEFv.post.name + '-' + LIP_EP_FEFv.target
print(" - load", projName)
LIP_EP_FEFv.connect_from_file(filename=saveDirConn+projName+'.data')
projLIP_VIS.add(LIP_EP_FEFv)

LIP_CD_FEFv = ANN.Projection(
    pre=LIP_.LIP_CD_Pop,
    post=VIS.FEFv,
    target='LIP2'
)
projName = LIP_CD_FEFv.pre.name + '-' + LIP_CD_FEFv.post.name + '-' + LIP_CD_FEFv.target
print(" - load", projName)
LIP_CD_FEFv.connect_from_file(filename=saveDirConn+projName+'.data')
projLIP_VIS.add(LIP_CD_FEFv)


# Connect first two dimensions of V4L23 (33*25*x) with first two dimension of LIP (21*16*21*16)
# via AuxE Population
AuxE_LIP_EP = ANN.Projection(
    pre=VIS.AuxE,
    post=LIP_.LIP_EP_Pop,
    target='V4'
)
projName = AuxE_LIP_EP.pre.name + '-' + AuxE_LIP_EP.post.name + '-' + AuxE_LIP_EP.target
print(" - load", projName)
AuxE_LIP_EP.connect_from_file(filename=saveDirConn+projName+'.data')
projLIP_VIS.add(AuxE_LIP_EP)

AuxE_LIP_CD = ANN.Projection(
    pre=VIS.AuxE,
    post=LIP_.LIP_CD_Pop,
    target='V4'
)
projName = AuxE_LIP_CD.pre.name + '-' + AuxE_LIP_CD.post.name + '-' + AuxE_LIP_CD.target
print(" - load", projName)
AuxE_LIP_CD.connect_from_file(filename=saveDirConn+projName+'.data')
projLIP_VIS.add(AuxE_LIP_CD)