#!/usr/bin/env python3

# Load files from each of the folders using pickle and use those to make RTI plots.

import numpy as n
import matplotlib.pyplot as plt
import glob
import h5py
import scipy.constants as c
import chirp_config as cc
import chirp_det as cd
import sys
import os
import time
import shutil
import datetime
from datetime import timezone
from numpy import unravel_index
import pickle
import matplotlib as mpl


import cartopy.crs as ccrs
import ipdb


rootdir = '/home/dev/Downloads/chirp_juha2b'
# for subdir, dirs, files in os.walk(rootdir):
dirs = sorted(os.listdir(rootdir))

output_dir1 = "/home/dev/Downloads/chirp_juha2b/Plots20"


def k_largest_index_argsort(S, k):
    idx = n.argsort(S.ravel())[:-k-1:-1]
    return n.column_stack(n.unravel_index(idx, S.shape))


def save_var(img_fname="img_1b.png"):
    print('check')

    global dB3, T03, range_gates, freqs, range_gates2, range_gates3
    # with open('/home/dev/Downloads/chirp_juha2b/Time_2.data', 'wb') as f:
    #    pickle.dump([T03, dB3, range_gates],f)

    #path1 = rootdir + '/' + dirs1 + '/' + dirs1[5:10] + 'c.data'
    path1 = output_dir1 + '/' + dirs1 + '/' + dirs1[5:10] + 'c.data'

    with open(path1, 'rb') as f:
        T03, dB3, range_gates, range_gates2, range_gates3, freqs = pickle.load(f)

    T03a = n.arange(T03[0], T03[-1] + 10, 720)
    T03b = T03a

    # Check if there is change in schedule -- get the modulus, round it and take the differences of all values -- if any change, one or more of the differences will not be zero
    x1 = [x % 720 for x in T03]
    x3 = [round(y, 2) for y in x1]
    x4 = n.diff([x3])[0]

    if len(n.where(abs(x4) > 1)[0]) > 0:
        x5 = n.where(abs(x4) > 1)[0][0]+1

    # if it spans the complete time-range (len(T03a) == 120) and if there is schedule change, apply the corrections 
    if (len(T03a) == 120) & (len(n.where(abs(x4) > 1)[0]) > 0):
        x1a = [x % 720 for x in T03a]
        x3a = [round(ya, 2) for ya in x1a]
        x4a = n.diff([x3a])[0]
        x5a = n.where(abs(x4a) > 1)[0][0] + 1
        T03a1 = T03a[0:(x5a)]
        T03a2 = n.arange(T03a[x5a] + x4a[x5a-1], T03a[-1] + 720, 720)
        T03a = n.concatenate((T03a1, T03a2))

    # x5 = [datetime.datetime.utcfromtimestamp(z) for z in T03]

    # We shall also check if the start time has gone a schedule change -- which it will at one point or another. That
    # is why at the moment it doesn't work now as expected. So, the following steps should be preceded by a check on
    # schedule change and incorporating that change in the following steps. That is it for today. # Apr 23, 2021
    # This is what has happened for the date 2021/01/06 -- as the chirp start time has 'shrinked' while changing -- that is
    # why when the new definition of T03a (line 75) is applied -- it goes beyond the last element of T03[b] as the last element
    # of T03[b] is less than (shrinked) its otherwise regular value (if there were no schedule change) ! So, the remedy is find when
    # the schedule change occurs and use those brackets while defining new T03a !

    # Make sure T03a covers the full 720*120 = 86400 secs for a UTC day. If it is less than that, build it !
    if len(T03a) < 120:
        dtest = int(datetime.datetime.utcfromtimestamp(T03[0]).strftime("%d"))
        jj = 0
        while True:
            #subtract 720 until it gets to beginning of the day and in next while loop, add 720 until it gets to the end of the day	
            if (int(datetime.datetime.utcfromtimestamp(T03[0] - 720*jj).strftime("%d")) - dtest) < 0:
                T03b = n.insert(T03b, 0, T03[0] - 720*(jj-1))
                print('jj= %1.2f' % (jj))
                break
            jj += 1

        jj1 = 0
        while True:
            if (int(datetime.datetime.utcfromtimestamp(T03[-1] + 720*jj1).strftime("%d")) - dtest) > 0:
                T03b = n.append(T03b, T03[-1] + 720*(jj1-1))
                print('jj1 = %1.2f' % (jj1))
                break
            jj1 += 1

        dt = datetime.datetime.utcfromtimestamp(T03b[-1])
        dt2 = dt.replace(minute=59, second=59)
        ## replacing the limit of the time-zone
        T03bb = dt2.replace(tzinfo=timezone.utc).timestamp()
        #T03a = n.arange(T03b[0], T03b[-1]+720, 720) ## commenting as it sometimes takes the data-points to next day
        T03a = n.arange(T03b[0], T03bb, 720)
            
        # It is assuming there will be only one schedule change in a day. I think it will be good to confirm that's what is being implemented (assumed)
        # and if it is the case, flag an error in case there is more than one schedule change if ever encountered.
        if len(n.where(abs(x4) > 1)[0]) > 0:
            jj2 = (jj - 1) + x5 - 1
            T03a1 = T03a[0:jj2]
            #T03a2 = n.arange(T03a[jj2] + x4[x5-1], T03b[-1] + 720, 720)
            T03a2 = n.arange(T03a[jj2] + x4[x5-1], T03bb, 720)
            # T03a = n.array([])
            T03a = n.concatenate((T03a1, T03a2))

    dB3test = n.full([3999, 120], None)
    dB3test[:] = n.NaN
    dB3new = n.full([3999, 120], None)
    
    range_gatestest = n.full([3999, 120], None)
    range_gatestest[:] = n.NaN
    range_gatesnew = n.full([3999,120],None)

    print(len(T03a))
    #ipdb.set_trace()
    
    ## STEPS : 
    
    #1. Built a regular time-series  - A (T03a)
    #2. Get the available time-series  - B (T03) . Note len(A) > len(B)
    #3. For every element in A, check if the closest corresponding element in B exists.
    #4. If it exists, keep the corresponding 'stripe' of dB3.
    #5. If it doesn't exist, insert a NaN stripe in new dB3.

    for i, x in enumerate(T03a):
        print(i)
        DIFF = abs(T03 - x)
        MIN = min(abs(T03-x))
        if MIN < 2:
            ij = n.where(DIFF == n.amin(DIFF))[0][0]
            dB3new[:, i] = dB3[:, ij]
            range_gatesnew[:,i] = range_gates3[:,ij]
            # it (ij) comes out as a tuple which contains an array. So, the first index [0] gets
            # the array out of the tuple. And the second index [0] gets the index out of the array.
        else:
            dB3new[:, i] = dB3test[:, i]
            range_gatesnew[:,i] = range_gatestest[:,i]

    # ipdb.set_trace()
    fig = plt.figure(figsize=(1.5*10, 1.5*3))

    ax0 = fig.add_subplot(121, projection=ccrs.PlateCarree())
    ax0.coastlines()
    ax0.gridlines(draw_labels=True)
    plt.plot(-75.799346, 41.373717, '*r', markersize=12)
    plt.text(-75.799346, 41.373717, "Scranton", fontsize=12)
    plt.plot(-76.287491, 36.768208, '*r', markersize=12)
    plt.text(-76.287491, 36.768208, "Virginia", fontsize=12)
    ax0.set_xlim(-140, -50)
    ax0.set_ylim(15, 75)
    ax0.text(0.5, -0.15, 'Longitude', ha='center', transform=ax0.transAxes)
    ax0.text(-0.15, 0.5, 'Latitude', ha='center', transform=ax0.transAxes, rotation=90)
    plt.title("Site Locations ")

    new_times = [datetime.datetime.utcfromtimestamp(x) for x in T03a]
    new_times = n.array(new_times)
    new_times1 = [datetime.datetime.fromtimestamp(x) for x in T03a]  # local-time
    new_times1 = n.array(new_times1)

    ax1 = fig.add_subplot(122)

    dB3new = dB3new.astype(n.float)
    
    mpl1 = mpl.dates.date2num(new_times)

    
    ipdb.set_trace()
    for ja in range(0,120):
                #print(ja)
                #plt.pcolormesh(new_times[ja:ja+2],np.column_stack((range_gatesnew[:,ja],range_gatesnew[:,ja])),dB3new[0:3998,ja:ja+1],vmin=-3,vmax=30.0,cmap="inferno")
                plt.pcolormesh(new_times[ja:ja+1], range_gatesnew[:,ja], dB3new[:,ja:ja+1],vmin=-3, vmax=30.0, cmap="inferno")


    #plt.pcolormesh(new_times, range_gates2, dB3new,vmin=-3, vmax=30.0, cmap="inferno")
    # plt.contourf(new_times, range_gates, dB3new, vmin=-3, vmax=30.0, cmap="inferno",levels=30)
    cb = plt.colorbar()
    cb.set_label("SNR (dB)")
    plt.title("RTI plot for  %1.2f MHz \n%s (UTC)" % (freqs[80]/1e6,  datetime.datetime.utcfromtimestamp(T03[1]).strftime('%Y-%m-%d')))
    plt.xlabel("Time (UTC)")
    plt.ylabel("One-way range offset (km)")
    # plt.ylim([dr-conf.max_range_extent/1e3,dr+conf.max_range_extent/1e3])
    plt.ylim([0, 4000])
    # plt.xlim([0, 15])

    # plt.savefig(img_fname)
    ipdb.set_trace()
    plt.tight_layout()
    #plt.savefig(img_fname, bbox_inches='tight')
    plt.show()

  
    # plt.savefig(img_fname1)
    # plt.savefig(img_fname2)
    plt.close()
    plt.clf()
    # ho.close()


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
                dB3 = n.array([])
                T03 = n.array([])
                T01 = n.array([])               
                range_gates = n.array([])
                range_gates2 = n.array([])
                range_gates3 = n.array([])
                freqs = n.array([])
                
                # ipdb.set_trace()
                # fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
                # fl = glob.glob("%s/lfm*.h5" % (conf.output_dir))

            if len(fl) > 1:
                save_var()
