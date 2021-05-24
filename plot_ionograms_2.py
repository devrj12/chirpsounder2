#!/usr/bin/env python

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

import ipdb


output_dir1 = "/home/dev/Downloads/chirp_juha2b/Plots10"


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
    # import ipdb; ipdb.set_trace()
    # Delete old directory if exists
    # if f == 1 and os.path.exists(out_dir):
    #    shutil.rmtree(out_dir)

    #import ipdb;ipdb.set_trace()

    # Create new output directory
    if not os.path.exists(out_dir1):
        os.makedirs(out_dir1)

    img_fname  =  "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (conf.output_dir, cd.unix2dirname(t0), cid, t0)
    img_fname1 = "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (output_dir1, cd.unix2dirname(t0), cid, t0)
    img_fname3 = "/%s/lfm_ionogram-%03d-%1.2f.png" % (cd.unix2dirname(t0), cid, t0)   
    img_fname2 = "%s/%s/lfm_ionogram-%03d-%04d-%02d-%02d-%02d-%02d-%02d.png" % (
        output_dir1, datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d')+str('-loc'), cid, int(t00[0:4]), int(t00[5:7]), int(t00[8:10]), int(t00[11:13]), int(t00[14:16]), int(t00[17:19]))

    # if os.path.exists(img_fname):
    # print("Ionogram plot %s already exists. Skipping"%(img_fname))
    #    ho.close()
    #    return

    print("Plotting %s rate %1.2f (kHz/s) t0 %1.5f (unix)" %
          (f, float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")]))))
    S = n.copy(ho[("S")])          # ionogram frequency-range
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
    range_gates = dr+2*ranges/1e3
    r0 = range_gates[max_range_idx]

    SSin = k_largest_index_argsort(S, k=10)
    SSrn = n.sort(range_gates[SSin[:, 1]])
    ipdb.set_trace()

    #if (Rate == 100) and (dr < 1000) and max(range_gates) > 1000 and min(range_gates) < 500:
    if (Rate == 100) and (dr < 1000) and SSrn[0] < 1000 and SSrn[0] > 500:
        
        output_dir11 = output_dir1 + '/' + cd.unix2dirname(t0)
        
        if not os.path.exists(output_dir11):
        	os.makedirs(output_dir11)
        try:    
        	shutil.copy(f,output_dir11)
        except shutil.SameFileError:
   	     pass
        #import ipdb; ipdb.set_trace()
        # print('inside')
        plt.figure(figsize=(1.5*8, 1.5*6))
        plt.pcolormesh(freqs/1e6, range_gates, dB,vmin=-3, vmax=30.0, cmap="inferno")
        cb = plt.colorbar()
        cb.set_label("SNR (dB)")
        # plt.title("Chirp-rate %1.2f kHz/s t0=%1.5f (unix s)\n%s (UTC)" %
        #          (float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")])), cd.unix2datestr(float(n.copy(ho[("t0")])))))
        plt.title("Chirp-rate %1.2f kHz/s t0=%1.5f (unix s)\n%s (LT)\n%s (UTC)" %
                  (float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")])), datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d %H:%M:%S'), cd.unix2datestr(float(n.copy(ho[("t0")])))))
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("One-way range offset (km)")
        # plt.ylim([dr-conf.max_range_extent/1e3,dr+conf.max_range_extent/1e3])
        plt.ylim([0, 4000])
        plt.xlim([0, 15])
        # plt.ylim([dr-1000.0,dr+1000.0])
        # import ipdb; ipdb.set_trace()
        # plt.xlim([0, conf.maximum_analysis_frequency/1e6])
        plt.tight_layout()
        # plt.savefig(img_fname)
        #plt.show()
        #import ipdb
        #ipdb.set_trace()
        #plt.savefig(img_fname1)
        ipdb.set_trace()
        #plt.savefig(output_dir1 + img_fname3)

        # plt.savefig(img_fname2)
        ipdb.set_trace()
        plt.close()
        plt.clf()
        ho.close()


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
    else:
        #fl=glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
        fl = glob.glob("%s/lfm*.h5" % (conf.output_dir))
        # import ipdb; ipdb.set_trace()
        fl.sort()
        for f in fl:
            plot_ionogram(conf, f)
