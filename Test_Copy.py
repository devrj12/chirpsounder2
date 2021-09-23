#!/usr/bin/env python3
# Test script where I test and debug new scripts

import ipdb
import glob
import os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


rootdir = '/home/dev/Downloads/chirp_juha2b'
# for subdir, dirs, files in os.walk(rootdir):
dirs = sorted(os.listdir(rootdir))


for j in range(0,len(dirs)):
    dirs1 = dirs[j]
 
    if dirs1[0:4] == '2021':
        path = os.path.join(rootdir, dirs1)
        os.chdir(path)
        ipdb.set_trace()
        
        
        
