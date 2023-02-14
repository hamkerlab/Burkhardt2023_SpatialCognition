"""
    Part of ANNarchy-SM

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import scipy
from ANNarchy import Population, Projection, np, CSR
from SM_neuron_model import *
from SM_load_mat_files import load_weights, print_shapes
from SM_parameters import ctrl_vars

weight_dict = load_weights()

# Care: Network size depends on loaded weights...
nb_neurons_H    = 1936
nb_neurons_BVC  = 816
nb_neurons_oPW  = 816
nb_neurons_OVC  = 816 # 51x16, steps of 7.2 degrees for theta, 0 and 360 degree are two different neurons
nb_neurons_PR   = 4
nb_neurons_oPR  = 9
nb_neurons_HD   = 100
nb_neurons_BVCone = np.ones( (nb_neurons_BVC,1) )

H_inhib_phi   = 0.4 # Will be multiplied with Hphi
BVC_inhib_phi = 0.2
PR_inhib_phi  = 9.0
HD_inhib_phi  = 0.4 # Will be multiplied with Hphi
TR_inhib_phi  = 0.075
oTR_inhib_phi = 0.1
PW_inhib_phi  = 0.165
PR_inhib_phi  = 9.0
OVC_inhib_phi = 0.7
oPW_inhib_phi = 0.2
oPR_inhib_phi = 1.0
OVC2oPR_inhib_phi = 0.0


# create Populations
HD = Population(nb_neurons_HD, neuron = HDNeuron, name = "HD")
BVC = Population(nb_neurons_BVC, neuron = BVCNeuron, name = "BVC")
PR = Population(nb_neurons_PR, neuron = PRNeuron, name = "PR")
oPR = Population(nb_neurons_oPR, neuron = oPRNeuron, name = "oPR")
PW = Population(nb_neurons_BVC, neuron = PWNeuron, name = "PW")
H = Population(nb_neurons_H, neuron = HNeuron, name = "H")
TR = Population( (nb_neurons_BVC, 20), neuron = TRNeuron, name = "TR")  # In MATLAB: 20 vectors of nb_neurons_BVC elements, we collapse them into one population (computationally the same)
IP = Population( 1, neuron = IPNeuron, name = "IP" )
oPW = Population(nb_neurons_oPW, neuron = oPWNeuron, name = "oPW")
OVC = Population(nb_neurons_OVC, neuron = OVCNeuron, name = "OVC")
oTR = Population( (nb_neurons_OVC, 20), neuron = oTRNeuron, name = "oTR")


# create Projections
default_delay = 0.05
inhib_delay = 0.025

HD2HD = Projection(pre = HD, post = HD, target = "HD2HD").connect_from_matrix(weight_dict['HD2HD'], delays = default_delay)
HDRotCCW = Projection(pre = HD, post = HD, target = "HDRotCCW").connect_from_matrix(weight_dict['Rotwts'], delays = default_delay)
HDRotCW = Projection(pre = HD, post = HD, target = "HDRotCW").connect_from_matrix(np.transpose(weight_dict['Rotwts']), delays = default_delay)
HD2IP = Projection(pre = HD, post = IP, target = "HD2IP").connect_all_to_all(weights=1.0, delays = inhib_delay)
IP2TR = Projection(pre = IP, post = TR, target = "IP2TR").connect_all_to_all(weights=1.0, delays = inhib_delay)
IP2oTR = Projection(pre = IP, post = oTR, target = "IP2oTR").connect_all_to_all(weights=1.0, delays = inhib_delay)
H2BVC = Projection(pre = H, post = BVC, target = "H2BVC").connect_from_matrix(weight_dict['H2BVC'], delays = default_delay)
BVC2H = Projection(pre = BVC, post = H, target = "BVC2H").connect_from_matrix(weight_dict['BVC2H'], delays = default_delay)
H2PR = Projection(pre = H, post = PR, target = "H2PR").connect_from_matrix(weight_dict['H2PR'], delays = default_delay)
H2oPR = Projection(pre = H, post = oPR, target = "H2oPR").connect_from_matrix(np.zeros([nb_neurons_oPR, nb_neurons_H]), delays = default_delay)
oPR2H = Projection(pre = oPR, post = H, target = "oPR2H").connect_from_matrix(np.zeros([nb_neurons_H, nb_neurons_oPR]), delays = default_delay)
oPR2PW = Projection(pre = oPR, post = PW, target = "oPR2PW").connect_from_matrix(np.zeros([nb_neurons_BVC, nb_neurons_oPR]), delays = default_delay)
oPR2HD = Projection(pre = oPR, post = HD, target = "oPR2HD").connect_from_matrix(np.zeros([nb_neurons_HD, nb_neurons_oPR]), delays = default_delay)
BVC2oPR = Projection(pre = BVC, post = oPR, target = "BVC2oPR").connect_from_matrix(np.zeros([nb_neurons_oPR, nb_neurons_BVC]), delays = default_delay)
oPR2BVC = Projection(pre = oPR, post = BVC, target = "oPR2BVC").connect_from_matrix(np.zeros([nb_neurons_BVC, nb_neurons_oPR]), delays = default_delay)
oPR2oPR = Projection(pre = oPR, post = oPR, target = "oPR2oPR").connect_from_matrix(np.eye(nb_neurons_oPR, nb_neurons_oPR) - oPR_inhib_phi, delays = default_delay)
PR2H = Projection(pre = PR, post = H, target = "PR2H").connect_from_matrix(weight_dict['PR2H'], delays = default_delay)
PR2PR = Projection(pre = PR, post = PR, target = "PR2PR").connect_from_matrix(weight_dict['PR2PR'], delays = default_delay)
PR2BVC = Projection(pre = PR, post = BVC, target = "PR2BVC").connect_from_matrix(weight_dict['PR2BVC'], delays = default_delay)
BVC2PR = Projection(pre = BVC, post = PR, target = "BVC2PR").connect_from_matrix(weight_dict['BVC2PR'], delays = default_delay)
BVC2BVC = Projection(pre = BVC, post = BVC, target = "BVC2BVC").connect_from_matrix(weight_dict['BVC2BVC'], delays = default_delay)
H2OVC = Projection(pre = H, post = OVC, target = "H2OVC").connect_from_matrix(np.zeros([nb_neurons_OVC, nb_neurons_H]), delays = default_delay)
OVC2H = Projection(pre = OVC, post = H, target = "OVC2H")
OVC2H.connect_from_matrix(np.zeros([nb_neurons_H, nb_neurons_OVC]), delays = default_delay)
OVC2BVC = Projection(pre = OVC, post = BVC, target = "OVC2BVC").connect_from_matrix(np.zeros([nb_neurons_BVC, nb_neurons_OVC]), delays = default_delay)
BVC2OVC = Projection(pre = BVC, post = OVC, target = "BVC2OVC").connect_from_matrix(np.zeros([nb_neurons_OVC, nb_neurons_BVC]), delays = default_delay)
OVC2OVC = Projection(pre = OVC, post = OVC, target = "OVC2OVC").connect_from_matrix(np.zeros([nb_neurons_OVC, nb_neurons_OVC]) - OVC_inhib_phi, delays = default_delay)
OVC2oPR = Projection(pre = OVC, post = oPR, target = "OVC2oPR").connect_from_matrix(np.zeros([nb_neurons_oPR, nb_neurons_OVC]) - OVC2oPR_inhib_phi, delays = default_delay)
oPR2OVC = Projection(pre = oPR, post = OVC, target = "oPR2OVC").connect_from_matrix(np.zeros([nb_neurons_OVC, nb_neurons_oPR]), delays = default_delay)

BVC2TR = []
TR2BVC = []
OVC2oTR = []
oTR2OVC = []
for i in range(20):
    BVC2TR.append(Projection(pre = BVC, post = TR[:,i], target = "BVC2TR").connect_from_sparse(weight_dict['BVC2TR'], delays = default_delay))
    TR2BVC.append(Projection(pre = TR[:,i], post = BVC, target = "TR2BVC").connect_from_sparse(weight_dict['TR2BVC'], delays = default_delay))
    OVC2oTR.append(Projection(pre = OVC, post = oTR[:,i], target = "OVC2oTR").connect_from_sparse(weight_dict['BVC2TR'], delays = default_delay))
    oTR2OVC.append(Projection(pre = oTR[:,i], post = OVC, target = "oTR2OVC").connect_from_sparse(weight_dict['TR2BVC'], delays = default_delay))

def load_TR_PW(ctrl_vars, default_delay):
    #print("load connections for SM model")
    #print(" - load TR-PW")
    filename = ctrl_vars['data_from_training']+'TRWeights_original.mat'

    # from_sparse_matrix() connector requires pre-ordererd pairs
    for i in range(20):
        weight_name = 'TR2PWwts'+str(i+1)
        weights = scipy.io.loadmat(filename)[weight_name].transpose()

        proj = Projection(pre = TR[:,i], post = PW, target = "TR2PW")
        proj.connect_from_sparse(weights, delays = default_delay)


def load_PW_TR(ctrl_vars, default_delay):
    """
    PW->TR are 816x816 slices stored as matlab sparse matrices. Please note, matlab stores in column-order.
    """
    #print(" - load PW-TR")
    filename = ctrl_vars['data_from_training']+'TRWeights_original.mat'

    # from_sparse_matrix() connector requires pre-ordererd pairs
    for i in range(20):
        weight_name = 'PW2TRwts'+str(i+1)
        weights = scipy.io.loadmat(filename)[weight_name].transpose()

        proj = Projection(pre = PW, post = TR[:,i], target = "PW2TR")
        proj.connect_from_sparse(weights, delays = default_delay)

def load_oTR_oPW(ctrl_vars, default_delay):
    #print(" - load oTR-oPW")
    filename = ctrl_vars['data_from_training']+'TRWeights_original.mat'

    # from_sparse_matrix() connector requires pre-ordererd pairs
    for i in range(20):
        weight_name = 'TR2PWwts'+str(i+1)
        weights = scipy.io.loadmat(filename)[weight_name].transpose()

        proj = Projection(pre = oTR[:,i], post = oPW, target = "oTR2oPW")
        proj.connect_from_sparse(weights, delays = default_delay)

def load_oPW_oTR(ctrl_vars, default_delay):
    """
    PW->TR are 816x816 slices stored as matlab sparse matrices. Please note, matlab stores in column-order.
    """
    #print(" - load oPW-oTR")
    filename = ctrl_vars['data_from_training']+'TRWeights_original.mat'

    # from_sparse_matrix() connector requires pre-ordererd pairs
    for i in range(20):
        weight_name = 'PW2TRwts'+str(i+1)
        weights = scipy.io.loadmat(filename)[weight_name].transpose()

        proj = Projection(pre = oPW, post = oTR[:,i], target = "oPW2oTR")
        proj.connect_from_sparse(weights, delays = default_delay)

# build up projections with pre-learned sparse matrices
load_TR_PW(ctrl_vars, default_delay)
load_PW_TR(ctrl_vars, default_delay)
load_oTR_oPW(ctrl_vars, default_delay)
load_oPW_oTR(ctrl_vars, default_delay)

# HD2TR
HD2TR = []
HD2oTR = []
for i in range(20):
    HD2TR.append(Projection(pre = HD, post = TR[:,i], target = "HD2TR").connect_from_matrix(weight_dict['HD2TR'][:,:,i], delays = default_delay))
    HD2oTR.append(Projection(pre = HD, post = oTR[:,i], target = "HD2oTR").connect_from_matrix(weight_dict['HD2TR'][:,:,i], delays = default_delay))

def layerwise_inhibition(pre, post, default_delay):
    synapses = CSR()
    values = np.ones(pre.geometry[0])
    delays = np.ones(pre.geometry[0])*default_delay

    for slice_idx in range(20):
        for post_idx_in_slice in range(post.geometry[0]):
            pre_positions = np.arange(0, pre.geometry[0])
            pre_ranks = [ pre.rank_from_coordinates((x, slice_idx)) for x in pre_positions ]
            post_rank = post.rank_from_coordinates((post_idx_in_slice, slice_idx))
            synapses.add(post_rank, pre_ranks, values, delays)

    return synapses

# Inhibitory connections with weight 1
H2H = Projection(pre = H, post = H, target = "H2H").connect_from_matrix(weight_dict['H2H'], delays = default_delay)
PW2PW = Projection(pre = PW, post = PW, target = "PW2PW").connect_all_to_all(weights=1, allow_self_connections=True, delays = default_delay)
oTR2oTR = Projection(pre=oTR, post=oTR, target = "oTR2oTR").connect_with_func(method=layerwise_inhibition, default_delay=default_delay)