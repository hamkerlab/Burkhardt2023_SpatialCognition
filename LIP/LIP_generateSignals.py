# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

# Loading parameters for LIP
from LIP_parameters import defParams

import math
import numpy
import sys
NO_STIM = sys.float_info.max

def generateEPsignal(SaccStart, SaccTarget, SaccOnset, SaccDur, duration):
    """
    generate eye position signal over time

    Parameters
    ----------
    SaccStart, SaccTarget : numpy array of 2 floats
        saccade start and target      
    SaccOnset : integer
        timestep of saccade onset
    SaccDur : integer
        saccade duration
    duration : integer
        duration of simulation

    Returns
    -------
    ep_sig : 3d numpy array
        eye position signal over time
    """

    precalcParam = {'iep_undershoot': numpy.array([0, 0])}

    size_w = defParams['layer_size_w']
    size_h = defParams['layer_size_h']

    # timstep of saccade offset
    SaccOffset = SaccOnset + SaccDur

    # timestep of EP update from fixation point to saccade target
    t_EP_update = SaccOffset + defParams['EP_update']
    # bounded between 0 and duration
    t_EP_update = min(max(0,t_EP_update), duration)

    # suppression during saccade
    suppMap = numpy.ones(duration)  # suppression factor during saccade
    if not defParams['EP_noSuppression']:
        # timstep of suppression onset
        t_EP_supp_on  = SaccOffset + defParams['EP_supp_on']
        # bounded between 0 and duration
        t_EP_supp_on = min(max(0,t_EP_supp_on), duration)
        # timstep of suppression offset
        t_EP_supp_off = SaccOffset + defParams['EP_supp_off']
        # bounded between 0 and duration
        t_EP_supp_off = min(max(0,t_EP_supp_off), duration)
        suppMap[t_EP_supp_on+1:t_EP_supp_off] = defParams['EP_supp_strength']

    # initialize signal
    ep_sig = numpy.zeros((duration, size_w, size_h))   # eye position signal

    # eye position at fixation point
    ep_sig[0:] = esig2d(size_w, size_h, SaccStart, defParams['EP_sigma'], precalcParam['iep_undershoot'], defParams['EP_strength'])

    # add gaussian decay onto fixation point after saccade
    tdecay = numpy.arange(t_EP_update, duration)
    factor = numpy.exp(-(tdecay-t_EP_update)*(tdecay-t_EP_update)/(2.0*defParams['EP_off_decay_gaussian']*defParams['EP_off_decay_gaussian']))
    ep_sig[tdecay] *= (factor* numpy.ones((size_h, size_w, 1))).T

    # eye position at saccade target
    ep_sig[t_EP_update:] += esig2d(size_w, size_h, SaccTarget, defParams['EP_sigma'], precalcParam['iep_undershoot'], defParams['EP_strength'])

    # add suppression
    ep_sig *= (suppMap * numpy.ones((size_h, size_w, 1))).T

    ## finished ##

    return ep_sig

def generateAttentionSignal(attention, duration):
    """
    generate attention signal over time

    Parameters
    ----------
    attention : list of dictionary
        attention definition containing 'name': string, 'position': numpy array of 2 floats,
        'starttime': integer and possible 'endtime': integer
    duration : integer
        duration of simulation

    Returns
    -------
    att_sig : 3d numpy array
        attention signal over time
    """

    precalcParam = {'att_undershoot': numpy.array([0, 0])}

    size_w = defParams['layer_size_w']
    size_h = defParams['layer_size_h']

    # initialize signal
    att_sig  = numpy.zeros((duration, size_w, size_h))     # attention (on Xh) signal

    # calculation of top-down attention signal for each attention position
    for att in attention:
        # onset of attention
        startAtt = att['starttime']
        # offset of attention (defined offset or attention until end)
        endAtt = att.get('endtime', duration)

        # add top-down attention signal for this attention position
        att_sig[startAtt:endAtt] += esig2d(size_w, size_h, att['position'], defParams['att_sigma'],
                                           precalcParam['att_undershoot'], defParams['att_strength'])

    return att_sig

#############################
#### auxiliary functions ####
#############################
def esig2d(width, height, ep, sigma, undershoot, strength):
    """
    Returns an internal eye position / attention signal given the head-centered eye / attention position in degrees.
    see Eq 5: r^X_PC_PC,in = strength_PC * exp(...) in Ziesche&Hamker (2011)

    Parameters
    ----------
    width, height : integer
        size of population        
    ep : numpy array of 2 floats
        head-centered eye / attention position       
    sigma : float
        width of signal       
    undershoot : numpy array of 2 floats
        undershoot if internal signal is disturbed
    strength : float
        strength of signal

    Returns
    -------
    X_PC : numpy array
        eye position / attention signal for given position
    """

    # add undershoot to ep if internal eye position signal is disturbed
    ep += undershoot

    idxs_w = numpy.arange(width)
    distances_w = ep[0]-idx_to_deg(idxs_w, width, defParams['v_w'])
    summand_w = (distances_w*distances_w).reshape(width, 1)
    idxs_h = numpy.arange(height)
    distances_h = ep[1]-idx_to_deg(idxs_h, height, defParams['v_h'])
    summand_h = (distances_h*distances_h).reshape(1, height)

    X_PC = strength*numpy.exp(-(summand_w + summand_h)/(2.0*sigma*sigma))

    return X_PC

def idx_to_deg(i, size, vf):
    """
    Maps neuron to a position in visual space (width or height)

    Parameters
    ----------
    i : integer
        index of neuron
    size : integer
        size of population
    vf : integer
        size of visual field

    Returns
    -------
    deg : float
        maped position
    """
    deg = vf*(i/(size-1)-0.5)    
    return deg
