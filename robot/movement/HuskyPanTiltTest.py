# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 10:36:58 2020

@author: tclemens

Code to test HuskyLens.

Moves pantilt servos so that object in camera frame is always centred in
the frame.

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
interval = 2
pan=0 #camera pan angle
tilt=0 # camera tilt angle
x_coords_range = 160 #Range of x coordinates
y_coords_range = 120 #Range of y coordinates
x_mid = 160 #Middle of x coordinates
y_mid = 120#Middle of y coordinates
x_max = 320#Max of x coordinates
y_max = 240#Max of x coordinates
pan_range = math.log(75)#Max range of motion for pan in log units
tilt_range = math.log(75)#Max range of motion for tilt in log units

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
    angles = ["x": None, "y": None]
    
    x=((pan_range/x_coords_range)*((husky.command_request_blocks()[0][0]-x_max)+x_mid))
    y=((tilt_range/y_coords_range)*((husky.command_request_blocks()[0][1]-y_max)+y_mid))

    pan_current = PT.get_pan()
    tilt_current = PT.get_tilt()

    if x > 0:
        x=(math.exp(x))+pan_current
    
    if y > 0:
        y=(math.exp(y))+tilt_current
        
    elif x < 0:
        x=(0-(math.exp(x)))+pan_current
        
    elif y < 0:
        y=(0-(math.exp(y)))+tilt_current
        
    if x in range(-75, 75):
        angles['x'] = x
    
    elif x not in range(-75,75):
        angles['x'] = pan_current
        
    if y in range(-75, 75):
        angles['y'] = y
    
    elif y not in range(-75,75):
        angles['y'] = tilt_current
        
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
                print("object in left of frame{}".format(calculate_pantilt_angle()['x']))
                print(calculate_pantilt_angle()['x'])
                PT.pan(calculate_pantilt_angle()['x'])
                #print(PT.get_pan())
                time.sleep(interval)
            
            if husky.command_request_blocks()[0][0] > 170:
                print("object in right of frame{}".format(calculate_pantilt_angle()['x']))
                print(calculate_pantilt_angle()['x'])
                PT.pan(calculate_pantilt_angle()['x'])
                #print(PT.get_pan())
                time.sleep(interval)
                
            if husky.command_request_blocks()[0][1] < 110:
                print("object in top half of frame{}".format(calculate_pantilt_angle()['y']))
                print(calculate_pantilt_angle()['y'])
                PT.tilt(calculate_pantilt_angle()['y'])
                #print(PT.get_tilt())
                time.sleep(interval)
            
            if husky.command_request_blocks()[0][1] > 130:
                print("object in bottom half of frame{}".format(calculate_pantilt_angle()['y']))
                print(calculate_pantilt_angle()['y'])
                PT.tilt(calculate_pantilt_angle()['y'])
                #print(PT.get_tilt())
                time.sleep(interval)
        
    except Exception as e:
        print(e)
        time.sleep(1)
        