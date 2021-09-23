#!/usr/bin/env python


import os
import pickle
import numpy
import ipdb
os.chdir('/home/dev/Downloads/chirp_juha')

with open('Time_1.data', 'rb') as f:
    TimeList = pickle.load(f)

x1 = [x % 720 for x in TimeList]
x3 = [round(y, 2) for y in x1]
x4 = []
x5 = []
for i in range(len(x3)):
    if i == 0:
        print('here')
        x4.append(x3[0])
        x5.append(TimeList[0])
        ipdb.set_trace()
        print(x4)
    elif abs(x3[i] - x3[i-1]) > 1:
        print(x3[i] - x3[i-1])
        x4.append(x3[i])
        x5.append(TimeList[i])
        print(x4)
        print(x5)
        ipdb.set_trace()
        
        
