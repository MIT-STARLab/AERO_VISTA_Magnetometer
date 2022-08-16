import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import os
import struct
import sys
from scipy import signal
from scipy.signal import butter,filtfilt
from scipy.fft import fft, ifft

sys.path.append(os.path.join('..', 'ASP', 'Helpers'))

from constants import MAG_DATA_HEADER_STRUCT

my_font_size=12
my_title_size=15

#RAW_DATA_DIRECTORY = os.path.join('..', 'data', 'mag')
RAW_DATA_DIRECTORY = r"C:\Users\nickb\Documents\MIT\AERO\ASP\scp_files\mag\raw"
PROCESSED_DATA_DIRECTORY = r"C:\Users\nickb\Documents\MIT\AERO\ASP\scp_files\mag\processed"
SAVE_DATA=False


def plot_histogram(data): 
    plt.figure()
    # An "interface" to matplotlib.axes.Axes.hist() method
    n, bins, patches = plt.hist(x=data, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('dt (seconds)')
    plt.ylabel('frequency')
    plt.title('Frequency vs Timing Between Data Capture')
    maxfreq = n.max()
    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
    plt.show()

def plot_timing_histogram():
    data = load_mag_data(RAW_DATA_DIRECTORY)
    time_difs = []
    for i in range (0, len(data)-1):
        dt = data[i+1][0] - data[i][0] # get difference between timestamps
        time_difs.append(dt)
        if dt > 0.03:
            #print(data[i+1])
            #print(data[i])
            pass
    histo = Counter(time_difs)
    plot_histogram(histo)

def plot_data(data,title=''):
    plt.figure()
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('epoch time (seconds)')
    plt.ylabel('uT')
    plt.title(title)

    # multiple line plots
    plt.plot( 'times', 'X0', data=data, marker='o', markerfacecolor='red', markersize=3, color='red', linewidth=2)
    plt.plot( 'times', 'Y0', data=data, marker='o', markerfacecolor='green', markersize=3, color='green', linewidth=2)
    plt.plot( 'times', 'Z0', data=data, marker='o', markerfacecolor='blue', markersize=3, color='blue', linewidth=2)
    # plt.plot( 'times', 'X1', data=data, marker='o', markerfacecolor='#670000', markersize=3, color='#670000', linewidth=2, linestyle='dashed')
    # plt.plot( 'times', 'Y1', data=data, marker='o', markerfacecolor='#004800', markersize=3, color='#004800', linewidth=2, linestyle='dashed')
    # plt.plot( 'times', 'Z1', data=data, marker='o', markerfacecolor='#000067', markersize=3, color='#000067', linewidth=2, linestyle='dashed')
    # show legend
    plt.legend()

def twos_comp(val,bits):
    ret=val
    if(val & (1<<(bits-1))) != 0:
        ret = val - (1<<bits)
    return ret

def load_mag_data(datadir):
    data = []
    files = os.listdir(datadir)
    for filename in files:
        file = open(os.path.join(RAW_DATA_DIRECTORY,filename), "rb")
        filedata = file.read()
        while len(filedata) >= 41:
            time, polarity = struct.unpack("db", filedata[:9])
            filedata = filedata[9:]
            reading = {}
            for i in range(0,8):
                temp=filedata[0+4*i:4+4*i]
                header=temp[0]
                mydata=(temp[1]<<16)+(temp[2]<<8)+temp[3]
                mydata=twos_comp(mydata,24)
                channel=(header>>4)&(0b111)
                reading[str(channel)]=[header,mydata]
            data.append([time, polarity, reading])
            filedata = filedata[32:]
    data = sorted(data, key=lambda x: x[0])
    return data

def plot_mag_data():
    B_gain=0.0364/1000 #uT per lsb
    data = load_mag_data(RAW_DATA_DIRECTORY)
    corrupted = 0
    graphdata={"times":[], "X0":[], "Y0":[], "Z0":[], "X1":[], "Y1":[], "Z1":[]}
    for i in range (0, len(data)):
        # polarity = data[i][1]
        polarity = 1
        if set(['0', '1', '2', '4', '5', '6']).issubset(data[i][2].keys()):
            graphdata["X0"].append(data[i][2]['0'][1]*B_gain*polarity)
            graphdata["Y0"].append(data[i][2]['1'][1]*B_gain*polarity)
            graphdata["Z0"].append(data[i][2]['2'][1]*B_gain*polarity)
            
            graphdata["X1"].append(data[i][2]['4'][1]*B_gain*polarity)
            graphdata["Y1"].append(data[i][2]['5'][1]*B_gain*polarity)
            graphdata["Z1"].append(data[i][2]['6'][1]*B_gain*polarity)

            graphdata["times"].append(data[i][0]) # get difference between timestamps
        else:
            corrupted += 1
    print("found", str(corrupted),"logs corrupted ")
    plt.figure(1)
    plot_data(graphdata,"Raw Data")
    return graphdata


def butter_lowpass_filter(data, cutoff, fs, order):
    nyq=0.5*fs
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def RMSE_10Hz(data,fs):
    lpdata=butter_lowpass_filter(data, 1, fs, 5)
    RMSE = np.sqrt(np.mean(lpdata**2))
    
    return RMSE

def frequency_dev_plot(data):
    times=data["times"]
    n=len(times)
    start=times[0]
    stop=times[-1]
    fs=n/(stop-start)
    #timeslin=np.linspace(times[0],times[-1],num=times)
    X=data["X0"] - np.mean(data["X0"])
    Y=data["Y0"] - np.mean(data["Y0"])
    Z=data["Z0"] - np.mean(data["Z0"])
    
    X2=data["X1"] - np.mean(data["X1"])
    Y2=data["Y1"] - np.mean(data["Y1"])
    Z2=data["Z1"] - np.mean(data["Z1"])
    

    fig,a =  plt.subplots(2,2,figsize=(8,6))

    a[0][0].plot(times,X,label='x',color='r')
    a[0][0].plot(times,Y,label='y',color='g')
    a[0][0].plot(times,Z,label='z',color='b')
    a[0][0].set_title("Time Domain Variation",fontsize=my_title_size)
    a[0][0].set_ylabel("B-field [uT]",fontsize=my_font_size)
    a[0][0].set_xlabel("Time (s)",fontsize=my_font_size)
    a[0][0].legend()
    
    
    diffX=X-X2
    diffY=Y-Y2
    diffZ=Z-Z2
    
    #For plotting primarily the other magnetometer
    # temp=[X,Y,Z]
    # X,Y,Z=[X2,Y2,Z2]
    # X2,Y2,Z2=temp


    a[1][0].set_title("Time Domain Gradient Variation",fontsize=my_title_size)
    a[1][0].plot(times,diffX,label='x',color='r')
    a[1][0].plot(times,diffY,label='y',color='g')
    a[1][0].plot(times,diffZ,label='z',color='b')
    a[1][0].set_ylabel("B-field [uT]",fontsize=my_font_size)
    a[1][0].set_xlabel("Time (s)",fontsize=my_font_size)
    a[1][0].legend()
    

    a[0][1].set_title("Noise Spectral Density",fontsize=my_title_size)
    a[0][1].psd(X,Fs=fs,label='X',color='r')
    a[0][1].psd(Y,Fs=fs,label='Y',color='g')
    a[0][1].psd(Z,Fs=fs,label='Z',color='b')
    a[0][1].set_ylabel("Spectral Density dBuT/Hz",fontsize=my_font_size)
    a[0][1].set_xlabel("Frequency [Hz]",fontsize=my_font_size)
    a[0][1].legend()
    
    a[1][1].set_title("Gradient Noise Spectral Density",fontsize=my_title_size)
    a[1][1].psd(diffX,Fs=fs,label='X',color='r')
    a[1][1].psd(diffY,Fs=fs,label='Y',color='g')
    a[1][1].psd(diffZ,Fs=fs,label='Z',color='b')
    a[1][1].set_ylabel("Spectral Density dBuT/Hz",fontsize=my_font_size)
    a[1][1].set_xlabel("Frequency [Hz]",fontsize=my_font_size)
    a[1][1].legend()
    
    fig.suptitle("Noise Analysis",fontsize=my_title_size)
    plt.show()
    plt.tight_layout()
    if SAVE_DATA:
        plt.savefig(PROCESSED_DATA_DIRECTORY + "\\" + "single_axis.png")
    
    
    RMSE=[RMSE_10Hz(X,fs),RMSE_10Hz(Y,fs),RMSE_10Hz(Z,fs)]
    
    diffRMSE=[RMSE_10Hz(diffX,fs),RMSE_10Hz(diffY,fs),RMSE_10Hz(diffZ,fs)]
    
    print("RMSE", RMSE)
    print("diffRMSE", diffRMSE)

def process_mag_data():
    B_gain=0.0364/1000 #uT per lsb
    data = load_mag_data(RAW_DATA_DIRECTORY)
    
    fs=(len(data)-1)/(data[-1][0]-data[0][0])
    

    prev_polarity = 0
    numSwitches = 0
    curTotal = {"X0":0.0, "Y0":0.0, "Z0":0.0, "X1":0.0, "Y1":0.0, "Z1":0.0}
    curDatapoints = 0
    skipn=4
    skips = skipn
    
    datakeys=["X0","Y0","Z0","X1","Y1","Z1"]

    rawdata={"times":[], "X0":[], "Y0":[], "Z0":[], "X1":[], "Y1":[], "Z1":[]}
    graphdata={"times":[], "X0":[], "Y0":[], "Z0":[], "X1":[], "Y1":[], "Z1":[]}
    polarity_avgs = {"times":[], "X0":[], "Y0":[], "Z0":[], "X1":[], "Y1":[], "Z1":[]}
    polarities = []
    
    Oestimate={"times":[],"X0":[], "Y0":[], "Z0":[], "X1":[], "Y1":[], "Z1":[]}
    switch_indices=[]
    
    for i in range (0, len(data)):
        try:
            rawdata["X0"].append(data[i][2]['0'][1]*B_gain)
            rawdata["Y0"].append(data[i][2]['1'][1]*B_gain)
            rawdata["Z0"].append(data[i][2]['2'][1]*B_gain)
            rawdata["X1"].append(data[i][2]['4'][1]*B_gain)
            rawdata["Y1"].append(data[i][2]['5'][1]*B_gain)
            rawdata["Z1"].append(data[i][2]['6'][1]*B_gain)
            rawdata["times"].append(data[i][0])
        except:
            print("Found one missing data")
            continue
        
        if skips > 0:
            skips -= 1
            continue

        polarity = data[i][1]
        if set(['0', '1', '2', '4', '5', '6']).issubset(data[i][2].keys()):
            if polarity != prev_polarity:
                # #A switching event has occured, this is when we estimate offset
                # if (i+3)<len(data):
                #     Oestimate["times"].append(np.mean((data[i-1][0],data[i+3][0])))
                #     for key in datakeys:
                #         Oestimate[key]=
                switch_indices.append(i)
                #Take care not to store mag data during switching
                for array in graphdata.values():
                    del array[-skipn:]
                del polarities[-skipn:]
                skips = skipn

                if numSwitches % 2 == 0 and numSwitches != 0:
                    for key in curTotal.keys():
                        if key != "times":
                            polarity_avgs[key].append(curTotal[key] / curDatapoints)

                    polarity_avgs["times"].append(data[i][0])
                    curTotal = {"X0":0.0, "Y0":0.0, "Z0":0.0, "X1":0.0, "Y1":0.0, "Z1":0.0}
                    curDatapoints = 0
              
                prev_polarity = polarity
                numSwitches += 1
                continue
          
            graphdata["X0"].append(data[i][2]['0'][1]*B_gain)
            graphdata["Y0"].append(data[i][2]['1'][1]*B_gain)
            graphdata["Z0"].append(data[i][2]['2'][1]*B_gain)
            
            graphdata["X1"].append(data[i][2]['4'][1]*B_gain)
            graphdata["Y1"].append(data[i][2]['5'][1]*B_gain)
            graphdata["Z1"].append(data[i][2]['6'][1]*B_gain)
            polarities.append(polarity)

            graphdata["times"].append(data[i][0]) # get difference between timestamps

            for key in curTotal.keys():
                  if key != "times":
                      curTotal[key] += graphdata[key][-1]
            
            curDatapoints += 1
            
    # fc=0.2
    # sos = signal.bessel(10, fc, fs=fs, output='sos')
    # zi = signal.sosfilt_zi(sos)
    # #filter_avg=
    # filt_avgs = {"X0":[], "Y0":[], "Z0":[], "X1":[], "Y1":[], "Z1":[]}
    
    # for key in filt_avgs:
    #     N=int(fs/fc)*5
    #     mystart=np.flip(rawdata[key][25:N+25])
    #     bias=np.mean(rawdata[key][0:N])
    #     #myzi=signal.sosfilt(sos, bias*np.ones(N),zi=zi*bias)[1]
    #     print(key,bias)
    #     filt_avgs[key]=signal.sosfilt(sos, np.concatenate((mystart,rawdata[key])))[N:]
    # filt_avgs["times"]=rawdata["times"]
    
    #Nicks method of estimating offset
    for i in switch_indices[1:-1]:
        for key in Oestimate.keys():
            Oestimate[key].append(np.mean((rawdata[key][i-1],rawdata[key][i+skipn])))
    
    Oavgd={}
    Oavgd["times"]=Oestimate["times"]
    for key in datakeys:
        w=9
        Oavgd[key]=np.pad((np.convolve(Oestimate[key], np.ones(w), 'valid') / w), (int(w/2), int(w/2)), 'edge')
        
    
    interp_avgs = {"X0":[], "Y0":[], "Z0":[], "X1":[], "Y1":[], "Z1":[]}
    for key in interp_avgs:
        interp_avgs[key] = np.interp(graphdata["times"], Oavgd["times"], Oavgd[key])
    
    plt.figure(2)
    plot_data(Oavgd,"Offset Estimation")
    
    # plt.figure()
    # plot_data(filt_avgs,"Filtered Averages")
    
    for i in range(len(graphdata["times"])):
        for key in interp_avgs.keys():
            graphdata[key][i] -= interp_avgs[key][i]
    
    plt.figure(3)
    plot_data(graphdata, "Average Subtracted")
    plt.plot(graphdata["times"], polarities, label="polarity")
    
    
    for i in range(len(graphdata["times"])):
        for key in interp_avgs.keys():
            graphdata[key][i] *= polarities[i]
            
    plt.figure(4)
    plot_data(graphdata, "Polarity Corrected")
    
    return graphdata

#An implementation of processing which provides an effective data rate
#equal to the 
#def max_resolution()


if __name__ == "__main__":
    mydata=load_mag_data(RAW_DATA_DIRECTORY)
    plot_timing_histogram()
    plot_mag_data()
    mydat=process_mag_data()
    frequency_dev_plot(mydat)
    plt.show()
    
