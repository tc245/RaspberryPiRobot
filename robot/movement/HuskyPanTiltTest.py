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
import pantilthat

#Instances
husky=HuskyLensLibrary("I2C","",address=0x32)#huskylens
PT=pantilthat.PanTilt()

#Centre the camera
PT.tilt(0)
PT.pan(0)

#Function to determine if object is centred
def is_object_centred(husky_object):
    try:
        x=husky_object.command_request()[0][0]
        y=husky_object.command_request()[0][1]
        
        if x not in range(150,170) or y not in range(110,130):
            return False
        
        elif x in range(150,170) and y in range(110,130):
            return True
        
    except IndexError:
        return False
        time.sleep(0.5)

#Get baseline values
input(""""Place an object in the huskylens camera frame
      and register it using the camera buttons.
      """)

#Main Loop
try:
    while True:
        while is_object_centred(husky):
            pass
        
        while not is_object_centred(husky):
            if husky.command_request()[0][0] < 150:
                PT.pan(PT.get_pan()+1)
            
            if husky.command_request()[0][0] >170:
                PT.pan(PT.get_pan()-1)
                
            if husky.command_request()[0][1] < 110:
                PT.pan(PT.get_tilt()+1)
            
            if husky.command_request()[0][1] >130:
                PT.pan(PT.get_tilt()-1)
        
except IndexError:
    print("No object in frame")
        