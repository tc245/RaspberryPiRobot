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
sys.path.append('/home/pi/thunderborg')
import ThunderBorg3 as ThunderBorg
import gpiozero

#disable servo until needed to save power
PT.idle_timeout(2)

#create robot object
#Set-up the thunderborg object
TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x0a
TB.Init()

#Instances
#Ai camera
husky=HuskyLensLibrary("I2C","",address=0x32)#huskylens

#Pan tilt
PT=pantilthat.PanTilt()
PT.idle_timeout(2)#disable servo until needed to save power

#Set-up the thunderborg object
TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x0a
TB.Init()

#Indicators to confirm ok to turn motors on
led1_pi = gpiozero.LED(26)
led2_pi = gpiozero.LED(13)
led1_pi.on()
led2_pi.on()


#Variables
interval = 0.1
pan=0 #camera pan angle
tilt=0 # camera tilt angle
x_coords_range = 160 #Range of x coordinates
y_coords_range = 120 #Range of y coordinates
x_mid = 160 #Middle of x coordinates
y_mid = 120#Middle of y coordinates
x_max = 320#Max of x coordinates
y_max = 240#Max of x coordinates
pan_range = 75 #Max range of motion for pan in log units
tilt_range = 75 #Max range of motion for tilt in log units
Xtarget = 0
Ytarget = 0
Yerror = 0
Xerror = 0
KP_x = 0.09
KP_y = 0.09
X_prev_error = 0
T_prev_error = 0

# Power settings
voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
voltageOut = 7.0                       # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

#Centre the camera
PT.tilt(tilt)
PT.pan(pan)

###########
#Functions#
###########

#Function to determine if object is centred
def is_object_centred(husky_object):
    try:
        x=Xtarget-husky_object.command_request_blocks()[0][0]
        y=husky_object.command_request_blocks()[0][1]-Ytarget
        
        if x not in range(-10,10) or y not in range(-10,10):
            return False
        
        elif x in range(-10,10) and y in range(-10,10):
            return True
        
    except IndexError:
        return False

#Set-up
input(""""Align your face with the camera and register it using the 
      camera buttons.""")

name = input("Type your name and press enter") 

#Main Loop
while True:
    try:
        Xerror = Xtarget - (husky.command_request_blocks()[0][0]-x_mid)
        Yerror = (husky.command_request_blocks()[0][1]-y_mid) - Ytarget
        print("Y error: {}, X error: {}".format(Yerror, Xerror))
        
        new_y = (KP_y * Yerror)+PT.get_tilt()
        new_x = (KP_x * Xerror)+PT.get_pan()
        print("Y new: {}, X new: {}".format(new_y, new_x))
        
        PT.pan(new_x)
        PT.tilt(new_y)
    
    except Exception as e:
        print(e)
    
    time.sleep(interval)