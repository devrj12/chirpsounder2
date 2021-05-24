#!/usr/bin/env python3
import numpy as np
import glob
import h5py
import datetime
import pandas as pd
import os
import shutil

import tqdm # Status bars

fnames = glob.glob('chirp*.h5') # Search directory for files
fnames.sort() # Sort filenames alphabetically

out_dir = 'output'

# Delete old directory if exists
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)

#Create new output directory
os.makedirs(out_dir)

ctimes      = []
ctimes_str  = []
chirp_rates = []
chirp_times = []
fnames_new  = []

print('Loading Files...')
for fname in tqdm.tqdm(fnames):
    
    h0          = h5py.File(fname,'r')
    chirp_rate  = h0['chirp_rate'][()]/1000.
    chirp_time  = h0['chirp_time'][()]
    # ctime       = datetime.datetime.fromtimestamp(chirp_time)
    # This "...fromtimestamp" is from previous version (by Dr. Nathaniel). It actually gives local-time but not the universal time. 
    # So, I am editing ctime to be "....utcfromtimestamp(chirp_time). 
    ctime       = datetime.datetime.utcfromtimestamp(chirp_time)
    ctime_str   = ctime.strftime('%Y-%m-%d.%H:%M:%S.%dUT')

    # Create a new file name
    fname_new   = 'chirp-{!s}.h5'.format(ctime_str)

    f0          = h0['f0'][()]
    i0          = h0['i0'][()]
    sr          = h0['sample_rate'][()]

    ctimes.append(ctime)
    ctimes_str.append(ctime)
    chirp_times.append(chirp_time)
    chirp_rates.append(chirp_rate)
    fnames_new.append(fname_new)


# Create Dataframe
df = pd.DataFrame({'chirp_rate':chirp_rates,'chirp_time':chirp_times,'fname':fnames,'fname_new':fnames_new},index=ctimes)

# Select only 100 kHz/s ionosondes
tf          = df['chirp_rate'] == 100.
df1         = df[tf].copy()

# Compute Modulo Time
modulo_time = df1['chirp_time'].astype(np.int) % 720
df1['modulo_time'] = modulo_time

df1 = df1.sort_index()

# Copy files to new location.
for row_index,row in df1.iterrows():
    fname       = row['fname']
    fname_new   = row['fname_new']
    outpath     = os.path.join(out_dir,fname_new)
    print('{!s} --> {!s}'.format(fname,outpath))

    shutil.copy(fname,outpath)
    

# Save sorted dataframe to HDF5 File.

now_str = datetime.datetime.utcnow().strftime('%Y%m%d.%H%M')
h5_name = 'files_sorted_on_{!s}UT.h5'.format(now_str)
h5_path = os.path.join(out_dir,h5_name)
df1.to_hdf(h5_path,'data')
print('HDF5 Data Table Saved to: {!s}'.format(h5_path))



