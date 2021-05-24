#!/usr/bin/env python

import matplotlib.pyplot as plt
import os
import pickle
import numpy as np
import ipdb
import datetime
import matplotlib.dates as mdates

with open('/home/dev/Downloads/chirp_juha/Coord_3.data', 'rb') as f:
    Coord2 = pickle.load(f)

CD  = [x[0] for x in Coord2]
CD2 = [datetime.datetime.fromtimestamp(x) for x in CD]
CD3 = [CD2[i].day for i in range(len(CD2))]  # indices for individual day
CD4 = [i for i in range(1, len(CD3)) if CD3[i] != CD3[i-1]]
CD4 = [-1] + CD4 + [-1]

# ipdb.set_trace()

for j in range(len(CD4)-1):

    fig1, ax1 = plt.subplots()
    # ipdb.set_trace() 
    color = 'tab:red'
    ax1.set_xlabel('Date-Time (LT)')
    ax1.set_ylabel('Heights of Ordinary Layer (km)')
    #ax1.plot(CD2[CD4[j]+1:CD4[j+1]], [x[2] for x in Coord2[CD4[j]+1:CD4[j+1]]], '-o', color=color)

    xx = mdates.date2num(CD2[CD4[j]+1:CD4[j+1]])
    yy = [x[2] for x in Coord2[CD4[j]+1:CD4[j+1]]]

    z4 = np.polyfit(xx, yy, 3)
    p4 = np.poly1d(z4)
    dd = mdates.num2date(xx)
    ax1.plot(dd, p4(xx), 'o-g')
    ax1.plot(dd, yy, '.-r')

    cjj = CD2[CD4[j]+1]
    cjj1 = cjj.replace(hour=0, minute=0, second=0, microsecond=0)
    cjj2 = cjj.replace(hour=23, minute=59, second=0, microsecond=0)
    ax1.set(xlim=[cjj1, cjj2])
    ax1.set(ylim=[500, 1200])
    ax1.tick_params(axis='y', labelcolor=color)

    
    fig2, axx1 = plt.subplots()
    axx1.plot(dd, yy - p4(xx), '-o', color=color)
    axx1.set(xlim=[cjj1, cjj2])
    axx1.set(ylim=[-300, 150])
    axx1.set_xlabel('Date-Time (LT)')
    axx1.set_ylabel('Heights of Ordinary Layer (km)')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Frequencies of Ordinary Layer (MHz)')
    #ax2.plot(CD2[0:27],[x[1] for  x in Coord2[0:27]], color=color)
    #ax2.plot(CD2[CD4[j]+1:CD4[j+1]], [x[1] for x in Coord2[CD4[j]+1:CD4[j+1]]], '-o', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    yy1 = [x[1] for x in Coord2[CD4[j]+1:CD4[j+1]]]

    z4a = np.polyfit(xx, yy1, 3)
    p4a = np.poly1d(z4a)
  
    
    ax2.plot(dd, p4a(xx), 'o-g')
    ax2.plot(dd, yy1, '.-b')
    ax2.set_title('Heights/Frequencies of Ordinary Layer vs Date-Time')
    fig1.tight_layout()  # otherwise the right y-label is slightly clipped
    #ax1.set_ylabel('Heights of Ordinary Layer (km)')
    ax2.set(ylim=[1, 12])
    img_fname = "%s/Iono_%03d_%03d.png"%("/home/dev/Downloads/chirp_juha/Plots/Second",dd[0].month,dd[0].day)
    fig1.savefig(img_fname)
    #ipdb.set_trace()
    
    axx2 = axx1.twinx()
    axx2.plot(dd, yy1 - p4a(xx), '-o', color=color)
    axx2.set_title('Heights/Frequencies of Ordinary Layer vs Date-Time')
    axx2.set(ylim=[-9, 3])
    axx2.set_ylabel('Frequencies of Ordinary Layer (MHz)')
    fig2.tight_layout()
    img_fname1 = "%s/Iono_%03d_%03d_%s.png"%("/home/dev/Downloads/chirp_juha/Plots/Second",dd[0].month,dd[0].day,'a')
    fig2.savefig(img_fname1)
    fig1.clf()
    fig2.clf()
    plt.close('all')
    #ipdb.set_trace() 
   
   
   
   
   
   
