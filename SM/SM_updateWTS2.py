"""
    Part of ANNarchy-SM
    This file contain implementation and comments of enocding objects in the SM model.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import numpy as np
from SM_network import nb_neurons_H, nb_neurons_BVC


def SM_updateWTS2(HDrate, OVCrate, Hrate, BVCrate, oPRrate, H2OVC, OVC2H, OVC2BVC, BVC2OVC, oPR2OVC, OVC2oPR, oPR2H, oPR2HD, H2oPR, step, OVC2oPR_inhib_phi):
    
    # update the following weights: 
    # OVC to PC, needed to trigger old SM imagery
    # (oPR to PC - optional) without this we don't have the problem of jumping in imagery due to a strong oID to PC connection
    # oPR to OVC  (does this reintroduce jumping?)
    # OVC to oPR - in order to be able to cue with RF and get object
    # oPR to HD - to resolve HD cueing but do not engage those weights under perception (suppose the are inhibited 
    #             by passing through interneurons which are silenced during perception as opposed to imagery)

    print('updating weights')
    #print(('time_' + str(step) + '_'))

    ## OVC2H weights

    OVC2Hwts_after = np.array( OVC2H.w )
    Hrate_for_update = np.matrix((Hrate > 0) * Hrate) #  because of negative activations
    OVCrate_for_update = np.matrix((OVCrate > 0) * OVCrate)

    OVCrate_thresh = 0.05 # Added for use with changed (3D) object coordinates
    OVCrate_for_update[ OVCrate_for_update < OVCrate_thresh ] = 0.0

    OVC_x_H_rate = np.dot( Hrate_for_update.T, OVCrate_for_update )
    OVC_x_H_rate = OVC_x_H_rate / (np.max(np.max(OVC_x_H_rate)))

    for dend in OVC2H.dendrites:
        tmp1_post, tmp1_pre = np.nonzero(OVC_x_H_rate[dend.post_rank, :] > 0.05) # individual rate threshold, specific to neuron type 
        if np.min(tmp1_pre.shape) > 0:
            OVC2Hwts_after[ dend.post_rank, tmp1_pre ] = np.array(dend.w)[ tmp1_pre ] + OVC_x_H_rate[ dend.post_rank, tmp1_pre ] 
            dend_w_array = OVC2Hwts_after[dend.post_rank, :]             
            dend.w = dend_w_array

    H2OVCwts_after = OVC2Hwts_after.T
    for dend in H2OVC.dendrites:
        dend_w_array = H2OVCwts_after[dend.post_rank, :]             
        dend.w = dend_w_array


    # Can only be unidirectional (OVCs to PCs) because otherwise OVC not
    # covered by an object remain permanently driven by the PC

    # Seems like the permanent OVC2H connection impedes the shift in PC to
    # reflect ongoing location.


    ## oPR2OVC and OVC2oPR weights

    OVC2oPRwts_after = np.array( OVC2oPR.w )
    oPRrate_for_update = np.matrix((oPRrate > 0) * oPRrate) # because of negative activations

    OVC_x_oPR_rate = np.dot( oPRrate_for_update.T, OVCrate_for_update )
    OVC_x_oPR_rate = OVC_x_oPR_rate / (np.max(np.max(OVC_x_oPR_rate)))
    OVC_x_oPR_rate[OVC_x_oPR_rate < 0.05] = 0

    for dend in OVC2oPR.dendrites:
        tmp1_post, tmp1_pre = np.nonzero(OVC_x_oPR_rate[dend.post_rank, :] > OVCrate_thresh) # test for use with changed (3D) object coordinates

        if np.min(tmp1_pre.shape) > 0:
            OVC2oPRwts_after[ dend.post_rank, tmp1_pre ] = np.array(dend.w)[ tmp1_pre ] + OVC_x_oPR_rate[ dend.post_rank, tmp1_pre ] 
            dend.w = OVC2oPRwts_after[dend.post_rank, :]

    # Generate OVC2oPRwts by transposing oPR2OVCwts:
    #for dend in oPR2OVC.dendrites:
    #    dend.w = OVC2oPRwts_after[:, dend.post_rank] 

    oPR2OVCwts_after = OVC2oPRwts_after.T
    for dend in oPR2OVC.dendrites:
        dend_w_array = oPR2OVCwts_after[dend.post_rank, :]             
        dend.w = dend_w_array


    ## oPR2H  weights

    oPR2Hwts_after = np.array( oPR2H.w )

    oPR_x_H_rate = np.dot( Hrate_for_update.T, oPRrate_for_update )
    oPR_x_H_rate = oPR_x_H_rate / (np.max(np.max(oPR_x_H_rate)))
   
    H_x_oPR_rate = oPR_x_H_rate.T

    for dend in oPR2H.dendrites:
        tmp1_post, tmp1_pre = np.nonzero(oPR_x_H_rate[dend.post_rank, :] > 0.2) # individual rate threshold, specific to neuron type

        if np.min(tmp1_pre.shape) > 0:
            oPR2Hwts_after[ dend.post_rank, tmp1_pre ] = np.array(dend.w)[ tmp1_pre ] + oPR_x_H_rate[ dend.post_rank, tmp1_pre ] 
            dend_w_array = oPR2Hwts_after[dend.post_rank, :]             
            dend.w = dend_w_array

    H2oPRwts_after = oPR2Hwts_after.T
    for dend in H2oPR.dendrites:
        dend_w_array = H2oPRwts_after[dend.post_rank, :]             
        dend.w = dend_w_array

    ## oPR to HD

    oPR2HDwts_after = np.array( oPR2HD.w )

    HDrate_for_update = np.matrix((HDrate > 0) * HDrate)
    oPR_x_HD_rate = np.dot( HDrate_for_update.T, oPRrate_for_update )
    oPR_x_HD_rate = oPR_x_HD_rate / (np.max(np.max(oPR_x_HD_rate)))

    
    HD_x_oPR_rate = oPR_x_HD_rate.T
  
    for dend in oPR2HD.dendrites:
        tmp1_post, tmp1_pre = np.nonzero(oPR_x_HD_rate[dend.post_rank, :] > 0.2) # individual rate threshold, specific to neuron type

        if np.min(tmp1_pre.shape) > 0:
            oPR2HDwts_after[ dend.post_rank, tmp1_pre ] = np.array(dend.w)[ tmp1_pre ] + oPR_x_HD_rate[ dend.post_rank, tmp1_pre ]   
            dend_w_array = oPR2HDwts_after[dend.post_rank, :]
            dend.w = dend_w_array 

    ## BVC2OVC, necessary to support OVC firing in imagery. the sole input from 1 oPR neuron is not enough

    BVC2OVCwts_after = np.array( BVC2OVC.w )
    OVCrate_for_update = np.matrix((OVCrate > 0) * OVCrate)         # Re-definition is necessary here, some values were set to zero above
    BVCrate_for_update = np.matrix((BVCrate > 0) * BVCrate)         # because of negative activations
    BVCrate_for_update[ BVCrate_for_update < 0.05] = 0

    BVC_x_OVC_rate = np.dot( OVCrate_for_update.T, BVCrate_for_update )
    BVC_x_OVC_rate = BVC_x_OVC_rate / (np.max(np.max(BVC_x_OVC_rate)))

    for dend in BVC2OVC.dendrites:
        tmp1_post, tmp1_pre = np.nonzero(BVC_x_OVC_rate[dend.post_rank, :] > 0.07) # individual rate threshold, specific to neuron type

        if np.min(tmp1_pre.shape) > 0:    
            BVC2OVCwts_after[ dend.post_rank, tmp1_pre ] = np.array(dend.w)[ tmp1_pre ] + BVC_x_OVC_rate[ dend.post_rank, tmp1_pre ] 
            dend_w_array = BVC2OVCwts_after[dend.post_rank, :] 
            dend.w = dend_w_array 

    OVC2BVCwts_after = BVC2OVCwts_after.T
    for dend in OVC2BVC.dendrites:
        dend_w_array = OVC2BVCwts_after[dend.post_rank, :]             
        dend.w = dend_w_array
            