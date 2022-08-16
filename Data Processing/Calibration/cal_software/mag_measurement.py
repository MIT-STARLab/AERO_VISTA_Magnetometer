# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 09:15:27 2021

@author: nickb
"""

#Measurement class contains magnetometer data and other reference data
#needed to perfrom calibration
import numpy as np
import matplotlib.pyplot as plt


class Measurement():
    def __init__(self):
        #self.data={"t":None,"B":None,"T":None,"Is":None,}
        self.time=None #Time stamps for the measurement
        #Shape is numpy array of shape (n,)
        self.mag=None  #Magnetometer data
        #Shape is numpy array of shape (n,3)
        self.temp=None #Temperature data
        #Shape is numpy array of shape (n,)
        self.Is=None   #Interfering currents
        #Shape is numpy array of shape (n,m) where m is number of interferers
        self.labels=[]
        #Shape is list of names in same order as the m interferers of Is
        self.info="Blank"
    
    #Will need all measurements on the same time base
    
    #Sets time from single vector
    def setTime(self,times):
        n=len(times)
        self.time=np.array(times)
        self.mag=np.zeros((n,3))
        self.temp=np.zeros(n)
        self.Is=np.zeros((n,))
        
    
    #Sets magnetic fields from matrix
    #If no time base provided, assumes same sampling as time
    def setB(self,Bs,times=None):
        if times is None:
            assert (len(Bs))==len(self.time)
            self.mag=np.array(Bs)
        else:
            for axis in range(3):
                self.mag[:,axis]=np.interp(self.time,times,Bs[:,axis])
    
     
    #Sets measurement temperature interpolating as necessary
    def setTemp(self,temps,times=None):
        if times is None:
            assert len(temps)==len(self.time)
            self.temp=np.array(temps)
        else:
            self.temp=np.interp(self.time,times,temps)

    def add_HK(self,value,label,times=None):
        value=float(value) #Convert to float for math operations
        if not times.any():
            assert (len(value))==len(self.time)
            dat=value
        else: 
            dat=np.interp(self.time,times,value)
            
        self.labels.append(label)
        if self.Is is None:
            self.Is=dat
        else:
            self.Is=np.concatenate((self.Is,dat),axis=1)
            
            
            
    def plot_B(self,title=None):
        if self.mag is None:
            print("No magnetic data for ploting")
            return
        
        lineObjects = plt.plot(self.time, self.mag, linestyle="None", marker="x")
        plt.legend(iter(lineObjects), ('X', 'Y', 'Z'))
        plt.title(title)