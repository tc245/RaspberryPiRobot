#!/usr/bin/python3

# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 11:27:08 2020

@author: tclemens
"""

import pantilthat
import time

#Pan tilt
PT=pantilthat.PanTilt()
#Centre the camera
PT.tilt(-15)
PT.pan(0)

time.sleep(2)

