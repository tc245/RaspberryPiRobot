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
interval = 1
pan=0 #camera pan angle
tilt=0 # camera tilt angle
x_coords_range = 160 #Range of x coordinates
y_coords_range = 120
x_mid = 160
y_mid = 120
x_max = 320
y_max = 240
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
    angles.append(((math.log(pan_range))/x_coords_range)*((husky.command_request_blocks()[0][0]-x_max)+x_mid))
    angles.append(((math.log(tilt_range))/y_coords_range)*((husky.command_request_blocks()[0][1]-y_max)+y_mid))
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
            time.sleep(interval)
        
        while not is_object_centred(husky):
            print("Object NOT centred in frame")
            if husky.command_request_blocks()[0][0] < 150:
                print("object in left of frame{}".format(calculate_pantilt_angle()[0]))
                PT.pan(calculate_pantilt_angle()[0])
                print(PT.get_pan())
                time.sleep(interval)
            
            if husky.command_request_blocks()[0][0] > 170:
                print("object in right of frame{}".format(calculate_pantilt_angle()[0]))
                PT.pan(calculate_pantilt_angle()[0])
                print(PT.get_pan())
                time.sleep(interval)
                
            if husky.command_request_blocks()[0][1] < 110:
                print("object in top half of frame{}".format(calculate_pantilt_angle()[1]))
                PT.tilt(calculate_pantilt_angle()[1])
                print(PT.get_tilt())
                time.sleep(interval)
            
            if husky.command_request_blocks()[0][1] > 130:
                print("object in bottom half of frame{}".format(calculate_pantilt_angle()[1]))
                PT.tilt(calculate_pantilt_angle()[1])
                print(PT.get_tilt())
                time.sleep(interval)
        
    except Exception as e:
        print(e)
        time.sleep(1)
        