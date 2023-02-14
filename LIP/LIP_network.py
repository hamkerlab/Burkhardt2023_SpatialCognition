"""
Network definition of the LIP Model

It is an ANNarchy-Python version of the original model and has been adapted for Spacecog. The original model is published in:
Bergelt, J., & Hamker, F. H. (2019). Spatial updating of attention across eye movements: A neuro-computational approach. Journal of Vision, 19(7), 10-10.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

from ANNarchy import Neuron, Population, Projection
from LIP_connectionPattern import gaussian2dTo4d_v, gaussian2dTo4d_diag, gaussian4dTo2d_diag, gaussian4d_diagTo4d_v, all2all_exp2d, all2all_exp4d, sur2dTo4d_diag # self-defined connection patterns
from LIP_parameters import defParams

##############################
#### Defining the neurons ####
##############################

# (head-centered) EP signal
EP_Neurons = Neuron(
    name='EP_Neuron',
    parameters="""
        tau = 'tau_EP' : population
        baseline = 0.0
    """,
    equations="""
        tau * dr_change/dt + r = pos(baseline) : min=0.0, max=1.0
        r = if (r_change)<0.00001: 0 else: r_change
    """,
    extra_values=defParams
)

# (head-centered) CD signal
X_FEF_Neurons = Neuron(
    name='XFEF_Neuron',
    parameters="""
        A = 'A_X_FEF' : population
        tau = 'tau_X_FEF' : population
        w_inh = 'K_inh_X_FEF' : population
        X_FEFsc = 0.2 : population
        num_neurons_w = 'layer_size_w' : population
        num_neurons_h = 'layer_size_h' : population
    """,
    equations="""
        num_neurons = num_neurons_w * num_neurons_h * num_neurons_w * num_neurons_h
        tau * dr_change/dt + r = X_FEFsc*sum(CD) * sum(EP) - r * w_inh * num_neurons * mean(r) : min = 0.0, max = 1.0
        r = if (r_change)<0.00001: 0 else: r_change
    """,
    extra_values=defParams
)

# LIP for EP
LIP_EP_Neurons = Neuron(
    name='LIPEP_Neuron',
    parameters="""
        A = 'A_LIP_EP' : population
        D = 'D_LIP_EP' : population
        tau = 'tau_LIP_EP' : population
        w_inh = 'K_inh_LIP_EP' : population
        FFsc = 0.35 : population
        FEFsc = 0.3 : population
        vSSP = 0.01: population
        num_neurons_w = 'layer_size_w' : population
        num_neurons_h = 'layer_size_h' : population
    """,
    equations="""
        num_neurons = num_neurons_w * num_neurons_h * num_neurons_w * num_neurons_h
        tau * dr_change/dt + r = (FFsc*sum(V4) + FEFsc*sum(FEF)) * pos(A - max(r))*sum(EP) + sum(FB)*sum(EP) + sum(exc) - (r + D) * w_inh * num_neurons * mean(r) - vSSP*sum(SSP) : min = 0.0, max = 1.0
        r = if (r_change)<0.00001: 0 else: r_change
    """,
    extra_values=defParams
)

# LIP for CD
LIP_CD_Neurons = Neuron(
    name='LIPCD_Neuron',
    parameters="""
        A = 'A_LIP_CD' : population
        D = 'D_LIP_CD' : population
        tau = 'tau_LIP_CD' : population
        w_inh = 'K_inh_LIP_CD' : population
        FBsc = 0.75 : population
        FEFsc = 0.15 : population
        vSSP = 0.4 : population
        num_neurons_w = 'layer_size_w' : population
        num_neurons_h = 'layer_size_h' : population
    """,
    equations="""
        num_neurons = num_neurons_w * num_neurons_h * num_neurons_w * num_neurons_h
        tau * dr_change/dt + r = (sum(V4) + FEFsc*sum(FEF)) * (1 + pos(A - r)*sum(CD)) + FBsc*sum(FB)*sum(CD) - (r + D) * w_inh *  num_neurons * mean(r) - vSSP*sum(SSP) : min = 0.0, max = 1.0
        r = if (r_change)<0.00001: 0 else: r_change
    """,
    extra_values=defParams
)

# Xh
Xh_Neurons = Neuron(
    name='Xh_Neuron',
    parameters="""
        D = 'D_Xh' : population
        tau = 'tau_Xh' : population
        dt_dep = 'dt_dep_Xh' : population
        tau_dep = 'tau_dep_Xh' : population
        d_dep = 'd_dep_Xh' : population
        w_inh = 'K_inh_Xh' : population
        neglect = 'neglect' : population
        FFsc = 1.2 : population
        NEsc = 0.7 : population
        INHsc = 1.2: population
        num_neurons_w = 'layer_size_w' : population
        num_neurons_h = 'layer_size_h' : population
        baseline = 0.0
    """,
    equations="""
        LIP_input = if neglect: NEsc * (sum(EP_neglect) + sum(CD_neglect)) else: FFsc* (sum(EP) + sum(CD))
        input = LIP_input + baseline
        s = s + (input - s)*dt_dep/tau_dep
        S2 = 1-d_dep*s : min = 0.0, max = 1.0
        num_neurons = num_neurons_w * num_neurons_h
        inh = (r + D) * INHsc*sum(inh)
        tau * dr_change/dt + r = input * S2 + sum(exc) - inh : min = 0.0, max = 1.0
        r = if (r_change)<0.00001: 0 else: r_change
    """,
    extra_values=defParams
)


###############################
#### Defining the synapses ####
###############################

#don't need them because we do not learn the weights


##################################
#### Creating the populations ####
##################################

# width is supposed to be greater or equal height
size_w = defParams['layer_size_w']
size_h = defParams['layer_size_h']

# (head-centered) EP signal
EP_Pop = Population(name='EP', geometry=(size_w, size_h), neuron=EP_Neurons)

# (head-centered) CD signal
X_FEF_Pop = Population(name='X_FEF', geometry=(size_w, size_h, size_w, size_h), neuron=X_FEF_Neurons)

# LIP
LIP_EP_Pop = Population(name='LIP_EP', geometry=(size_w, size_h, size_w, size_h), neuron=LIP_EP_Neurons)
LIP_CD_Pop = Population(name='LIP_CD', geometry=(size_w, size_h, size_w, size_h), neuron=LIP_CD_Neurons)

# Xh
Xh_Pop = Population(name='Xh', geometry=(size_w, size_h), neuron=Xh_Neurons)


##################################
#### Creating the projections ####
##################################

v = float(defParams['v_w']) # visual field
print("create LIP connections")

EP_X_FEF = Projection(
    pre=EP_Pop,
    post=X_FEF_Pop,
    target='EP'
).connect_with_func(method=gaussian2dTo4d_v, mv=defParams['K_EP_X_FEF'],
                    radius=defParams['sigma_EP_X_FEF']/v)

EP_LIP_EP = Projection(
    pre=EP_Pop,
    post=LIP_EP_Pop,
    target='EP'
).connect_with_func(method=gaussian2dTo4d_v, mv=defParams['K_EP_LIP_EP'],
                    radius=defParams['sigma_EP_LIP_EP']/v)

Xh_LIP_EP = Projection(
    pre=Xh_Pop,
    post=LIP_EP_Pop,
    target='FB'
).connect_with_func(method=gaussian2dTo4d_diag, mv=defParams['K_Xh_LIP_EP'],
                    radius=defParams['sigma_Xh_LIP_EP']/v)

LIP_EP_exc = Projection(
    pre=LIP_EP_Pop,
    post=LIP_EP_Pop,
    target='exc'
).connect_with_func(method=all2all_exp4d, factor=defParams['K_exc_LIP_EP'],
                    radius=defParams['sigma_exc']/v)

X_FEF_LIP_CD = Projection(
    pre=X_FEF_Pop,
    post=LIP_CD_Pop,
    target='CD'
).connect_with_func(method=gaussian4d_diagTo4d_v, mv=defParams['K_X_FEF_LIP_CD'],
                    radius=defParams['sigma_X_FEF_LIP_CD']/v)

Xh_LIP_CD = Projection(
    pre=Xh_Pop,
    post=LIP_CD_Pop,
    target='FB'
).connect_with_func(method=gaussian2dTo4d_diag, mv=defParams['K_Xh_LIP_CD'],
                    radius=defParams['sigma_Xh_LIP_CD']/v)

LIP_EP_Xh = Projection(
    pre=LIP_EP_Pop,
    post=Xh_Pop,
    target='EP'
).connect_with_func(method=gaussian4dTo2d_diag, mv=defParams['K_LIP_EP_Xh'],
                    radius=defParams['sigma_LIP_EP_Xh']/v)

LIP_EP_Xh_neglect = Projection(
    pre=LIP_EP_Pop,
    post=Xh_Pop,
    target='EP_neglect'
).connect_with_func(method=gaussian4dTo2d_diag, mv=defParams['K_LIP_EP_Xh'],
                    radius=defParams['sigma_LIP_EP_Xh']/v, neglect=True)

LIP_CD_Xh = Projection(
    pre=LIP_CD_Pop,
    post=Xh_Pop,
    target='CD'
).connect_with_func(method=gaussian4dTo2d_diag, mv=defParams['K_LIP_CD_Xh'],
                    radius=defParams['sigma_LIP_CD_Xh']/v)

LIP_CD_Xh_neglect = Projection(
    pre=LIP_CD_Pop,
    post=Xh_Pop,
    target='CD_neglect'
).connect_with_func(method=gaussian4dTo2d_diag, mv=defParams['K_LIP_CD_Xh'],
                    radius=defParams['sigma_LIP_CD_Xh']/v, neglect=True)

Xh_exc = Projection(
    pre=Xh_Pop,
    post=Xh_Pop,
    target='exc'
).connect_with_func(method=all2all_exp2d, factor=defParams['K_exc_Xh'],
                    radius=defParams['sigma_exc']/v)

Xh_inh = Projection(
    pre=Xh_Pop,
    post=Xh_Pop,
    target='inh'
).connect_with_func(method=all2all_exp2d, factor=defParams['K_inh_Xh'],
                    radius=defParams['sigma_inh_Xh']/v)

Xh_LIP_EP = Projection(
    pre=Xh_Pop,
    post=LIP_EP_Pop,
    target='SSP'
).connect_with_func(method=sur2dTo4d_diag, mv=50.0, radius=5)

Xh_LIP_CD = Projection(
    pre=Xh_Pop,
    post=LIP_CD_Pop,
    target='SSP'
).connect_with_func(method=sur2dTo4d_diag, mv=50.0, radius=5)