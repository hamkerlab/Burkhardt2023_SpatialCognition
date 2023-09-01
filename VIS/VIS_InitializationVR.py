"""
   This program initializes the proper parameters for the LGN and V1 processing. The function initV1() should
   be imported in the main program (expVR.py). The output of this function is a class (called 'this'
   here and 'objV1' in expVR.py) which contains essential parameters for LGN/V1 processing.

   Functions:
   - initV1()              : The main function
   --------------------------------------------------
   LGN/V1 processing - part orientation:
   - customgauss()
   - gaborKernel()
   LGN/V1 processing - part color:
   - initColor()
   - initColorContrast()
   - initGabor()
   - rotgauss()

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""



import math
import copy
import numpy as np

def initV1(ModelParam):

    class this:
        pass

    if ModelParam['FastTest'] == 0:
        this.delay = 60
    else:
        this.delay = 0

    if ModelParam['Sim_Env'] == 'VR':
        this.nChannel = 16
    else:
        this.nChannel = 8

    ## Define Filter Bank
    if ModelParam['FilterBankV1'] == 1:
        this.nC = 3
        this.enableDOcell = 0
        this.colorW, this.colorFeat = initColor(ModelParam['kernelSizesReal'],
                                                ModelParam['kernelSizes'], ModelParam['resIm'][2],
                                                this.enableDOcell, ModelParam)
        this = initColorContrast(this)
        this = initGabor(this, ModelParam)
    else:
        print("Error: Unknown V1 Filterbank", ModelParam['FilterBankV1'])
        exit(1)

    # Note: Eccentricity independent RF sizes

    # V1
    this.rfsizeDeg = ModelParam['v1RFsizeDeg']
    # spatial size of RF, standard is 13
    this.rfsize = ModelParam['kernelSizes']
    # number of pre-synaptic cells per patch (only gray-scale)
    this.rfNo = this.rfsize[0] * this.rfsize[1] * 1.
    # shift between 2 RFs must be 1, otherwise the Gabor filter find not all structeres in the image
    this.rfshift = 1
    assert this.rfshift >= 1

    this.res = [ModelParam['VF_px'][1], ModelParam['VF_px'][0], this.nC, this.nChannel]

    # LGN
    this.resChannelLgn = [ModelParam['VF_px'][1], ModelParam['VF_px'][0], 8]

    this.resChannelV1 = [this.res[0], this.res[1], this.nChannel]

    if ModelParam['Sim_Env'] == 'VR':
        this.vLgnColorContrast = [3.4554, 2.6566, 3.4338, 2.4434]
        this.vV1PoolChannel = [1.5, 1, 1]
    else:
        this.vLgnColorContrast = [3, 3, 3, 3]
        this.vV1PoolChannel = [1, 1, 1]

    if ModelParam['enablePoolingV1'] == 0:
        this.poolingMode = 0
        this.poolFactor = 1
    else:
        this.poolingMode = ModelParam['enablePoolingV1']
        this.poolFactor = ModelParam['poolFactor']

    if this.poolingMode == 0:
        this.resPooled = this.res
    else:
        this.resPooled = [int(math.floor(this.res[0] / this.poolFactor)),
                          int(math.floor(this.res[1] / this.poolFactor)), this.res[2], this.res[3]]

    return this


def customgauss(gsize, sigmax, sigmay, theta, offset, factor, center):
    '''
    Calculates a Gaussian 2D kernel
    '''

    ret = np.zeros(gsize.astype(int))

    rbegin = -(gsize[0] / 2. + 0.5)
    cbegin = -(gsize[1] / 2. + 0.5)

    for r in range(1, int(gsize[0]) + 1):
        for c in range(1, int(gsize[1]) + 1):
            ret[r - 1, c - 1] = rotgauss(rbegin + r, cbegin + c, theta, sigmax, sigmay, offset,
                                         factor, center)

    return ret


def gaborKernel(kernelSize, halfSDsq, theta, f, psi, spatialCompression):
    '''
    Calculates a Gabor kernel
    '''

    if spatialCompression[0] < 1 or spatialCompression[1] < 1:
        print("Error: Spatial Compressions should be at least 1")
        exit(1)

    # Some terms for the gabor equation
    twopiF = 2. * np.pi * f
    theta = theta + np.pi / 2.

    # Calculate grids (calculation points) for RF
    a = (kernelSize - 1) / 2. # Half support upper boundary

    # The following block is equal to this Matlab syntax: [X,Y] = meshgrid(-a:a, a:-1:-a);
    Y, X = np.mgrid[-a:a + 1, -a:a + 1]
    for i in range(int(a)):
        tmp = copy.deepcopy(Y[i, :])
        Y[i, :] = copy.deepcopy(Y[2 * int(a) - i, :])
        Y[2 * int(a) - i, :] = copy.deepcopy(tmp)

    X = spatialCompression[1] * X
    Y = spatialCompression[0] * Y

    XT1 = 1. * ((X) * math.cos(theta) + Y * math.sin(theta))
    YT1 = 1. * (Y * math.cos(theta) - (X) * math.sin(theta))

    # Receptive Field (RF)
    # Standard normalisation is: 1 / sqrt(2 * pi * sigmaX) *  1 / sqrt(2 * pi * sigmaY)

    K = np.exp(-halfSDsq[0] * (XT1 * XT1) - halfSDsq[1] * (YT1 * YT1)) * np.cos(twopiF * XT1 + psi)

    if spatialCompression[1] > 1:
        pass                            # TODO

    if spatialCompression[0] > 1:
        pass                            # TODO

    return K


def initColor(kernelSizeReal, kernelSize, imgDepth, enableDOcell, ModelParam):
    '''
    Initialising the color on/off cells in LGN and V1 ,
    i.e. the red-green and blue-yellow color contrast cells.
    '''

    if enableDOcell == 1:
        wFeat = 6                # Number of features after convolution (~= Number of features LGN!)
    else:
        wFeat = 8

    xChan = kernelSize[0] * kernelSize[1]   # Matlab syntax is: xChan = prod(kernelSize)
                                            # Number of cells per image channel feature

    rfNo = xChan * imgDepth                 # Number of cells in the receptive field
    if ModelParam['Sim_Env'] == 'VR':
        rfNo = xChan * (imgDepth + 1)
    curW = np.zeros([int(rfNo), wFeat])

    ## Midget RGC (parvo) L-M; Type I, center surround interaction
    #  sigmas after Wiesel & Hubel 1966
    #  => the cells react to red/green contrasts

    # We use discretizised Gauss in +-1.5 sigma for the surround
    sigma_c_parvo = kernelSizeReal / 12.    # We use here no different sigma in X/Y, we use mean
    sigma_s_parvo = kernelSizeReal / 3.     # We use here no different sigma in X/Y, we use mean

    # The sum of the Gauss is normalized to one
    # The inhibitory part of M is only in the surround, not in the center
    # This DoG approach fits the physiological data better, see wiesel66_fig2 for details
    bound_x = kernelSize

    theta = 0.
    offset = 0.
    center = np.asarray([0., 0.])
    factor = 1.
    pos = customgauss(bound_x, sigma_c_parvo[0], sigma_c_parvo[1], theta, offset, factor, center)
    pos = pos / sum(sum(pos))
    neg = customgauss(bound_x, sigma_s_parvo[0], sigma_s_parvo[1], theta, offset, factor, center)
    neg = neg / sum(sum(neg))
    DoG = pos - neg
    DoGlin = np.reshape(DoG, DoG.shape[0] * DoG.shape[1])

    Gcenter = copy.deepcopy(DoG)
    Gcenter[Gcenter < 0] = 0
    Gcenter = Gcenter / sum(sum(Gcenter))
    GcenterLin = np.reshape(Gcenter, Gcenter.shape[0] * Gcenter.shape[1])

    Gsurround = copy.deepcopy(-DoG)
    Gsurround[Gsurround < 0] = 0
    Gsurround = Gsurround / sum(sum(Gsurround))
    GsurroundLin = np.reshape(Gsurround, Gsurround.shape[0] * Gsurround.shape[1])

    x1 = 1                                       # L  channel part of the weight matrix
    x2 = int(copy.deepcopy(xChan))
    x3 = int(copy.deepcopy(xChan)) + 1           # M  channel part of the weight matrix
    x4 = 2 * int(copy.deepcopy(xChan))
    x5 = 2 * int(copy.deepcopy(xChan)) + 1       # S  channel part of the weight matrix
    x6 = 3 * int(copy.deepcopy(xChan))

    # In VR
    x7 = 3 * int(copy.deepcopy(xChan)) + 1       # LM channel part of the weight matrix
    x8 = 4 * int(copy.deepcopy(xChan))

    if enableDOcell == 0:
        # Single opponent cells

        # ON
        # LplusMminus
        curW[x1 - 1:x2, 0] = copy.deepcopy(GcenterLin)
        curW[x3 - 1:x4, 0] = -copy.deepcopy(GsurroundLin)
        # MplusLminus
        curW[x3 - 1:x4, 1] = copy.deepcopy(GcenterLin)
        curW[x1 - 1:x2, 1] = -copy.deepcopy(GsurroundLin)

        # OFF
        # LminusMplus
        curW[x1 - 1:x2, 2] = -copy.deepcopy(GcenterLin)
        curW[x3 - 1:x4, 2] = copy.deepcopy(GsurroundLin)
        # MminusLplus
        curW[x3 - 1:x4, 3] = -copy.deepcopy(GcenterLin)
        curW[x1 - 1:x2, 3] = copy.deepcopy(GsurroundLin)
        l = 4 # Next free postFeature (Python = Matlab - 1)
    else:
        # Symmetric double opponent cells
        # L DoG
        curW[x1 - 1:x2, 0] = copy.deepcopy(DoGlin)
        # M DoG
        curW[x1 - 1:x2, 1] = copy.deepcopy(DoGlin)
        l = 2 # Next free postFeature (Python = Matlab - 1)

    ## Parasol RGC (magno) L+M; Type III, center surround interaction
    #  We use now mean (LM=(L+M)/2) instead of LM=L+M like Hansen, see plots in gegenfurtner 2003
    # NatRevNeurosci, fig 1f

    sigma_c_magno = copy.deepcopy(sigma_c_parvo)
    sigma_s_magno = copy.deepcopy(sigma_s_parvo)

    pos = customgauss(bound_x, sigma_c_magno[0], sigma_c_magno[1], theta, offset, factor, center)
    pos = pos / sum(sum(pos))
    neg = customgauss(bound_x, sigma_s_magno[0], sigma_s_magno[1], theta, offset, factor, center)
    neg = neg / sum(sum(neg))
    DoG = pos - neg

    Gcenter = copy.deepcopy(DoG)
    Gcenter[Gcenter < 0] = 0
    Gcenter = Gcenter / sum(sum(Gcenter))
    GcenterLin = np.reshape(Gcenter, Gcenter.shape[0] * Gcenter.shape[1])

    Gsurround = copy.deepcopy(-DoG)
    Gsurround[Gsurround < 0] = 0
    Gsurround = Gsurround / sum(sum(Gsurround))
    GsurroundLin = np.reshape(Gsurround, Gsurround.shape[0] * Gsurround.shape[1])

    if ModelParam['Sim_Env'] == 'VR':
        # ON
        # LMplusLMminus
        curW[x7 - 1:x8, l] = GcenterLin - GsurroundLin

        # OFF
        # LMminusLMplus
        curW[x7 - 1:x8, l + 1] = - GcenterLin + GsurroundLin

        l = l + 2

        ## Bistratified RGC (konio) S+LM-; Type II, no center-surround
        #  => react to blue or yellow areas
        #  Version after wiesel & hubel 1966, type II cells

        sigma_III = copy.deepcopy(sigma_s_parvo)
        G = customgauss(bound_x, sigma_III[0], sigma_III[1], theta, offset, factor, center)
        G = G / sum(sum(G))
        Glin = np.reshape(G, G.shape[0] * G.shape[1])

        # S ON
        # SplusLMminus
        curW[x5 - 1:x6, l] = Glin
        curW[x7 - 1:x8, l] = -Glin

        # S OFF
        # SminusLMplus
        curW[x5 - 1:x6, l + 1] = -Glin
        curW[x7 - 1:x8, l + 1] = Glin
    else:
        # ON
        # LMplusLMminus
        curW[x1 - 1:x2, l] = GcenterLin / 2. - GsurroundLin / 2.
        curW[x3 - 1:x4, l] = GcenterLin / 2. - GsurroundLin / 2.

        # OFF
        # LMminusLMplus
        curW[x1 - 1:x2, l + 1] = - GcenterLin / 2. + GsurroundLin / 2.
        curW[x3 - 1:x4, l + 1] = - GcenterLin / 2. + GsurroundLin / 2.

        l = l + 2

        ## Bistratified RGC (konio) S+LM-; Type II, no center-surround
        #  => react to blue or yellow areas
        #  Version after wiesel & hubel 1966, type II cells

        sigma_III = copy.deepcopy(sigma_s_parvo)
        G = customgauss(bound_x, sigma_III[0], sigma_III[1], theta, offset, factor, center)
        G = G / sum(sum(G))
        Glin = np.reshape(G, G.shape[0] * G.shape[1])

        # S ON
        # SplusLMminus
        curW[x5 - 1:x6, l] = Glin
        curW[x1 - 1:x2, l] = -Glin / 2.
        curW[x3 - 1:x4, l] = -Glin / 2.

        # S OFF
        # SminusLMplus
        curW[x5 - 1:x6, l + 1] = -Glin
        curW[x1 - 1:x2, l + 1] = +Glin / 2.
        curW[x3 - 1:x4, l + 1] = +Glin / 2.

    K = []
    K.append(curW)

    return K, wFeat


def initColorContrast(this):

    this.colorContrastMode = 6  #only '6' allowed
    # 6 => 2x 1D Gauss at the axis, hence for 0..1 for R and 0..1 for G
    return this


def initGabor(this, ModelParam):
    '''
    Initialising the orientations cells in LGN/V1.
    '''

    wScale = 3

    # This and the next line is equal to this Matlab syntax: this.gaborW = cell(modelParam.N, 1);
    this.gaborW = []
    for i in range(ModelParam['N']):
        this.gaborW.append([])

    # For constant RF sizes, N is 1
    # This and the next line is equal to this Matlab syntax: kernelCenter = cell(8,1);
    kernelCenter = []
    for i in range(8):
        kernelCenter.append([])

    for k in range(ModelParam['N']):
        # Number of cells inside the receptive field
        rfNo = int(ModelParam['kernelSizes'][0] * ModelParam['kernelSizes'][1])

        # Defining gabor kernel
        kernelSizeMax = max(ModelParam['kernelSizesReal'])
        f = 1. / kernelSizeMax
        theta = 0                                                       # Orientation
        psi = -np.pi / 2.                                               # Phase shift of a gabor

        # halfSDsq = 1 / (2 * sigma ^ 2)
        halfSDsq1 = [1. / (2 * (kernelSizeMax / 4.) ** 2), 1. / (2 * (kernelSizeMax / 1.) ** 2)]

        for o in range(8):
            if ModelParam['N'] == 1:
                spatialCompression = kernelSizeMax / ModelParam['kernelSizesReal']
            else:
                pass        # Should be implemented later

            # The gabor-function is only implemented for squared kernels...
            if ModelParam['kernelSizes'][0] != ModelParam['kernelSizes'][1]:
                print("Error: The gabor-function is only implemented for squared kernels.")
                exit(1)
            kernelCenterSingle = gaborKernel(ModelParam['kernelSizes'][0], halfSDsq1, theta, f, psi,
                                             spatialCompression)

            # Normalization Gabor that sum(positive) = 1
            # No need to adjust negative sum, the Gabor is in 90 degree step totally symmetric
            tmp = copy.deepcopy(kernelCenterSingle)
            tmp[tmp < 0] = 0
            sumGabor = sum(sum(tmp))
            kernelCenter[o] = (np.reshape(np.transpose(kernelCenterSingle),
                                          kernelCenterSingle.shape[0]*kernelCenterSingle.shape[1])
                               / sumGabor * wScale)
            theta = theta + np.pi / 4.

        # Set kernel to matrix
        curW = np.zeros([rfNo, this.nChannel])
        for o in range(8):
            # Grayscale garbor
            curW[:, o] = +kernelCenter[o]

        this.gaborW[k] = curW

    return this


def rotgauss(x, y, theta, sigmax, sigmay, offset, factor, center):

    xc = center[0]
    yc = center[1]
    theta = (theta / 180.) * np.pi
    xm = (x - xc) * math.cos(theta) - (y - yc) * math.sin(theta)
    ym = (x - xc) * math.sin(theta) + (y - yc) * math.cos(theta)
    u = (xm / sigmax) ** 2. + (ym / sigmay) ** 2.
    val = offset + factor * math.exp(-u / 2.)

    return val