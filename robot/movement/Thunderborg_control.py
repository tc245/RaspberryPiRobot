#!/usr/bin/env python

#Thunderborg board to control robot

import time
import pygame
import gpiozero
import numpy
import math
import os
import pantilthat
import sys

sys.path.append('/home/pi/thunderborg')
import ThunderBorg

#Indicator to confirm ok to turn motors on
led_pi = gpiozero.LED(26)

#Initialise pygame
pygame.init()

#Blinking LEDs to show controller not connected
ready = False
while not ready:
    led_pi.on()
    time.sleep(0.5)
    led_pi.off()
    time.sleep(0.5)
    pygame.init()
    if pygame.joystick.get_count() == 0:
        pygame.joystick.quit()
    elif pygame.joystick.get_init() == 1 and pygame.joystick.get_count() == 1:
        led_pi.on()
        ready = True

#Create joystick object
joystick = pygame.joystick.Joystick(0)
joystick.init()

#Light LED to show controller working
led_pi.on()

#create robot object
#Set-up the thunderborg object
TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x0a
TB.Init()

# Power settings
voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
voltageOut = 7.5                       # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)



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
                    TB.SetMotors(forward*maxPower)
                elif joystick.get_axis(1) < 0: #and backwards
                    backward = joystick.get_axis(1) #To positive values
                    TB.SetMotors(backward*maxPower)
            elif joystick.get_axis(3) !=0: #axis values for robot left
                if joystick.get_axis(3) > 0:
                    leftMotorForward = joystick.get_axis(3)
                    rightMotorReverse = (-1) + (1-joystick.get_axis(3))
                    TB.SetMotor1(leftMotorForward*maxPower)
                    TB.SetMotor2(rightMotorReverse*maxPower)                    
                elif joystick.get_axis(3) < 0: #and right
                    leftMotorReverse = joystick.get_axis(3)
                    rightMotorForward = 1 - (1 + joystick.get_axis(3))
                    TB.SetMotor1(leftMotorReverse*maxPower)
                    TB.SetMotor2(rightMotorForward*maxPower) 
            elif joystick.get_axis(1) == 0 or joystick.get_axis(3) == 0:
                TB.MotorsOff() #stop robot with axis values = 0
