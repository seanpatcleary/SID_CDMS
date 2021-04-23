# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 10:28:03 2021

@author: cleary.186
"""

import glob as glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from matplotlib.widgets import EllipseSelector
from matplotlib.patches import Ellipse




def ellipse_check(x,y,x_cen, y_cen,width,height):
    
    value = ((x-x_cen)**2/(width**2)) + ((y-y_cen)**2/(height**2))
    if value > 1:
        return False
    else:
        return True
            
def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    toggle_selector.ES.x1, toggle_selector.ES.y1 = eclick.xdata, eclick.ydata
    toggle_selector.ES.x2, toggle_selector.ES.y2 = erelease.xdata, erelease.ydata



def toggle_selector(event):
    if toggle_selector.ES.x1 < toggle_selector.ES.x2:
        x1 = toggle_selector.ES.x1
        x2 = toggle_selector.ES.x2
    if toggle_selector.ES.y1 < toggle_selector.ES.y2:
        y1 = toggle_selector.ES.y1
        y2 = toggle_selector.ES.y2
    if toggle_selector.ES.x2 < toggle_selector.ES.x1:
        x2 = toggle_selector.ES.x1
        x1 = toggle_selector.ES.x2
    if toggle_selector.ES.y2 < toggle_selector.ES.y1:
        y2 = toggle_selector.ES.y1
        y1 = toggle_selector.ES.y2
    
    if event.key == 'enter':
        x_cen = (x2-x1)/2 + x1
        y_cen = (y2-y1)/2 + y1
        width = x2-x1
        height = y2 - y1
        oval_vals = [x_cen,y_cen,width,height]
        ovals.append(oval_vals)
        
        for i in range(len(ovals)):
            ellipse = Ellipse(xy=(ovals[i][0], ovals[i][1]), width=ovals[i][2], 
                              height=ovals[i][3], edgecolor='r', fc='None', 
                              lw=2)
            
            ax.add_patch(ellipse)
        plt.draw()
        
    elif event.key == 'delete':
        ax.clear()
        ax.imshow(heatmap, aspect = 'auto', vmax = 50, origin = 'lower',
               cmap = 'jet', interpolation= 'gaussian',
               extent=[yedges[0], yedges[-1], xedges[0],xedges[-1]])
        ovals.pop()
        for i in range(len(ovals)):
            ellipse = Ellipse(xy=(ovals[i][0], ovals[i][1]), width=ovals[i][2], 
                              height=ovals[i][3], edgecolor='r', fc='None', 
                              lw=2)
            
            ax.add_patch(ellipse)
        plt.draw()
    
    elif event.key == 'e':
        print('parsing files')
        for i in range(len(ovals)):
            check = []
            for j in range(len(mz_axis)):
                value = ellipse_check(mz_axis[j], slope[j], ovals[i][0], 
                                      ovals[i][1], ovals[i][2], ovals[i][3])
                check.append(value)
                
            df_new = df
            df_new['check'] = check
            df_final = df_new.loc[(df_new['check'] == True)]
            label = str(int(ovals[i][0])) + "_" + str(int(ovals[i][1])) +".csv"
            df_final.to_csv(label, index=False)
            print(str((i+1)/len(ovals)*100) + '% finished')

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', default='all')
parser.add_argument('-bmz', '--bins_mz', default = 1000)
parser.add_argument('-bm', '--bins_mass', default = 100)
parser.add_argument('-sf', '--smooth_function', default = 'gaussian')
args = parser.parse_args()

args.bins_mz = int(args.bins_mz)
args.bins_mass = int(args.bins_mass)

files = glob.glob("*.csv")

df = pd.read_csv(files[0], delimiter='\t')

for i in range(1,len(files)):
    df_temp = pd.read_csv(files[i], delimiter='\t')
    df = [df,df_temp]
    df = pd.concat(df)

slope = np.array(df["Slope"])
mz_axis = np.array(df["M/Z"])

ovals = []
heatmap, xedges, yedges = np.histogram2d(slope, mz_axis, 
                                         bins=[args.bins_mass, args.bins_mz])
fig, ax = plt.subplots() 
ax.imshow(heatmap, aspect = 'auto', vmax = 50, origin = 'lower',
               cmap = 'jet', interpolation= args.smooth_function,
               extent=[yedges[0], yedges[-1], xedges[0],xedges[-1]])
ax.set_xlabel('m/z')
ax.set_ylabel('slope')
c1 = 0
            
toggle_selector.ES = EllipseSelector(ax, line_select_callback,
                                       drawtype='box', useblit=True,
                                       button=[1, 3],  # don't use middle button
                                       minspanx=5, minspany=5,
                                       spancoords='pixels',
                                       interactive=True)
plt.connect('key_press_event', toggle_selector)
plt.show()
