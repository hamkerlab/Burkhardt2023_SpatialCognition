"""
    Part of ANNarchy-SM

    An ANNarchy version of the SM model published in:
    Bicanski, A. and Burgess, N. (2018). A neural-level model of spatial memory and imagery. eLife, 7:e33752. DOI: 10.7554/eLife.33752.

    This file contains all the neuron definitions required to 
    build up the model. This file is imported by network.py

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

from ANNarchy import Neuron

# Head direction cells
HDNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        HD2HDphi = 15.0 : population
        oPR2HDphi = 60.0 : population
        cue = 0.0
        cue_init = 0.0
        percep_flag = 1 : population
        imag_flag = 0 : population
        Rotphi = 4.0
        CWturn = 0: population
        CCWturn = 0: population
    """,
    equations = """
        k = -act + HD2HDphi * sum( HD2HD ) + cue_init + percep_flag * cue + Rotphi * CCWturn * sum( HDRotCCW ) + Rotphi * CWturn * sum( HDRotCW ) + imag_flag * oPR2HDphi * sum( oPR2HD )
        tau * dact/dt = k
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """, 
    name = "HD_Neuron"                                  
)

# Inhibitory feedback neuron
IPNeuron = Neuron(
    parameters = """
        alpha = 50
        beta = 0.1
        tau = 20.0
        HD2IPphi = 10 : population
    """,
    equations = """
        r = 1 / (1 + exp( -2 * beta * (HD2IPphi * sum(HD2IP) - alpha) ) )
    """,
    name = "IP_Neuron"
)

# Place cells (H -> Hippocampus)
HNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        ICtau = 20.0
        nb_neurons_H  = 1936
        Pmod = 0.05 : population
        Imod = 0.05 : population
        Hphi = 25.0 : population
        BVC2Hphi = 437.0 : population
        PR2Hphi = 25.0 : population
        OVC2Hphi = 5.0 : population
        oPR2Hphi = 100.0 : population
        use_syninput = 0 : population
    """,
    equations = """
        k = -act + use_syninput * ( Hphi * sum( H2H ) + Pmod * BVC2Hphi * sum( BVC2H ) + PR2Hphi * sum( PR2H ) + OVC2Hphi * sum( OVC2H ) + Imod * oPR2Hphi * sum( oPR2H ) + I_comp )
        tau * dact/dt = k
        r = (1 / (1 + exp( -2 * beta * ( act - alpha) ) ) )
        ICtau * dI_comp/dt = 15 - nb_neurons_H * mean(r);
    """, 
    name = "H_Neuron"   
)

# Boundary vector cells
BVCNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        Pmod = 0.05 : population
        Imod = 0.05 : population
        H2BVCphi = 2860.0 : population
        OVC2BVCphi = 0.0 : population
        TR2BVCphi = 30.0 : population
        PR2BVCphi = 3.0 : population
        use_syninput = 0 : population
    """,
    equations = """        
        k = -act + use_syninput * (sum( BVC2BVC ) + Imod * H2BVCphi * sum( H2BVC ) + OVC2BVCphi * sum( OVC2BVC ) + PR2BVCphi * sum( PR2BVC ) + Pmod * TR2BVCphi * sum( TR2BVC ))
        tau * dact/dt = k
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """, 
    # TR2BVCphi = 40.0 and H2BVCphi = 4000.0 slightly improve place cell accuracy and might be used instead (but should be tested again)
    name = "BVC_Neuron"
)

# Perirhinal boundary cells
PRNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 1
        alpha = 5.0
        Pmod = 0.05 : population
        Imod = 0.05 : population
        H2PRphi = 6000.0 : population
        BVC2PRphi = 75.0 : population
        use_syninput = 0 : population
        cue_percep = 0
    """,
    equations = """                
        k = -act + use_syninput * ( sum( PR2PR ) + Imod * H2PRphi * sum( H2PR ) + BVC2PRphi * sum( BVC2PR ) ) + cue_percep
        tau * dact/dt = k        
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """,
    name = "PR_Neuron"
)

# Perirhinal object cells
oPRNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        Pmod = 0.05 : population
        Imod = 0.05 : population
        oPR2oPRphi = 115.0 : population
        H2oPRphi = 1.0 : population
        OVC2oPRphi = 5.0 : population
        use_syninput = 0 : population
        percep_flag = 1 : population
        recallobj = 0 : population
        oPR_drive = 0.0
        Cue = 0
    """,
    equations = """
        k = -act + use_syninput * ( (oPR2oPRphi * sum(oPR2oPR) + H2oPRphi * sum( H2oPR ) + OVC2oPRphi * sum( OVC2oPR ) + recallobj * Cue) + percep_flag * 200 * oPR_drive )
        tau * dact/dt = k        
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """,
    name = "oPR_Neuron"
)

# Parietal window cells (boundaries)
PWNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        BcueScale = 1.6
        Pmod = 0.05 : population
        Imod = 0.05 : population
        TR2PWphi = 35 : population
        bath = 0.165 : population
        use_ego_cue_percep = 0 : population
        ego_cue_percep = 0.0
        use_syninput = 0 : population
    """,
    equations = """
        k = - act + use_syninput * ( -100 * bath + Imod * TR2PWphi * sum(TR2PW)  + BcueScale * use_ego_cue_percep * ego_cue_percep)
        tau * dact/dt = k
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """,
    name = "PW_Neuron"
)

# Parietal window cells (objects)
oPWNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        OcueScale = 0.3
        nb_neurons_oPW = 816
        Pmod = 0.05 : population
        Imod = 0.05 : population
        TR2oPWphi = 30 : population
        bath = 0.2 : population
        use_syninput = 0 : population
        ObjCue_percep = 0
    """,
    equations = """
        k = - act + use_syninput * ( -(nb_neurons_oPW * mean(r)) * bath + Imod * TR2oPWphi * sum( oTR2oPW ) ) + OcueScale * ObjCue_percep
        tau * dact/dt = k
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """,
    name = "oPW_Neuron"
)

# Transformation cells (boundaries)
TRNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        Pmod = 0.05 : population
        Imod = 0.05 : population
        bath = 0.075 : population
        HD2TRphi = 15 : population
        IP2TRphi = 90 : population
        PW2TRphi = 50 : population
        BVC2TRphi = 45 : population
        use_syninput = 0 : population
    """,
    equations = """                
        k = -act + use_syninput * ( -sum( TR2TR ) * bath + HD2TRphi * sum( HD2TR ) - IP2TRphi * sum( IP2TR ) + Imod * BVC2TRphi * sum( BVC2TR ) + Pmod * PW2TRphi * sum( PW2TR ) )
        tau * dact/dt = k
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """,
    name = "TR_Neuron"
)

# Object vector cells
OVCNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        Pmod = 0.05 : population
        Imod = 0.05 : population
        H2OVCphi = 2.1 : population
        TR2OVCphi = 60.0 : population
        OVC2OVCphi = 1.0 : population
        BVC2OVCphi = 0.0 : population
        oPR2OVCphi = 7.2 : population
        use_syninput = 0 : population
    """,
    equations = """                 
        k = -act + use_syninput * (OVC2OVCphi * sum( OVC2OVC ) + BVC2OVCphi * sum( BVC2OVC ) + Imod * H2OVCphi * sum( H2OVC ) + Imod * oPR2OVCphi * sum( oPR2OVC ) + Pmod * TR2OVCphi * sum( oTR2OVC ))
        tau * dact/dt = k
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """,                                                        
    name = "OVC_Neuron"
)

# Tranformation cells (objects)
oTRNeuron = Neuron(
    parameters = """
        tau = 20.0
        beta = 0.1
        alpha = 5.0
        Pmod = 0.05 : population
        Imod = 0.05 : population
        bath = 0.1 : population
        HD2oTRphi = 15 : population
        IP2oTRphi = 90 : population
        oPW2oTRphi = 60 : population
        OVC2oTRphi = 110 : population
        use_syninput = 0 : population
    """,
    equations = """
        k = -act + use_syninput * ( -sum( oTR2oTR ) * bath + HD2oTRphi * sum( HD2oTR ) - IP2oTRphi * sum( IP2oTR ) + Imod * OVC2oTRphi* sum( OVC2oTR ) + Pmod * oPW2oTRphi * sum( oPW2oTR ) )
        tau * dact/dt = k
        r = 1 / (1 + exp( -2 * beta * ( act - alpha ) ) )
    """,
    # OVC2oTRphi = 45 in eLife code, we have to adjust it since we use the actual weights instead of an identity matrix
    name = "oTR_Neuron"
)