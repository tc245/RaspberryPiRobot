#!/usr/bin/env python

import time
import gpiozero
import numpy
import math

#Indicator to confirm ok to turn motors on
led_pi = gpiozero.LED(21)
led_pi.off()
led_pi.blink(on_time=0.5, off_time=0.5, n=10)
time.sleep(2)
led_pi.on()
time.sleep(10)
led_pi.off()
