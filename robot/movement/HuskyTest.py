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
input("Place an object in the centre of the huskylens camera")
xb=husky.command_request()[0][0]
yb=husky.command_request()[0][1]

while True:
    try:
        if not husky.command_request_blocks():
            print("No objects in camera")
        
        elif husky.command_request_blocks():
            
            if husky.command_request()[0][0] < xb-5:
                print("Robot pointing right")
        
            elif husky.command_request()[0][0] > xb+5:
                print("Robot pointing left")
            
            elif husky.command_request()[0][0] in range((xb-5), (xb+5)):
                print("Robot pointing ahead")
        
        time.sleep(0.2)
        
    except IndexError:
        print("No objects in camera")
        
    
