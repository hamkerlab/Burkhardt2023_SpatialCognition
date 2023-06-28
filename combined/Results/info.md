# Results from simulations will be placed in this folder.
The folder also contains the simulation data from the paper.

- Exp11, Exp12, and Exp13 contain 100 random simulations
- Exp21, Exp22, and Exp23 contain the same 100 simulations but in a cluttered environment after recall
- Exp33 contains a neglect simulation (Simulation_1) and an identical simulation without neglect (Simulation_2)

These data can be used to replicate simulations from the paper without using the VR (see config.yaml).

### Files:

 - setting_data.txt contains the setting data for each simulation
 - 00* files show visual information from the VR and neural activation from key populations of the model at the time points of encoding, recall and re-localisation
 - rep_agent* and rep_main* files are used as input when replicating simulations without the VR
 - VisualField files contain the visual field during various steps of the simulation
    - VisualField_pos shows the visual field from the encoding phase, with the red circle indicating the maximally firing FEFm neuron, and the blue circle indicating the maximally firing Xh neuron
    - VisualField_att shows (if used) the spatial attention signal and the maximally firing FEFm neuron for the second object localization in the recall phase
 - If record_encoding == True in the config.yaml file, then an additional video of key neural populations during visual encoding can be generated

### Additional information:
- In some cases, the maximalli FEFm and Xh neuron shows activity slightly above/next the green crane. Here, the model still encodes the correct object (V4 activity is just slightly expanded in this case)