#!/usr/bin/env python
# Modify plot_ionograms.py to manually get 'onlick events' for the F-region traces in the ionograms

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
import datetime
import pandas as pd
import pickle

Coord = []


def plot_ionogram(conf, f, normalize_by_frequency=True):
    #import ipdb;ipdb.set_trace()
    #ho = h5py.File(f, "r")
    try:
        ho = h5py.File(f, "r")
        t0 = float(n.copy(ho[("t0")]))
        if not "id" in ho.keys():
            return
        cid = int(n.copy(ho[("id")]))  # ionosonde id

        img_fname = "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (
            conf.output_dir, cd.unix2dirname(t0), cid, t0)
        # if os.path.exists(img_fname):
        # print("Ionogram plot %s already exists. Skipping"%(img_fname))
        # ho.close()
        # return

        print("Plotting %s rate %1.2f (kHz/s) t0 %1.5f (unix)" % (f, float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")]))))
        S = n.copy(ho[("S")])          # ionogram frequency-range
        freqs = n.copy(ho[("freqs")])  # frequency bins
        ranges = n.copy(ho[("ranges")])  # range gates
        Rate = n.copy(ho['rate'])/1e3

        if normalize_by_frequency:
            for i in range(S.shape[0]):
                noise = n.median(S[i, :])
                S[i, :] = (S[i, :]-noise)/noise
                S[S <= 0.0] = 1e-3

        max_range_idx = n.argmax(n.max(S, axis=0))

        dB = n.transpose(10.0*n.log10(S))
        if normalize_by_frequency == False:
            dB = dB-n.nanmedian(dB)

    # assume that t0 is at the start of a standard unix second
    # therefore, the propagation time is anything added to a full second

        dt = (t0-n.floor(t0))
        dr = dt*c.c/1e3
        range_gates = dr+2*ranges/1e3
        r0 = range_gates[max_range_idx]

        if (Rate == 100) and (dr < 1000) and max(range_gates) > 1000 and min(range_gates) < 500:
            fig = plt.figure(figsize=(1.5*8, 1.5*6))
            #plt.figure(figsize=(1.5*8, 1.5*6))
            plt.pcolormesh(freqs/1e6, range_gates, dB,
                           vmin=-3, vmax=30.0, cmap="inferno")
            cb = plt.colorbar()
            cb.set_label("SNR (dB)")
            plt.title("Chirp-rate %1.2f kHz/s t0=%1.5f (unix s)\n%s (UTC)" %
                      (float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")])), cd.unix2datestr(float(n.copy(ho[("t0")])))))
            plt.xlabel("Frequency (MHz)")
            plt.ylabel("One-way range offset (km)")
            #plt.ylim([dr-conf.max_range_extent/1e3, dr+conf.max_range_extent/1e3])
            plt.ylim([0, 4000])
            plt.xlim([0, 15])
            # plt.ylim([dr-1000.0,dr+1000.0])

            #plt.xlim([0, conf.maximum_analysis_frequency/1e6])
            plt.tight_layout()
            # plt.show()
            import ipdb
            ipdb.set_trace()
            ctime = datetime.datetime.fromtimestamp(t0)
            ctime_str = ctime.strftime('%Y-%m-%d-%H-%M-%S-%dUT')
            print(ctime)
            # ctime is in Local-Time (I think !)

            def onclick(event):
                print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % (
                    'double' if event.dblclick else 'single', event.button, event.x, event.y, event.xdata, event.ydata))
                Coord.append([t0, event.xdata, event.ydata, ctime, ctime_str])

            # single click: button=1, x=507, y=202, xdata=7.247788, ydata=728.640032

            fig = plt.gcf()
            cid = fig.canvas.mpl_connect('button_press_event', onclick)
            plt.show()

            fig.canvas.mpl_disconnect(cid)

            with open('/home/dev/Downloads/chirp_juha/N_Coord.data', 'wb') as f:
                pickle.dump(Coord, f)

            # plt.savefig(img_fname)
            # save foF, hF, (foE , hE ??) t0 , ctime , ctime_str
            plt.close()
            plt.clf()
            ho.close()

    except OSError as error : 
        print('Undefined')


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
        #fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
        # for a single folder
        fl = glob.glob("%s*/lfm*.h5" % (conf.output_dir))
        fl.sort()
        for f in fl:
            plot_ionogram(conf, f)
