"""
This file contains functions for graphical visualization and printing.

Classes & Functions:
   - Visualization (Class)
       --  create()
       --  Update()
   - Highlight()
   - PrintNetStruct()


:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
"""

import matplotlib.patches as patches
import matplotlib.pyplot  as plt
import os

######################################################################################################################################################
# Class for visual field and visualization
class Visualization:

    def __init__(self, VisualField, pathToSave=''):
        
        self.counter = 1
        self.pathToSave = pathToSave
        if not os.path.exists(pathToSave):
            os.makedirs(pathToSave)
        
        self.create(VisualField)
        
    def create(self, VisualField):
        # Create the figure
        self.fig = plt.figure(figsize = (8, 6))

        # insert background image
        plt.imshow(VisualField, zorder = 0)

        # Initialize plots
        self.plots = []
        
        ax = self.fig.add_subplot(111)
        
        # Plot an invisible circle
        d = ax.add_patch(patches.Circle((100, 100), radius = 40, alpha= 0, color = 'red'))      # alpha = 0 means invisible
        self.plots.append(d)
        
        plt.subplots_adjust(left = 0.05, right = 0.99, bottom = 0.05, top = 0.99)

        # Show the figure
        self.fig.show()
        plt.savefig(self.pathToSave + "Figure" + '%0.3d' %(self.counter) + ".png", dpi=100)
        self.counter += 1
        
    def Update(self, PlotCircle, CCX, CCY):
        # Set new center of the circle
        if PlotCircle == True:
            self.plots[0].set_alpha(0.5)
            self.plots[0].center = (CCX, CCY)
            

        self.fig.canvas.draw()
        plt.savefig(self.pathToSave + "Figure" + '%0.3d' %(self.counter) + ".png", dpi=100)
        self.counter += 1


######################################################################################################################################################
#   Pprint your output texts and messages in different colors 
#   Input Parameter(s):
#   - String: The input string which you want to print on the console.
#   - Color : The desired color.
#   - Bold  : If you want to print the string in Bold, set this parameter to True.
#
#   Return Value(s):
#   - A string which could be directly printed on console.
def Highlight(String, Color, Bold):
    AllColors = {'Gray': '30', 'Red': '31', 'Green': '32', 'Yellow': '33', 'Blue': '34', 'Pink': '35', 'Cyan': '36', 'White': '37'}
    Attr = []
    Attr.append(AllColors[Color])
    if Bold: Attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(Attr), String)