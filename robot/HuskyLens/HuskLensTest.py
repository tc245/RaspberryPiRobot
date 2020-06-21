# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 18:18:45 2020

@author: tclemens
"""

import sys
sys.path.append('/home/pi/HUSKYLENSPython')
from huskylensPythonLibrary import HuskyLensLibrary

husky= HuskyLensLibrary("I2C","",address=0x32)

print(husky.command_request_knock()) 