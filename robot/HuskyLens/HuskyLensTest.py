# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 18:18:45 2020

@author: tclemens
"""

import sys
sys.path.append('/home/pi/HUSKYLENSPython/HUSKYLENS/')
from huskylensPythonLibrary import HuskyLensLibrary

# Initlialize the HuskyLens
test = HuskyLensLibrary("I2C","",address=0x32)
print("First request a knock: {}".format(test.command_request_knock()))

# Change to facial recognition algorhtim
test.command_request_algorthim("ALGORITHM_FACE_RECOGNITION")

"""Other commands are:
command_request_algorthim(ALG_NAME)
    * ALG_NAME is a string whose value can be the following
        "ALGORITHM_OBJECT_TRACKING"
        "ALGORITHM_FACE_RECOGNITION"
        "ALGORITHM_OBJECT_RECOGNITION"
        "ALGORITHM_LINE_TRACKING"
        "ALGORITHM_COLOR_RECOGNITION"
        "ALGORITHM_TAG_RECOGNITION"
        "ALGORITHM_OBJECT_CLASSIFICATION"
"""

# Display a simple menu where you can call every function in a loop!
ex=1
print("""
        Menu options:
        1) command_request()
        2) command_request_blocks()
        3) command_request_arrows()
        4) command_request_learned()
        5) command_request_blocks_learned()
        6) command_request_arrows_learned()
        7) command_request_by_id() ***format 7 ID_VAL***
        8) command_request_blocks_by_id() ***format 8 ID_VAL***
        9) command_request_arrows_by_id() ***format 9 ID_VAL***
        10) Exit
        """)
while(ex==1):
    v=input("Enter cmd number:")
    numEnter=v
    if(numEnter=="10"):
        ex=0
    v=int(v[0])
    if(v==1):
        print(test.command_request())
    elif(v==2):
        print(test.command_request_blocks())
    elif(v==3):
        print(test.command_request_arrows())
    elif(v==4):
        print(test.command_request_learned())
    elif(v==5):
        print(test.command_request_blocks_learned())
    elif(v==6):
        print(test.command_request_arrows_learned())
    elif(v==7):
        print(test.command_request_by_id(int(numEnter[2:])))
    elif(v==8):
        print(test.command_request_blocks_by_id(int(numEnter[2:])))
    elif(v==9):
        print(test.command_request_arrows_by_id(int(numEnter[2:])))