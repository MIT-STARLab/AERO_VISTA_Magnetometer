# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 22:17:56 2021

@author: nickb
"""

import numpy as np

import full_calibration
import file_loader
import os.path
import matplotlib.pyplot as plt
from mag_measurement import Measurement
import copy

def difference_viewer(mes1,mes2,title="Measurement Difference"):
    diff=mes2.mag-mes1.mag
    plt.figure()
    lineObjects = plt.plot(mes2.time, diff, linestyle="None", marker="x")
    plt.legend(iter(lineObjects), ('X', 'Y', 'Z'))
    plt.title(title)
    

#This compares two measurements just for magnetic effects
#No interfering source or temperature effects considered
#This is used with the two RM3100 on magEval
def test1():
    filename=os.path.join('test_files','magEval','magData2','ref.csv')
    
    test_mes, ref_mes = file_loader.RM3100pair(filename)
    
    plt.figure()
    test_mes.plot_B(title="Test Magnetometer Raw Data")
    plt.figure()
    ref_mes.plot_B(title="Reference Magnetometer Raw Data")
    
    difference_viewer(test_mes,ref_mes,title="Difference plot before calibration")
    
    mycal=full_calibration.Calibration()
    mycal.flagPreset("Bonly")
    mycal.calibrate(test_mes,ref_mes)
    resultB=mycal.apply(test_mes)
    
    cald_mes=copy.deepcopy(test_mes)
    cald_mes.mag=resultB
    cald_mes.info="Calibrated measurement"
    
    print("Calibration complete")
    mycal.print()
    
    difference_viewer(cald_mes,ref_mes,title="Difference after calibration")
    
    
#This compares two measurements including all temeprature effects
#This is used with one reference and one test magnetometer on magEval
def test2():
    test_file=os.path.join('test_files','magEval','magData2','test.csv')
    ref_file=os.path.join('test_files','magEval','magData2','ref.csv')
    
    test_mes, ref_mes = file_loader.magEval(test_file,ref_file)
    
    plt.figure()
    test_mes.plot_B(title="Test Magnetometer Raw Data")
    plt.figure()
    ref_mes.plot_B(title="Reference Magnetometer Raw Data")
    
    difference_viewer(test_mes,ref_mes,title="Difference plot before calibration")
    
    mycal=full_calibration.Calibration()
    mycal.flagPreset("allnoI")
    mycal.calibrate(test_mes,ref_mes)
    resultB=mycal.apply(test_mes)
    
    cald_mes=copy.deepcopy(test_mes)
    cald_mes.mag=resultB
    cald_mes.info="Calibrated measurement"
    
    print("Calibration complete")
    mycal.print()
    
    difference_viewer(cald_mes,ref_mes,title="Difference after calibration")
    
def test3():
    path = 'C:\\Users\\nickb\\Documents\\MIT\\Magnetic Calibration\\phone_data\calibration\\'
    test_mes,ref_mes = file_loader.phoneCal(path+"phone_cal_test.csv",path+"phone_cal_ref.csv")
    plt.figure()
    test_mes.plot_B()
    plt.title("Test Measurement")
    plt.figure()
    ref_mes.plot_B()
    plt.title("Reference Measurement")
    
    mycal=full_calibration.Calibration()
    mycal.flagPreset("basic")
    mycal.calibrate(test_mes,ref_mes)
    
    print("Calibration Complete")
    
    
if __name__=="__main__":
    test3()