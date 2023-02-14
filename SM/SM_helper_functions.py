"""
    Part of ANNarchy-SM
    This file contain implementation and comment of helper functions.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import numpy as np
from math import pi, floor, ceil, sqrt
from SM_load_mat_files import load_grid_parameters

def CueHDActivity(bump_locs, nb_neurons_HD):
    """
    Python implementation of *helper_cue_HD_Activity*. For more detailed information
    refer to original matlab file.

    Parameter:

        *bump_locs*: array of activity bumps, must be from 0 to 2*pi minus one neuron's resolution
        *nb_neurons_HD*: number of neurons in head direction population
    """
    # type check and conversion if necessary
    if isinstance(bump_locs, (int,float)):
        bump_locs = [bump_locs]
    if isinstance(bump_locs, list):
        bump_locs = np.array(bump_locs)

    # some constants
    NHD = nb_neurons_HD
    sig = 0.1885
    amp = 1

    # initializations
    bump_locs = NHD * bump_locs / (2*pi)
    sig       = NHD * sig / (2*pi)
    Activity  = np.zeros((NHD))
    x = np.arange(1, NHD+1)
    Wide_x = np.zeros( (3 * NHD) )

    # extent x to left and right side
    Wide_x[0:NHD] = x - NHD
    Wide_x[NHD:2*NHD] = x
    Wide_x[2*NHD:3*NHD] = x + NHD

    for x0 in bump_locs:
        # to calculate on vectors, you need to use
        # numpy.exp instead of math.exp
        Gaussian = amp * ( np.exp( -((Wide_x-x0)/sig) ** 2 ) +
                   np.exp(-((Wide_x-x0-NHD)/sig)**2) +
                   np.exp(-((Wide_x-x0+NHD)/sig)**2))

        # take middle part and add to activity
        Activity = Activity + Gaussian[NHD:2*NHD]

    return Activity

def cart2pol(x, y):
    """
    Transformation between cartesian and polar coordinates.

    Parameter:
        * x coordinate
        * y coordinate

    Returns:
        * tuple (th, r) whereas th is the angle and r the radius.
    """
    th = np.arctan2(y, x)
    r = np.sqrt(x**2 + y**2)

    return (th, r)

def pol2cart(th, r):
    """
    Transformation between polar and cartesian coordinates.

    Parameter:
        * th angle in radians
        * r radius

    Returns:
        * tuple (th, r) whereas th is the angle and r the radius.
    """
    x = r * np.cos(th)
    y = r * np.sin(th)

    return (x, y)

def CueGridActivityMultiseg(res, env, nb_neurons_BVC):
    """
    Note that this function actually calculates something proportional
    to BVC FIRING RATE when an bndry is present. I use it to generate
    cuing current as well.

    Parameters:

        *res*:  ...
        *env*:  Env will contain vector of start and endpoints for visible
                boundary segments. Must find cartesian coords of each
                bndrypoint. env is actually egocues, which we calculated
                for the perceptual drive.
        *nb_neurons_BVC*: ...

    """
    # grid parameters
    Hres, maxR, maxX, maxY, minX, minY, polarAngRes, polarDistRes = load_grid_parameters()

    # Assign polar coordinates to each Grid (BVC/PW or whatever) neuron.
    # Numbering moves outward along radius, starting at 0 radians
    NGridR       = round((maxR)/polarDistRes)
    NGridTheta   = floor((2*pi-0.01)/polarAngRes)+1
    NGrid        = NGridR*NGridTheta # Num. grid neurons

    polarDist = radscaling(maxR) #MB: Added radial scaling (according to eLife code)
    polarAng = [ polarAngRes * x for x in range(0, int(NGridTheta)) ]
    [pDist, pAng] = np.meshgrid(polarDist, polarAng)

    # Vector of distances and angles for each neuron from origin
    GridDist = np.reshape(pDist, pDist.shape[0] * pDist.shape[1]) # the transpose in original matlab code is not required
    GridAng = np.reshape(pAng, pAng.shape[0] * pAng.shape[1])
    GridAng = GridAng - 2*pi*(GridAng > pi) # fix range [ -pi .. pi ]

    # Create cartesian gridpoints in window containing
    # region covered by Grid neurons.
    minX  = - maxR
    maxX  = maxR
    minY  = - maxR
    maxY  = maxR
    Nx    = round((maxX-minX)/res)
    Ny    = round((maxY-minY)/res)

    # original loop uses 'res' as step size instead of 1, so I rescale 'Nx' with res
    x = [ minX + res/2 + i*res for i in range( 0, int(ceil((Nx/res-0.5)*res)) ) ]
    y = [ minY + res/2 + i*res for i in range( 0, int(ceil((Nx/res-0.5)*res)) ) ]
    [X, Y] = np.meshgrid(x,y)

    Grid_Act = np.zeros((int(NGrid)))


    # The environment will contain vector of start and endpoints for visible
    # boundary segments. Must find cartesian coords of each bndrypoint.
    # The variable 'env' is actually egocues, which we calculated for the perceptual drive

    if np.min(env.shape) > 0:
        for bndryNum in range(0, env.shape[0]):
            xi = env[bndryNum, 0] # In Matlab, env is a row vector with indices (1,1) to (1,4)!
            xf = env[bndryNum, 2]
            yi = env[bndryNum, 1]
            yf = env[bndryNum, 3]

            den = sqrt((xf-xi)**2+(yf-yi)**2)
            nx  = (xf-xi)/den
            ny  = (yf-yi)/den

            # Equation of line is given by x(t) = xi + t(xf-xi); y = yi + t(yf-yi). t is taken from [0,1].
            # I used alpha in some other routines here for the same purpose
            # First find perp(endicular) disp(lacement) from grid points to the entire line.
            PerpDispFromGrdPtsX = -(X-xi)*(1-nx**2) + (Y-yi)*ny*nx
            PerpDispFromGrdPtsY = -(Y-yi)*(1-ny**2) + (X-xi)*nx*ny

            # Calculate t-value of the line point which is perp from each grid point
            if abs( xf - xi ) > 0.0001: # equivalent to ~=
                t = (X+PerpDispFromGrdPtsX-xi)/(xf-xi)
            else:
                t = (Y+PerpDispFromGrdPtsY-yi)/(yf-yi)

            # Eliminate all grid points without a perp point, and farther away than res/2.

            # to implement this, I split up the matlab logical term in several sub term,
            # each of the six condition into three variables:
            #       + within_range: all values in 't' are between [0..1]
            #       + within_x_res: all values in 'PerpDispFromGrdPtsX' are between [-res/2..res/2]
            #       + within_y_res: all values in 'PerpDispFromGrdPtsY' are between [-res/2..res/2]
            lb = (t>=0)
            ub = (t<=1)
            within_range = np.logical_and( lb, ub )
            within_x_res = np.logical_and( PerpDispFromGrdPtsX>=-res/2, PerpDispFromGrdPtsX<res/2 )
            within_y_res = np.logical_and( PerpDispFromGrdPtsY>=-res/2, PerpDispFromGrdPtsY<res/2 )

            # final matrix
            BndryPts = np.logical_and( within_range, within_x_res )
            BndryPts = np.logical_and( BndryPts, within_y_res )

            XBndryPts = X[ np.where( BndryPts == 1 ) ]
            YBndryPts = Y[ np.where( BndryPts == 1 ) ]

            # Convert bndrypts to polar coordinates
            [ThetaBndryPts,RBndryPts] = cart2pol(XBndryPts,YBndryPts)

            for bndryNum in range( ThetaBndryPts.shape[0] ):
                AngDiff1 = abs(GridAng-ThetaBndryPts[bndryNum])
                AngDiff2 = 2*pi-abs(-GridAng+ThetaBndryPts[bndryNum])
                AngDiff = (AngDiff1<pi)*AngDiff1 + (AngDiff1>pi)*AngDiff2

                #Grid_Act = Grid_Act + 1/RBndryPts[bndryNum]*np.exp( (-0.05*np.power(AngDiff,2)/(0.005)) - ( np.power(GridDist-RBndryPts[bndryNum],2)/(0.1)) )
                sigmaTH = sqrt(0.05) #MB: Added following 4 lines according to eLife code
                sigmaR0 = 0.08
                sigmaR = (RBndryPts[bndryNum]+8)*sigmaR0
                Grid_Act = Grid_Act + 1/RBndryPts[bndryNum] * (np.exp(-(np.power(((AngDiff)/sigmaTH),2) ))  * np.exp(-(np.power(((GridDist-RBndryPts[bndryNum])/sigmaR),2))) )

    maximum = np.amax(Grid_Act)

    if maximum > 0.0:
        Grid_Act = Grid_Act/maximum # Normalize

    return Grid_Act

# radial scaling for circular populations
def radscaling(maxR):
    RFinc = 0.1*np.arange(1,maxR+1, 1)
    polarDist = np.zeros(maxR)

    for rr in range(maxR):
        if rr == 0:
            polarDist[rr] = 1
        else:
            polarDist[rr] = polarDist[rr-1]+RFinc[rr]

    polarDist = polarDist/max(polarDist)*(maxR-0.5)
    return polarDist

def intersection(r0_1, r0_2, dir1, dir2):
    """
    Figures out how far along each line two lines intersect.
    """

    den2 = np.cross(dir1, dir2)
    NaN_ind = np.nonzero(den2 == 0) 
    den2[NaN_ind] = np.nan
    den1 = -den2
    alpha2 = np.divide(np.cross(r0_2 - r0_1, dir1), den2) # element-wise division
    alpha1 = np.divide(np.cross(r0_1 - r0_2, dir2), den1)

    # cross product will tell you how this calculation works
    alpha1 = alpha1[:,2]
    alpha2 = alpha2[:,2]

    return alpha1, alpha2
