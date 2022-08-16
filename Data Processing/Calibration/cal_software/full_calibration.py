# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 22:51:09 2021

@author: nickb
"""

import numpy as np
import pickle
import itertools
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from numpy.linalg import norm
import matplotlib.pyplot as plt


class Calibration():
    #Holds a calibration state and functions needed to perform calibration
    def __init__(self):
        self.S=np.identity(3) #Sensitivity matrix
        self.KS=np.zeros((3,3)) #Sensitivity matrix temperature dependence
        self.O=np.zeros((3)) #Offset vector
        self.KO=np.zeros((3)) #Offset vector temperature dependence
        self.D=np.zeros((3,0)) #External dependence, 3 by m
        #The use flags deermine which elements of the calibration will be used
        self.flagPreset("basic")
        
        self.result=[None,None,None]
        
    def flagPreset(self,calName="basic"):
        if calName == "linear":
            self.useFlags={"Sv":True,"Soa":False,"KSv":True,"KSoa":False,\
                   "O":True,"KO":True,"I":True}
        elif calName == "noT":
            self.useFlags={"Sv":True,"Soa":True,"KSv":False,"KSoa":False,\
                   "O":True,"KO":True,"I":True}
        elif calName == "allnoI":
            self.useFlags={"Sv":True,"Soa":True,"KSv":True,"KSoa":True,\
                   "O":True,"KO":True,"I":False}
        elif calName == "Bonly":
            self.useFlags={"Sv":True,"Soa":True,"KSv":False,"KSoa":False,\
                   "O":True,"KO":False,"I":False}
        if calName == "basic":
            self.useFlags={"Sv":True,"Soa":False,"KSv":False,"KSoa":False,\
                   "O":True,"KO":False,"I":False}
        if calName == "basicwithI":
            self.useFlags={"Sv":True,"Soa":False,"KSv":False,"KSoa":False,\
                   "O":True,"KO":False,"I":True}

            
    #Puts needed coefficients into list, complimentary to update_from_coeffs        
    def get_coeffs(self,axis):
        coeffs=[]
        if self.useFlags["Sv"]:
            coeffs.append(self.S[axis,axis])
        if self.useFlags["Soa"]:
            coeffs.append(self.S[axis,axis-2])
            coeffs.append(self.S[axis,axis-1])
        if self.useFlags["KSv"]:
            coeffs.append(self.KS[axis,axis])
        if self.useFlags["KSoa"]:
            coeffs.append(self.KS[axis,axis-2])
            coeffs.append(self.KS[axis,axis-1])
        if self.useFlags["O"]:
            coeffs.append(self.O[axis])
        if self.useFlags["KO"]:
            coeffs.append(self.KO[axis])
        if self.useFlags["I"]:
            for val in self.D[axis,:]:
                coeffs.append(val)
        return coeffs

        # return np.concatenate([i.flatten() for i in\
        #     [self.S[axis,:],self.KS[axis,:],self.O[axis],self.KO[axis],self.D[axis,:]]])
    
    #Updates class variables from coefficeint list, complimentary to get_coeffs
    def update_from_coeffs(self,coeffs,axis):
        i=0
        if self.useFlags["Sv"]:
            self.S[axis,axis]=coeffs[i]
            i+=1
        if self.useFlags["Soa"]:
            self.S[axis,axis-2]=coeffs[i]
            self.S[axis,axis-1]=coeffs[i]
            i+=2
        if self.useFlags["KSv"]:
            self.KS[axis,axis]=coeffs[i]
            i+=1
        if self.useFlags["KSoa"]:
            self.KS[axis,axis-2]=coeffs[i]
            self.KS[axis,axis-1]=coeffs[i]
            i+=2
        if self.useFlags["O"]:
            self.O[axis]=coeffs[i]
            i+=1
        if self.useFlags["KO"]:
            self.KO[axis]=coeffs[i]
            i+=1
        if self.useFlags["I"]:
            self.D[axis,:]=coeffs[i:]
        
        # self.S[axis,:]=coeffs[0:3]
        # self.KS[axis,:]=coeffs[3:6]
        # self.O[axis]=coeffs[6]
        # self.KO[axis]=coeffs[7]
        # self.D[axis,:]=coeffs[8:]
        
    def print(self):
        print("S:")
        print(self.S)
        print("KS:")
        print(self.KS)
        print("O:")
        print(self.O)
        print("KO:")
        print(self.KO)
        print("D:")
        print(self.D)


    #Main calibration function
    def calibrate(self,mydata,refdata):
        #refdata is used only for its "true" magentic field
        #Mydata is expected to have all the things to calibrate against
        
        for i in range(3):
            self.calibrate_axis(mydata,refdata,i)
            
    def calibrate_axis(self,mydata,refdata,axis):
        x0=self.get_coeffs(axis)
        lsq_res = least_squares(self.residual_axis, x0, args=(mydata, refdata, axis))
        self.result[axis]=lsq_res
        return lsq_res
    
    def apply(self,data):
        """Apply calibration to get actual B from measured B"""
        result=[]
        n=len(data.time)
        Bm=data.mag
        if data.temp.any():
            T=data.temp
        else:
            T=np.zeros(n)
        
        for i in range(n): #Result is size (3,)
            Ba = np.matmul((self.S+self.KS*T[i]),Bm[i,:]) + (self.O + self.KO*T[i])
            if data.Is.any(): #Apply if there is data to be applied
                I=data.Is
                Ba=Ba-np.matmul(self.D,I)
            result.append(Ba)
        return np.array(result)

    def residual_axis(self,coeffs,mydata,refdata,axis):
        self.update_from_coeffs(coeffs,axis)
        res=abs(self.apply(mydata) - refdata.mag)[:,axis]
        return res
    