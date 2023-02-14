import queue
import random
import sys
import threading

from .annar4Interface import *
from .annarProtoRecv import *
from .annarProtoSend import *
from .MsgObject_pb2 import *

RAND_MAX = 32767

class AnnarProtoSend(object):
    """

    AnnarProtoSend object to manage outgoing protobuf messages to Unity.

    Arguments:
        socketVR: Socket for the environment.
        socketAgent: Socket for an agent.

    """

    def __init__(self, socketVR, socketAgent):

        self.mutex = False
        self.done = True
        self.socketVR = socketVR
        self.socketAgent = socketAgent
        self.sentQueue = queue.Queue()

    ####################
    ## START - Messages
    ####################

    def sendVersionCheck(self, versionString):
        """

        Checks the version of the Unity server.

        Arguments:
            versionString: Version string of the client.

        """

        unit = MsgObject()

        unit.msgVersionCheck.version = versionString

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False


    def saccFlag(self, flag):
        """

        Send a flag to change the saccade mode from Van Opstal to linear
        Takes no arguments, sends 1 (True)
        
        """
        unit = MsgObject()

        unit.msgSaccFlag.flag = flag

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False


    def sendAgentMovement(self, degree, distance):
        """

        Execute a movement of the agent.
        Message name: MsgAgentMovement

        Arguments:
            degree: Float32, the direction to walk in degree(0 to 360). This direction 
            is relative to the world- or global coordinate system.
            distance: Float, the distance to walk.
        
        """
        unit = MsgObject()
        
        id = random.randrange(0, RAND_MAX)
        unit.msgAgentMovement.actionID = id
        unit.msgAgentMovement.distance = distance
        unit.msgAgentMovement.degree = degree

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


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
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentEyemovement.actionID = id
        unit.msgAgentEyemovement.panLeft = panLeft
        unit.msgAgentEyemovement.panRight = panRight
        unit.msgAgentEyemovement.tilt = tilt

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


    def sendEyeFixation(self, targetX, targetY, targetZ):
        """

        This command fixates the eyes at a certain point in the world coordinate system.
        Message name: MsgAgentEyefixation

        Arguments:
            targetX: Float32, the X-coordinate of the target point.
            targetY: Float32, the Y-coordinate of the target point.
            targetZ: Float32, the Z-coordinate of the target point.
        
        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentEyeFixation.actionID = id
        unit.msgAgentEyeFixation.targetX = targetX
        unit.msgAgentEyeFixation.targetY = targetY
        unit.msgAgentEyeFixation.targetZ = targetZ

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


    def sendEnvironmentReset(self, type):
        """

        Send a command that sets the VR back to a chosen state. This message should be
        used for restarting the whole experiment.
        Message name: MsgEnvironmentReset

        Arguments:
            type: Optional Int32, a parameter that selects one configuration if there 
            are more than one.
        
        """
        unit = MsgObject()

        unit.msgEnvironmentReset.Type = type

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False


    def sendTrialReset(self, type):
        """

        Send a command that sets partly the VR back to an chosen state. This message should
        be used for starting a new trial in an experiment.
        Message name: MsgTrialReset

        Arguments:
            type: Optional Int32, a parameter that selects one configuration if there 
            are more than one.
        
        """
        unit = MsgObject()

        unit.msgTrialReset.Type = type

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False


    def sendGeneralMsg(self, ownMsg):
        """

        NOTE: NOT TESTED YET.

        """

        self.mutex = True
        self.sentQueue.put(ownMsg)
        self.mutex = False


    def sendPointID(self, objectID):
        """

        Point at an object with the given ID.
        Message name: MsgAgentPointID

        NOTE: Not tested yet.

        Arguments:
            objectID: Int32, the value to identify the target object. The mapping value to 
            unity object depends on the current scenario.

        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentPointID.actionID = id
        unit.msgAgentPointID.objectID = objectID

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id

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
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentPointPos.actionID = id
        unit.msgAgentPointPos.targetX = targetX
        unit.msgAgentPointPos.targetY = targetY


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


    def sendGraspID(self, objectID):
        """

        Try to grasp an object with the given ID.
        Message name: MsgAgentGraspID

        Arguments:
            objectID:  Int32, the value to identify the target object. The mapping value 
            to unity object depends on the current scenario.
        
        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentGraspID.actionID = id
        unit.msgAgentGraspID.objectID = objectID


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


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
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentGraspPos.actionID = id
        unit.msgAgentGraspPos.targetX = targetX
        unit.msgAgentGraspPos.targetY = targetY


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id



    def sendGraspRelease(self):
        """

        Commands the agent to let go of whatever object it holds in its hand.

        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentGraspRelease.actionID = id


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


    def sendAgentTurn(self, degree):
        """

        Turns the Agent around the vertical axis.
        Message name: MsgAgentTurn

        Arguments:
            degree: Float value, the angle for the clockwise turn relative to the current 
            direction of the agent.

        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentTurn.actionID = id
        unit.msgAgentTurn.degree = degree


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id

    def sendAgentMoveTo(self, x, y, z, targetMode):
        """

        Execute a movement of the agent to a certain position along a path.
        Message name: MsgAgentMoveTo

        NOTE: Currently only usable in the SpartialCognition scene which has
        space grid and A* search.

        x: Float32, the X-coordinate of the target point.
        y: Float32, the Y-coordinate of the target point.
        z: Float32, the Z-coordinate of the target point.

        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentMoveTo.actionID = id
        unit.msgAgentMoveTo.posX = x
        unit.msgAgentMoveTo.posY = y
        unit.msgAgentMoveTo.posZ = z
        unit.msgAgentMoveTo.targetMode = targetMode


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


    def sendAgentCancelMovement(self):
        """

        The agent interrupts whatever movement it's currently executing.

        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentCancelMovement.actionID = id


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id

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
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentInteractionID.actionID = id
        unit.msgAgentInteractionID.objectID = objectID


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


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
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgAgentInteractionPos.actionID = id
        unit.msgAgentInteractionPos.targetX = targetX
        unit.msgAgentInteractionPos.targetY = targetY


        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id

    def sendStopSync(self):
        """

        NOTE: NOT TESTED YET.

        """
        unit = MsgObject()

        id = random.randrange(0, RAND_MAX)
        unit.msgStopSync

        self.mutex = True
        self.sentQueue.put(unit)
        self.mutex = False

        return id


        #####################
        ## END messages
        #####################


    def start(self):
        """ Starts a thread for the sending loop. """

        if self.done:

            self.done = False
            self.thread = threading.Thread(target=self.mainLoop)
            self.thread.start()


    def stop(self, wait):
        """ Stops the thread for the receiving loop. """

        if not self.done:

            self.done = True
            if wait:
                self.thread.join()


    def mainLoop(self):
        """ Loop function to serialize and send messages from the queue, to be executed by a thread. """

        while not self.done:

            try:

                if not self.mutex:
                    if not self.sentQueue.empty():
                        unit = self.sentQueue.get()
                        self.serializeAndSend(unit)
                time.sleep(1/1000000.0)
            except:
                print("ERROR(AnnarProtoSend): FAILED SENDING MESSAGE")
                raise


    def serializeAndSend(self, unit):
        """

        Serializes a protobuf message object to a string and sends it to the server together
        with a 4 byte header encoding the length of the message.

        Arguments:
            unit: Protobuf message object.

        """

        out = unit.SerializeToString()
        length = len(out)
        
        # a 4 byte header containg the length of the message after it, byte order and data type of the header is important ('<i')
        data = struct.pack('<i', length) + out

        # decision which socket to use
        if (unit.HasField("msgEnvironmentReset") or unit.HasField("msgTrialReset")):

            if (self.socketVR == -1):

                print("ERROR: SocketVR not initialized!")
                sys.exit(1)
            self.socketVR.sendall(data)

        else:
            self.socketAgent.sendall(data)


    def printBuffer(self, data):
        """ Simple function to print the data. """

        print(data)

