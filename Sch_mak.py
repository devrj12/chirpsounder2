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
import pickle
import ipdb
import datetime

Time_1     = []
fname1     = 'Sch_conf_'
Time_unix  = []
Time_chirp = []


def schedule_watch(conf, f, normalize_by_frequency=True):
    ho = h5py.File(f, "r")
    t0 = float(n.copy(ho[("t0")]))
    if not "id" in ho.keys():
        return
    cid = int(n.copy(ho[("id")]))    # ionosonde id

    S = n.copy(ho[("S")])       # ionogram frequency-range
    freqs = n.copy(ho[("freqs")])   # frequency bins
    ranges = n.copy(ho[("ranges")])  # range gates
    Rate = n.copy(ho['rate'])/1e3

    #import ipdb; ipdb.set_trace()
    max_range_idx = n.argmax(n.max(S, axis=0))

    # assume that t0 is at the start of a standard unix second
    # therefore, the propagation time is anything added to a full second

    dt = (t0-n.floor(t0))
    dr = dt*c.c/1e3
    range_gates = dr+2*ranges/1e3  # (Why ?)
    r0 = range_gates[max_range_idx]

    if (Rate == 100) and (dr < 1000) and max(range_gates) > 1000 and min(range_gates) < 500:
        Time_1.append(t0)
        x1 = [x % 720 for x in Time_1]
        x3 = [round(y, 2) for y in x1]
        if len(x1) == 1:
            print('First')
            Time_new  = x3[0]
            ctime     = datetime.datetime.utcfromtimestamp(Time_1[-1])
            ctime_str = ctime.strftime('%Y-%m-%d-%H-%M-%S-%dUT')
            fname     = fname1 + ctime_str + '.ini'
            Time_chirp.append(Time_new)
            Time_unix.append(t0)
            Time_unix_str = " ".join(str(x) for x in Time_unix)
            Time_chirp_str = " ".join(str(x) for x in Time_chirp)
            sounders = {'rep': 720, 'chirpt': Time_new, 'name': 'vaq', 'rate': 100e3,
                        'dur': 200, 'cf': 10.0e6, 'rmin': 0, 'rmax': 5000.0, 'fmin': 0.0, 'fmax': 20.0}
            sounders_str = '[['+str(sounders)+']]'
            with open(fname, 'w') as fl:
                fl.write(sounders_str)
                fl.write("\n")
                fl.write(Time_chirp_str)
                fl.write("\n")
                fl.write(Time_unix_str)
        elif len(x1) > 1 and abs(x3[-1] - x3[-2]) > 1:
            print('Then')
            Time_new = x3[-1]
            ctime     = datetime.datetime.utcfromtimestamp(Time_1[-1])
            ctime_str = ctime.strftime('%Y-%m-%d-%H-%M-%S-%dUT')
            fname     = fname1 + ctime_str + '.ini'
            Time_chirp.append(Time_new)
            Time_unix.append(t0)
            Time_unix_str = " ".join(str(x) for x in Time_unix)
            Time_chirp_str = " ".join(str(x) for x in Time_chirp)
            sounders = {'rep': 720, 'chirpt': Time_new, 'name': 'vaq', 'rate': 100e3,
                        'dur': 200, 'cf': 10.0e6, 'rmin': 0, 'rmax': 5000.0, 'fmin': 0.0, 'fmax': 20.0}
            sounders_str = '[['+str(sounders)+']]'
            with open(fname, 'w') as fl:
                fl.write(sounders_str)
                fl.write("\n")
                fl.write(Time_chirp_str)
                fl.write("\n")
                fl.write(Time_unix_str)


            ipdb.set_trace()

#Time_chirp_str = " ".join(str(x) for x in Time_chirp)
#def write_newline(fname):
#    with open(fname, "a+") as fl:
#        fl.seek(0)
#        ipdb.set_trace()
    # If file is not empty then append '\n'
#        data = fl.read(100)
#        if len(data) > 0:
#            fl.write("\n")
#        fl.write(Time_chirp_str)


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
                schedule_watch(conf, f)
            time.sleep(10)
    else:
        fl = glob.glob("%s/*/lfm*.h5" % (conf.output_dir))
        fl.sort()
        for f in fl:
            schedule_watch(conf, f)
            #write_newline(fname)
