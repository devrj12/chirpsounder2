#!/usr/bin/env python3

import os, pickle
import numpy as n
import datetime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

#rootdir = '/home/dev/Downloads/chirp_juha2b/2021-01-10'
#dirs = sorted(os.listdir(rootdir))
#path1 = rootdir + '/' + dirs[0]

#output_dir1 = "/home/dev/Downloads/chirp_juha2b/Plots6"

#path1 = '/home/dev/Downloads/chirp_juha2b/Plots6/01-10a.data'

#path1 = '/home/dev/Downloads/chirp_juha2b/Plots7/2021-01-10/01-10.data'

path1 = '/home/dev/Downloads/chirp_juha2b/Plots8/2021-01-10/01-10.data'



with open(path1, 'rb') as f:
        T03, dB3, range_gates, freqs = pickle.load(f)

#global ch1, dB3, T03, T01, range_gates, freqs
    # with open('/home/dev/Downloads/chirp_juha2b/Time_2.data', 'wb') as f:
    #    pickle.dump([T03, dB3, range_gates],f)

    # with open('/home/dev/Downloads/chirp_juha2b/Time_2.data', 'rb') as f:
    #    T03, dB3, range_gates =  pickle.load(f)

    # import ipdb; ipdb.set_trace()
    # ipdb.set_trace()
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
ax0.text(0.5, -0.15, 'Longitude', ha ='center', transform  = ax0.transAxes)
ax0.text(-0.15, 0.5, 'Latitude', ha='center', transform = ax0.transAxes, rotation = 90)
plt.title("Site Locations ")

new_times = [datetime.datetime.utcfromtimestamp(x) for x in T03a]
new_times = n.array(new_times)
new_times1 = [datetime.datetime.fromtimestamp(x) for x in T03a]  # local-time
new_times1 = n.array(new_times1)

ax1 = fig.add_subplot(122)
    # import ipdb; ipdb.set_trace()
dB3new = dB3new.astype(n.float)
plt.pcolormesh(new_times, range_gates, dB3new,vmin=-3, vmax=30.0, cmap="inferno")
    # plt.contourf(new_times, range_gates, dB3new, vmin=-3, vmax=30.0, cmap="inferno",levels=30)
cb = plt.colorbar()
cb.set_label("SNR (dB)")
plt.title("RTI plot for  %1.2f MHz \n%s (UTC)" %(freqs[80]/1e6,  datetime.datetime.utcfromtimestamp(T03[1]).strftime('%Y-%m-%d')))
plt.xlabel("Time (UTC)")
plt.ylabel("One-way range offset (km)")
    # plt.ylim([dr-conf.max_range_extent/1e3,dr+conf.max_range_extent/1e3])
plt.ylim([0, 4000])
    # plt.xlim([0, 15])

    # plt.savefig(img_fname)

plt.tight_layout()
    # plt.savefig(img_fname1a,bbox_inches ='tight')
    # plt.show()

import ipdb
ipdb.set_trace()
    # plt.savefig(img_fname1)
    # plt.savefig(img_fname2)
plt.close()
plt.clf()
