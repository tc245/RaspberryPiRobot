# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 10:36:58 2020

@author: tclemens

Code to test HuskyLens.

Prints to console whether object has moved in frame (in all dimensions)

"""

import sys
sys.path.append('/home/pi/HUSKYLENSPython/HUSKYLENS/')
from huskylensPythonLibrary import HuskyLensLibrary
import time

#Husky object
husky=HuskyLensLibrary("I2C","",address=0x32)

#Get baseline values
xb=husky.command_request()[0][0]
yb=husky.command_request()[0][1]

while True:
    if not husky.command_request_blocks():
        print("No objects in camera")
    
    elif husky.command_request_blocks() == True:
        
        if husky.command_request()[0][0] < xb-5:
            print("Robot pointing right")
    
        elif husky.command_request()[0][0] > xb+5:
            print("Robot pointing left")
        
        else:
            print("Robot pointing ahead")
    
    time.sleep(0.2)    
    
