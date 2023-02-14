"""
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import yaml

defParams = {}

# Initialize parameters from config
with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

defParams['save_connections'] = config['create_connections']
defParams['saveConnAt'] ='connections'

if config['Experiment'] == 4 or (config['RemoteDesktop'] == False and config['replication_experiment'] == 4):
    defParams['neglect'] = True
else:
    defParams['neglect'] = False  


## model parameters
# population size
defParams['v_h'] = 75
defParams['v_w'] = 100
defParams['layer_size_h'] = defParams['v_h']//5 + 1
defParams['layer_size_w'] = defParams['v_w']//5 + 1

# input signals
# top-down attention
defParams['att_sigma'] = 4.0
defParams['att_strength'] = 1.0
# EP signal
defParams['EP_noSuppression'] = 1
defParams['EP_off_decay_gaussian'] = 35
defParams['EP_update'] = 32
defParams['EP_sigma'] = 2.5
defParams['EP_strength'] = 0.3
defParams['EP_supp_off'] = 32
defParams['EP_supp_on'] = -50
defParams['EP_supp_strength'] = 0.1

# ODE
defParams['A_LIP_CD'] = 0.5
defParams['A_LIP_EP'] = 1.0
defParams['A_X_FEF'] = 1.0
defParams['D_LIP_CD'] = 0.1
defParams['D_LIP_EP'] = 0.1
defParams['D_Xh'] = 0.6
defParams['d_dep_Xh'] = 2.2
defParams['dt_dep_Xh'] = 1.0
defParams['tau_EP'] = 10.0
defParams['tau_LIP_CD'] = 10.0
defParams['tau_LIP_EP'] = 10.0
defParams['tau_X_FEF'] = 10.0
defParams['tau_Xh'] = 10.0
defParams['tau_dep_Xh'] = 10000.0

# connections
# strength
defParams['K_EP_LIP_EP'] = 1.0
defParams['K_EP_X_FEF'] = 10.0
defParams['K_FEFm_LIP_CD'] = 2.0
defParams['K_FEFm_LIP_EP'] = 2.0
defParams['K_FEFm_X_FEF'] = 20.0
defParams['K_LIP_CD_Xh'] = 0.015
defParams['K_LIP_EP_Xh'] = 0.05
defParams['K_X_FEF_LIP_CD'] = 30.0
defParams['K_Xh_LIP_CD'] = 1.3
defParams['K_Xh_LIP_EP'] = 1.3
defParams['K_exc_LIP_EP'] = 0.6
defParams['K_exc_Xh'] = 1.0
defParams['K_inh_LIP_CD'] = 0.03
defParams['K_inh_LIP_EP'] = 0.06
defParams['K_inh_X_FEF'] = 0.2
defParams['K_inh_Xh'] = 0.1
# width
defParams['sigma_EP_LIP_EP'] = 5.0
defParams['sigma_EP_X_FEF'] = 2.5
defParams['sigma_FEFm_LIP_CD'] = 1.25
defParams['sigma_FEFm_LIP_EP'] = 1.25
defParams['sigma_FEFm_X_FEF'] = 1.25
defParams['sigma_LIP_CD_Xh'] = 5
defParams['sigma_LIP_EP_Xh'] = 5
defParams['sigma_X_FEF_LIP_CD'] = 1.25
defParams['sigma_Xh_LIP_CD'] = 5.0
defParams['sigma_Xh_LIP_EP'] = 5.0
defParams['sigma_exc'] = 1.25
defParams['sigma_inh_Xh'] = 25.0
