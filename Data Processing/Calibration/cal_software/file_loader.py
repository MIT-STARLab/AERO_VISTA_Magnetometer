# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 09:15:45 2021

@author: nickb
"""

#Contains functions which will populate a mesaurement object from files

from mag_measurement import Measurement

import numpy as np

from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import (
    DateFormatter, AutoDateLocator, AutoDateFormatter, datestr2num
)

#finds the times which are valid for two datasets
def find_time_overlap(times1,times2):
    mymin=max(min(times1),min(times2))
    mymax=min(max(times1),max(times2))
    
    mini=min(range(len(times1)), key=lambda i: abs(times1[i]-mymin)) #get index
    maxi=min(range(len(times1)), key=lambda i: abs(times1[i]-mymax)) #get index
    
    return times1[mini:maxi]

def remove_too_fast(mes,delta=0.5):
    mytimes=[]
    for i in range(1,len(mes.time)-1):
        del1=np.linalg.norm(mes.mag[i,:]-mes.mag[i-1,:])
        del2=np.linalg.norm(mes.mag[i,:]-mes.mag[i+1,:])
        if del1<delta and del2<delta:
            mytimes.append(mes.time[i])
    
    return np.array(mytimes)

#Returns deltaT = time1-time2 that results in maximum correlation
#Time1 is considered fixed, Add deltaT to bring time2 to the time1 time base
#If they cover different spans, time1 should be a subset of time2
def find_max_correlation(data1,time1,data2,time2):
    guess = time1[0] - time2[0] #Start by assuming they started as same time
    search_size = 20
    search_resolution = 0.01 #Search to 1 ms
    deltaTs = np.linspace(guess-search_size,guess+search_size,int(2*search_size/search_resolution))
    Cs = np.zeros(len(deltaTs))
    for i in range(len(deltaTs)):
        x = data1
        y = np.interp(time1,time2+deltaTs[i],data2)
        Cs[i] = np.corrcoef(x,y)[0,1]
    plt.figure()
    plt.plot(deltaTs,Cs)
    plt.title("Covariance")
    
    return deltaTs[np.argmax(Cs)]

#These functions load data from predefined files into the measurement classes

#Loads two magentometer only data points from the same file
#Such as like generated from the two RM3100 on the magEval board
def RM3100pair(filename):
    dat = np.genfromtxt(filename, delimiter=',')
    test_mes=Measurement()
    test_mes.info="Test measurement of RM3100"
    ref_mes=Measurement()
    ref_mes.info="Reference measurement of RM3100"
    n=len(dat[:,0])
    #n=4*20
    times=dat[:n,0]
    
    test_mes.setTime(times)
    ref_mes.setTime(times)
    
    test_mes.setB(dat[:n,1:4],times=times)
    ref_mes.setB(dat[:n,4:7],times=times)
    
    return test_mes, ref_mes

#Loads a test file with magnetometer and temperature information
# and a reference file with only magnetometer information
def magEval(filename_test,filename_ref):
    test_dat=np.genfromtxt(filename_test, delimiter=',')
    ref_dat=np.genfromtxt(filename_ref, delimiter=',')
    
    test_mes=Measurement()
    test_mes.info="Test measurement with HMC1053 on magEval"
        
    ref_mes=Measurement()
    ref_mes.info="Reference measurement of RM3100"
    
    #Remove too fast
    ref_mes.setTime(ref_dat[:,0])
    ref_mes.setB(ref_dat[:,1:4])
    times1=remove_too_fast(ref_mes)
    
    times=find_time_overlap(times1,test_dat[:,0])

    test_mes.setTime(times)
    ref_mes.setTime(times)
    
    ref_mes.setB(ref_dat[:,1:4],times=ref_dat[:,0])
    
    test_mes.setB(test_dat[:,1:4],times=test_dat[:,0])
    test_mes.setTemp(test_dat[:,4]-273,times=test_dat[:,0])
    
    return test_mes,ref_mes

    
#Used for cellphone calibration
def phoneCal(filename_test,filename_ref): #09:23:53:559
    convert = lambda x: (datetime.strptime((x+b"000").decode(), "%H:%M:%S:%f")\
        - datetime(1900, 1, 1)).total_seconds()
    test_dat=np.genfromtxt(filename_test, delimiter=',',skip_header=1,converters={0:convert},dtype=float)
    ref_dat=np.genfromtxt(filename_ref, delimiter=',')
    
    #Get rid of unwanted data
    plt.figure()
    plt.plot(test_dat[:,1])
    plt.title("Before trim")
    plt.figure()
    
    test_dat = test_dat[600:3500,:]
    
    plt.plot(test_dat[:,1])
    plt.title("After trim")
    
    plt.figure()
    plt.plot(ref_dat[:,0],ref_dat[:,1])
    plt.title("Reference Data")
    
    plt.plot(test_dat[:,0],test_dat[:,1])
    plt.title("Test Data")
    
    test_mes=Measurement()
    test_mes.info="Test measurement from cell phone magnetometer"
        
    ref_mes=Measurement()
    ref_mes.info="Reference measurement of RM3100"
    
    deltaT = find_max_correlation(test_dat[:,1],test_dat[:,0],ref_dat[:,1],ref_dat[:,0])
    
    times = find_time_overlap(test_dat[:,0]-deltaT,ref_dat[:,0])
    
    test_mes.setTime(times)
    ref_mes.setTime(times)
    
    ref_mes.setB(ref_dat[:,1:4],times=ref_dat[:,0])
    
    test_mes.setB(test_dat[:,1:4],times=test_dat[:,0]-deltaT)

    return test_mes,ref_mes
    
    
if __name__ == "__main__":
    pass   