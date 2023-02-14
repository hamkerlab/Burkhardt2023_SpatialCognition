"""
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import math
import time

from ANNarchy import CSR

printDebug = False # print progress during creation

# minimal value for weight
MIN_CONNECTION_VALUE = 0.001

################
#### Output ####
################

class DebugOutput:
    def __init__(self, connection, pre, post):
        self.startTime = time.time()
        self.prename = pre.name
        self.postname = post.name
        self.connection = connection

        print("Create Connection {0} -> {1} with pattern {2}".format(self.prename, self.postname, connection))

    def Debugprint(self, value, maxvalue, connectioncreated):

        if printDebug:
            endtime = time.time() - self.startTime
            timestr = "%3d:%02d" % (endtime / 60, endtime % 60)

            progress = value*100.0/(maxvalue)

            if progress > 0:
                estimatedtime = endtime / progress * 100
                estimatedtimestr = "%3d:%02d" % (estimatedtime / 60, estimatedtime % 60)
            else:
                estimatedtimestr = "--:--"

            print("{0} | {1} -> {2} | {3:.4f}% | {4: <7} | {5: <7} | {6: >15}".format(
                self.connection, self.prename, self.postname,
                value*100.0/(maxvalue), timestr, estimatedtimestr, connectioncreated))


############################
#### Connection pattern ####
############################
def all2all_exp2d(pre, post, factor, radius):
    """
    connecting two maps (normally these maps are equal) with gaussian receptive field depending on distance
    maps are 2d

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    factor : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("all2all_exp2d", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1])
    postDimLength = (post.geometry[0], post.geometry[1])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (preDimLength[0]-1)
    # Ratio of size between maps
    ratio_w = (preDimLength[0]-1)/float(postDimLength[0]-1)
    ratio_h = (preDimLength[1]-1)/float(postDimLength[1]-1)

    synapses = CSR()

    # for speedup
    m_exp = math.exp

    numOfConnectionsCreated = 0

    for post1 in range(postDimLength[0]):

        dout.Debugprint(post1, postDimLength[0], numOfConnectionsCreated)

        for post2 in range(postDimLength[1]):

            values = []
            pre_ranks = []

            for pre1 in range(preDimLength[0]):
                for pre2 in range(preDimLength[1]):

                    # distance between 2 neurons
                    dist_w = (ratio_w*post1-pre1)**2
                    dist_h = (ratio_h*post2-pre2)**2

                    val = factor * m_exp(-((dist_w+dist_h)/sigma/sigma))

                    #if val > MIN_CONNECTION_VALUE:
                    # connect
                    numOfConnectionsCreated += 1
                    pre_rank = pre.rank_from_coordinates((pre1, pre2))
                    pre_ranks.append(pre_rank)
                    values.append(val)

            post_rank = post.rank_from_coordinates((post1, post2))
            synapses.add(post_rank, pre_ranks, values, [0])

    dout.Debugprint(1, 1, numOfConnectionsCreated)

    return synapses


def all2all_exp4d(pre, post, factor, radius):
    """
    connecting two maps (normally these maps are equal) with gaussian receptive field depending on distance
    maps are 4d

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    factor : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("all2all_exp4d", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1], pre.geometry[2], pre.geometry[3])
    postDimLength = (post.geometry[0], post.geometry[1], post.geometry[2], post.geometry[3])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (preDimLength[0]-1)
    # Ratio of size between maps
    ratio_w = (preDimLength[0]-1)/float(postDimLength[0]-1)
    ratio_h = (preDimLength[1]-1)/float(postDimLength[1]-1)

    synapses = CSR()

    # for speedup
    m_exp = math.exp

    numOfConnectionsCreated = 0

    max_dist = sigma * math.sqrt(-math.log(MIN_CONNECTION_VALUE/factor))

    for post1 in range(postDimLength[0]):
        dout.Debugprint(post1, postDimLength[0], numOfConnectionsCreated)

        for post2 in range(postDimLength[1]):

            for post3 in range(postDimLength[2]):
                for post4 in range(postDimLength[3]):
                    pre_ranks  = []
                    values = []

                    # for speedup
                    rks_app = pre_ranks.append
                    vals_app = values.append
                    min1 = max(0, int(math.ceil(ratio_w*post1-max_dist)))
                    max1 = min(preDimLength[0]-1, int(math.floor(ratio_w*post1+max_dist)))
                    min2 = max(0, int(math.ceil(ratio_h*post2-max_dist)))
                    max2 = min(preDimLength[1]-1, int(math.floor(ratio_h*post2+max_dist)))
                    min3 = max(0, int(math.ceil(ratio_w*post3-max_dist)))
                    max3 = min(preDimLength[2]-1, int(math.floor(ratio_w*post3+max_dist)))
                    min4 = max(0, int(math.ceil(ratio_h*post4-max_dist)))
                    max4 = min(preDimLength[3]-1, int(math.floor(ratio_h*post4+max_dist)))

                    for pre1 in range(min1, max1+1): #xrange(preDimLength[0]):
                        for pre2 in range(min2, max2+1): #xrange(preDimLength[1]):
                            for pre3 in range(min3, max3+1): #xrange(preDimLength[2]):
                                for pre4 in range(min4, max4+1): #xrange(preDimLength[3]):

                                    # distance between 2 neurons
                                    dist_w = (ratio_w*post1-pre1)**2 + (ratio_w*post3-pre3)**2
                                    dist_h = (ratio_h*post2-pre2)**2 + (ratio_h*post4-pre4)**2

                                    val = factor * m_exp(-((dist_w+dist_h)/sigma/sigma))
                                    if val > MIN_CONNECTION_VALUE:

                                        # connect
                                        numOfConnectionsCreated += 1
                                        pre_rank = pre.rank_from_coordinates((pre1, pre2, pre3, pre4))
                                        rks_app(pre_rank)
                                        vals_app(val)

                    post_rank = post.rank_from_coordinates((post1, post2, post3, post4))
                    synapses.add(post_rank, pre_ranks, values, [0])

    dout.Debugprint(1, 1, numOfConnectionsCreated)

    return synapses


def gaussian2dTo4d_h(pre, post, mv, radius, delay=0):
    """
    connect two maps with a gaussian receptive field 2d to 4d

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    mv : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field
    delay : integer
        delay between transmission, default: 0

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("gaussian2dTo4d_h", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1])
    postDimLength = (post.geometry[0], post.geometry[1], post.geometry[2], post.geometry[3])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (preDimLength[0]-1)
    # Ratio of size between maps
    ratio_w = (preDimLength[0]-1)/float(postDimLength[0]-1)
    ratio_h = (preDimLength[1]-1)/float(postDimLength[1]-1)

    synapses = CSR()

    # for speedup
    m_exp = math.exp

    numOfConnectionsCreated = 0

    max_dist = sigma * math.sqrt(-math.log(MIN_CONNECTION_VALUE/mv))

    #w_post
    for post1 in range(postDimLength[0]):

        dout.Debugprint(post1, postDimLength[0], numOfConnectionsCreated)

        for post2 in range(postDimLength[1]):

            #h_post
            for post3  in range(postDimLength[2]):
                for post4 in range(postDimLength[3]):
                    pre_ranks  = []
                    values = []

                    # for speedup
                    min1 = max(0, int(math.ceil(ratio_w*post1-max_dist)))
                    max1 = min(preDimLength[0]-1, int(math.floor(ratio_w*post1+max_dist)))
                    min2 = max(0, int(math.ceil(ratio_h*post2-max_dist)))
                    max2 = min(preDimLength[1]-1, int(math.floor(ratio_h*post2+max_dist)))

                    for pre1 in range(min1, max1+1): #xrange(preDimLength[0]):
                        for pre2 in range(min2, max2+1): #xrange(preDimLength[1]):

                            dist_w = (ratio_w*post1-pre1)**2
                            dist_h = (ratio_h*post2-pre2)**2

                            val = mv * m_exp(-((dist_w+dist_h)/sigma/sigma))
                            if val > MIN_CONNECTION_VALUE:
                                # connect
                                numOfConnectionsCreated += 1

                                pre_rank = pre.rank_from_coordinates((pre1, pre2))
                                pre_ranks.append(pre_rank)
                                values.append(val)

                    post_rank = post.rank_from_coordinates((post1, post2, post3, post4))
                    synapses.add(post_rank, pre_ranks, values, [delay])

    dout.Debugprint(1, 1, numOfConnectionsCreated)

    return synapses


def gaussian2dTo4d_v(pre, post, mv, radius):
    """
    connect two maps with a gaussian receptive field 2d to 4d

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    mv : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("gaussian2dTo4d_v", pre, post)

    preDimLength  = (pre.geometry[0], pre.geometry[1]) # w, h
    postDimLength = (post.geometry[0], post.geometry[1], post.geometry[2], post.geometry[3]) # w1, w2, h1, h2

    # Normalization along width of sigma values on afferent map
    sigma = radius * (preDimLength[0]-1)
    # Ratio of size between maps
    ratio_w = (preDimLength[0]-1)/float(postDimLength[2]-1)
    ratio_h = (preDimLength[1]-1)/float(postDimLength[3]-1)

    synapses = CSR()

    # for speedup
    m_exp = math.exp


    numOfConnectionsCreated = 0

    max_dist = sigma * math.sqrt(-math.log(MIN_CONNECTION_VALUE/mv))

    #w_post
    for post1 in range(postDimLength[0]):

        dout.Debugprint(post1, postDimLength[0], numOfConnectionsCreated)

        for post2  in range(postDimLength[1]):

            #h_post
            for post3  in range(postDimLength[2]):
                for post4  in range(postDimLength[3]):

                    # for speedup
                    min1 = max(0, int(math.ceil(ratio_w*post3-max_dist)))
                    max1 = min(preDimLength[0]-1, int(math.floor(ratio_w*post3+max_dist)))
                    min2 = max(0, int(math.ceil(ratio_h*post4-max_dist)))
                    max2 = min(preDimLength[1]-1, int(math.floor(ratio_h*post4+max_dist)))

                    values = []
                    pre_ranks = []

                    for pre1 in range(min1, max1+1): #xrange(preDimLength[0]):
                        for pre2 in range(min2, max2+1): #xrange(preDimLength[1]):

                            dist_w = (ratio_w*post3-pre1)**2
                            dist_h = (ratio_h*post4-pre2)**2

                            val = mv * m_exp(-((dist_w+dist_h)/sigma/sigma))
                            if val > MIN_CONNECTION_VALUE:
                                # connect
                                numOfConnectionsCreated += 1

                                pre_rank = pre.rank_from_coordinates((pre1, pre2))
                                pre_ranks.append(pre_rank)
                                values.append(val)

                    post_rank = post.rank_from_coordinates((post1, post2, post3, post4))
                    synapses.add(post_rank, pre_ranks, values, [0])

    dout.Debugprint(1, 1, numOfConnectionsCreated)

    return synapses


def gaussian4dTo2d_h(pre, post, mv, radius, delay=0):
    """
    connect two maps with a gaussian receptive field 4d to 2d

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    mv : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field
    delay : integer
        delay between transmission, default: 0

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("gaussian4dTo2d_h", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1], pre.geometry[2], pre.geometry[3])
    postDimLength = (post.geometry[0], post.geometry[1])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (preDimLength[0]-1)
    # Ratio of size between maps
    ratio_w = (preDimLength[0]-1)/float(postDimLength[0]-1)
    ratio_h = (preDimLength[1]-1)/float(postDimLength[1]-1)

    synapses = CSR()

    # for speedup
    m_exp = math.exp

    numOfConnectionsCreated = 0

    max_dist = sigma * math.sqrt(-math.log(MIN_CONNECTION_VALUE/mv))

    # w_post
    for post1 in range(postDimLength[0]):

        dout.Debugprint(post1, postDimLength[0], numOfConnectionsCreated)

        for post2 in range(postDimLength[1]):

            values = []
            pre_ranks =[]

            # for speedup
            min1 = max(0, int(math.ceil(ratio_w*post1-max_dist)))
            max1 = min(preDimLength[0]-1, int(math.floor(ratio_w*post1+max_dist)))
            min2 = max(0, int(math.ceil(ratio_h*post2-max_dist)))
            max2 = min(preDimLength[1]-1, int(math.floor(ratio_h*post2+max_dist)))

            # w_pre
            for pre1 in range(min1, max1+1): #xrange(preDimLength[0]):
                for pre2 in range(min2, max2+1): #xrange(preDimLength[1]):

                    dist_w = (ratio_w*post1-pre1)**2
                    dist_h = (ratio_h*post2-pre2)**2

                    val = mv * m_exp(-((dist_w+dist_h)/sigma/sigma))
                    if val > MIN_CONNECTION_VALUE:
                        # connect

                        # h_pre
                        for pre3 in range(preDimLength[2]):
                            for pre4 in range(preDimLength[3]):
                                numOfConnectionsCreated += 1

                                pre_rank = pre.rank_from_coordinates((pre1, pre2, pre3, pre4))
                                pre_ranks.append(pre_rank)
                                values.append(val)


            post_rank = post.rank_from_coordinates((post1, post2))
            synapses.add(post_rank, pre_ranks, values, [delay])

    dout.Debugprint(1, 1, numOfConnectionsCreated)

    return synapses


def gaussian2dTo4d_diag(pre, post, mv, radius):
    """
    connect two maps with a gaussian receptive field 2d to 4d diagonally

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    mv : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("gaussian2dTo4d_diag", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1])
    postDimLength = (post.geometry[0], post.geometry[1], post.geometry[2], post.geometry[3])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (postDimLength[2]-1)

    offset_w = (preDimLength[0]-1)/2.0
    offset_h = (preDimLength[1]-1)/2.0

    synapses = CSR()

    # for speedup
    m_exp = math.exp

    numConnectionCreated = 0

    max_dist = sigma * math.sqrt(-math.log(MIN_CONNECTION_VALUE/mv))

    # w_post
    for post1 in range(postDimLength[0]):

        dout.Debugprint(post1, postDimLength[0], numConnectionCreated)

        for post2 in range(postDimLength[1]):

            # h_post
            for post3 in range(postDimLength[2]):
                for post4 in range(postDimLength[3]):

                    values = []
                    pre_ranks =[]

                    # for speedup
                    min1 = max(0, int(math.ceil(post1+post3-offset_w-max_dist)))
                    max1 = min(preDimLength[0]-1, int(math.floor(post1+post3-offset_w+max_dist)))
                    min2 = max(0, int(math.ceil(post2+post4-offset_h-max_dist)))
                    max2 = min(preDimLength[1]-1, int(math.floor(post2+post4-offset_h+max_dist)))

                    # w_pre
                    for pre1 in range(min1, max1+1): #xrange(preDimLength[0]):
                        for pre2 in range(min2, max2+1): #xrange(preDimLength[1]):

                            dist_w = (post1+post3-pre1 - offset_w)**2
                            dist_h = (post2+post4-pre2 - offset_h)**2

                            val = mv * m_exp(-((dist_w+dist_h)/sigma/sigma))
                            if val > MIN_CONNECTION_VALUE:
                                # connect
                                numConnectionCreated += 1

                                pre_rank = pre.rank_from_coordinates((pre1, pre2))
                                pre_ranks.append(pre_rank)
                                values.append(val)

                    post_rank = post.rank_from_coordinates((post1, post2, post3, post4))
                    synapses.add(post_rank, pre_ranks, values, [0])

    dout.Debugprint(1, 1, numConnectionCreated)

    return synapses


def gaussian4dTo2d_diag(pre, post, mv, radius, neglect=False):
    """
    connect two maps with a gaussian receptive field 4d to 2d diagonally
    intended to connect the central RBF maps to Xh

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    mv : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field
    neglect : bool, optional
        left side neglect, default is False

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("gaussian4dTo2d_diag", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1], pre.geometry[2], pre.geometry[3])
    postDimLength = (post.geometry[0], post.geometry[1])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (preDimLength[2]-1)

    offset_w = (preDimLength[0]-1)/2.0
    offset_h = (preDimLength[1]-1)/2.0

    synapses = CSR()

    # for speedup
    m_exp = math.exp

    numOfConnectionsCreated = 0

    max_dist = sigma * math.sqrt(-math.log(MIN_CONNECTION_VALUE/mv))

    if neglect:
        range_pre1 = [preDimLength[0]//2, preDimLength[0]]
        range_pre2 = [0, preDimLength[1]]
    else:
        range_pre1 = [0, preDimLength[0]]
        range_pre2 = [0, preDimLength[1]]

    # w_post
    for post1 in range(postDimLength[0]):
        dout.Debugprint(post1, postDimLength[0], numOfConnectionsCreated)
        for post2  in range(postDimLength[1]):

            values = []
            pre_ranks = []

            # w_pre
            for pre1 in range(range_pre1[0], range_pre1[1]):
                for pre2 in range(range_pre2[0], range_pre2[1]):

                    # for speedup
                    min1 = max(0, int(math.ceil(post1+offset_w-pre1-max_dist)))
                    max1 = min(preDimLength[2]-1, int(math.floor(post1+offset_w-pre1+max_dist)))
                    min2 = max(0, int(math.ceil(post2+offset_h-pre2-max_dist)))
                    max2 = min(preDimLength[3]-1, int(math.floor(post2+offset_h-pre2+max_dist)))

                    # h_pre
                    for pre3 in range(min1, max1+1): #xrange(preDimLength[2]):
                        for pre4 in range(min2, max2+1): #xrange(preDimLength[3]):

                            dist_w = (post1-(pre1+pre3) + offset_w)**2
                            dist_h = (post2-(pre2+pre4) + offset_h)**2

                            val = mv * m_exp(-((dist_w+dist_h)/sigma/sigma))
                            if val > MIN_CONNECTION_VALUE:
                                # connect
                                numOfConnectionsCreated += 1

                                pre_rank = pre.rank_from_coordinates((pre1, pre2, pre3, pre4))
                                pre_ranks.append(pre_rank)
                                values.append(val)

            post_rank = post.rank_from_coordinates((post1, post2))
            synapses.add(post_rank, pre_ranks, values, [0])

    dout.Debugprint(1, 1, numOfConnectionsCreated)

    return synapses


def gaussian4d_diagTo4d_v(pre, post, mv, radius):
    """
    connect two maps with a gaussian receptive field 4d to 4d
    it is intended to connect a 4d CD (that is retinotopic CD with eye position gain field, X_FEF)
    read out diagonally to the CD input side of LIP_CD

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    mv : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("gaussian4d_diagTo4d_v", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1], pre.geometry[2], pre.geometry[3])
    postDimLength = (post.geometry[0], post.geometry[1], post.geometry[2], post.geometry[3])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (postDimLength[2]-1)

    offset_w = (preDimLength[0]-1)/2.0
    offset_h = (preDimLength[1]-1)/2.0

    synapses = CSR()

    # for speedup
    m_exp = math.exp

    numConnectionCreated = 0

    max_dist = sigma * math.sqrt(-math.log(MIN_CONNECTION_VALUE/mv))

    #w_post
    for post1 in range(postDimLength[0]):
        for post2 in range(postDimLength[1]):

            dout.Debugprint(post1*postDimLength[1]+post2, postDimLength[0]*postDimLength[1], numConnectionCreated)

            #h_post
            for post3 in range(postDimLength[2]):
                for post4 in range(postDimLength[3]):

                    values = []
                    pre_ranks =[]

                    # w_pre
                    for pre1 in range(preDimLength[0]):
                        for pre2 in range(preDimLength[1]):

                            # for speedup
                            min1 = max(0, int(math.ceil(post3+offset_w-pre1-max_dist)))
                            max1 = min(preDimLength[2]-1, int(math.floor(post3+offset_w-pre1+max_dist)))
                            min2 = max(0, int(math.ceil(post4+offset_h-pre2-max_dist)))
                            max2 = min(preDimLength[3]-1, int(math.floor(post4+offset_h-pre2+max_dist)))

                            # h_pre
                            for pre3 in range(min1, max1+1): #xrange(preDimLength[2]):
                                for pre4 in range(min2, max2+1): #xrange(preDimLength[3]):

                                    dist_w = (post3-(pre1+pre3) + offset_w)**2
                                    dist_h = (post4-(pre2+pre4) + offset_h)**2

                                    val = mv * m_exp(-((dist_w+dist_h)/sigma/sigma))
                                    if val > MIN_CONNECTION_VALUE:
                                        # connect
                                        numConnectionCreated += 1
                                        pre_rank = pre.rank_from_coordinates((pre1, pre2, pre3, pre4))
                                        pre_ranks.append(pre_rank)
                                        values.append(val)

                    post_rank = post.rank_from_coordinates((post1, post2, post3, post4))
                    synapses.add(post_rank, pre_ranks, values, [0])

    dout.Debugprint(1, 1, numConnectionCreated)

    return synapses


def sur2dTo4d_diag(pre, post, mv, radius):
    """
    surround suppression for LIP

    Parameters
    ----------
    pre, post : ANNarchy.Population
        maps which should be connected
    mv : float
        strength of gaussian receptive field
    radius : float
        width of gaussian receptive field

    Returns
    -------
    synapses : ANNarchy.CSR
        ANNarchy description of connection pattern

    """

    dout = DebugOutput("sur2dTo4d_diag", pre, post)

    preDimLength = (pre.geometry[0], pre.geometry[1])
    postDimLength = (post.geometry[0], post.geometry[1], post.geometry[2], post.geometry[3])

    # Normalization along width of sigma values on afferent map
    sigma = radius * (postDimLength[2]-1)

    offset_w = (preDimLength[0]-1)/2.0
    offset_h = (preDimLength[1]-1)/2.0

    synapses = CSR()

    numConnectionCreated = 0

    # w_post
    for post1 in range(postDimLength[0]):
        for post2 in range(postDimLength[1]):

            dout.Debugprint(post1*postDimLength[1]+post2, postDimLength[0]*postDimLength[1], numConnectionCreated)

            # h_post
            for post3 in range(postDimLength[2]):
                for post4 in range(postDimLength[3]):

                    values = []
                    pre_ranks = []

                    # w_pre
                    for pre1 in range(preDimLength[0]):
                        for pre2 in range(preDimLength[1]):

                            dist_w = (post1+post3-pre1 - offset_w)**2
                            dist_h = (post2+post4-pre2 - offset_h)**2

                            if dist_w > sigma or dist_h > sigma:
                                val = mv
                                # connect
                                numConnectionCreated += 1
                                pre_rank = pre.rank_from_coordinates((pre1, pre2))
                                pre_ranks.append(pre_rank)
                                values.append(val)

                    post_rank = post.rank_from_coordinates((post1, post2, post3, post4))
                    synapses.add(post_rank, pre_ranks, values, [0])

    dout.Debugprint(1, 1, numConnectionCreated)

    return synapses