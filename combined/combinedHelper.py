"""
    Simulations save data in a setting_data.txt file.
    The functions in this file extract information from these files for additional simulations or evaluation purposes. 

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import os
import natsort
import sys
import matplotlib.animation as animation
import numpy as np
import matplotlib.patches
from scipy.io import loadmat
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib import image as mpimg
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PIL import Image, ImageFont, ImageDraw
import matplotlib.font_manager as fm

sys.path.append('../VIS/')
from VIS_ParamVR import ModelParam

def label_VFs(ResultDir, target):
  posImage = Image.open(ResultDir + "VisualField_pos.png")
  draw = ImageDraw.Draw(posImage)
  font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 20)
  draw.text((10,10), "Encoding: " + str(target), font=font, fill=(0,0,0))
  posImage.save(ResultDir + "VisualField_pos.png")

  try:
    posImage = Image.open(ResultDir + "VisualField_att.png")
    draw = ImageDraw.Draw(posImage)
    font = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')), 20)
    draw.text((10,10), "Recall: " + str(target), font=font, fill=(0,0,0))
    posImage.save(ResultDir + "VisualField_att.png")
  except:
    pass

def create_video(ResultDir, exp, target, sn, saccade_step):
  print("Creating video")
  # load rates
  if sn == 0:
      fn = ResultDir + "rates_encoding.mat"
      img = mpimg.imread(ResultDir + "VisualField_pos.png")
      title = "Experiment " +str(exp) + ": Encode " + target
      fname = "encoding"
      dictRates = loadmat(fn)
      saccade_step = -1
  if sn == 1:
      fn = ResultDir + "rates_recall.mat"
      img = mpimg.imread(ResultDir + "VisualField_att.png")
      title = "Experiment " +str(exp) + ": Recall " + target
      fname = "recall"
      dictRates = loadmat(fn)
      saccade_step = saccade_step

  # take max over lip (otherwise average)
  max_lip = True

  # plot
  timestep = 0
  maxstep = dictRates['Xh'].shape[0]-1
  fig, ax = plt.subplots(2,3, figsize=(12,9))

  plt.subplots_adjust(left=0.02,
                      bottom=0, 
                      right=0.96, 
                      top=1, 
                      wspace=0.2, 
                      hspace=0.1)    
  
  fig.suptitle("")

  # Xh
  r = dictRates['Xh'][saccade_step]
  i0 = ax[0,0].imshow(r.T)
  ax[0,0].set_title("Xh")
  ax[0,0].set_xticks([])
  ax[0,0].set_yticks([])
  im_ratio = r.shape[1]/r.shape[0]
  fig.colorbar(i0, ax=ax[0,0], fraction=0.047*im_ratio)

  # LIP EP
  if max_lip:
    r = np.max(np.max(dictRates['LIP_EP'][saccade_step], axis=3), axis=2)
  else:
    r = np.average(np.average(dictRates['LIP_EP'][saccade_step], axis=3), axis=2)
  i1 = ax[0,1].imshow(r.T)
  ax[0,1].set_title("LIP EP")
  ax[0,1].set_xticks([])
  ax[0,1].set_yticks([])
  im_ratio = r.shape[1]/r.shape[0]
  fig.colorbar(i1, ax=ax[0,1], fraction=0.047*im_ratio)

  # FEFm
  r = dictRates['FEFm'][saccade_step]
  i2 = ax[1,0].imshow(r.T)
  ax[1,0].set_title("FEFm")
  ax[1,0].set_xticks([])
  ax[1,0].set_yticks([])
  im_ratio = r.shape[1]/r.shape[0]
  fig.colorbar(i2, ax=ax[1,0], fraction=0.047*im_ratio)

  # V4/IT L2/2
  r = np.max(dictRates['HVA23'][saccade_step], axis=2)
  i3 = ax[1,1].imshow(r.T)
  ax[1,1].set_title("V4/IT L2/3")
  ax[1,1].set_xticks([])
  ax[1,1].set_yticks([])
  im_ratio = r.shape[1]/r.shape[0]
  fig.colorbar(i3, ax=ax[1,1], fraction=0.047*im_ratio)

  # VF
  i4 = ax[1,2].imshow(img)
  ax[1,2].set_title("Visual Field")
  ax[1,2].set_xticks([])
  ax[1,2].set_yticks([])

  fig.delaxes(ax.flatten()[2])
  
  def animate_rates(timestep):
      if timestep >= maxstep:
        r = dictRates['Xh'][-1]
        i0.set_array(r.T)

        if max_lip:
          r = np.max(np.max(dictRates['LIP_EP'][-1], axis=3), axis=2)
        else:
          r = np.average(np.average(dictRates['LIP_EP'][-1], axis=3), axis=2)
        i1.set_array(r.T)

        r = dictRates['FEFm'][-1]
        i2.set_array(r.T)

        r = np.max(dictRates['HVA23'][-1], axis=2)
        i3.set_array(r.T)  

        if timestep % 20 == 0:
          print("timestep", timestep, "/", (dictRates['Xh'].shape[0]+40))
      
      else:
        r = dictRates['Xh'][timestep]
        i0.set_array(r.T)

        if max_lip:
          r = np.max(np.max(dictRates['LIP_EP'][timestep], axis=3), axis=2)
        else:
          r = np.average(np.average(dictRates['LIP_EP'][timestep], axis=3), axis=2)
        i1.set_array(r.T)

        r = dictRates['FEFm'][timestep]
        i2.set_array(r.T)

        r = np.max(dictRates['HVA23'][timestep], axis=2)
        i3.set_array(r.T)

        if timestep % 20 == 0:
          print("timestep", timestep, "/", (dictRates['Xh'].shape[0]+40))
          
        fig.suptitle(str(title) + " (step " + str(timestep) + ")", fontsize=20, fontweight="bold")
      return

  anim = animation.FuncAnimation(fig, animate_rates, frames=dictRates['Xh'].shape[0]+40)
  anim.save(ResultDir + fname + '.mp4', writer=animation.FFMpegWriter(fps=5))
  plt.close()

# Extracts the simulation steps from all setting_data files and calculates the average
def calculate_average_steps(timeout_runs):
  set_timeouts = set(timeout_runs)
  print("Simulations excluded from evaluation:", set_timeouts)
  
  for Experiment in range(1,4):
    folder = './Results/Exp' + str(Experiment) +'/'
    directories = natsort.natsorted(os.listdir(folder))
    
    first_loc_steps_average = 0
    second_loc_steps_average = 0
    total_runs = 0

    for simulation in directories:
      if simulation not in set_timeouts:
        total_runs += 1
        lines = []                             
        with open (str(folder + simulation + '/setting_data.txt'), 'rt') as setting_data: 
            for line in setting_data:                
                lines.append(line)           

        first_loc_steps_average += int(lines[2][18:21])
        second_loc_steps_average += int(lines[4][18:21])

    first_loc_steps_average /= total_runs
    second_loc_steps_average /= total_runs

    first_loc_steps_average = round(first_loc_steps_average)
    second_loc_steps_average = round(second_loc_steps_average)

    print("Exp", Experiment, ":", first_loc_steps_average, second_loc_steps_average)
  
  return 

def check_timeout():
  timeouts = []
  
  for Experiment in range(1,4):
    folder = './Results/Exp' + str(Experiment) +'/'
    directories = natsort.natsorted(os.listdir(folder))

    for simulation in directories:
      lines = []                             
      with open (str(folder + simulation + '/setting_data.txt'), 'rt') as setting_data: 
          for line in setting_data:                
              lines.append(line)           

      if int(lines[4][18:21]) > 600:
            timeouts.append(simulation)
  return timeouts

# Gets all positions from all available results folders
def read_positions(folder):
    directories = natsort.natsorted(os.listdir(folder))

    # get all positions as string
    positions = []
    for simulations in directories:
        lines = []                             
        with open (str(folder + simulations + '/setting_data.txt'), 'rt') as setting_data: 
            for line in setting_data:           
                lines.append(line)        
        positions.append(lines[1][15:-2])

    # convert strings into a list of lists
    positions_list = []
    for i in range(len(positions)):
        pos = positions[i].split(",")
        pos_list = []
        for j in pos:
            pos_list.append(float(j))
        positions_list.append(pos_list)
    
    return positions_list


# Gets all objects from all available results
def read_objects(folder):
    directories = natsort.natsorted(os.listdir(folder))

    # get all positions as string
    objects = []
    for simulations in directories:
        lines = []                             
        with open (str(folder + simulations + '/setting_data.txt'), 'rt') as setting_data: 
            for line in setting_data:                
                lines.append(line)        
        objects.append(int(lines[0][10:11]))
    
    return objects


# Used for the evaluation in Table 1
#timeout_runs = check_timeout()
#calculate_average_steps(timeout_runs)