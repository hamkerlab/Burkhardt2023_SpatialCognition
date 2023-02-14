# Results from simulations will be placed in this folder.
The folder also contains the simulation data from the paper.

- Exp1, Exp2, and Exp3 contain 100 random simulations
- Exp 4 contains a neglect simulation (Simulation_1) and an identical simulation without neglect (Simulation_2)

These data can be used to replicate simulations from the paper without using the VR (see config.yaml).

### Files:

 - setting_data.txt contains the setting data for each simulation
 - SM_00* files show visual information from the VR and neural activation from key populations of spatial memory and imagery
 - rep_agent* and rep_main* files are used as input when replicating simulations without the VR
 - VisualField files contain the visual field during various steps of the simulation
    - VisualField_pos shows the visual field from the encoding phase, with the red circle indicating the maximally firing FEFm neuron, and the blue circle indicating the maximally firing Xh neuron
    - VisualField_att shows (if used) the spatial attention signal and the maximally firing FEFm neuron for the second object localization in the recall phase
 - If record_encoding == True in the config.yaml file, then an additional video of key neural populations during visual encoding can be generated

### Known issues:

- In rare (random) occations, the agent will send a VF before completing the entire turn during recall. If this happens, the simulation needs to be re-done.

- Due to the distortion, the final saccade will be slightly too big when using the spherical projection shader. The shader can be disabled in *UnityVR/unity2019/APPConfig.config*.

- In some cases, FEFm and Xh show activity slightly above the green crane. Even though the model technically still encodes the correct object (V4 activity is just slightly expanded in this case), these trials were marked as erroneous in our evaluation.