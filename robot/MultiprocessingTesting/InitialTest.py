# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 17:35:09 2020

@author: tclemens
"""

import gpiozero
import time
import multiprocessing

led1_pi = gpiozero.LED(26)
led2_pi = gpiozero.LED(13)
led1_pi.off()
led2_pi.off()

def LED_pattern():
    while True:
        led1_pi.off()
        led2_pi.off()
        time.sleep(0.5)
        led1_pi.on()
        led2_pi.on()
        time.sleep(0.5)
        
# Set up neopixel processes - neopixel code is in ~/RedBoard/neopixels.py   
p1 = multiprocessing.Process(target = LED_pattern)

#main loop

n = 0
while True:
    if n < 10:
        print("Loop number: {}".format(n))
        n += 1
        time.sleep(5)
    elif n >= 10 and n < 20:
        print("Loop number: {}".format(n))
        n += 1
        if p1.is_alive():
            pass
        if not p1.is_alive():
            p1.start() 
        time.sleep(5)
    elif n >= 20 and n < 30:
        print("Loop number: {}".format(n))
        n += 1
        if p1.is_alive():
            p1.terminate()
        if not p1.is_alive():
            pass 
        time.sleep(5)
    elif n >= 30:
        print("Loop number: {}".format(n))
        n += 1
        if p1.is_alive():
            p1.terminate()
        if not p1.is_alive():
            p1.start()  
        time.sleep(5)
        
        
        
