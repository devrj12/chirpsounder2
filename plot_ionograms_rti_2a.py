#!/usr/bin/env python3

# Stack frequency plot (subplots)

# Load files from each of the folders using pickle and use those to make RTI plots.
# 3. If Schedule change occurs twice in adjacent points, remove the middle one as it must be spurious (Raise error for more involved schedule changes).

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
#from datetime import datetime
from numpy import unravel_index
import pickle
import matplotlib as mpl
import math


import cartopy.crs as ccrs
import ipdb

freqlist = [60, 80, 100, 120, 160, 180]
#rootdir = '/home/dev/Downloads/chirp_juha2b'
rootdir = '/media/dev/Seagate Backup Plus Drive/lfm_files'
# for subdir, dirs, files in os.walk(rootdir):
dirs = sorted(os.listdir(rootdir))

output_dir1 = "/home/dev/Downloads/chirp_juha2b/Plots20"
output_dir2 = "/home/dev/Downloads/chirp_juha2b/Plots20/AllRTI"


def k_largest_index_argsort(S, k):
    idx = n.argsort(S.ravel())[:-k-1:-1]
    return n.column_stack(n.unravel_index(idx, S.shape))


# def save_var(img_fname="img_1b.png"):
def save_var(DataDict):
    print('check')

    path1 = rootdir + '/' + dirs1 + '/' + dirs1[5:10] + 'b.data'
    path2 = output_dir1 + '/' + dirs1 + '/' + dirs1[5:10] + 'f.data'

    img_fname1 = "%s/%s/RTIf-%s.png" % (output_dir1, dirs1, dirs1[0:10])
    img_fname2 = "%s/RTI-%sf.png" % (output_dir2, dirs1[0:10])

    #img_fname1 = "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (output_dir1, cd.unix2dirname(t0), cid, t0)

    with open(path2, 'rb') as f:
        #T03, dB3, dB3a, dB3b, dB3c, range_gates, range_gates2, range_gates3, freqs = pickle.load(f)
        DataDict = pickle.load(f)

        #T03, dB3, range_gates, freqs = pickle.load(f)
    #ipdb.set_trace()
    # Check if there is change in schedule -- get the modulus, round it and take the differences of all values -- if any change, one or more of the differences will not be zero

    T03 = DataDict['Time']
    x1 = [x % 720 for x in T03]
    x3 = [round(y, 2) for y in x1]
    x4 = n.diff([x3])[0]
    sch_ch = n.where(abs(x4) > 1)[0]
    len_ch = len(sch_ch)
    SS = n.split(sch_ch,n.argwhere(n.diff(sch_ch) > 1)[:,0]+1)
    SS1 = [len(j) for j in SS]
    SS2  = [idx for idx, x in enumerate(SS1) if x  == 2]


    # I am using x33 to get an array of three elements.
    # Actually it is applicable for consecutive schedule changes (for such schedule change - sch_ch will have two consecutive elements and sch_ch[-1] + 2 will
    # help me to get three elements for x33. There should be a check if there are multiple such consecutive schedule changes.

    range_gates3 = DataDict['range_gates3']
    range_gates2 = DataDict['range_gates2']
    freqlist = DataDict['freqlist']
    freqs = DataDict['freqs']

    # check if schedule change occurs more than once in a given day and use that to remove spurious 'ionograms'
    # I am beginning with a simple case : only twice and consecutive which may not be the case as spurious detections can happen anywhere in any order
    if len_ch > 1:
        x33 = x3[sch_ch[0]:sch_ch[-1]+2]
        if len_ch == 2 and x33[0] == x33[-1]:
            T03 = n.delete(T03, sch_ch[0]+1)
            for k in [j for j in DataDict['DBall'].keys()]:
                DataDict['DBall'][k] = n.delete(DataDict['DBall'][k], sch_ch[0]+1, 1)
                range_gates3 = n.delete(range_gates3, sch_ch[0]+1, 1)
            x1 = [x % 720 for x in T03]
            x3 = [round(y, 2) for y in x1]
            x4 = n.diff([x3])[0]
    elif len_ch > 2:
        print("Not handled in this script : Needs editing")
        # This will be the case where schedule will change more than once in a single day !

    ipdb.set_trace()
    T03a = n.arange(T03[0], T03[-1] + 10, 720)
    T03b = T03a

    if len(n.where(abs(x4) > 1)[0]) > 0:
        x5 = n.where(abs(x4) > 1)[0][0]+1

    # if it spans the complete time-range (len(T03a) == 120) and if there is schedule change, apply the corrections
    if (len(T03a) == 120) and (len(n.where(abs(x4) > 1)[0]) > 0):
        x1a = [x % 720 for x in T03a]
        x3a = [round(ya, 2) for ya in x1a]
        x4a = n.diff([x3a])[0]
        # The increase has happened at x5 and hence, I am looking for equivalent element in T03a corresponding to (x5-1) position of T03. That's because
        # upto that position, T03 is changed and I want to keep T03a unchanged upto that equivalent position which will be given by nn1!
        NN = abs(T03a - T03[x5-1])
        nn1 = n.where(NN == NN.min())[0][0]
        # Going upto nn1 requires it write [0:(nn1+1)] as the last element is not taken in Python. So, this portion is unchanged.
        T03a1 = T03a[0:(nn1+1)]
        # Edit the final element of T03ab
        dta = datetime.datetime.utcfromtimestamp(T03[-1])
        dta2 = dta.replace(minute=59, second=59)
        # replacing the limit of the time-zone
        T03ab = dta2.replace(tzinfo=timezone.utc).timestamp()
        # Change starts here : Start it from (nn1 +1)the position as nn1 position is already covered. And, add the "change = x4[x5-1]" at (nn1 + 1)th position
        T03a2 = n.arange(T03a[nn1+1] + x4[x5-1], T03ab, 720)
        T03a = n.concatenate((T03a1, T03a2))

    # Make sure T03a covers the full 720*120 = 86400 secs for a UTC day. If it is less than that, build it !
    if len(T03a) < 120:
        dtest = int(datetime.datetime.utcfromtimestamp(T03[0]).strftime("%d"))
        jj = 0
        while True:
            # subtract 720 until it gets to beginning of the day and in next while loop, add 720 until it gets to the end of the day
            print('jj=%d' %(jj))
            if abs((int(datetime.datetime.utcfromtimestamp(T03[0] - 720*jj).strftime("%d")) - dtest)) > 0:
                T03b = n.insert(T03b, 0, T03[0] - 720*(jj-1))
                print('jj= %1.2f' % (jj))
                break
            jj += 1

        jj1 = 0
        while True:
            print('jj1=%d' %(jj1))
            if abs((int(datetime.datetime.utcfromtimestamp(T03[-1] + 720*jj1).strftime("%d")) - dtest)) > 0:
                T03b = n.append(T03b, T03[-1] + 720*(jj1-1))
                print('jj1 = %1.2f' % (jj1))
                break
            jj1 += 1

        dt = datetime.datetime.utcfromtimestamp(T03b[-1])
        dt2 = dt.replace(minute=59, second=59)
        # replacing the limit of the time-zone
        T03bb = dt2.replace(tzinfo=timezone.utc).timestamp()
        # T03a = n.arange(T03b[0], T03b[-1]+720, 720) ## commenting as it sometimes takes the data-points to next day
        T03a = n.arange(T03b[0], T03bb, 720)

        if len(n.where(abs(x4) > 1)[0]) > 0:
            jj2 = (jj - 1) + x5
            # Because the change happens at x5 in x3 (or T03), I need to cover upto x5-1. To have elements upto x5 - 1, I need to use the index upto x5 as the last index isn't taken in python !
            T03a1 = T03a[0:jj2]
            #T03a2 = n.arange(T03a[jj2] + x4[x5-1], T03b[-1] + 720, 720)
            T03a2 = n.arange(T03a[jj2] + x4[x5-1], T03bb, 720)
            # T03a = n.array([])
            T03a = n.concatenate((T03a1, T03a2))

    dB3test = n.full([3999, 120], None)
    dB3test[:] = n.NaN

    DataDict['DBallnew'] = {}
    for k in [j for j in DataDict['DBall'].keys()]:
        DataDict['DBallnew'][k] = n.full([3999, 120], None)

    range_gatestest = n.full([3999, 120], None)
    range_gatestest[:] = n.NaN
    range_gatesnew = n.full([3999, 120], None)

    for i, x in enumerate(T03a):
        #print(i)
        DIFF = abs(T03 - x)
        MIN = min(abs(T03-x))
        if MIN < 2:
            #print(i)
            ij = n.where(DIFF == n.amin(DIFF))[0][0]
            
            for k in [j for j in DataDict['DBall'].keys()]:
                DataDict['DBallnew'][k][:, i] = DataDict['DBall'][k][:, ij]

            range_gatesnew[:, i] = range_gates3[:, ij]
            # it (ij) comes out as a tuple which contains an array. So, the first index [0] gets
            # the array out of the tuple. And the second index [0] gets the index out of the array.
        else:

            for k in [j for j in DataDict['DBall'].keys()]:
                DataDict['DBallnew'][k][:, i] = dB3test[:, i]

            range_gatesnew[:, i] = range_gates2

    #fig = plt.figure(figsize=(1.5*10, 1.5*3))
    fig = plt.figure(figsize=(1.5*6, 1.5*12))
    #ax0 = fig.add_subplot(511, projection=ccrs.PlateCarree())
    # ax0.coastlines()
    # ax0.gridlines(draw_labels=True)
    #plt.plot(-75.799346, 41.373717, '*r', markersize=12)
    #plt.text(-75.799346, 41.373717, "Scranton", fontsize=12)
    #plt.plot(-76.287491, 36.768208, '*r', markersize=12)
    #plt.text(-76.287491, 36.768208, "Virginia", fontsize=12)
    #ax0.set_xlim(-140, -50)
    #ax0.set_ylim(15, 75)
    #ax0.text(0.5, -0.15, 'Longitude', ha='center', transform=ax0.transAxes)
    #ax0.text(-0.15, 0.5, 'Latitude', ha='center', transform=ax0.transAxes, rotation=90)
    #plt.title("Site Locations ")

    fig.suptitle("RTI plots : %s UTC" % datetime.datetime.utcfromtimestamp(T03[1]).strftime('%Y-%m-%d'),weight='bold')
    new_times = [datetime.datetime.utcfromtimestamp(x) for x in T03a]
    new_times = n.array(new_times)
    new_times1 = [datetime.datetime.fromtimestamp(x) for x in T03a]  # local-time
    new_times1 = n.array(new_times1)


    for j, k in enumerate(reversed([j for j in DataDict['DBall'].keys()])):
        #ax1 = fig.add_subplot(4, 1, k.astype(n.int64)-2)
        ax1 = fig.add_subplot(6, 1, j+1)
        for ja in range(0, 118):
            plt.pcolormesh(new_times[ja:ja+2], n.column_stack((range_gatesnew[:, ja], range_gatesnew[:, ja])),DataDict['DBallnew'][k].astype(n.float)[:-1, ja:ja+1], vmin=-3, vmax=30.0,cmap="inferno")
        
        cb = plt.colorbar()
        cb.set_label("SNR (dB)")
        #plt.title("RTI plot for %1.2f MHz" %(k))
        #plt.title("RTI plot for %1.2f MHz" %(freqs[freqlist[k.astype(n.int64)]]/1e6))
        #plt.xlabel("Time (UTC)")
        #plt.ylabel("One-way range offset (km)")
        plt.ylabel("%1.2f MHz\n Range (km)" %(k), weight='bold')
        plt.ylim([0, 4000])
        plt.xlim(new_times[0], new_times[-1])
        plt.tight_layout(pad=3.0)
        #plt.savefig(img_fname1, bbox_inches='tight')
        #plt.savefig(img_fname2, bbox_inches='tight')

    #cb = plt.colorbar()
    plt.xlabel("Time (UTC)",weight='bold')
    plt.savefig(img_fname1, bbox_inches='tight')
    plt.savefig(img_fname2, bbox_inches='tight')
    ipdb.set_trace()
    plt.show()
    # plt.savefig(img_fname1)
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
            dtt1 = datetime.datetime.strptime('2021-05-31','%Y-%m-%d').date()
            dtt2 = datetime.datetime.strptime(dirs1[0:10],'%Y-%m-%d').date()

            #if dirs1[0:10] == '2021-04-30':
            if dirs1[0:4] == '2021':
            #if dtt2 > dtt1 :
                path = os.path.join(rootdir, dirs1)
                print(dirs1)
                os.chdir(path)
                fl = glob.glob("%s/lfm*.h5" % (path))
                fl.sort()

                DataDict = {}

                # fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
                # fl = glob.glob("%s/lfm*.h5" % (conf.output_dir))
                
                if len(fl) > 1:
                    save_var(DataDict) 
