"""
    Part of ANNarchy-SM
    This file contains the implementation of Pdrive_PW.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import numpy as np
from SM_helper_functions import intersection

def SM_PdrivePW_withObj(r0, dir, line, BndryPtX, BndryPtY, X, Y, HD, step, obj):
    """
    In the SM model translation is modeled in the following way (direct quote 
    from the paper, except for parentheses): Motor efference drives the
    spatial updating of the egocentric representation of the locations of
    landmarks (meaning spatial updating of the egocentric PW representation).
    Specifically, modulation of the posterior parietal egocentric-allocentric
    transformation by motor efference causes allocentric locations to be
    mapped to the egocentric locations pertaining after the current segment
    of movement. The reactivation of the BVCs by this shifted egocentric
    representation then updates the medial temporal representation to be
    consistent with the (egocentric) parietal representation.

    Schematic:
   
    BVCs activity profile before translational movement --> via BVCtoPW
    transformation + translation(!!!) weights --> translated PW repres. -->
    back to BVC via normal transformation weigths  -->  BVC activity profile
    after translation. 
   
    Comment:
    
    This is necessary for mental navigation in imagery, but for real navigation
    ('eyes open'), it should not be used. The above quote means that - in the 
    old SM (!) - there was no direct, continuously updating, perceptual drive 
    to the PW which can function without the MTL component. 
    For SpaceCog we need the perceptual drive. It will then be substituted by
    the Spacecog VR
      
    Implementation:
    
    X,Y will be given from a trajectory update. Then we calculate
    from X,Y the distance to all landmarks in front of the agent
    (meaning determined by its egocentric location), i.e. landmarks in its
    field of view centered on HD. The return variable egocue will then be
    the input for the cueing current, with the help of the function.
    helper_cue_Grid_Activity(egocue). That is, this script effectively
    computes the into which neurons of the PW sheet current needs to be injected.

    Agent movement resolved in the function "SM_trajectory". It gives us new position X,Y
    now used to drive PW activity. Note, SM_trajectory is called in the
    main integration loop, in case you came here from the initialization part
    of the main script.
    """

    total_lines = line
    occ_one = np.ones([total_lines, 1])
    TrainX = X
    TrainY = Y
    NTrainPts = 1

    num_bndry_pts = BndryPtX.shape[0]           # equal to np.size(BndryPtX, 0)
    bpone = np.ones([num_bndry_pts, 1])         # helper arrays
    bpzero = np.zeros(num_bndry_pts)            # row vector
    bpzero_2 = np.zeros([num_bndry_pts, 1])

    VisXY = np.nan * np.ones([2, num_bndry_pts, NTrainPts])

    """
    This determines which boundary/line points can be seen from a given
    training location, this cannot be out sourced, but loopsize can be
    reduced to 1, because instead of multiple training locations we only have the agent location
    """

    posx = TrainX
    posy = TrainY                                                       # xy coords of current training loc.
    TrainingLoc = [posx, posy]
    local_r0 = r0 - occ_one * [posx, posy, 0]                           # Transform all boundary coordinates so that current training loc. is origin
    Loc_bndry_pts = np.concatenate((BndryPtX - posx, BndryPtY - posy, bpzero_2), axis=1) # also adding third dim with 0s because function crossprod in routing intersection needs 3D vectors
    occluded_pts = bpzero.T

    if not obj:
        for occ_bndry in range(total_lines):
            alpha_pt, alpha_occ = intersection(np.array([bpzero, bpzero, bpzero]).T, bpone*local_r0[occ_bndry,:], Loc_bndry_pts, bpone*dir[occ_bndry,:]) # The intersection routine figures out where two lines intersect and returns both alphas
            occluded_pts = np.logical_or(occluded_pts,np.logical_and(alpha_pt< 1-10**-5, np.logical_and(alpha_pt>0, np.logical_and(alpha_occ<=1, alpha_occ>=0)))) # This variable accumulates boundary pts that are occluded by some other boundary from current training loc.
        occluded_pts = occluded_pts.T
    
    unocc_ind = np.nonzero(occluded_pts==0)[0]                          # same as pl.find(occluded_pts==0) from module pylab
    num_vis_pts = unocc_ind.shape[0]
    for dim in range(1, len(unocc_ind.shape)):                         # equiv. to Matlab expression "num_vis_pts = prod(size(unocc_ind))"
        num_vis_pts *= unocc_ind.shape[dim]

    VisXY[:, 0:num_vis_pts, 0] = Loc_bndry_pts[unocc_ind, 0:2].T + np.array([[posx], [posy]]) * np.ones([1, num_vis_pts]) 
                                                                        # xy coords of unoccluded bndry pts - Accumulates over all locations - transforms back to previous origin

    VisX = np.transpose(VisXY[0, :, :])                                 # Puts x,y coords of unoccluded pts in separate variables
    VisY = np.transpose(VisXY[1, :, :])

    posX = TrainingLoc[0]                                               # Get x,y coords for this location
    posY = TrainingLoc[1]                                               

    tmp = np.nonzero(np.isnan(VisX[0,:])==0)                            # Clean up some arrays. This will remove trailing NaN entries
    VisBndryPtsX = VisX[0, tmp] - posX                                  # Get coords of bndry points visible from current location
    VisBndryPtsY = VisY[0, tmp] - posY
    VisBndryPtsX = VisBndryPtsX[0, :]                                   # Eliminating "extra" dimension
    VisBndryPtsY = VisBndryPtsY[0, :]

    # rotate and translate unoccluded boundary pts to match agent rotation
    if obj == False:
        R = np.array([[np.cos(HD), -np.sin(HD)], [np.sin(HD), np.cos(HD)]]) # set up rotation matrix
    else:
        R = np.array([[np.cos(HD), -np.sin(HD)], [np.sin(HD), np.cos(HD)]]) # set up rotation matrix
        R = R.T

    object_vectors = np.array([VisBndryPtsX, VisBndryPtsY])            # array of vectors, note, object refers to boundary elements here, don't confuse with discrete objects
    rotated_vectors = np.dot(R, object_vectors)                        # rotation (by matrix-vector multiplication)
    VisBndryPtsX_rottrans = rotated_vectors[0,:]
    VisBndryPtsY_rottrans = rotated_vectors[1,:]


    # now we want all boundary pts with Y'>0, corresponding to a 180 deg. field of view
    ind1 = VisBndryPtsY_rottrans > 0                                    # select pts then use diff to separate landmark segments
    diffvec = np.array([[np.diff(VisBndryPtsX[ind1])], [np.diff(VisBndryPtsY[ind1])]]).T # use unrotated
    diffvec = diffvec[:, 0, :]                                          # Eliminating "extra" dimension

    Lmarks = []
    FOVy = VisBndryPtsY[ind1]                                           # first index zero to obtain correct shape out of 1xN-array
    FOVx = VisBndryPtsX[ind1]

    c2 = 0
    counter = 1
    while c2 < len(np.nonzero(ind1)[0])-1 :
        diffsum = np.round((np.abs(diffvec[c2, 0]) + np.abs(diffvec[c2, 1])) * 10)
        if diffsum == 3 - obj:                                               # depends on res 3
            Lmarks.append( np.array([[FOVx[c2]], [FOVy[c2]]]) )              # enter start pt of landmark
            while diffsum == 3 - obj and c2 + counter < len(np.nonzero(ind1)[0])-1 :
                diffsum = np.round((np.abs(diffvec[c2 + counter, 0]) + np.abs(diffvec[c2 + counter, 1])) * 10)
                counter += 1
            Lmarks.append(np.array([[FOVx[c2 + counter - 1]], [FOVy[c2 + counter - 1]]]))   # enter end pt of landmark
        c2 += counter
        counter = 1


    if len(Lmarks) == 0:
        egocue = np.array([[]])
        Lmarks_rot = np.array([[]])
    else:
        Lmarks_rot = np.dot(R, Lmarks)

            # Lmarks_rot contains the egocentric coordinates of the limiting landmark vertices of all visible boundary segments
            #   x1-start  x1-end  x2-start  x2-end ...
            #   y1-start  y1-end  ...
            # needs to be this way for the application of the rotation matrix. Now reshape for egocue
            # egocue has shape  [-4,3.5,4,3.5] = [x1s,y1s,x1e,y1e], new row for nect linesegment

        egocue  = np.array([[]])
        counter = 1
        for i in range(int(len(Lmarks_rot[0, :]) / 2)):
            if i == 0:
                egocue = np.concatenate((egocue, np.reshape(Lmarks_rot[:, counter-1 : counter+1], [1,4], order='F')), axis=1)       
                # "Fortran-like" order for reshape as in Matlab
                # Concatenation of a 1x4 row vector with an empty 1x0 vector is done along the second axis, result: 1x4 row vector
            else:
                egocue = np.concatenate((egocue, np.reshape(Lmarks_rot[:, counter-1 : counter+1], [1,4], order='F')), axis=0)
                # Further concatenations are done along the first axis, result: (i+1)x4 array
            counter += 2

    """
    Returns:
    
        currently fixed parameters, processed by later steps (only correct for. The most variables
        are only with the correct size. Content is missing
    """

    """
    egocue = np.array([ [-4.3750, 0.1750, -4.3750, 5.2750],
                        [-4.0000, 5.0625,  6.8000, 5.0625],
                        [ 6.3750, 0.1000,  6.3750, 4.3000] ])


    VisBndryPtsX_rottrans = np.zeros((1,197))
    VisBndryPtsY_rottrans = np.zeros((1,197))
    Lmarks_rot = np.zeros((2,6))

    TrainX = 5
    TrainY = 0
    """
    return egocue, VisBndryPtsX_rottrans, VisBndryPtsY_rottrans, Lmarks_rot, BndryPtX, BndryPtY, TrainX, TrainY














