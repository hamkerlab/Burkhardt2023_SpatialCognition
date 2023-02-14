Quick start
============

Computational Model
-------------------

You can perform the initial setup and some testing simulations without using the virtual environment.
	
1. Navigate to the *combined/* folder and run the *combined.py* script. Using multiple jobs is advised. Depending on how many cores you have available on your system, you could use e.g. 8 jobs. Additionally, at least 32GB of RAM are recommended, but on a native Linux system you might get away with 16GB as long as you don't record and save any neuronal activity.

	With python from distribution run:

		python3 combined.py -j8 # run on 8 cores
		
	With Anaconda/Miniconda run:

		python combined.py -j8 # run on 8 cores

2. This should generate a few large connections and will afterwards compile the network. Once compiled, the connections will be saved and a default simulation will be run (the whole process will take roughly 10-20 minutes, depending on your system)

3. After the simulation is finished, navigate to the *Results/* folder to see some results from the simulation.

4. This simulation is a testing version, which only includes basic object localization on a pre-saved image and you are very limited with what you can do here. However, if you want, you can change the searched object in the *config.yaml* file.

		SET_TARGET: True
		TARGET: 1 # chose between 0 (yellow crane), 1 (green crane), 2 (green racecar)

5. You can now also use the previously saved connections in your future simulations to speed up the startup process by setting

		create_connections: False

5. For most other things, you will need to set up the virtual environment as described in the next section.

Virtual Environment
-------------------

We start with inizializing the virtual environment:

1. Navigate to *unity2019->APPConfig.config* and change the IP to your local IP.
	
		<IPAddress>YOURIP</IPAddress>

2. Open the Unity Hub and open the *unity2019* folder as a project. This might take several minutes, as Unity has to build the required modules. 

3. You will get many errors when starting for the first time after compiling. Restart Unity, and they should be gone.

4. In the bottom menu, navigate to *Project* -> *Assets/Scenes* and open the *SpatialCognition.unity* scene.

5. Start the scene by pressing the play button at the top. If everything is good to go, Felice should make a pointing animation towards the target objects.

6. To test the network interface, you can now run the *demo.py* script on your server, which will run the computational network. The file is located in the *UnityVR/newAgentbrain/* folder, and you will need to add the IP of the Unity computer.


To use Unity with the computational model, we need one last setup step on the Python side:

1. Open the *config.yaml* file which is located in the model folder and insert the IP address of your Unity machine:

		VR_IP_ADDRESS = 'YOURIP'

2. You can now activate the VR in the *config.yaml*

		RemoteDesktop: True

3. All other options in the *config.yaml* can now be used in combination with Unity.

4. If you get a timeout when running the model, you might need to create a rule in the Windows firewall, which allows connections between Unity and your compute server.