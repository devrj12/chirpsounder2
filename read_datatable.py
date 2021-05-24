#!/usr/bin/env python3

import pandas as pd

h5file = 'output/files_sorted_on_20201201.1622UT.h5'

df1 = pd.read_hdf(h5file,'data')

import ipdb; ipdb.set_trace()
