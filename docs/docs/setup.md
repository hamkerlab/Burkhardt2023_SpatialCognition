# Initial Setup

This page will provide some information about how to set up the neural network and Unity on different plattforms.

Generally, the computational network is meant to be used in combination with a Unity environment, which provides sensory information from the agent. However, simulation data from the paper is provided to run some simulations without Unity (see next page). So if you just want to get the network up and running, you can skip the Unity installation.


## Computational Model

The computational model is build with Python3 and the ANNarchy neural simulator. 
To run and install ANNarchy you need a GNU/Linux or OSX operating system. 
If you have a Windows PC, you need to use the Windows subsystem for linux (WSL2).


### Linux with Python from distribution
		
1. Navigate into the *Burkhardt2023_Spacecog* folder

2. Get all the required python packages (this might vary if you manage your python packages in a different way):

		pip3 install -r requirements.txt --user

### Linux with Anaconda/Miniconda

1. It might be smart to create a new conda environment:
	
		conda create --name spacecog python=3.9.2
		conda activate spacecog

2. Navigate into the *Burkhardt2023_Spacecog* folder

5. Get all the required python packages (this might vary if you manage your python packages in a different way):

		pip install -r requirements.txt


### Windows (with WSL2)

1. Install e.g. Ubuntu in a WSL2 environment. All further steps will have to be performed in WSL2.
		 
		https://www.omgubuntu.co.uk/how-to-install-wsl2-on-windows-10

2. Follow one of the two steps above (Linux with Python from distribution / Linux with Anaconda/Miniconda)


## Virtual Environment

The model uses Unity 2019.2.17f1, which has to be installed on a Windows PC. In Unity, the cognitive agent Felice will move through her room and provide the neural network with visual (and high-level positional) information.

	
1. Install Unity 2019.2.17f1:
	
		https://unity3d.com/de/get-unity/download/archive/

2. Get the *unity2019* folder from the repository.