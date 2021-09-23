#!/usr/bin/env python

# Initial version of RTI Plot which had both 'going through' a certain day's data to save essential variables and then making the RTI plot

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
from numpy import unravel_index
import pickle

import cartopy.crs as ccrs
import ipdb


RTI = []
ch1 = 0
dB3 = n.array([])
T03 = n.array([])
T01 = n.array([])
range_gates = n.array([])
range_gates3 = n.array([])
freqs = n.array([])

output_dir1 = "/home/dev/Downloads/chirp_juha2b/PlotsRTI"


def k_largest_index_argsort(S, k):
    idx = n.argsort(S.ravel())[:-k-1:-1]
    return n.column_stack(n.unravel_index(idx, S.shape))


def plot_ionogram(conf, f, normalize_by_frequency=True):
    ho = h5py.File(f, "r")
    t0 = float(n.copy(ho[("t0")]))
    if not "id" in ho.keys():
        return
    cid = int(n.copy(ho[("id")]))  # ionosonde id

    out_dir1 = os.path.join(output_dir1, cd.unix2dirname(t0))
    # out_dir1 = os.path.join(output_dir1, datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d') + str('-loc'))
    t00 = datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d.%H:%M:%S')

    # Delete old directory if exists
    # if f == 1 and os.path.exists(out_dir):
    #    shutil.rmtree(out_dir)


    with open('/home/dev/JUHA/chirpsounder2/RG.data', 'rb') as f1:
    		rg_ch =  pickle.load(f1)

    # Create new output directory
    if not os.path.exists(out_dir1):
        os.makedirs(out_dir1)

    #global img_fname, img_fname1, img_fname2, img_fname1a

    img_fname = "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (conf.output_dir, cd.unix2dirname(t0), cid, t0)
    img_fname1 = "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (output_dir1, cd.unix2dirname(t0), cid, t0)
    img_fname1a = "%s/lfm_ionogram-%03d-%1.2f.png" % (output_dir1, cid, t0)
    img_fname2 = "%s/%s/lfm_ionogram-%03d-%04d-%02d-%02d-%02d-%02d-%02d.png" % (output_dir1, datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d')+str('-loc'), cid, int(t00[0:4]), int(t00[5:7]), 						int(t00[8:10]), int(t00[11:13]), int(t00[14:16]), int(t00[17:19]))

    # if os.path.exists(img_fname):
    # print("Ionogram plot %s already exists. Skipping"%(img_fname))
    #    ho.close()
    #    return

    print("Reading %s rate %1.2f (kHz/s) t0 %1.5f (unix)" % (f, float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")]))))
    S = n.copy(ho[("S")])          # ionogram frequency-range

    global freqs
    freqs = n.copy(ho[("freqs")])  # frequency bins
    ranges = n.copy(ho[("ranges")])  # range gates
    Rate = n.copy(ho[("rate")])/1000  # Rate

    if normalize_by_frequency:
        for i in range(S.shape[0]):
            noise = n.median(S[i, :])
            S[i, :] = (S[i, :]-noise)/noise
        S[S <= 0.0] = 1e-3

    # Three tips - chirp-rate / range / use list to append
    max_range_idx = n.argmax(n.max(S, axis=0))
    # axis 0 is the direction along the rows

    dB = n.transpose(10.0*n.log10(S))
    if normalize_by_frequency == False:
        dB = dB-n.nanmedian(dB)

    # assume that t0 is at the start of a standard unix second
    # therefore, the propagation time is anything added to a full second
    # if Rate == 100:
    dt = (t0-n.floor(t0))
    dr = dt*c.c/1e3
    global range_gates
    range_gates = dr+2*ranges/1e3
    r0 = range_gates[max_range_idx]
    SSin = k_largest_index_argsort(S, k=10)
    SSrn = n.sort(range_gates[SSin[:, 1]])
    dB1 = dB[:, 80]
    RG_ch = range_gates - rg_ch
    if abs(sum(RG_ch[0])) > 0:
    	print('here')

    
    #if (Rate == 100) and (dr < 1000) and max(range_gates) > 1000 and min(range_gates) < 500:
    if (Rate == 100) and (dr < 1000) and SSrn[0] < 1000 and SSrn[0] > 500:

        global range_gates2
        range_gates2 = range_gates
        
        # global ch1, dB3, T03, T01
        output_dir2 = output_dir1 + '/' + cd.unix2dirname(t0) + '-lfm1'
        if not os.path.exists(output_dir2):
        	os.makedirs(output_dir2)
        try:
            shutil.copy(f, output_dir2)
        except shutil.SameFileError:
            pass
        #ipdb.set_trace()
	
        global ch1, dB3, T03, T01, range_gates3
        ch1 += 1

        if ch1 == 1:
            dB3 = dB1
            range_gates3 = range_gates
            T01 = n.array([t0])
            T03 = T01
        else:
            dB3 = n.column_stack((dB3, dB1))
            T03 = n.hstack((T03, n.array([t0])))
            range_gates3 = n.column_stack((range_gates3,range_gates))
            # T03 = T03.flatten()

        print(len(T03))
        ho.close()


# def save_var(img_fname="img_1.png"):
def save_var():
    print('check')

    global ch1, dB3, T03, T01, range_gates2, freqs, range_gates3
    # with open('/home/dev/Downloads/chirp_juha2b/Time_2.data', 'wb') as f:
    #    pickle.dump([T03, dB3, range_gates],f)

    # with open('/home/dev/Downloads/chirp_juha2b/Time_2.data', 'rb') as f:
    #    T03, dB3, range_gates =  pickle.load(f)


    T03a = n.arange(T03[0], T03[-1], 720)
    T03b = T03a

    # Make sure T03a covers the full 720*120 = 86400 secs for a UTC day. If it is less than that, build it !
    if len(T03a) < 120:
        dtest = int(datetime.datetime.utcfromtimestamp(T03[0]).strftime("%d"))
        jj = 0
        while True:
            if (int(datetime.datetime.utcfromtimestamp(T03[0] - 720*jj).strftime("%d")) - dtest) < 0:
                T03b = n.insert(T03b, 0, T03[0] - 720*(jj-1))
                print(jj)
                break
            jj += 1

        jj1 = 0
        while True:
            if (int(datetime.datetime.utcfromtimestamp(T03[-1] + 720*jj1).strftime("%d")) - dtest) > 0:
                T03b = n.append(T03b, T03[-1] + 720*(jj1-1))
                print(jj1)
                break
            jj1 += 1

        T03a = n.arange(T03b[0], T03b[-1]+720, 720)
        if len(T03a) > 120:
            T03a = T03a[0:120]

    dB3test = n.full([3999, 120], None)
    dB3test[:] = n.NaN
    dB3new = n.full([3999, 120], None)

    # Reconstruct dB3
    for i, x in enumerate(T03a):
        DIFF = abs(T03 - x)
        MIN = min(abs(T03-x))
        if MIN < 2:
            ij = n.where(DIFF == n.amin(DIFF))[0][0]
            # ij gives the position where it is minimum in DIFF
            dB3new[:, i] = dB3[:, ij]
            # it (ij) comes out as a tuple which contains an array. So, the first index [0] gets
            # the array out of the tuple. And the second index [0] gets the index out of the array.
        else:
            dB3new[:, i] = dB3test[:, i]

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
    
    plt.pcolormesh(new_times, range_gates2, dB3new,vmin=-3, vmax=30.0, cmap="inferno")
    #plt.contourf(new_times, range_gates, dB3new, vmin=-3, vmax=30.0, cmap="inferno",levels=30)
    cb = plt.colorbar()
    cb.set_label("SNR (dB)")
    plt.title("RTI plot for  %1.2f MHz \n%s (UTC)" % (freqs[80]/1e6,  datetime.datetime.utcfromtimestamp(T03[1]).strftime('%Y-%m-%d')))
    plt.xlabel("Time (UTC)")
    plt.ylabel("One-way range offset (km)")
    # plt.ylim([dr-conf.max_range_extent/1e3,dr+conf.max_range_extent/1e3])
    plt.ylim([0, 4000])
    # plt.xlim([0, 15])

    # plt.savefig(img_fname)

    plt.tight_layout()
    #plt.savefig(img_fname1a,bbox_inches ='tight')
    plt.show()
    ipdb.set_trace()
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
        #fl=glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
        fl = glob.glob("%s/lfm*.h5" % (conf.output_dir))

        fl.sort()
        for f in fl:
            plot_ionogram(conf, f)

        ipdb.set_trace()
        save_var()
