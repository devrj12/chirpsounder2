
import h5py
import os
import glob

dir = os.getcwd()
fl = glob.glob("%s/*.h5" % (dir))
ho = h5py.File(fl[0], "r")

##
# Both axis plot

import matplotlib.pyplot as plt
CD4        = [-1, 27, 108, 130, 135, 169, 211, 232, 245, 291, 343, 372, 416, 462, 509, 592, 671]
CD4 + [-1] = [-1, 27, 108, 130, 135, 169, 211, 232, 245, 291, 343, 372, 416, 462, 509, 592, 671, -1]


for j in range(len(CD4)-1):

	fig, ax1 = plt.subplots()

	color = 'tab:red'
	ax1.set_xlabel('Date-Time (LT)')
	ax1.set_ylabel('Heights of Ordinary Layer (km)')
	#ax1.plot(CD2[CD4[j]+1:CD4[j+1]],[x[2] for  x in Coord2[CD4[j]+1:CD4[j+1]]], color=color)
	ax1.plot(CD2[CD4[j]+1:CD4[j+1]],[x[2] for  x in Coord2[CD4[j]+1:CD4[j+1]]],'-o',color=color)   
	ax1.tick_params(axis='y', labelcolor=color)

	ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

	color = 'tab:blue'
	ax2.set_ylabel('Frequencies of Ordinary Layer (MHz)')
	#ax2.plot(CD2[0:27],[x[1] for  x in Coord2[0:27]], color=color)
	ax2.plot(CD2[CD4[j]+1:CD4[j+1]],[x[1] for  x in Coord2[CD4[j]+1:CD4[j+1]]],'-o',color=color)   
	ax2.tick_params(axis='y', labelcolor=color)
	ax2.set_title('Heights/Frequencies of Ordinary Layer vs Date-Time')
	fig.tight_layout()  # otherwise the right y-label is slightly clipped
	plt.show()
	ipdb.set_trace()
	

#
A = []
for j in range(0,len(Coord),2):
	A.append([Coord[j][0], Coord[j][1], Coord[j+1][2]])
        # t0, foF, hF
        
A1 = []
for j in range(0,len(Coord1),2):
	A1.append([Coord1[j][0], Coord1[j][1], Coord1[j][2], Coord1[j+1][1], Coord1[j+1][2]])

CD  = [x[0] for x in Coord2]
CD2 = [datetime.datetime.fromtimestamp(x) for x in CD]
CD3 = [CD2[i].day for i in range(len(CD2))] # indices for individual day
CD4 = [i for i in range(1,len(CD3)) if CD3[i]!=CD3[i-1] ]
CD4 = [-1] + CD4

#plt.plot(CD2,[x[2] for  x in Coord2],'-ok')
plt.plot(CD2,[x[2] for  x in Coord2],'.', color='black')
plt.plot(CD2,[x[2] for  x in Coord2],'.', color='black')
plt.ylabel("Heights of Ordinary Layer (km)")
plt.xlabel("Date-Time (LT)")
plt.title("Heights vs Date-Time")


# Schedule
import os
import pickle
import numpy

os.chdir('/home/dev/Downloads/chirp_juha')

with open('/home/dev/Downloads/chirp_juha/Time_2.data','wb') as f:
           pickle.dump(Time_1,f)

with open('Time_1.data', 'rb') as f:
	    TimeList = pickle.load(f)

     x1  = [x % 720 for x in TimeList]
     indexes = numpy.unique(x1, return_index=True)[1]
     x2  = numpy.unique(x1)
     x3  = [round(y,2) for y in x2]
     x4  = numpy.unique(x3)


     x1  = [x % 720 for x in TimeList]
     x3  = [round(y,2) for y in x2]
     x4  = []
     for i in range(len(x3)):
        if i == 0:
        	print(here)
        	x4.append(x3[0])
        	print(x4)
        elif (x3[i] - x3[i-1]) > 1:
        	x4.append(x3[i])
        

     for x in x3:
       x4.append(x3[0])
       x5 = x3[1:-1]
       for x 
     
     x4  = [x[0] for x in  x3, if x[-1] - [x-2] > 1  for x in  x3: x[-1]] 

# In calc_ionograms.py
sr  = conf.sample_rate
dec = 2500

def get_m_per_Hz(rate):
    """
    Determine resolution of a sounding.
    """
    dt=1.0/rate
    # m/Hz round trip
    return(dt*c.c/2.0)


    dr=conf.range_resolution
    df=conf.frequency_resolution
    sr_dec = sr/dec
    ds=get_m_per_Hz(rate)
    fftlen = int(sr_dec*ds/dr/2.0)*2
    fft_step=int((df/rate)*sr_dec)

    S=spectrogram(n.conj(zd),window=fftlen,step=fft_step,wf=ss.hann(fftlen))

    freqs=rate*n.arange(S.shape[0])*fft_step/sr_dec
    range_gates=ds*n.fft.fftshift(n.fft.fftfreq(fftlen,d=1.0/sr_dec))
    
    ridx=n.where(n.abs(range_gates) < conf.max_range_extent)[0]

    try:
        print(t0)
        dname="%s/%s"%(conf.output_dir,cd.unix2dirname(t0))
        if not os.path.exists(dname):
            os.mkdir(dname)
        ofname="%s/lfm_ionogram-%03d-%1.2f.h5"%(dname,cid,t0)
        print(ofname)
        ho=h5py.File(ofname,"w")
        ho["S"]=S[:,ridx]          # ionogram frequency-range
        ho["freqs"]=freqs  # frequency bins
        ho["rate"]=rate    # chirp-rate
        ho["ranges"]=range_gates[ridx]
        ho["t0"]=t0
        ho["id"]=cid
        ho["sr"]=float(sr_dec) # ionogram sample-rate
        ho["ch"]=ch            # channel name
        ho.close()   
    
    
# How they are written ?     
    
    conf=cc.chirp_config(sys.argv[1])
    
    
# In plot_ionograms.py


    dt = (t0-n.floor(t0))
    #import ipdb; ipdb.set_trace()
    dr = dt*c.c/1e3  # distance traveled in km
    range_gates = dr+2*ranges/1e3   # Why ??    (ranges here are range_gates as defined above in line 35 ! Are they ?) 
    
    
    
###

h5ls -r chirp-40177822100000000.h5  # These chirp .. files created by detect_chirps.py
/                        Group
/chirp_rate              Dataset {SCALAR}
/chirp_time              Dataset {SCALAR}
/f0                      Dataset {SCALAR}
/i0                      Dataset {SCALAR}
/n_samples               Dataset {SCALAR}
/sample_rate             Dataset {SCALAR}
/snr                     Dataset {SCALAR}


h5ls -r par-1607112727.0000.h5 # These par ... files created by find_timings.py
/                        Group
/chirp_rate              Dataset {SCALAR}
/f0                      Dataset {5}
/snrs                    Dataset {5}
/t0                      Dataset {SCALAR}
/t0s                     Dataset {5}

h5ls -r lfm_ionogram-000-1607124643.00.h5  # These lfm_ .. files created by calc_ionograms.py 
/                        Group
/S                       Dataset {498, 3999}
/ch                      Dataset {SCALAR}
/freqs                   Dataset {498}
/id                      Dataset {SCALAR}
/ranges                  Dataset {3999}
/rate                    Dataset {SCALAR}  # This is chirp-rate
/sr                      Dataset {SCALAR}
/t0                      Dataset {SCALAR}
    
# Goal :  find chirptime for every ionogram and detect the change whenever it happens
# [steps] : [1] Create a list (keep appending) of chirptime (start) for every ionogram (for 100 KHz/sec)
#           [2] Keep taking the difference and if it exceeds the average difference - report the change 
#           [3] Plug that in schedule       
            
#    
os.chdir('/home/dev/Downloads/chirp_juha')

