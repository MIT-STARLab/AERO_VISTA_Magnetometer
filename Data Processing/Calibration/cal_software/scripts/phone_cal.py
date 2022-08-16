# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 13:07:23 2022

@author: nickb
"""

from calibration_test import *


path = 'C:\\Users\\nickb\\Documents\\MIT\\Magnetic Calibration\\phone_data\calibration\\'
test_mes,ref_mes = phoneCal(path+"phone_cal_test.csv",path+"phone_cal_ref.csv")
plt.figure()
test_mes.plot_B()
plt.title("Test Measurement")
plt.figure()
ref_mes.plot_B()
plt.title("Reference Measurement")