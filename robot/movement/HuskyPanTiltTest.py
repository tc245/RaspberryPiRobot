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
import math

#Instances
husky=HuskyLensLibrary("I2C","",address=0x32)#huskylens
PT=pantilthat.PanTilt()

#Variables
pan=0 #camera pan angle
tilt=0 # camera tilt angle
x_coords_range = 150 #Range of x coordinates
y_coords_range = 110
pan_range = 75
tilt_range = 75

#Centre the camera
PT.tilt(tilt)
PT.pan(pan)

###########
#Functions#
###########

#Function to determine if object is centred
def is_object_centred(husky_object):
    try:
        x=husky_object.command_request_blocks()[0][0]
        y=husky_object.command_request_blocks()[0][1]
        
        if x not in range(150,170) or y not in range(110,130):
            return False
        
        elif x in range(150,170) and y in range(110,130):
            return True
        
    except IndexError:
        return False
        time.sleep(0.5)

#Function to calculate pan angle
def calculate_pantilt_angle():
    angles = []
    angles[0] = ((math.log(pan_range))/150)*husky.command_request_blocks()[0][0]
    angles[1] = ((math.log(tilt_range))/150)*husky.command_request_blocks()[0][1]
    return angles

#Set-up 
input(""""Place an object in the huskylens camera frame
      and register it using the camera buttons.
      """)

#Main Loop
while True:
    try:
        while is_object_centred(husky):
            print("Object centred in frame")
            time.sleep(1)
        
        while not is_object_centred(husky):
            print("Object NOT centred in frame")
            if husky.command_request_blocks()[0][0] < 150:
                PT.pan(calculate_pantilt_angle()[0])
                print(PT.get_pan())
                time.sleep(0.5)
            
            if husky.command_request_blocks()[0][0] > 170:
                PT.pan(0-calculate_pantilt_angle()[0])
                print(PT.get_pan())
                time.sleep(0.5)
                
            if husky.command_request_blocks()[0][1] < 110:
                PT.tilt(calculate_pantilt_angle()[1])
                print(PT.get_tilt())
                time.sleep(0.5)
            
            if husky.command_request_blocks()[0][1] > 130:
                PT.tilt(calculate_pantilt_angle()[1])
                print(PT.get_tilt())
                time.sleep(0.5)
        
    except Exception as e:
        print(e)
        time.sleep(1)
        