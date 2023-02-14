"""
   This program prepares the pre-processed image. The function stepV1() should be imported in main
   program (expVR.py). The outputs of this function are the pre-processed images for V1-Simple and
   V1-Complex layers.

   Functions:
   - stepV1()              : The main function
   --------------------------------------------------
   - ColorSpace()
   - cat02lms()
   - GetTransform()
   - gauss1Dfunc()
   - invgammacorrection()
   - Lanczos()
   - LanczosMatrix()
   - RGB()
   - rgb2grayLocal()
   - stepColorContrasts()
   - stepColorR2()
   - stepGabor()
   - xyz()

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""



import copy
import math
import numpy as np
from numpy.linalg import inv
import cv2
from PIL.Image import fromarray

def stepV1(rgb, objV1, ModelParam):

    rV1 = np.zeros(list(map(int, objV1.res)))

    ## Convert RGB to LMS
    #  Necessary for all filter banks.
    if ModelParam['LMSinput'] == 0:
        lms = ColorSpace('rgb', 'cat02lms', rgb)
    else:
        lms = rgb

    ## Filtering to create LGN-Color responses
    # - Necessary for many filter banks
    # - Symetrical single-opponent cells
    rLgnColor = stepColorR2(lms, objV1, ModelParam)
    # Half rectification: set neg values to 0
    rLgnColor[rLgnColor < 0] = 0

    # Build from lgn cells V1 Red-Green and Blue-Yellow contrast cells
    rRG, rBY = stepColorContrasts(rLgnColor, objV1, ModelParam)
    rV1[:, :, 0, :] = rRG
    rV1[:, :, 1, :] = rBY

    # Build edge filters (Gabor)
    rV1[:, :, 2, :] = stepGabor(rgb, objV1)

    ## Half rectification: set neg values to 0
    rV1[rV1 < 0] = 0

    # Saturation is needed for security and Filterbank1, submode 6
    rV1[rV1 > 1] = 1

    if objV1.poolingMode == 0:
        rV1pooled = rV1
    elif objV1.poolingMode == 1:
        # Max pooling should be implemented here.
        pass
    elif objV1.poolingMode == 2:
        # There is no equivalent function in Python
        pass
    elif objV1.poolingMode == 3:
        # Should be implemented later
        pass
    elif objV1.poolingMode == 4:
        rV1pooled = np.zeros(objV1.resPooled)
        #Img = fromarray(rV1[:, :, 0, 0])
        #Img.resize((31, 41), PIL.Image.LANCZOS)
        #print Img
        #exit(1)
        for c in range(objV1.res[2]):
            for l in range(objV1.res[3]):
                if ModelParam['imresize_Kernel'] == 'Lanczos4':
                    rV1pooled[:, :, c, l] = cv2.resize(rV1[:, :, c, l],
                                                       (objV1.resPooled[1], objV1.resPooled[0]),
                                                       interpolation=cv2.INTER_LANCZOS4)
                elif ModelParam['imresize_Kernel'] == 'Bilinear':
                    rV1pooled[:, :, c, l] = cv2.resize(rV1[:, :, c, l],
                                                       (objV1.resPooled[1], objV1.resPooled[0]))
                elif ModelParam['imresize_Kernel'] == 'Lanczos3':
                    # For Lanczos-3, Lanczos_a = 3 and for Lanczos-2, Lanczos_a = 2
                    Lanczos_a = 3.

                    Added_Margin = int(Lanczos_a * objV1.poolFactor * 2)
                    Half_Margin = int(Added_Margin / 2)
                    rV1_with_Margin = np.zeros([int(objV1.res[0] + Added_Margin),
                                                int(objV1.res[1] + Added_Margin)])

                    rV1_with_Margin[Half_Margin:rV1_with_Margin.shape[0]-Half_Margin, Half_Margin:rV1_with_Margin.shape[1]-Half_Margin] = rV1[:, :, c, l]

                    A2_Kernel = LanczosMatrix(Lanczos_a, objV1.poolFactor)
                    A2 = cv2.filter2D(rV1_with_Margin, -1, cv2.flip(A2_Kernel, -1), anchor=(0, 0))
                    Convolved_Matrix = A2[0:A2.shape[0] - A2_Kernel.shape[0] + 1,
                                          0:A2.shape[1] - A2_Kernel.shape[1] + 1]

                    Pooled_Matrix = np.zeros([objV1.resPooled[0], objV1.resPooled[1]])
                    Rpt = -1
                    Cpt = -1

                    for Ro in range(Convolved_Matrix.shape[0]):
                        if Ro % objV1.poolFactor == 3:
                            Rpt = Rpt + 1
                            for Co in range(Convolved_Matrix.shape[1]):
                                if Co % objV1.poolFactor == 3:
                                    Cpt = Cpt + 1
                                    if Rpt < Pooled_Matrix.shape[0] and Cpt < Pooled_Matrix.shape[1]: Pooled_Matrix[Rpt, Cpt] = Convolved_Matrix[Ro, Co]
                            Cpt = -1

                    rV1pooled[:, :, c, l] = copy.deepcopy(Pooled_Matrix)

        rV1pooled[rV1pooled > 1] = 1
        rV1pooled[rV1pooled < 0] = 0

    if ModelParam['Sim_Env'] == 'VR':
        PoolChannel = np.asarray([1.5, 1., 1.])
        for c in range(0, 3):
            rV1pooled[:, :, c, :] = rV1pooled[:, :, c, :] * PoolChannel[c]
        rV1pooled[rV1pooled > 1] = 1

    return rV1pooled, rV1


def ColorSpace(SrcSpace, DestSpace, ImgMat):
    LocalImage = copy.deepcopy(ImgMat)
    SrcT = GetTransform(SrcSpace)
    DestT = GetTransform(DestSpace)

    # The MATLAB code 'Image = feval(DestT, Image, SrcSpace);' should be implemented.
    ResultImage = cat02lms(LocalImage, SrcT)
    return ResultImage


def cat02lms(InputImage, SrcSpace):
    Image1 = copy.deepcopy(InputImage)
    ImgMat = xyz(Image1, SrcSpace)

    T = np.asarray([[0.7328, 0.4296, -0.1624], [-0.7036, 1.6975, 0.0061], [0.0030, 0.0136, 0.9834]])
    X = copy.deepcopy(ImgMat[:, :, 0])
    Y = copy.deepcopy(ImgMat[:, :, 1])
    Z = copy.deepcopy(ImgMat[:, :, 2])
    ImgMat[:, :, 0] = T[0, 0] * X + T[0, 1] * Y + T[0, 2] * Z
    ImgMat[:, :, 1] = T[1, 0] * X + T[1, 1] * Y + T[1, 2] * Z
    ImgMat[:, :, 2] = T[2, 0] * X + T[2, 1] * Y + T[2, 2] * Z

    return ImgMat


def GetTransform(Space):
    if Space == 'rgb' or Space == 'cat02lms' or Space == 'xyz' or Space == 'hsv' or Space == 'hsl' or Space == 'lab' or Space == 'luv' or Space == 'lch':
        T = Space
    elif Space == 'ypbpr':
        T = [[0.299, 0.587, 0.114, 0], [-0.1687367, -0.331264, 0.5, 0],
             [0.5, -0.418688, -0.081312, 0]]
    elif Space == 'yuv':
        T = [[0.299, 0.587, 0.114, 0], [-0.147, -0.289, 0.436, 0], [0.615, -0.515, -0.100, 0]]
    elif Space == 'ydbdr':
        T = [[0.299, 0.587, 0.114, 0], [-0.450, -0.883, 1.333, 0], [-1.333, 1.116, 0.217, 0]]
    elif Space == 'yiq':
        T = [[0.299, 0.587, 0.114, 0], [0.595716, -0.274453, -0.321263, 0],
             [0.211456, -0.522591, 0.311135, 0]]
    elif Space == 'ycbcr':
        T = [[65.481, 128.553, 24.966, 16], [-37.797, -74.203, 112.0, 128],
             [112.0, -93.786, -18.214, 128]]
    elif Space == 'jpegycbcr':
        T = [[0.299, 0.587, 0.114, 0], [-0.168736, -0.331264, 0.5, 0.5],
             [0.5, -0.418688, -0.081312, 0.5]]
    else:
        T = 'Unknown'

    return T


def gauss1Dfunc(X, mu, sigma):

    K = np.exp(-0.5 * ((X - mu) / (sigma)) ** 2)
    return K


def invgammacorrection(Rp):
    R = np.zeros(Rp.shape)
    NofRow, NofCol = Rp.shape

    i = 0
    while i < NofRow:
        j = 0
        while j < NofCol:
            if Rp[i, j] <= 0.0404482362771076:
                R[i, j] = Rp[i, j] / 12.92
            else:
                R[i, j] = ((Rp[i, j] + 0.055) / 1.055) ** 2.4
            j = j + 1
        i = i + 1

    return R


def Lanczos(x, a=3.):
    if x == 0:
        L = 1.
    elif abs(x) > 0 and abs(x) < a:
        P = np.pi
        L = (a * np.sin(P * x) * np.sin((P * x) / a)) / (P * P * x * x)
    else:
        L = 0.
    return L


def LanczosMatrix(dim, interval, Sinc=False):
    M = np.zeros(list(map(int, [dim * interval * 2 + 1, dim * interval * 2 + 1])))
    delta = dim * 2. / (M.shape[0] - 1)
    x = -dim - delta
    y = dim + delta

    for i in range(M.shape[0]):
        y = y - delta
        for j in range(M.shape[1]):
            x = x + delta
            if Sinc:
                M[i, j] = np.sinc(x) * np.sinc(y)
            else:
                M[i, j] = Lanczos(x, dim) * Lanczos(y, dim)
        x = -dim - delta
    M = M / M.sum()         # To normalize the matrix. Now the sum of M would be 1.
    return M


def RGB(InputImage, SrcSpace):
    Image1 = copy.deepcopy(InputImage)
    if SrcSpace == 'rgb':
        return Image1
    else:
        pass


def rgb2grayLocal(InpRGB):

    RGB = copy.deepcopy(InpRGB)
    if RGB.shape[2] != 3:    # Check if we have really 3 values at 3th dimension
        print("Error: The RGB image is not 3-D.")
        exit(1)

    T = inv(np.asarray([[1.0, 0.956, 0.621], [1.0, -0.272, -0.647], [1.0, -1.106, 1.703]]))
    coef = T[0, :]

    GRAY = coef[0] * RGB[:, :, 0] + coef[1] * RGB[:, :, 1] + coef[2] * RGB[:, :, 2]

    return GRAY


def stepColorContrasts(vV1, objV1, ModelParam):

    rRG = np.zeros(list(map(int, objV1.resChannelV1)))
    rBY = np.zeros(list(map(int, objV1.resChannelV1)))

    vV1_mean = np.zeros([int(objV1.res[0]), int(objV1.res[1]), 4])

    # Matlab: vV1_mean(:,:,1) = max(vV1(:,:,[1,4]), [], 3);
    tmp = np.zeros([int(objV1.res[0]), int(objV1.res[1]), 2])
    tmp[:, :, 0] = copy.deepcopy(vV1[:, :, 0])
    tmp[:, :, 1] = copy.deepcopy(vV1[:, :, 3])
    vV1_mean[:, :, 0] = np.amax(tmp, 2)

    # Matlab: vV1_mean(:,:,2) = max(vV1(:,:,[2,3]), [], 3);
    tmp[:, :, 0] = copy.deepcopy(vV1[:, :, 1])
    tmp[:, :, 1] = copy.deepcopy(vV1[:, :, 2])
    vV1_mean[:, :, 1] = np.amax(tmp, 2)

    # Matlab: vV1_mean(:,:,3:4) = vV1(:,:,7:8);
    vV1_mean[:, :, 2] = vV1[:, :, 6]
    vV1_mean[:, :, 3] = vV1[:, :, 7]

    ## Transform vV1 to cell values
    # How the v1 cells are constructed (std==5)
    # 6 => 2x 1D Gauss at the axis, hence for 0..1 for R and 0..1 for G
    if objV1.colorContrastMode == 6:
        nG = int(math.floor(objV1.nChannel / 2.))
        maxV = 1                        # Saterature all values larger than this one
        if ModelParam['Sim_Env'] == 'VR':
            wScale = np.asarray([3.4554, 2.6566, 3.4338, 2.4434])
        else:
            wScale = 3

        # Center and sigma values of the 1D Gauss
        # +0.08 and +1 avoids Gauss curves at 0.
        # This would be bad for not present colors and black background...
        mus = np.linspace(0.08, maxV, nG + 1)
        # 0.08 is good for natural scenes, 0.2 good to distinguish object 11 and 12

        mus = mus[1:mus.size]
        sigma = (mus[1] - mus[0]) / 2.5             # At 45% of maximum

        if ModelParam['Sim_Env'] == 'VR':
            for l in range(0, 4):
                vV1_mean[:, :, l] = vV1_mean[:, :, l] * wScale[l]
        else:
            vV1_mean = vV1_mean * wScale

        vV1_mean[vV1_mean > maxV] = maxV

        # Red-Green channel
        for l in range(nG):
            rRG[:, :, l] = gauss1Dfunc(vV1_mean[:, :, 0], mus[nG - l - 1], sigma)           # Red
            rRG[:, :, l + nG] = gauss1Dfunc(vV1_mean[:, :, 1], mus[l], sigma)               # Green

        # Blue-Yellow channel
        for l in range(nG):
            rBY[:, :, l] = gauss1Dfunc(vV1_mean[:, :, 2], mus[nG - l - 1], sigma)           # Blue
            rBY[:, :, l + nG] = gauss1Dfunc(vV1_mean[:, :, 3], mus[l], sigma)               # Yellow
    else:
        print("Error: Unknown colorContrastMode.")
        exit(1)

    return rRG, rBY


def stepColorR2(lms, objV1, ModelParam):

    # In VR we have to add LM channel (Yellow)
    Yellow = np.minimum(lms[:, :, 0], lms[:, :, 1])

    # concatenate yellow matrix at the end of lms matrix.
    lmsy = np.zeros([lms.shape[0], lms.shape[1], lms.shape[2] + 1])
    lmsy[:, :, lmsy.shape[2] - 1] = Yellow
    lmsy[:, :, 0:lmsy.shape[2] - 1] = lms

    ## 2) Do the filtering
    rLGN = np.zeros(list(map(int, objV1.resChannelLgn)))

    # no of cells per image channel feature
    xChan = ModelParam['kernelSizes'][0] * ModelParam['kernelSizes'][1]

    x1 = 1                                       # L  channel part of the weight matrix
    x2 = int(copy.deepcopy(xChan))
    x3 = int(copy.deepcopy(xChan)) + 1           # M  channel part of the weight matrix
    x4 = 2 * int(copy.deepcopy(xChan))
    x5 = 2 * int(copy.deepcopy(xChan)) + 1       # S  channel part of the weight matrix
    x6 = 3 * int(copy.deepcopy(xChan))

    # The following two lines are added for VR
    x7 = 3 * int(copy.deepcopy(xChan)) + 1       # LM channel part of the weight matrix
    x8 = 4 * int(copy.deepcopy(xChan))

    # Convolve for each feature
    w = objV1.colorW[0]
    ks = ModelParam['kernelSizes'].astype(int)

    # In VR
    # L+/M- cells
    for l in range(0, 4):
        A2_Kernel = np.reshape(w[x1 - 1:x2, l], ks)
        A2 = cv2.filter2D(lmsy[:, :, 0], -1, cv2.flip(A2_Kernel, -1), anchor=(0, 0))
        rLGN[:, :, l] = A2[0:A2.shape[0] - A2_Kernel.shape[0] + 1,
                           0:A2.shape[1] - A2_Kernel.shape[1] + 1]

        A2_Kernel = np.reshape(w[x3 - 1:x4, l], ks)
        A2 = cv2.filter2D(lmsy[:, :, 1], -1, cv2.flip(A2_Kernel, -1), anchor=(0, 0))
        rLGN[:, :, l] += A2[0:A2.shape[0] - A2_Kernel.shape[0] + 1,
                            0:A2.shape[1] - A2_Kernel.shape[1] + 1]

        # The third convolution can be left out, as for these l the Kernel is zero.

    # In VR
    # LM+/LM- cells
    for l in range(4, 6):
        A2_Kernel = np.reshape(w[x7 - 1:x8, l], ks)
        A2 = cv2.filter2D(lmsy[:, :, 3], -1, cv2.flip(A2_Kernel, -1), anchor=(0, 0))
        rLGN[:, :, l] = A2[0:A2.shape[0] - A2_Kernel.shape[0] + 1,
                           0:A2.shape[1] - A2_Kernel.shape[1] + 1]

    # In VR
    # S/LM cells
    for l in range(6, 8):
        A2_Kernel = np.reshape(w[x5 - 1:x6, l], ks)
        A2 = cv2.filter2D(lmsy[:, :, 2], -1, cv2.flip(A2_Kernel, -1), anchor=(0, 0))
        rLGN[:, :, l] = A2[0:A2.shape[0] - A2_Kernel.shape[0] + 1,
                           0:A2.shape[1] - A2_Kernel.shape[1] + 1]

        A2_Kernel = np.reshape(w[x7 - 1:x8, l], ks)
        A2 = cv2.filter2D(lmsy[:, :, 3], -1, cv2.flip(A2_Kernel, -1), anchor=(0, 0))
        rLGN[:, :, l] += A2[0:A2.shape[0] - A2_Kernel.shape[0] + 1,
                            0:A2.shape[1] - A2_Kernel.shape[1] + 1]

    ## Create symmetric double opponent L/M cells in this place (and not in initColor.m)
    #  because of the positive-function
    if objV1.enableDOcell == 1:
        pass                        # Should be implemented later

    # Half rectification: set neg values to 0
    rLGN[rLGN < 0] = 0

    return rLGN


def stepGabor(InpRGB, objV1):

    rGabor = np.zeros(list(map(int, objV1.resChannelV1)))
    ThisRGB = copy.deepcopy(InpRGB)
    gray = rgb2grayLocal(ThisRGB)

    # Constant RF sizes
    # Fast version for rfshift = 1
    if objV1.rfshift:
        GW = objV1.gaborW[0]
        for l in range(objV1.res[3]):
            G = np.transpose(np.reshape(GW[:, l], (objV1.rfsize).astype(int)))
            A2 = cv2.filter2D(gray, -1, cv2.flip(G, -1), anchor=(0, 0))
            rGabor[:, :, l] = A2[0:A2.shape[0] - G.shape[0] + 1, 0:A2.shape[1] - G.shape[1] + 1]
    else:
        # TODO
        pass

    return rGabor


def xyz(InputImage, SrcSpace):
    Image1 = copy.deepcopy(InputImage)
    WhitePoint = [0.950456, 1, 1.088754]
    if SrcSpace == 'xyz':
        return Image1
    elif SrcSpace == 'luv':
        pass
    elif SrcSpace == 'lab' or SrcSpace == 'lch':
        pass
    elif SrcSpace == 'cat02lms':
        pass
    else:
        ImgMat = RGB(Image1, SrcSpace)
        R = invgammacorrection(ImgMat[:, :, 0])
        G = invgammacorrection(ImgMat[:, :, 1])
        B = invgammacorrection(ImgMat[:, :, 2])
        T = inv(np.asarray([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415],
                            [0.0557, -0.2040, 1.057]]))
        ImgMat[:, :, 0] = T[0, 0] * R + T[0, 1] * G + T[0, 2] * B
        ImgMat[:, :, 1] = T[1, 0] * R + T[1, 1] * G + T[1, 2] * B
        ImgMat[:, :, 2] = T[2, 0] * R + T[2, 1] * G + T[2, 2] * B
        return ImgMat