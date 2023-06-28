"""
    Part of ANNarchy-SM

    This file contains simple helper functions needed for communication
    with the Unity VR, e. g. retrieve current agent position.

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

from SM_parameters import ctrl_vars

import numpy as np
import time
from imageio import imwrite

def get_agent_pos(annarInterface, raw = False):
    """
    Get the current position of the agent in the VR.

    *parameter*:

        * *annarInterface*: instance of the python VR interface
        * *raw*: if set to true, the original position and orientation is returned, otherwise
                 a tuple (Xag, Yag, HDag) in SM space (by default set to *false*)

    *return*:

        either tuple (X, Y, Z, Xangle, Yangle, Zangle) or a tuple (Xag, Yag, HDag), see the *raw*
        parameter for more details.
    """
    # get position
    avail = annarInterface.checkGridSensorData()
    while not avail:
        avail = annarInterface.checkGridSensorData()

    agent_pos = annarInterface.getGridSensorData()

    # adapt to differing coordinate system
    Xag = agent_pos[0]
    Yag = agent_pos[2]
    # CCW orientation
    HDag = 2 * np.pi - (agent_pos[4] * np.pi / 180.0)

    if raw:
        return agent_pos
    else:
        return Xag, Yag, HDag

def get_eye_pos(annarInterface):
    
    avail = annarInterface.checkEyePosition()
    while not avail:
        avail = annarInterface.checkEyePosition()

    eyepos = annarInterface.getEyePosition()
    return eyepos

def get_object_pos(annarInterface):
    
    avail = annarInterface.checkObjectPosition()
    while not avail:
        avail = annarInterface.checkObjectPosition()

    objpos = annarInterface.getObjectPosition()
    return objpos

def wait_for_finished_walk(annarInterface, id, show_coords=False):
    print('Wait for finished agent walk ( id =', id, ')')
    avail = annarInterface.checkActionExecState(id) 
    while not avail:
        avail = annarInterface.checkActionExecState(id)
    
    state = annarInterface.getActionExecState()
     
    # Workaround for a network interface bug: Felice turns before she starts to walk which aborts the walking on linux side
    # In the interface the walk still continues but with id += 1, therefore we check if the turn has finished with idflag and then assign a new movement ID for the walk that follows
    idflag = False
    while True:        
        time.sleep(0.2)
        
        # We arrived at the target position
        if state == 1:
            time.sleep(1)
            break
        
        if show_coords:
            print('Position', get_agent_pos(annarInterface, True))
            
        avail = annarInterface.checkActionExecState(id)
        while not avail:
            avail = annarInterface.checkActionExecState(id)

        state = annarInterface.getActionExecState()
        print('', id, state)
        
    # get position
    avail = annarInterface.checkGridSensorData()
    while not avail:
        avail = annarInterface.checkGridSensorData()

    return annarInterface.getGridSensorData()

def wait_for_finished_turn(annarInterface, id, show_angle=False):
    """
    Wait for finished agent turn, encoded by action id *id*.

    *return*:
        None
    """
    print('Wait for finished agent turn ( id =', id, ')')
    avail = annarInterface.checkActionExecState(id)
    while not avail:
        avail = annarInterface.checkActionExecState(id)

    state = annarInterface.getActionExecState()
    while state != 1:
        time.sleep(2)

        if show_angle:
            print('  angle', get_agent_pos(annarInterface, True)[4])
            
        avail = annarInterface.checkActionExecState(id)
        while not avail:
            avail = annarInterface.checkActionExecState(id)

        state = annarInterface.getActionExecState()
        print('    ', id, state)

def wait_for_finished_eye_movement(annarInterface, id, show_angle=False):
    """
    Wait for finished eye movement, encoded by action id *id*.
    
    *return*:
        None
    """
    print('Wait for finished eye movement ( id =', id, ')')
    avail = annarInterface.checkActionExecState(id)
    while not avail:
        avail = annarInterface.checkActionExecState(id)
    
    state = annarInterface.getActionExecState()
    while state != 1:
        time.sleep(2)

        avail = annarInterface.checkActionExecState(id)
        while not avail:
            avail = annarInterface.checkActionExecState(id)

        state = annarInterface.getActionExecState()
        print('    ', id, state)

def transform_SM_to_VR(Xcoord, Ycoord):
    """
    Transforms decoded positions from [0..20, 0..20] to [-10..10, 0..20 ]
    """
    return Xcoord, Ycoord

def get_image(annarInterface):
    """
    Get the latest available image from the VR and store it.
    """
    avail = annarInterface.checkImages()
    while not avail:
        time.sleep(5)
        avail = annarInterface.checkImages() 

    leftImage = np.array(annarInterface.getImageLeft())
    
    return leftImage

def get_image2(annarInterface):
    """
    Get the latest available main camera image from the VR and store it.
    """
    avail = annarInterface.checkImages()
    while not avail:
        time.sleep(5)
        avail = annarInterface.checkImages() 

    mainImage = np.array(annarInterface.getImageMain())
    
    return mainImage 

def get_and_store_image(annarInterface, filename):
    """
    Get the latest available image from the VR and store it.
    """
    avail = annarInterface.checkImages()
    while not avail:
        time.sleep(5)
        avail = annarInterface.checkImages()

    leftImage = get_image(annarInterface)
    imwrite(filename, leftImage)