"""
    Part of ANNarchy-SM

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import numpy as np

def SM_BoundaryCueing(VBX_rt, VBY_rt, HD, Xag, Yag):
    # a simple routine to cue with the wall identity, which we assume the agent
    # can recognize. We determine the minimum distance to each wall (N,S,E,W)
    # and how many boundary points of each wall are visible. Both factors
    # contribute to the PRcue during perception, which drives the PR neurons.
    # This helps the model remove ambiguity in the simple 4 wall environment.

    R = np.array([[np.cos(HD), -np.sin(HD)], [np.sin(HD), np.cos(HD)]])
    tmp  = np.array([VBX_rt, VBY_rt])
    tmp2 = np.dot(R, tmp)               # matrix-vector multiplication (LG) -> (2x2) x (2xVB)
    Xtmp = tmp2[0, :] + Xag
    Ytmp = tmp2[1, :] + Yag
    Xtmp = Xtmp[ VBY_rt > 0] 
    Ytmp = Ytmp[ VBY_rt > 0]

    W = len(np.nonzero(Xtmp == 1)[0])   # amount of West wall pts
    E = len(np.nonzero(Xtmp==21)[0])    # amount of East wall pts
    S = len(np.nonzero(Ytmp==1)[0])     # amount of South wall pts
    N = len(np.nonzero(Ytmp==21)[0])    # amount of North wall pts

    if W>0:   W /= np.abs( np.min(Xtmp[Xtmp==1]) - Xag )   # the closer to the wall the more input
    if E>0:   E /= np.abs( np.min(Xtmp[Xtmp==21])- Xag )
    if S>0:   S /= np.abs( np.min(Ytmp[Ytmp==1]) - Yag )
    if N>0:   N /= np.abs( np.min(Ytmp[Ytmp==21])- Yag )

    totmax = np.amax([W, E, S, N])

    if totmax == 0:
        totmax = 1

    PRcue_percep = np.array([N, W, S, E]) * 50.0 / totmax
    
    return PRcue_percep
