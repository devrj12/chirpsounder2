#!/usr/bin/env python

## Modification of plot_ionograms.py

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

import pprint
import re

Var_1 = []
Time_1 = []


def save_data(conf, f, normalize_by_frequency=True):
    ho = h5py.File(f, "r")
    t0 = ho["t0"].value
    if not "id" in ho.keys():
        return
    cid = ho["id"].value  # ionosonde id

    img_fname = "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (
        conf.output_dir, cd.unix2dirname(t0), cid, t0)
    # if os.path.exists(img_fname):
    #    #print("Ionogram plot %s already exists. Skipping"%(img_fname))
    #    ho.close()
    #    return

    print("Plotting %s rate %1.2f (kHz/s) t0 %1.5f (unix)" %
          (f, ho["rate"].value/1e3, ho["t0"].value))
    S = ho["S"].value          # ionogram frequency-range
    freqs = ho["freqs"].value  # frequency bins
    ranges = ho["ranges"].value  # range gates
    Rate = ho["rate"].value/1e3

   # Add more
    Freq_1 = freqs[100]/1e6
    #Ranges_1 = ranges[:,100];
    S_1 = S[:, 100]
   ##
    if normalize_by_frequency:
        for i in range(S.shape[0]):
            noise = n.median(S[i, :])
            S[i, :] = (S[i, :]-noise)/noise
        S[S <= 0.0] = 1e-3

    # Axis 0 will act on all the ROWS in each COLUMN
    max_range_idx = n.argmax(n.max(S, axis=0))

    dB = n.transpose(10.0*n.log10(S))
    if normalize_by_frequency == False:
        dB = dB-n.nanmedian(dB)

    dB1 = dB[:, 100]  # Freqs[100]/1e6 = 5 MHz
    Freq_2 = freqs[374]/1e6  # Freqs
    dB2 = dB[:, 374]

    # assume that t0 is at the start of a standard unix second
    # therefore, the propagation time is anything added to a full second

    dt = (t0-n.floor(t0))
    #import ipdb; ipdb.set_trace()
    dr = dt*c.c/1e3  # distance traveled in km
    range_gates = dr+2*ranges/1e3   # Why ??
    r0 = range_gates[max_range_idx]
    plt.figure(figsize=(1.5*8, 1.5*6))
    plt.pcolormesh(freqs/1e6, range_gates, dB,
                   vmin=-3, vmax=30.0, cmap="inferno")
    cb = plt.colorbar()
    cb.set_label("SNR (dB)")
    plt.title("Chirp-rate %1.2f kHz/s t0=%1.5f (unix s)\n%s (UTC)" %
              (ho["rate"].value/1e3, ho["t0"].value, cd.unix2datestr(ho["t0"].value)))
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("One-way range offset (km)")
    # plt.ylim([dr-1000.0,dr+1000.0])
    # plt.ylim([0,4000])
    # plt.xlim([0,15])
    plt.tight_layout()
    print(n.max(range_gates))
    print(n.min(range_gates))
    #import ipdb
    # ipdb.set_trace()
    # plt.show()
    plt.savefig(img_fname)
    plt.close()

    # Check by Rate , range and start-time (?)
    if (Rate == 100) and (dr < 1000) and max(range_gates) > 1000 and min(range_gates) < 500:
        idx1 = (n.abs(range_gates - 400)).argmin()
        idx2 = (n.abs(range_gates - 900)).argmin()
        dB3 = dB1[idx1:idx2]
        Range_gates3 = range_gates[idx1:idx2]
        RG = Range_gates3[n.argmax(dB3)]
        Var_1.append(RG)
        Time_1.append(t0)

    plt.clf()
    ho.close()

#pat     = re.compile("^lfm.*h5$")
#dirlist = filter(pat.match,os.listdir("/home/dev/Desktop/H5/2020-11-17/"))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        conf = cc.chirp_config(sys.argv[1])
    else:
        conf = cc.chirp_config()

    fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
    for f in fl:
        save_data(conf, f)  # ??
