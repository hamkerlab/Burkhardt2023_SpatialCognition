import queue
import random
import struct
import sys
from PIL import Image
import io
import time
import numpy as np

from .annar4Interface import *
from .annarProtoRecv import *
from .annarProtoSend import *
from .MsgObject_pb2 import *

RAND_MAX = 32767
S_MSG = 1400
MAX_MSG = 16*2024*1024


def recvall(sock, count):
    """

    Function to receive a message of a certain length, that is bigger than the maximum buffer size.

    Arguments:
        sock: Socket object.
        count: Message length.

    """
    buf = bytes()
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


class AnnarProtoReceive(object):
    """

    AnnarProtoReceive object to manage incoming protobuf messages from Unity.

    Arguments:
        socketVR: Socket for the environment.
        socketAgent: Socket for an agent.

    """
    
    def __init__(self, socketVR, socketAgent):

        self.versionString = ""

        self.messageLength = 0
        self.done = True
        self.mutex = False
        self.socketVR = socketVR
        self.socketAgent = socketAgent

        self.validExternalReward = False
        self.externalReward = 0

        self.validGridsensor = False
        self.targetX = 0
        self.targetY = 0
        self.targetZ = 0
        self.targetRotationX = 0
        self.targetRotationY = 0
        self.targetRotationZ = 0

        self.validCollision = False
        self.actionColID = 0
        self.colliderID = 0

        self.validActionState = False

        self.validMenuItem = False
        self.eventID = 0

        self.hasReceivedStartSync = False

        self.validHeadMotion = False
        self.velocityX = 0
        self.velocityY = 0
        self.velocityZ = 0
        self.accelerationX = 0
        self.accelerationY = 0
        self.accelerationZ = 0
        self.rotationVelocityX = 0
        self.rotationVelocityY = 0
        self.rotationVelocityZ = 0
        self.rotationAccelerationX = 0
        self.rotationAccelerationY = 0
        self.rotationAccelerationZ = 0

        self.validEyePosition = False
        self.rotationPositionX = 0
        self.rotationPositionY = 0
        self.rotationPositionZ = 0
        self.rotationVelocityEyeX = 0
        self.rotationVelocityEyeY = 0
        self.rotationVelocityEyeZ = 0

        self.validObjectPosition = False
        self.greenCraneX = None
        self.greenCraneY  = None
        self.yellowCraneX  = None
        self.yellowCraneY  = None
        self.greenRacecarX  = None
        self.greenRacecarY  = None

        self.actionExecutionMap = {}

        self.parameter = None

        self.thread = None

        self.buffer = None
        self.messageStream = None


    def getImageData(self):
        """

        Turns image strings into PIL image objects and returns them as well as a bool for success.

        Returns:
            leftImage: Image of the left camera eye as a PIL object.
            rightImage: Image of the right camera eye as a PIL object.
            res: True, if image conversion to PIL objects was successful.

        """
        self.waitForMutexUnlock()

        #leftBuff = io.StringIO()
        #rightBuff = io.StringIO()
        #mainBuff = io.StringIO()

        leftBuff = io.BytesIO()
        rightBuff = io.BytesIO()
        mainBuff = io.BytesIO()

        leftBuff.write(self.leftImageString)
        rightBuff.write(self.rightImageString)
        mainBuff.write(self.mainImageString)

        leftBuff.seek(0)
        rightBuff.seek(0)
        mainBuff.seek(0)

        leftImage = Image.open(leftBuff)
        rightImage = Image.open(rightBuff)
        mainImage = Image.open(mainBuff)
        
        if (leftImage != None and rightImage != None and mainImage != None):
            res = True
        else:
            res = False

        return [leftImage, rightImage, mainImage, res]


    def getVersion(self):
        """

        Returns the version string.

        Returns:
            versionString: Version string.

        """
        self.waitForMutexUnlock()

        return self.versionString


    def getGridSensorData(self):
        """

        Returns grid sensor data and bool for retrieval success.

        Returns:
            targetX: Float32, the X-coordinate of the agent.
            targetY: Float32, the Y-coordinate of the agent.
            targetZ: Float32, the Z-coordinate of the agent.
            targetRotationX: Float32, the X-coordinate of the agent's rotation in the world.
            targetRotationY: Float32, the Y-coordinate of the agent's rotation in the world.
            targetRotationZ: Float32, the Z-coordinate of the agent's rotation in the world.
            res: Bool, True if retrieval was successful.

        """

        if not self.validGridsensor:
            res = False
        else:
            res = True
        self.waitForMutexUnlock()

        return [self.targetX, self.targetY, self.targetZ, self.targetRotationX, self.targetRotationY, self.targetRotationZ, res]


    def getExternalReward(self):
        """

        Returns the external reward and a bool for retrieval success.

        Returns:
            externalReward: Float32, the user-specified external reward for the agent.
            res: Bool, True if retrieval was successful.

        """

        if not self.validExternalReward:
            res = False
        else:
            res = True
        self.waitForMutexUnlock()

        return [self.externalReward, res]


    def getActionExecState(self, actionID):
        """

        Returns the action execution state for a specific action and a bool for retrieval success.

        Arguments:
            actionID: Id of the target action.

        Returns:
            actionExecutionMap[actionID]: Action execution state for the given action id.
            res: Bool, True if retrieval was successful.

        """

        if (not self.validActionState) or (not (actionID in self.actionExecutionMap)):
            res = False
        else:
            res = True
        self.waitForMutexUnlock()

        while not (actionID in self.actionExecutionMap):

            time.sleep(0.001)

        return [self.actionExecutionMap[actionID], res]


    def getCollision(self):
        """

        Returns collision data and a bool for retrieval success.

        Returns:
            actionColID: Int32, the value to identify the current action.
            colliderID: Int32, the ID of the collided item.
            res: Bool, True if retrieval was successful.

        """

        if not self.validCollision:
            res = False
        else:
            res = True

        return [self.actionColID, self.colliderID, res]


    def getEyePosition(self):
        """

        Returns eye position data and bool for retrieval success.

        Returns:
            rotationPositionX: Float32, X-coordinate of current rotation positon.
            rotationPositionY: Float32, Y-coordinate of current rotation positon.
            rotationPositionZ: Float32, Z-coordinate of current rotation positon.
            rotationVelocityEyeX: Float32, X-coordinate of current rotation alteration (per frame).
            rotationVelocityEyeY: Float32, Y-coordinate of current rotation alteration (per frame).
            rotationVelocityEyeZ: Float32, Z-coordinate of current rotation alteration (per frame).
            res: Bool, True if retrieval was successful.

        """

        if not self.validEyePosition:
            res = False
        else:
            res = True
        self.waitForMutexUnlock()

        return [self.rotationPositionX, self.rotationPositionY, self.rotationPositionZ, self.rotationVelocityEyeX, self.rotationVelocityEyeY, self.rotationVelocityEyeZ, res]

    def getObjectPosition(self):
        """

        Returns object positions and bool for retrieval success.

        Returns:
            X and Y positions of the objects as float32, 
            res: Bool, True if retrieval was successful.

        """

        if not self.validObjectPosition:
            res = False
        else:
            res = True
        self.waitForMutexUnlock()

        return [self.greenCraneX, self.greenCraneY, self.yellowCraneX, self.yellowCraneY, self.greenRacecarX, self.greenRacecarY, res]


    def getHeadMotion(self):
        """

        Returns head motion data and a bool for retrieval success.

        Returns:
            velocityX: Float32, X-coordinate of current movement alteration (per frame).
            velocityY: Float32, Y-coordinate of current movement alteration (per frame).
            velocityZ: Float32, Z-coordinate of current movement alteration (per frame).
            accelerationX: Float32, speedup X-coordinate of current rotation (per frame).
            accelerationY: Float32, speedup Y-coordinate of current rotation (per frame).
            accelerationZ: Float32, speedup Z-coordinate of current rotation (per frame).
            rotationVelocityX: Float32, X-coordinate of current rotation alteration (per frame).
            rotationVelocityY: Float32, Y-coordinate of current rotation alteration (per frame).
            rotationVelocityZ: Float32, Z-coordinate of current rotation alteration (per frame).
            rotationAccelerationX: Float32, speedup X-coordinate of current rotation (per frame).
            rotationAccelerationY: Float32, speedup Y-coordinate of current rotation (per frame).
            rotationAccelerationZ: Float32, speedup Z-coordinate of current rotation (per frame).
            res: Bool, True if retrieval was successful.

        """

        if not self.validHeadMotion:
            res = False
        else:
            res = True
        self.waitForMutexUnlock()

        return [self.velocityX, self.velocityY, self.velocityZ, self.accelerationX, self.accelerationY, self.accelerationZ, self.rotationVelocityX, self.rotationVelocityY, self.rotationVelocityZ, self.rotationAccelerationX, self.rotationAccelerationY, self.rotationAccelerationZ, res]


    def getMenuItem(self):
        """

        Returns menu item data and a bool for retrieval success.

        Returns:
            eventID: Int32, an enum to identify the event: 0 = start simulation, 1= stop simulation.
            parameter: Optional string, a string to send additional parameters.
            res: Bool, True if retrieval was successful.

        """

        if not self.validMenuItem:
            res = False
        else:
            res = True
        self.waitForMutexUnlock()

        return [self.eventID, self.parameter, res]


    def hasStartSyncReceived(self):
        """

        Returns bool for hasReceivedStartSync.

        Returns:
            True, if start sync was received.

        """

        if not self.hasReceivedStartSync:
            return False
        self.waitForMutexUnlock()

        self.hasReceivedStartSync = False
        return True


    def storeData(self, dataLength):
        """

        Parses a Protobuf message object from string and retrieves the available data from it.

        Arguments:
            dataLength: Length of the stored Protobuf message.

        """

        tmp = MsgObject()
        tmp.ParseFromString(self.messageStream)

        if tmp.HasField("msgImages"):
            self.mutex = True

            self.leftImageString = tmp.msgImages.leftImage
            self.rightImageString = tmp.msgImages.rightImage
            self.mainImageString = tmp.msgImages.mainImage


            self.mutex = False

        if tmp.HasField("msgReward"):
            self.mutex = True

            self.externalReward = tmp.msgReward.reward
            self.validExternalReward = True

            self.mutex = False

        if tmp.HasField("msgGridPosition"):
            self.mutex = True
            self.targetX = tmp.msgGridPosition.targetX
            self.targetY = tmp.msgGridPosition.targetY
            self.targetZ = tmp.msgGridPosition.targetZ
            self.targetRotationX = tmp.msgGridPosition.targetRotationX
            self.targetRotationY = tmp.msgGridPosition.targetRotationY
            self.targetRotationZ = tmp.msgGridPosition.targetRotationZ

            self.validGridsensor = True
            self.mutex = False


        if tmp.HasField("msgEyePosition"):
            self.mutex = True

            self.rotationPositionX = tmp.msgEyePosition.rotationPositionX
            self.rotationPositionY = tmp.msgEyePosition.rotationPositionY
            self.rotationPositionZ = tmp.msgEyePosition.rotationPositionZ
            self.rotationVelocityX = tmp.msgEyePosition.rotationVelocityX
            self.rotationVelocityY = tmp.msgEyePosition.rotationVelocityY
            self.rotationVelocityZ = tmp.msgEyePosition.rotationVelocityZ

            self.validEyePosition = True
            self.mutex = False

        if tmp.HasField("msgObjectPosition"):
            self.mutex = True

            self.greenCraneX = tmp.msgObjectPosition.greenCraneX
            self.greenCraneY = tmp.msgObjectPosition.greenCraneY
            self.yellowCraneX = tmp.msgObjectPosition.yellowCraneX
            self.yellowCraneY = tmp.msgObjectPosition.yellowCraneY
            self.greenRacecarX = tmp.msgObjectPosition.greenRacecarX
            self.greenRacecarY = tmp.msgObjectPosition.greenRacecarY

            self.validObjectPosition = True
            self.mutex = False

        if tmp.HasField("msgHeadMotion"):
            self.mutex = True

            self.velocityX = tmp.msgHeadMotion.velocityX
            self.velocityY = tmp.msgHeadMotion.velocityY
            self.velocityZ = tmp.msgHeadMotion.velocityZ
            self.accelerationX = tmp.msgHeadMotion.accelerationX
            self.accelerationY = tmp.msgHeadMotion.accelerationY
            self.accelerationZ = tmp.msgHeadMotion.accelerationZ
            self.rotationVelocityX = tmp.msgHeadMotion.rotationVelocityX
            self.rotationVelocityY = tmp.msgHeadMotion.rotationVelocityY
            self.rotationVelocityZ = tmp.msgHeadMotion.rotationVelocityZ
            self.rotationAccelerationX = tmp.msgHeadMotion.rotationAccelerationX
            self.rotationAccelerationY = tmp.msgHeadMotion.rotationAccelerationY
            self.rotationAccelerationZ = tmp.msgHeadMotion.rotationAccelerationZ

            self.validHeadMotion = True
            self.mutex = False


        if tmp.HasField("msgActionExecutationStatus"):
            self.mutex = True

            self.actionExecutionMap[tmp.msgActionExecutationStatus.actionID] = tmp.msgActionExecutationStatus.status

            self.validActionState = True
            self.mutex = False

        if tmp.HasField("msgCollision"):
            self.mutex = True
            self.actionColID = tmp.msgCollision.actionID
            self.colliderID = tmp.msgCollision.colliderID
            self.validCollision = True

            self.mutex = False


        if tmp.HasField("msgMenu"):
            self.mutex = True

            self.eventID = tmp.msgMenu.eventID
            if tmp.msgMenu.HasField("parameter"):
                self.parameter = tmp.msgMenu.parameter
            self.validMenuItem = True
            self.mutex = False


        if tmp.HasField("msgStartSync"):
            self.mutex = True

            self.hasReceivedStartSync = True

            self.mutex = False


        if tmp.HasField("msgVersionCheck"):
            self.mutex = True

            self.versionString = tmp.msgVersionCheck.version

            self.mutex = False


    def start(self):
        """ Starts a thread for the receiving loop. """

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
        """ Loop function to receive incoming messages, to be executed by a thread. """

        while not self.done:

            try:
                # retrieve header of message encoding the length of the rest
                dataLengthbuf = recvall(self.socketAgent, 4)
                if dataLengthbuf == None:
                    time.sleep(1.0/1000.0)
                    continue
                
                # bit order of header is important when converting it into an integer type ('<i')
                dataLength = struct.unpack('<i', dataLengthbuf)[0]
                if dataLength != 0:
                    if dataLength > 0:
                        if dataLength > MAX_MSG:
                            print("ERROR(AnnarProtoRecv): MSG TOO LONG!")
                        self.messageStream = recvall(self.socketAgent, dataLength)
                    else:
                        print("ERROR(AnnarProtoRecv): MSG IS EMPTY!")
                time.sleep(1/1000000.0)
                self.storeData(dataLength)

            except Exception as e:
                #print(e)
                #print("ERROR(AnnarProtoRecv): FAILED RECEIVING MESSAGE (close terminal if persists)")
                #time.sleep(1/1000.0)
                pass

    def waitForMutexUnlock(self):
        """ Simple function to wait until the mutex in unlocked. """

        while self.mutex:
            time.sleep(1/1000000.0)


