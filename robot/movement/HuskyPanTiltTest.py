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

#Function to determine if object is centred
def is_object_centred(husky_object):
    x=husky_object.command_request()[0][0]
    y=husky_object.command_request()[0][1]
    
    if x in range(150,170) and y in range(110,130):
        return True
    
    elif x not in range(150,170) and y not in range(110,130):
        return False

#Get baseline values
input("Place an object in the centre of the huskylens camera")

while True:
    try:
        center=is_object_centred(husky)
        print(center)
        time.sleep(0.5)
        
    except IndexError:
        print("No objects in camera")
        

    
    
    
        
    