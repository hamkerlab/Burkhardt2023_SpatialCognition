import time
import sys
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

sys.path.append('../UnityVR/newAgentBrain/')
import newAnn4Interface

# unity server
VR_IP_ADDRESS = "192.168.0.12"
VR_UNITY_PORT = 1337
VR_AGENT_NO = 0

# create object and start threads
annarInterface = newAnn4Interface.Annar4Interface(VR_IP_ADDRESS, VR_UNITY_PORT, VR_AGENT_NO, False)
annarInterface.start()

# functions
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

# unity commands
annarInterface.sendEnvironmentReset(3)

#annarInterface.sendAgentMoveTo(9.0, 0.0, 5.0, 1)
#time.sleep(6)
#annarInterface.sendAgentTurn(100)
#time.sleep(3)

annarInterface.sendAgentMovement(180, 12)
time.sleep(5)

annarInterface.sendEyeMovement(10, 10, -15)
time.sleep(2)

t0 = time.time()
img = get_image(annarInterface)
t1 = time.time()
ms = (t1-t0)*1000
print(f"Getting image took {ms:.2f} ms\n")

plt.imshow(img)
plt.show()

# stop threads and delete object
annarInterface.stop(True)