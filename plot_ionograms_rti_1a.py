#!/usr/bin/env python

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


rootdir = '/home/dev/Downloads/chirp_juha2b'
# for subdir, dirs, files in os.walk(rootdir):
dirs = sorted(os.listdir(rootdir))

output_dir1 = "/home/dev/Downloads/chirp_juha2b/Plots20"


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

    print("Reading %s rate %1.2f (kHz/s) t0 %1.5f (unix)" % (f, float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")]))))
    S = n.copy(ho[("S")])          # ionogram frequency-range
    freqs = n.copy(ho[("freqs")])  # frequency bins
    ranges = n.copy(ho[("ranges")])  # range gates
    Rate = n.copy(ho[("rate")])/1000  # Rate
    
    DataDict["freqs"] = freqs

    if normalize_by_frequency:
        for i in range(S.shape[0]):
            noise = n.median(S[i, :])
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
    
    unarg1 = unravel_index(dB.argmax(),dB.shape)
    
    #ipdb.set_trace()

    # Assume that t0 is at the start of a standard unix second therefore, the propagation time is anything added to a full second
    # if Rate == 100:
    dt = (t0-n.floor(t0))
    dr = dt*c.c/1e3    
    range_gates = dr+2*ranges/1e3
    r0 = range_gates[max_range_idx]
    SSin = k_largest_index_argsort(S, k=10)
    SSrn = n.sort(range_gates[SSin[:, 1]])
    
    DataDict["range_gates"] = range_gates
    
    #dBlist = [60, 80, 100, 120]
    #for i,j in enumerate(dBlist):

    dBB1 = dB[:,60]
    dBB2 = dB[:,80]
    dBB3 = dB[:,100]
    dBB4 = dB[:,120]
        
    dB1a = dB[:,unarg1[1]]
    dB2 = dB1a[dB1a>0]
    pos = n.argwhere(dB1a > 0)
    rg_2 = range_gates[pos]
    ast = n.std(dB2)
    am = n.max(dB2)
    apos = n.argwhere(dB2 > (am -3*ast))
    rg_3 = rg_2[apos]

    arr = []
    for j in rg_3:
            arr.append(j[0][0])
            
    arr1 = n.array(arr)            
    pos1 = n.argwhere(arr1 < 1000)
    
    #dict = {'geek': 1, 'supergeek': True, 4: 'geeky'}
   
    ch1 = DataDict['ch1']
    if ((Rate == 100) and (r0 < 1000)) |((Rate == 100) and (r0 > 1000) and (len(pos1) > 0)) :
        print('yes')
        #global range_gates2
        range_gates2 = range_gates
        DataDict['range_gates2'] = range_gates
        T0all.append(t0)

        #global dB3a, dB3b, dB3c, dB3d, T03, T01, range_gates3
      
        ch1 += 1
        if ch1 == 1:
        
            dB3a = dBB1
            dB3b = dBB2
            dB3c = dBB3
            dB3d = dBB4
            T01 = n.array([t0])
            T03 = T01
            range_gates3 = range_gates
            
        else:
            
            ipdb.set_trace()
            dB3a = n.column_stack((DataDict['DBall']['DB1'], dBB1))            
            dB3b = n.column_stack((DataDict['DBall']['DB2'], dBB2))
            dB3c = n.column_stack((DataDict['DBall']['DB3'], dBB3))
            dB3d = n.column_stack((DataDict['DBall']['DB4'], dBB4))
            T03 = n.hstack((DataDict['Time'], n.array([t0])))
            range_gates3 = n.column_stack((DataDict['range_gates3'],range_gates))
            # T03 = T03.flatten()
    
    DB3 = {'DB1': dB3a, 'DB2': dB3b, 'DB3': dB3c, 'DB4': dB3d}
    print(ch1)
    DataDict['DBall'] = DB3 
    DataDict['Time'] = T03
    DataDict['range_gates3'] = range_gates3
    DataDict['ch1']  = ch1
    #ipdb.set_trace()


def save_var(DataDict):
    #global ch1, dB3, dB3a, dB3b, dB3c, T03, T01, range_gates, range_gates2, range_gates3, freqs

    #path1 = rootdir + '/' + dirs1 + '/' + dirs1[5:10] + 'c.data'
    path1 = output_dir1 + '/' + dirs1 + '/' + dirs1[5:10] + 'e.data'
    #path1 = output_dir1 + '/' + cd.unix2dirname(T03[0])[5:10] + '.data'

    print(path1)
    ipdb.set_trace()
    with open(path1, 'wb') as f:
        #pickle.dump([T03, dB3a, dB3b, dB3c, dB3d, range_gates, range_gates2, range_gates3, freqs], f)
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
                plot_ionogram(conf, f)
            time.sleep(10)
            save_var()
    else:
        for j in range(0, len(dirs)):
            dirs1 = dirs[j]
            if dirs1[0:4] == '2021':
                path = os.path.join(rootdir, dirs1)
                print(dirs1)
                os.chdir(path)
                fl = glob.glob("%s/lfm*.h5" % (path))
                fl.sort()

                ch1 = 0
                print('here : why ?')
                ipdb.set_trace()
                dB3a = n.array([])
                dB3b = n.array([])
                dB3c = n.array([])
                dB3d = n.array([])
                T03 = n.array([])
                T01 = n.array([])
                T0all = []
                range_gates = n.array([])
                range_gates3 = n.array([])
                freqs = n.array([])
                DataDict = {'freqlist' : [60, 80, 100, 120] }
                DataDict['ch1'] = ch1

                #if len(DataDict.keys()) > 2:
                #	del DataDict['freqs']
                #	del DataDict['range_gates']
                #	del DataDict['range_gates2']
                #	del DataDict['DBall']
                #	del DataDict['Time']
                #	del DataDict['range_gates']


                # fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
                # fl = glob.glob("%s/lfm*.h5" % (conf.output_dir))

            if len(fl) > 1:
                for jf, f in enumerate(fl):
                    print('jf=%d' %(jf))
                    print('ch1=%d' %(ch1))
                    plot_ionogram(conf, f, DataDict)
                    
                ipdb.set_trace() 
                save_var(DataDict)
                
