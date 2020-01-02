#!/usr/bin/env python

import time
import pygame
import gpiozero
import numpy
import math
import os

#Indicator to confirm ok to turn motors on
led_pi = gpiozero.LED(21)

#Initialise pygame
pygame.joystick.init()

#Blinking LEDs to show controller not connected
ready = True
while not ready:
    led_pi.on()
    time.sleep(0.5)
    led_pi.off()
    time.sleep(0.5)

#Set up pygame and the controller    
while not ready:
    if pygame.joystick.get_init == 1 and pygame.joystick.get_count == 0:
        pygame.joystick.quit()
        time.sleep
        pygame.joystick.init()
    elif pygame.joystick.get_init == 1 and pygame.joystick.get_count == 1:
        led_pi.on()
        ready = True

print("got to the end!")
  
