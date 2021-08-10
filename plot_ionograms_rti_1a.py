#!/usr/bin/env python3

# Save files in each of the folders using pickle (multi-frequency) and later load the files to make the plots through another script.
# Generalize

## 

import pickle
from numpy import unravel_index
import datetime
import shutil
import time
import sys
import chirp_det as cd
import chirp_config as cc
import scipy.constants as c
import h5py
import numpy as n

import glob
import os

import matplotlib.pyplot as plt
import pandas as pd
import ipdb


#rootdir = '/home/dev/Downloads/chirp_juha2b'
rootdir = '/media/dev/Seagate Backup Plus Drive/lfm_files'

# for subdir, dirs, files in os.walk(rootdir):
dirs = sorted(os.listdir(rootdir))

output_dir1 = "/home/dev/Downloads/chirp_juha2b/Plots20"
freqlist = [60, 80, 100, 120, 140, 160] 


def k_largest_index_argsort(S, k):
    idx = n.argsort(S.ravel())[:-k-1:-1]
    return n.column_stack(n.unravel_index(idx, S.shape))


def plot_ionogram(conf, f, Datadict, normalize_by_frequency=True):
    ho = h5py.File(f, "r")
    t0 = float(n.copy(ho[("t0")]))
    
    if not "id" in ho.keys():
        return
    cid = int(n.copy(ho[("id")]))  # ionosonde id

    # Delete old directory if exists
    # if f == 1 and os.path.exists(out_dir):
    #    shutil.rmtree(out_dir)

    #	strftime('%Y-%m-%d')+str('-loc'), cid, int(t00[0:4]), int(t00[5:7]), int(t00[8:10]), int(t00[11:13]), int(t00[14:16]), int(t00[17:19]))

    # if os.path.exists(img_fname):
    # print("Ionogram plot %s already exists. Skipping"%(img_fname))
    #    ho.close()
    #    return
    
    out_dir1 = os.path.join(output_dir1, cd.unix2dirname(t0))
       # Create new output directory
    if not os.path.exists(out_dir1):
        os.makedirs(out_dir1)

    #print("Reading %s rate %1.2f (kHz/s) t0 %1.5f (unix)" % (f, float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")]))))
    S = n.copy(ho[("S")])          # ionogram frequency-range
    freqs = n.copy(ho[("freqs")])  # frequency bins
    ranges = n.copy(ho[("ranges")])  # range gates
    Rate = n.copy(ho[("rate")])/1000  # Rate
    
    DataDict["freqs"] = freqs
   
    if normalize_by_frequency:
        for i in range(S.shape[0]):
            #noise = n.nanmedian(S[i, :])
            noise = n.median(S[i, :])
            #print('i=%d' %(i)) 
            if noise !=	0: 
                S[i, :] = (S[i, :]-noise)/noise
                                   
        S[S <= 0.0] = 1e-3

    # Three tips - chirp-rate / range / use list to append
    max_range_idx = n.argmax(n.max(S, axis=0))
    # axis 0 is the direction along the rows
        
    from numpy import unravel_index
    unarg = unravel_index(S.argmax(),S.shape)
    
    dB = n.transpose(10.0*n.log10(S))
    if normalize_by_frequency == False:
        dB = dB-n.nanmedian(dB)
    
    #unarg1 = unravel_index(dB.argmax(),dB.shape)
    unarg1 = unravel_index(n.nanargmax(dB),dB.shape)
    
    # Assume that t0 is at the start of a standard unix second therefore, the propagation time is anything added to a full second
    # if Rate == 100:
    dt = (t0-n.floor(t0))
    dr = dt*c.c/1e3    
    range_gates = dr+2*ranges/1e3
    r0 = range_gates[max_range_idx]
    SSin = k_largest_index_argsort(S, k=10)
    SSrn = n.sort(range_gates[SSin[:, 1]])
    
    DataDict["range_gates"] = range_gates
    
    dBB = {}
    for freq in freqlist:
        dBB[freqs[freq]/1e6] = dB[:, freq]
    
    #  I am trying to find positions in dB where positive dB values [for the frequency for which the maximum in dB has occurred] 
    #  are greater than a threshold [the threshold being : am - 3*ast]
    dB1a = dB[:,unarg1[1]]
    dB2 = dB1a[dB1a>0]
    pos = n.argwhere(dB1a > 0)
    rg_2 = range_gates[pos]
    ast = n.std(dB2)
    #ipdb.set_trace()
    am = n.max(dB2)
    apos = n.argwhere(dB2 > (am -3*ast))
    rg_3 = rg_2[apos]

    arr = []
    for j in rg_3:
            arr.append(j[0][0])
            
    arr1 = n.array(arr)            
    pos1 = n.argwhere((arr1 > 400) & (arr1 < 1000))
       
    ch1 = DataDict['ch1']
   
    if ((Rate == 100) and (400 < r0 < 1000)) |((Rate == 100) and (1000 < r0 < 1500) and (len(pos1) > 0)) :
        print('yes')
        range_gates2 = range_gates
        DataDict['range_gates2'] = range_gates
        #T0all.append(t0)
    
        ch1 += 1
        if ch1 == 1:
            
            DB3 = {}
            for freq in freqlist:
               DB3[freqs[freq]/1e6]  = dBB[freqs[freq]/1e6]
  
            T01 = n.array([t0])
            T03 = T01
            range_gates3 = range_gates
            
        else:
           
            DB3 = {}
            for freq in freqlist:
            	DB3[freqs[freq]/1e6]  = n.column_stack((DataDict['DBall'][freqs[freq]/1e6], dBB[freqs[freq]/1e6]))            
            	
            T03  = n.hstack((DataDict['Time'], n.array([t0])))
            range_gates3 = n.column_stack((DataDict['range_gates3'],range_gates))
             
        DataDict['DBall'] = DB3
        DataDict['Time'] = T03
        DataDict['range_gates3'] = range_gates3
        DataDict['ch1'] = ch1
        ipdb.set_trace()
        print('ch1_inside=%d' %(ch1))

def save_var(DataDict):
    #global ch1, dB3, dB3a, dB3b, dB3c, T03, T01, range_gates, range_gates2, range_gates3, freqs

    #path1 = rootdir + '/' + dirs1 + '/' + dirs1[5:10] + 'c.data'
    path1 = output_dir1 + '/' + dirs1 + '/' + dirs1[5:10] + 'j.data'
    #path1 = output_dir1 + '/' + cd.unix2dirname(T03[0])[5:10] + '.data'

    print(path1)
    ipdb.set_trace()
    with open(path1, 'wb') as f:
        pickle.dump(DataDict, f)

    # with open('/home/dev/Downloads/chirp_juha2b/Time_2.data', 'rb') as f:
    #    T03, dB3, range_gates =  pickle.load(f)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        conf = cc.chirp_config(sys.argv[1])
    else:
        conf = cc.chirp_config()

    if conf.realtime:
        while True:
            fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
            fl.sort()
            for f in fl:
                plot_ionogram(conf, f,DataDict)
            time.sleep(10)
            save_var()
    else:
        for j in range(0, len(dirs)):
            dirs1 = dirs[j]
            
            dtt1 = datetime.datetime.strptime('2021-05-31','%Y-%m-%d').date()
            dtt2 = datetime.datetime.strptime(dirs1[0:10],'%Y-%m-%d').date()
            #ipdb.set_trace()
            #if dtt2 > dtt1 :
            if dirs1[0:10] == '2021-05-02':
            #if dirs1[0:4] == '2021':
                path = os.path.join(rootdir, dirs1)
                print(dirs1)
                os.chdir(path)
                fl = glob.glob("%s/lfm*.h5" % (path))
                fl.sort()

                ch1 = 0
                DataDict = {}
                DataDict = {'freqlist': freqlist}
                DataDict['ch1'] = ch1

                # fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
                # fl = glob.glob("%s/lfm*.h5" % (conf.output_dir))
                
                if len(fl) > 1:
                    for jf, f in enumerate(fl):
                        print('jf=%d' %(jf))
                        #print('ch1=%d' %(ch1))
                        plot_ionogram(conf, f, DataDict)
                    
                    #ipdb.set_trace() 
                    if DataDict['ch1'] > 1:
                        save_var(DataDict)
                
