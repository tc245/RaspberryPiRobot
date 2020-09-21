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

#Clear the lights
PT.light_mode(pantilthat.WS2812)
PT.light_type(pantilthat.GRBW)
PT.set_all(0, 0, 0, 0)
PT.show()

time.sleep(2)

