#!/usr/bin/env python

import time
import pygame
import gpiozero
import pygame
import numpy
import math

#Indicator to confirm ok to turn motors on
led_pi = gpiozero.LED(21)
for x in range(1, 5):
    led_pi.off()
    time.sleep(0.5)
    led_pi.on()
    time.sleep(0.5)

#Set up controller with pygame
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

#create robot object
robot = gpiozero.Robot(left=(17, 18), right=(27, 22))

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


