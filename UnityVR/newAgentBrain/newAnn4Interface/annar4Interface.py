"""
Script for the Annar4Interface class, used to communicate with the according SimpleNetwork API for Unity.
"""

from .annar4Interface import *
from .annarProtoRecv import *
from .annarProtoSend import *
from .MsgObject_pb2 import *


import signal
import socket
import struct
import os
import threading
import time
import sys

MONITOR_INTERVAL = 1000


def waitForFullExec(annarInterface, id, timeout = -1):
    """
    
    Function to wait until an action is completely executed in the VR
    (only for actions which have an action execution state).

    Arguments:
        annarInterface: Annar4Interface object instance.
        id: Id of an action.
        timeout: Timeout parameter (default = -1).

    Returns:
        actionState: Action Execution Status Meaning:
            0 = InExecution
            1 = Finished
            2 = Aborted
            3 = Walking
            4 = Rotating
            5 = WalkingRotating

    """

    ret = False
    actionState = 0
        
    if timeout == -1:  
    
        while actionState != 1 and actionState != 2:
            ret = annarInterface.checkActionExecState(id)
            if ret:
                actionState = annarInterface.getActionExecState()
        return actionState
            
    else:
        
        start_time = time.time()
        dur = 0      
        while (actionState == 0) and dur < timeout:
            dur = time.time() - start_time
            ret = annarInterface.checkActionExecState(id)
            if ret:
                actionState = annarInterface.getActionExecState()
                
        if(dur >= timeout):
            print("Timeout")

        return actionState


def waitForExec(annarInterface, id, timeout = -1):
    """
    
    Function to wait until an action is completely executed in the VR
    (only for actions which have an action execution state).

    NOTE: Not sure if this is old (since it only checks for the 'InExecution' 
    action execution state, or if it only waits until the action was started 
    in the VR, not completed).

    Arguments:
        annarInterface: Annar4Interface object instance.
        id: Id of an action.
        timeout: Timeout parameter (default = -1).

    Returns:
        actionState: Action execution state.
            0 = InExecution
            1 = Finished
            2 = Aborted
            3 = Walking
            4 = Rotating
            5 = WalkingRotating

    """

    ret = False
    actionState = 0
        
    if timeout == -1:
        while actionState == 0:
            ret = annarInterface.checkActionExecState(id)
            if ret:
                actionState = annarInterface.getActionExecState()
        return actionState
            
    else:
        
        start_time = time.time()
        dur = 0      
        while (actionState == 0) and dur < timeout:
            dur = time.time() - start_time
            ret = annarInterface.checkActionExecState(id)
            if ret:
                actionState = annarInterface.getActionExecState()
                
        if(dur >= timeout):
            print("Timeout")

        return actionState


def timeout_loop(self):
    """ Loop function executed by a thread, which terminates object if a given timeout is exceeded. """

    while not done:

        if (softwareInterfaceTimeout != -1) and (interfaceNotUsed > softwareInterfaceTimeout):

            stop(False)

        

        time.sleep(MONITOR_INTERVAL/1000000.0)

        self.interfaceNotUsed = self.interfaceNotUsed + 1


class Annar4Interface(object):
    """

    Annar4Interface class, used to communicate with the according SimpleNetwork API for Unity.
    
    Arguments:
        srv_addr: IP-address of the Unity-VR host.
        remotePortNo: Port of the Unity-VR host (usually 1337, if not: look at APPConfig.config).
        agentNo: Id of the agent to be controlled.
        agentOnly: If True: Only sockets for agent controlling will be created.
        softwareInterfaceTimeout: Set a timeout threshold for the network communication (default = -1).

    """


    def __init__(self, srv_addr, remotePortNo, agentNo, agentOnly, softwareInterfaceTimeout=-1):

        ######################################
        ##### VERSION OF THE WHOLE INTERFACE
        ######################################

        self.version = "1.0"

        ######################################

        # since not all actions have an action execution state (for example sendEnvironmentReset), 
        # we wait a bit before sending the next message, so the VR has time to process the last Msg
        self.msgWaitingTime = 0.5

        self.leftImage = None
        self.rightImage = None

        self.gridSensorDataX = None
        self.gridSensorDataY = None
        self.gridSensorDataZ = None
        self.gridSensorDataRotationX = None
        self.gridSensorDataRotationY = None
        self.gridSensorDataRotationZ = None

        self.headMotionVelocityX = None
        self.headMotionVelocityY = None
        self.headMotionVelocityZ = None
        self.headMotionAccelerationX = None
        self.headMotionAccelerationX = None
        self.headMotionAccelerationX = None
        self.headMotionRotationVelocityX = None
        self.headMotionRotationVelocityY = None
        self.headMotionRotationVelocityZ = None
        self.headMotionRotationAccelerationX = None
        self.headMotionRotationAccelerationX = None
        self.headMotionRotationAccelerationX = None


        self.eyeRotationPositionX = None
        self.eyeRotationPositionY = None
        self.eyeRotationPositionZ = None
        self.eyeRotationVelocityX = None
        self.eyeRotationVelocityY = None
        self.eyeRotationVelocityZ = None

        self.greenCraneX = None
        self.greenCraneY = None
        self.yellowCraneX = None
        self.yellowCraneY = None
        self.greenRacecarX = None
        self.greenRacecarY = None

        self.externalReward = None

        self.state = None
        self.actionColID = None
        self.colliderID = None
        self.eventID = None
        self.parameter = None

        #################
        # CREATE SOCKETS
        #################
        if (not agentOnly):
       
        # create socket for VR

            try:

                self.socketVR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #timeval = struct.pack('ll', 1, 0)
                #self.socketVR.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
                self.socketVR.settimeout(5.0)
                self.socketVR.connect((srv_addr, remotePortNo))
            except socket.error as e:
                print("ERROR CONNECTING: " + str(e))
                sys.exit(1)      
        else:
            self.socketVR = -1

        # create socket for Agent

        try:
            #print "creating socket"
            self.socketAgent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #timeval = struct.pack('ll', 1, 0)
            #self.socketAgent.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
            self.socketAgent.settimeout(5.0)
            self.socketAgent.connect((srv_addr, remotePortNo + agentNo + 1))
        except socket.error as e:
            print("ERROR CONNECTING: " + str(e))
            sys.exit(1)

        # create sender and receiver

        self.sender = AnnarProtoSend(self.socketVR, self.socketAgent)
        self.receiver = AnnarProtoReceive(self.socketVR, self.socketAgent)


        if (softwareInterfaceTimeout == -1):
            self.softwareInterfaceTimeout = -1
        else:
            self.softwareInterfaceTimeout = softwareInterfaceTimeout*1000*1000/MONITOR_INTERVAL

        self.done = True
        self.interfaceNotUsed = 0


    def abort_signal(self, signal, frame):
        """

        If Ctrl-C is called, threads are closed properly to avoid having to 
        close the terminal every time something goes wrong.

        """

        print("\nMANUAL TERMINATION: Stopping all threads...")
        self.stop(True)
        sys.exit(0)


    def start(self):
        """

        Start Sender & Receiver and compare version 
        strings with the server (if versions are different, program exits).

        """

        
        # start the Ctrl-C signal handler
        signal.signal(signal.SIGINT, self.abort_signal)

        if (self.softwareInterfaceTimeout != -1) and (self.done):
            
            self.done = False
            self.thread = threading.Thread(target=timeout_loop)


        self.sender.start()
        self.receiver.start()

        self.sender.sendVersionCheck(self.version)
        VRVersion = ""
        while(VRVersion == ""):
            VRVersion = self.receiver.getVersion()
        print("/////////////////////////////////////")
        print("Client Version: " + self.version)
        print("VR Version: " + VRVersion)
        print("/////////////////////////////////////")
        print("")
        if (self.version != VRVersion):
            print("ERROR: Versions are different, please update your client!")
            self.stop(True)
            sys.exit(1)


    def stop(self, wait=True):
        """
        
        Terminates the Sender & Receiver threads.
        
        Arguments:
            wait: If True, wait for threads to terminate before exiting (default = True).
        
        """

        print("")
        print("/////////////////////////////////////")
        print("EXITING...")

        if self.sender is not None:

            self.sender.stop(wait)

        if self.receiver is not None:

            self.receiver.stop(wait)

        if (self.softwareInterfaceTimeout != -1) and (not self.done):
            
            self.done = True
            
            if wait:
                self.thread.join()

        print("DONE.")
        print("/////////////////////////////////////")


    ############################################################################################
    ### RECEIVING FUNCTIONS
    ###
    ### The receiving functions have 2 steps:
    ### 1) check the data, which loads new data from the receiving buffer, returning a True is successfully retrieved
    ### 2) get the data, which actually returns the wanted data
    ############################################################################################


    def checkImages(self):
        """

        Retrieves images and returns bool for successs (needs to be executed if you want to load new images).

        Returns:
            res: True, if data retrieval was successful.

        """

        self.leftImage, self.rightImage, self.mainImage, res = self.receiver.getImageData()

        return res


    def getImageLeft(self):
        """

        Returns left image previously retrieved by checkImages().

        Returns:
            leftImage: Byte [], the byte data of the left image in png-format.

        """

        return self.leftImage


    def getImageRight(self):
        """

        Returns right image previously retrieved by checkImages().

        Returns:
            rightImage: Byte [], the byte data of the right image in png-format.

        """

        return self.rightImage
    
    
    def getImageMain(self):
        """

        Returns main image previously retrieved by checkImages().

        Returns:
            mainImage: Byte [], the byte data of the right image in png-format.

        """

        return self.mainImage


    def checkGridSensorData(self):
        """

        Retrieves grid sensor data and returns bool for success (needs to be executed if you want to get new grid sensor data).

        Returns:
            res: True, if data retrieval was successful.

        """


        self.gridSensorDataX, self.gridSensorDataY, self.gridSensorDataZ, self.gridSensorDataRotationX, self.gridSensorDataRotationY, self.gridSensorDataRotationZ, res = self.receiver.getGridSensorData()
        return res


    def getGridSensorData(self):
        """

        This delivers the coordinates of the agent (previously retrieved by 
        checkGridSensorData()), like a GPS device. It is disabled by default and can be 
        enabled by AgentScript::SendGridPosition=true.
        Message name: MsgGridPosition

        Returns:
            gridData: List with grid sensor data including:
                gridSensorDataX: Float32, the X-coordinate of the agent.
                gridSensorDataY: Float32, the Y-coordinate of the agent.
                gridSensorDataZ: Float32, the Z-coordinate of the agent.
                gridSensorDataRotationX: Float32, the X-coordinate of the agent's rotation in the world.
                gridSensorDataRotationY: Float32, the Y-coordinate of the agent's rotation in the world.
                gridSensorDataRotationZ: Float32, the Z-coordinate of the agent's rotation in the world.

        """

        gridData = []

        gridData.append(self.gridSensorDataX)
        gridData.append(self.gridSensorDataY)
        gridData.append(self.gridSensorDataZ)
        gridData.append(self.gridSensorDataRotationX)
        gridData.append(self.gridSensorDataRotationY)
        gridData.append(self.gridSensorDataRotationZ)

        return gridData


    def checkHeadMotion(self):
        """

        Retrieves head motion data and returns bool for success (needs to be executed if you want to get new head motion data).

        Returns:
            res: True, if data retrieval was successful.

        """

        self.headMotionVelocityX, self.headMotionVelocityY, self.headMotionVelocityZ, self.headMotionAccelerationX, self.headMotionAccelerationY, self.headMotionAccelerationZ, self.headMotionRotationVelocityX, self.headMotionRotationVelocityY, self.headMotionRotationVelocityZ, self.headMotionRotationAccelerationX, self.headMotionRotationAccelerationY, self.headMotionRotationAccelerationZ, res = self.receiver.getHeadMotion()

        return res


    def getHeadMotion(self):
        """

        Delivers status information of the agent's head
        (previously retrieved by checkHeadMotion()).
        Message name: MsgHeadMotion

        Returns:
            headMotion: List with head motion data including:
                headMotionVelocityX: Float32, X-coordinate of current movement alteration (per frame).
                headMotionVelocityY: Float32, Y-coordinate of current movement alteration (per frame).
                headMotionVelocityZ: Float32, Z-coordinate of current movement alteration (per frame).
                headMotionAccelerationX: Float32, speedup X-coordinate of current rotation (per frame).
                headMotionAccelerationY: Float32, speedup Y-coordinate of current rotation (per frame).
                headMotionAccelerationZ: Float32, speedup Z-coordinate of current rotation (per frame).
                headMotionRotationVelocityX: Float32, X-coordinate of current rotation alteration (per frame).
                headMotionRotationVelocityY: Float32, Y-coordinate of current rotation alteration (per frame).
                headMotionRotationVelocityZ: Float32, Z-coordinate of current rotation alteration (per frame).
                headMotionRotationAccelerationX: Float32, speedup X-coordinate of current rotation (per frame).
                headMotionRotationAccelerationY: Float32, speedup Y-coordinate of current rotation (per frame).
                headMotionRotationAccelerationZ: Float32, speedup Z-coordinate of current rotation (per frame).

        """

        headMotion = []

        headMotion.append(self.headMotionVelocityX)
        headMotion.append(self.headMotionVelocityY)
        headMotion.append(self.headMotionVelocityZ)
        headMotion.append(self.headMotionAccelerationX)
        headMotion.append(self.headMotionAccelerationY)
        headMotion.append(self.headMotionAccelerationZ)
        headMotion.append(self.headMotionRotationVelocityX)
        headMotion.append(self.headMotionRotationVelocityY)
        headMotion.append(self.headMotionRotationVelocityZ)
        headMotion.append(self.headMotionRotationAccelerationX)
        headMotion.append(self.headMotionRotationAccelerationY)
        headMotion.append(self.headMotionRotationAccelerationZ)

        return headMotion


    def checkEyePosition(self):
        """

        Retrieves eye position data and returns bool for success (needs to be executed if you want to get new eye position data).

        Returns:
            res: True, if data retrieval was successful.

        """

        self.eyeRotationPositionX, self.eyeRotationPositionY, self.eyeRotationPositionZ, self.eyeRotationVelocityX, self.eyeRotationVelocityY, self.eyeRotationVelocityZ, res = self.receiver.getEyePosition()

        return res


    def getEyePosition(self):
        """

        Delivers status information of the eyes of the agent
        (previously retrieved by checkEyePosition()).
        Message name: MsgEyePosition


        Returns:
            eyePosition: List with eye position data including:
                eyeRotationPositionX: Float32, X-coordinate of current rotation positon.
                eyeRotationPositionY: Float32, Y-coordinate of current rotation positon.
                eyeRotationPositionZ: Float32, Z-coordinate of current rotation positon.
                eyeRotationVelocityX: Float32, X-coordinate of current rotation alteration (per frame).
                eyeRotationVelocityY: Float32, Y-coordinate of current rotation alteration (per frame).
                eyeRotationVelocityZ: Float32, Z-coordinate of current rotation alteration (per frame).

        """

        eyePosition = []

        eyePosition.append(self.eyeRotationPositionX)
        eyePosition.append(self.eyeRotationPositionY)
        eyePosition.append(self.eyeRotationPositionZ)
        eyePosition.append(self.eyeRotationVelocityX)
        eyePosition.append(self.eyeRotationVelocityY)
        eyePosition.append(self.eyeRotationVelocityZ)
    
        return eyePosition


    def checkObjectPosition(self):
        """

        Retrieves object position data and returns bool for success (needs to be executed if you want to get new object position data).

        Returns:
            res: True, if data retrieval was successful.

        """

        self.greenCraneX, self.greenCraneY, self.yellowCraneX, self.yellowCraneY, self.greenRacecarX, self.greenRacecarY, res = self.receiver.getObjectPosition()

        return res
    
    def getObjectPosition(self):
        """

        Delivers status information of the opbject positions
        Message name: MsgObjectPosition


        Returns:
            ObjectPosition: List with object position data (X,Y)

        """

        objectPosition = []

        objectPosition.append(self.greenCraneX)
        objectPosition.append(self.greenCraneY)
        objectPosition.append(self.yellowCraneX)
        objectPosition.append(self.yellowCraneY)
        objectPosition.append(self.greenRacecarX)
        objectPosition.append(self.greenRacecarY)
    
        return objectPosition

    def checkExternalReward(self):
        """

        Retrieves external reward data and returns bool for success (needs to be executed if you want to get new external reward data).

        Returns:
            res: True, if data retrieval was successful.

        """

        self.externalReward, res = self.receiver.getExternalReward()

        return res


    def getExternalReward(self):
        """

        Delivers reward (previously retrieved by checkExternalReward()) to the agent.
        Message name: MsgReward

        Returns:
            externalReward:  Float32, the user-specified external reward for the agent.

        """

        return self.externalReward


    def checkActionExecState(self, actionID):
        """

        Retrieves action execution state for a specific action and returns bool for success (needs to be executed if you want to get new action execution state data).

        Arguments:
            actionID: Int32, the value to identify the action.

        Returns:
            res: True, if data retrieval was successful.

        """

        self.state, res = self.receiver.getActionExecState(actionID)
        
        return res


    def getActionExecState(self):
        """

        Delivers the execution status of the last action
        (previously retrieved by checkActionExecState()).
        Message name: MsgActionExecutationStatus

        Returns:
            state: Int32, An enum describing the execution status of the action:
                0 = InExecution
                1 = Finished
                2 = Aborted
                3 = Walking
                4 = Rotating
                5 = WalkingRotating

        """

        return self.state


    def checkCollision(self):
        """

        Retrieves collision data and returns bool for success (needs to be executed if you want to get new collision data).

        Returns:
            res: True, if data retrieval was successful.

        """
        self.actionColID, self.colliderID, res = self.receiver.getCollision()

        return res


    def getCollision(self):
        """

        Returns the collision data previously retrieved by checkCollision().

        Returns:
            collisionData: List of collision data includig:
                actionColID: Int32, the value to identify the current action.
                colliderID: Int32, the ID of the collided item.

        """
        collisionData = []

        collisionData.append(self.actionColID)
        collisionData.append(self.colliderID)

        return collisionData


    def checkMenuItem(self):
        """

        Retrieves menu item data and returns bool for success (needs to be executed if you want to get new menu item data).

        Returns:
            res: True, if data retrieval was successful.

        """
        self.eventID, self.parameter, res = self.receiver.getMenuItem()

        return res


    def getMenuItemID(self):
        """

        Returns the menu item id previously retrieved by checkMenuItem().

        Returns:
            eventID: Int32, an enum to identify the event: 0 = start simulation, 1= stop simulation.


        """
        return self.eventID


    def getMenuItemParameter(self):
        """

        Returns the menu item parameter previously retrieved by checkMenuItem().

        Returns:
            parameter: Optional string, a string to send additional parameters.

        """
        return self.parameter


    def hasStartSyncReceived(self):
        """

        Returns True if start sync has been received.

        Returns:
            hasStartSyncReceived(): True, if start sync has been received.

        """

        return self.receiver.hasStartSyncReceived()


    ############################################################################################
    ### SENDING FUNCTIONS
    ###
    ### Functions which HAVE an Action Execution State, are executed with the waitForFullExec() function.
    ### If you don't want to wait for the full execution, you can look at the waitForExec() function at the top of the file.
    ############################################################################################

    
    def saccFlag(self, flag):
        """

        Send a flag to change the saccade mode from Van Opstal to linear
        Takes no arguments, sends True

        """
        print("Switch to linear saccade")
        return self.sender.saccFlag(flag)

    def videoSync(self, flag):
        """

        Send a flag for the agent to only walk small steps and wait afterwards
        It needs to be sent every time the Python side is ready do receive another image during video creation
        Takes no arguments, sends True

        """
        return self.sender.videoSync(flag)

    
    # send the agent to walk a certain distance in a certain direction (degrees)
    def sendAgentMovement(self, degree, distance):
        """

        Execute a movement of the agent.
        Message name: MsgAgentMovement

        Arguments:
            degree: Float32, the direction to walk in degree(0 to 360). This direction 
            is relative to the world- or global coordinate system.
            distance: Float, the distance to walk.
        
        """
        print("SEND & WAIT: AgentMovement")
        #waitForFullExec(self, self.sender.sendAgentMovement(degree, distance))
        return self.sender.sendAgentMovement(degree, distance) 

    def sendEyeMovement(self, panLeft, panRight, tilt):
        """

        This command rotates the eyes of the agent.
        Message name: MsgAgentEyemovement


        Arguments:
            panLeft: Float32, the rotation angle of the left eye in horizontal direction 
            (positive values rotate it leftwards). The view angle range is -30 to +30.
            panRight: Float32, the rotation angle of the right eye in horizontal direction 
            (positive values rotate it leftwards). The view angle range is -30 to +30.
            tilt: Float32, the rotation angle of the left and right eye in vertical direction. 
            The view angle range is -30 to +30.
        
        """
        print("SEND & WAIT: EyeMovement")
        #waitForFullExec(self, self.sender.sendEyeMovement(panLeft, panRight, tilt))
        return self.sender.sendEyeMovement(panLeft, panRight, tilt)

    def sendEyeFixation(self, targetX, targetY, targetZ):
        """

        This command fixates the eyes at a certain point in the world coordinate system.
        Message name: MsgAgentEyefixation

        Arguments:
            targetX: Float32, the X-coordinate of the target point.
            targetY: Float32, the Y-coordinate of the target point.
            targetZ: Float32, the Z-coordinate of the target point.
        
        """
        print("SEND & WAIT: EyeFixation")
        waitForFullExec(self, self.sender.sendEyeFixation(targetX, targetY, targetZ))


    def sendEnvironmentReset(self, type=0):
        """

        Send a command that sets the VR back to a chosen state. This message should be
        used for restarting the whole experiment.
        Message name: MsgEnvironmentReset


        NOTE: Waiting time, because EnvironmentReset does NOT return an execution status. If you experience
        the reset not being finished in time, increase msgWaitingTime parameter.

        Arguments:
            type: Optional Int32, a parameter that selects one configuration if there 
            are more than one.

        """
        print("SEND: EnvironmentReset")
        res = self.sender.sendEnvironmentReset(type)
        time.sleep(self.msgWaitingTime)
        return res


    def sendTrialReset(self, type=0):
        """

        Send a command that sets partly the VR back to an chosen state. This message should
        be used for starting a new trial in an experiment.
        Message name: MsgTrialReset


        NOTE: Waiting time, because TrialReset does NOT return an execution status. If you experience
        the reset not being finished in time, increase msgWaitingTime parameter.

        Arguments:
            type: Optional Int32, a parameter that selects one configuration if there 
            are more than one.
        
        """
        print("SEND: TrialReset")
        res = self.sender.sendTrialReset(type)
        time.sleep(self.msgWaitingTime)
        return res


    def sendGraspID(self, objectID):
        """

        Try to grasp an object with the given ID.
        Message name: MsgAgentGraspID

        Arguments:
            objectID:  Int32, the value to identify the target object. The mapping value 
            to unity object depends on the current scenario.
        
        """
        print("SEND & WAIT: GraspID")
        waitForFullExec(self, self.sender.sendGraspID(objectID))


    def sendGraspPos(self, targetX, targetY):
        """

        Try to grasp an object at the given position, specified in the viewfield coordinate
        system of the left eye.
        Message name: MsgAgentGraspPos

        Arguments:
            targetX: Float value, the X-coordinate of the position in the coordinate system 
            of the left eye.
            targetY: Float value, the Y-coordinate of the position in the coordinate system 
            of the left eye.
        
        """
        print("SEND & WAIT: GraspPos")
        waitForFullExec(self, self.sender.sendGraspPos(targetX, targetY))


    def sendPointPos(self, targetX, targetY):
        """

        Point at a position, specified in the viewfield coordinate system of the left eye. 
        Coordinate 0/0 is in the upper left corner.
        Message name: MsgAgentPointPos

        NOTE: Not tested yet.

        Arguments:
            targetX: Float value, the X-coordinate of the position in the coordinate system of 
            the left eye.
            targetY: Float value, the Y-coordinate of the position in the coordinate system of 
            the left eye.

        """
        print("SEND & WAIT: PointPos")
        waitForFullExec(self, self.sender.sendPointPos(targetX, targetY))


    def sendPointID(self, objectID):
        """

        Point at an object with the given ID.
        Message name: MsgAgentPointID

        NOTE: Not tested yet.

        Arguments:
            objectID: Int32, the value to identify the target object. The mapping value to 
            unity object depends on the current scenario.

        """

        print("SEND & WAIT: PointID")
        waitForFullExec(self, self.sender.sendPointID(objectID))


    def sendInteractionID(self, objectID):
        """

        Interact with an object with the given ID. The type of interaction should be specified
        and implemented in the VR itself.
        Message name: MsgAgentInteractionID

        NOTE: Not tested yet.

        Arguments:
            objectID: Int32, the value to identify the target object. The mapping value to 
            unity object depends on the current scenario.

        """

        print("SEND & WAIT: InteractionID")
        waitForFullExec(self, self.sender.sendInteractionID(objectID))


    def sendInteractionPos(self, targetX, targetY):
        """

        Interact with an object at a given position, specified in the viewfield coordinate 
        system of the left eye. Coordinate 0/0 is in the upper left corner. The type of
        interaction should be specified and implemented in the VR itself.
        Message name: MsgAgentInteractionPos

        NOTE: Not tested yet.

        Arguments:
            targetX: Float value, the x coordinate of the position in the coordinate system 
            of the left eye.
            targetY: Float value, the y coordinate of the position in the coordinate system 
            of the left eye.

        """

        print("SEND & WAIT: InteractionPos")
        waitForFullExec(self, self.sender.sendInteractionPos(targetX, targetY))


    def sendStopSync(self):
        """

        NOTE: NOT TESTED YET.

        """

        print("SEND: StopSync")
        res = self.sender.sendStopSync()
        time.sleep(self.msgWaitingTime)
        return res


    def sendGraspRelease(self):
        """

        Commands the agent to let go of whatever object it holds in its hand.

        """
        print("SEND & WAIT: GraspRelease")
        waitForFullExec(self, self.sender.sendGraspRelease())


    def sendAgentTurn(self, degree):
        """

        Turns the Agent around the vertical axis.
        Message name: MsgAgentTurn

        Arguments:
            degree: Float value, the angle for the clockwise turn relative to the current 
            direction of the agent.

        """

        print("SEND & WAIT: AgentTurn")
        #waitForFullExec(self, self.sender.sendAgentTurn(degree))
        return self.sender.sendAgentTurn(degree)        


    def sendAgentMoveTo(self, x, y, z, targetMode=0):
        """

        Execute a movement of the agent to a certain position along a path.
        Message name: MsgAgentMoveTo

        NOTE: Currently only usable in the SpartialCognition scene which has
        space grid and A* search.

        x: Float32, the X-coordinate of the target point.
        y: Float32, the Y-coordinate of the target point.
        z: Float32, the Z-coordinate of the target point.

        """

        print("SEND & WAIT: AgentMoveTo")
        #waitForFullExec(self, self.sender.sendAgentMoveTo(x, y, z, targetMode))
        return self.sender.sendAgentMoveTo(x, y, z, targetMode)


    def sendAgentCancelMovement(self):
        """

        The agent interrupts whatever movement it's currently executing 
        (only possible WITHOUT the use of the waitForFullExec() function).

        """

        print("SEND: AgentCancelMovement")
        res = self.sender.sendAgentCancelMovement()
        time.sleep(self.msgWaitingTime)
        return res


    def sendVersionCheck(self):
        """

        Checks the version of the Unity server 
        (this is called automatically when initializing the interface object).

        """

        res = self.sender.sendVersionCheck()
        time.sleep(self.msgWaitingTime)
        return res
