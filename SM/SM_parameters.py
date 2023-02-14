"""
    Part of the ANNarchy-SM model
    
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""
import numpy as np

ctrl_vars = dict()

# SIMULATION PARAMETERS
ctrl_vars['period'] = 30       # How many time steps for a bottom-up OR a top-down cycle

#
# AGENT MODEL TRAJECTORY AND PERCEPTION
#
ctrl_vars['Xag'] = 4
ctrl_vars['Yag'] = 17
ctrl_vars['HDag'] = np.pi
ctrl_vars['forward'] = 0

ctrl_vars['Vlin'] = 0.05        # 0.05 for video, default 0.1 - linear velocity start value, MUST BE SUPPLIED BY VR 
ctrl_vars['imag_flag'] = 0      # when this is 1, the old imagery setup is used, top-down and bottom-up alternate (see *** above)
ctrl_vars['navi_flag'] = 0      # start sim with navigation but only after a brief interval

# the "flags" set the state of the model. Names should be self-explanatory.
# E.g. while the percept_flag is equal to 1 we are in bottom-up parceptual
# model, i.e. the model is driven by perceptual input of where the
# boundaries are, meaning we force a PW activity onto the agent, based on
# what it sees. This activity goes throught tghe transformation circuit and
# drives BVC activity. Pattern completion in the MTL retrieves the correct
# place cell (the agent "knows" where it is).
ctrl_vars['DWELL'] = 150            # dwelltime at each target, including initial location, this is how long the agent stays fixed in front of the object
ctrl_vars['dwell'] = ctrl_vars['DWELL']
ctrl_vars['move2nextTarget'] = 0    # flag that indicates the agent should move to the next target in the list (see below). 

# NOTE! Targets need not be objects. We can simply supply a list of 2D
# coordinates for the agent. This can be replaced by the VR.
ctrl_vars['locateNextTarget'] = 0
ctrl_vars['rotResolved'] = 1
ctrl_vars['target_no'] = -1                        # index of next target, init with -1 (HD: In original matlab code they start with 0, but python is zero-indexed).
ctrl_vars['targetlist'] = np.array([ [ 3.5, 14.0], # list of target coordinates to be visited sequentially
                                     [ 8.0, 19.0],
                                     [18.0, 15.0],
                                     [ 9.0,  5.0],
                                     [15.0,  5.0] ]) # REPLACE THIS BY VR AGENT INPUT
ctrl_vars['n_targets'] = len(ctrl_vars['targetlist'][:,0])

ctrl_vars['HDestim'] = ctrl_vars['HDag']                           # for later use, estimate of HD
ctrl_vars['toturn'] = 0                                            # ..., how far does the agent still need to turn (ongoing, i.e. changes as total angle diminshes).
ctrl_vars['ang2f_tot'] = 0                                         # total angle to turn before we started turing
ctrl_vars['dist2f_cur'] = 0                                        # total distance to target location

#
# INTRODUCE OBJECTS, PREP FOR DETECT AND ENCODE
#
ctrl_vars['ObjEncThresh'] = 6.0                                    # Encode object when closer than this distance, 2.5 should work with your 1 unit boundary around objects which the agent cannot step into
ctrl_vars['ObjAttThresh'] = 10                                     # Attend all object within this radius (in front of you, 180 deg FOV) 
ctrl_vars['Xobj'] = 5                                              # this way, combined with the above trajectory the object will be 1 distance unit away upon completion of the first forward movement.
ctrl_vars['Yobj'] = 2
ctrl_vars['encoded'] = 0                                           # tells us if the next object is encoded ...
ctrl_vars['encoding'] = 0                                          # ... or still encoding
ctrl_vars['bup'] = 0

ctrl_vars['recallobj'] = 0                                         # flag will tell us to recall
ctrl_vars['imag_cuedur'] = 3000                                    # how long do we cue with the object identity
ctrl_vars['switchdur']   = 60                                      # how much time do we give the netweork for swituiching between modes (recall vs percep)
ctrl_vars['imag_start']  = 140000                                  # start to imagine at thuis time pt
ctrl_vars['imag_loc']  = 1                                         # NEW: starting imagination at a given location, not time

ctrl_vars['modstep'] = 100                                         # for Pdrive_PW
ctrl_vars['vidstep'] = 50                                          # for video
ctrl_vars['plt_ttl_flag'] = 1                                      # flag for plotting title in plot. 1=perception based navi, 2=imag, 3=reestablishing perception

ctrl_vars['Nobj'] = 9
ctrl_vars['data_from_training'] = '../SM/data_from_training/'             # Path to data_from_training folder
ctrl_vars['images'] = '../SM/'                                            # Path to images e.g. vr_img0
ctrl_vars['roomGrid'] = '../SM/'                                          # Path to roomGrid.txt

#   Angles in the model (HD and OVC) increase counterclockwise:
#   VR_ang = 2*pi - HD_ang, and vice versa
#   Additionally, an OVC angle of zero is "egocentric right"
ctrl_vars['angle_offset_VRvs4B'] = 2*np.pi
ctrl_vars['angle_offset_OVCvsHD'] = 0.5*np.pi

