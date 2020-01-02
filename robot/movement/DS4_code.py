#!/usr/bin/env python

import time
import pygame
import gpiozero
import numpy
import math
import os

#Indicator to confirm ok to turn motors on
led_pi = gpiozero.LED(21)

#Set up pygam and the controller
ready = False
while not ready:
    pygame.joystick.init() #initialise joystick module
    if pygame.joystick.get_count() > 0:
        ready = True
    elif pygame.joystick.get_count() == 0: ##Blnk LED to signal controller and motors are ready to turn on
        led_pi.on()
        time.sleep(0.5)
        led_pi.off()
        time.sleep(0.5)
        pygame.joystick.quit()        
    
#set up controller
joystick = pygame.joystick.Joystick(0)
joystick.init()

#Light LED to show controller working
led_pi.on()

#create robot object
robot = gpiozero.Robot(left=(18, 17), right=(22, 27))

#create flag object to exit while loop below
done = False

# -------- Main Program Loop -----------
while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(9) == True: #when share pressed quit loop
                print("User Quit")
                done = True
                os.system("sudo shutdown -h now")
        elif event.type == pygame.JOYAXISMOTION: #Grab forward axis values 
            if joystick.get_axis(1) != 0:
                if joystick.get_axis(1) > 0:
                    forward = joystick.get_axis(1)
                    robot.forward(forward)
                elif joystick.get_axis(1) < 0: #and backwards
                    backward = math.sqrt(joystick.get_axis(1)**2) #To positive values
                    robot.backward(backward)
            elif joystick.get_axis(3) !=0: #axis values for robot left
                if joystick.get_axis(3) > 0:
                    left = joystick.get_axis(3)
                    robot.left(left)
                elif joystick.get_axis(3) < 0: #and right
                    right = math.sqrt(joystick.get_axis(3)**2)
                    robot.right(right)
            elif joystick.get_axis(1) == 0 or joystick.get_axis(3) == 0:
                robot.stop() #stop robot with axis values = 0


