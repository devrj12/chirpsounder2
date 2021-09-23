#!/usr/bin/env python

##
import numpy as np
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


import cartopy.crs as ccrs
import h5py
import ipdb


output_dir1 = "/home/dev/Downloads/chirp_juha2b/Plots4"


res_1  = []
res_2  = []
Time_3 = []
t0_1   = []

def k_largest_index_argsort(S, k):
    idx = np.argsort(S.ravel())[:-k-1:-1]
    return np.column_stack(np.unravel_index(idx, S.shape))


def plot_ionogram(conf, f, normalize_by_frequency=True):
    ho = h5py.File(f, "r")
    t0 = float(np.copy(ho[("t0")]))
    if not "id" in ho.keys():
        return
    cid = int(np.copy(ho[("id")]))  # ionosonde id

    out_dir1 = os.path.join(output_dir1, cd.unix2dirname(t0))
   
    t00 = datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d.%H:%M:%S')
   
    # Delete old directory if exists
    # if f == 1 and os.path.exists(out_dir):
    #    shutil.rmtree(out_dir)

   

    # Create new output directory
    if not os.path.exists(out_dir1):
        os.makedirs(out_dir1)

    img_fname = "%s/%s/lfm_ionogram-%03d-%1.2f.png" % (
        conf.output_dir, cd.unix2dirname(t0), cid, t0)
    img_fname1 = "%s/%s/tec_iono-%03d-%1.2f.png" % (
        output_dir1, cd.unix2dirname(t0), cid, t0)
    

    # if os.path.exists(img_fname):
    # print("Ionogram plot %s already exists. Skipping"%(img_fname))
    #    ho.close()
    #    return

    print("Plotting %s rate %1.2f (kHz/s) t0 %1.5f (unix)" %
          (f, float(np.copy(ho[("rate")]))/1e3, float(np.copy(ho[("t0")]))))
    S = np.copy(ho[("S")])          # ionogram frequency-range
    freqs = np.copy(ho[("freqs")])  # frequency bins
    ranges = np.copy(ho[("ranges")])  # range gates
    Rate = np.copy(ho[("rate")])/1000  # Rate

    if normalize_by_frequency:
        for i in range(S.shape[0]):
            noise = np.median(S[i, :])
            S[i, :] = (S[i, :]-noise)/noise
        S[S <= 0.0] = 1e-3

    # Three tips - chirp-rate / range / use list to append
    max_range_idx = np.argmax(np.max(S, axis=0))
    # axis 0 is the direction along the rows

    dB = np.transpose(10.0*np.log10(S))
    if normalize_by_frequency == False:
        dB = dB-np.nanmedian(dB)

    # assume that t0 is at the start of a standard unix second
    # therefore, the propagation time is anything added to a full second
    # if Rate == 100:
    dt = (t0-np.floor(t0))
    dr = dt*c.c/1e3
    range_gates = dr+2*ranges/1e3
    r0 = range_gates[max_range_idx]

    SSin = k_largest_index_argsort(S, k=10)
    SSrn = np.sort(range_gates[SSin[:, 1]])

    if (Rate == 100) and (dr < 1000) and max(range_gates) > 1000 and min(range_gates) < 500:


        # Check which tec time and t0 match

        f = h5py.File('/home/dev/Downloads/chirp_juha2b/Plots1/2021-01-07/TEC-01-07/Data&Scripts/gps210107g.001.hdf5', 'r')
        #f = h5py.File('/home/dev/Downloads/chirp_juha2b/Plots1/2021-01-08/Data/gps210108g.001.hdf5', 'r')
      
       
        dset = f['Data']

        d1   = dset['Array Layout']['2D Parameters']['tec']
        lat  = dset['Array Layout']['gdlat']
        lon  = dset['Array Layout']['glon']
        Time = dset['Array Layout']['timestamps']

        Time_1 = []
        for j in range(len(Time)):
            Time_1.append(Time[j])

        Time_2 = []
        for i in range(len(Time_1)):
            Time_2.append(abs(Time_1[i] - t0))

        temp = t0
        res  = [i for i, j in enumerate(Time_2) if j == min(Time_2)]
        res_1.append(res)
        res_2.append(len(res))
        t0_1.append(t0)
        Time_3.append(Time_1[res[0]])

        d1 = dset['Array Layout']['2D Parameters']['tec']
        d2 = d1[:, :, res[0]]
        d3 = np.log10(d2)

        fig = plt.figure(figsize=(20, 5))
        #fig = plt.figure()
        #fig, (ax0, ax1) = plt.subplots(1,2)
        ax0 = fig.add_subplot(121, projection=ccrs.PlateCarree())
        #ax0 = fig.add_subplot(121)
         
        # ax.pcolormesh
        # ax.contourf
        # ax.pcolorfast

        ax0.coastlines()
        ax0.gridlines(draw_labels=True)

        # ax0.pcolorfast(lon,lat,d3)

        # plt.draw()
        cmap = plt.get_cmap('jet')
        im = ax0.pcolormesh(lon, lat, d3, cmap=cmap, vmin=0, vmax=1.4)
        clb = fig.colorbar(im, ax=ax0, pad=0.10)
        #clb.set_label("log10(TEC)", loc='top')
        clb.ax.set_title("log10(TEC)")
        # plt.draw()
        # Scranton
        plt.plot(-75.799346,41.373717,'*r',markersize=12)  
        plt.text(-75.799346,41.373717, "Scranton",fontsize=12)

        # Virginia
        plt.plot(-76.287491,36.768208,'*r',markersize=12)
        plt.text(-76.287491,36.768208, "Virginia",fontsize=12)
        
        ax0.set_xlim(-140, -50)
        ax0.set_ylim(15, 75)
        ax0.text(0.5,-0.15,'Longitude',ha ='center',transform  = ax0.transAxes) 
        #ax0.text(0.5,-0.1,’Longitude’,ha=‘center’,transform=ax.transAxes,fontdict={‘weight’:’bold’,’size’:28}) 
        ax0.text(-0.15,0.5,'Latitude', ha ='center', transform = ax0.transAxes,rotation = 90) 
        #ax0.set_xlabel("Longitude")
        #ax0.set_ylabel("Latitude")
        plt.title("Geodetic median vertical TEC at  %s " % (datetime.datetime.utcfromtimestamp(Time_1[res[0]]).strftime('%Y-%m-%d %H:%M:%S UT')))
        
         
        #41.373717 -- lat , -75.799346 -- lon  -- Scranton
        
        #36.768208 -- lat , -76.287491 -- lon  -- VA 

        #
        ax1 = fig.add_subplot(122)
        #ax1 = plt.figure(figsize=(1.5*8, 1.5*6))
        plt.pcolormesh(freqs/1e6, range_gates, dB, vmin=-3, vmax=30.0, cmap="inferno")
        cb = plt.colorbar()
        #cb.set_title("SNR(dB)")
        cb.set_label("SNR (dB)", labelpad=-20, y=1.08, rotation=0)
        # plt.title("Chirp-rate %1.2f kHz/s t0=%1.5f (unix s)\n%s (UTC)" %
        #          (float(n.copy(ho[("rate")]))/1e3, float(n.copy(ho[("t0")])), cd.unix2datestr(float(n.copy(ho[("t0")])))))
        plt.title("Chirp-rate %1.2f kHz/s t0=%1.5f (unix s)\n%s (LT)\n%s (UT)" %
                  (float(np.copy(ho[("rate")]))/1e3, float(np.copy(ho[("t0")])), datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d %H:%M:%S'), cd.unix2datestr(float(np.copy(ho[("t0")])))))
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("One-way range offset (km)")
        # plt.ylim([dr-conf.max_range_extent/1e3,dr+conf.max_range_extent/1e3])
        plt.ylim([0, 4000])
        plt.xlim([0, 15])
        # plt.ylim([dr-1000.0,dr+1000.0])
       
        # plt.xlim([0, conf.maximum_analysis_frequency/1e6])
        plt.tight_layout()

        #plt.show()
 
        plt.savefig(img_fname1,bbox_inches ='tight')
        #ipdb.set_trace()
        # plt.savefig(img_fname2)
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
       
        fl.sort()
        for f in fl:
            plot_ionogram(conf, f)
