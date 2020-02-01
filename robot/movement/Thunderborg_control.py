#!/usr/bin/env python

#Stuff still to do:
#Install the text to speak stuff from here: https://www.dexterindustries.com/howto/make-your-raspberry-pi-speak/
#Including installling num2words package using; sudo pip3 install num2words
#Adjust wiring on PI to add another GPIO LED (pin 5)

#Thunderborg board to control robot

import time
import pygame
import gpiozero
import numpy
import math
import os
import pantilthat
import sys
from subprocess import call

sys.path.append('/home/pi/thunderborg')
import ThunderBorg

#Indicators to confirm ok to turn motors on
led1_pi = gpiozero.LED(26)
led2_pi = gpiozero.LED(13)
led1_pi.off()
led2_pi.off()


#Initialise pygame
pygame.init()

#Create instance of the pantilthat class
PT = pantilthat.PanTilt()
#create counter variables for the pantilt
pan = 0
tilt = 0

#Centre the camera
PT.pan(pan)
PT.tilt(tilt)

#disable servo until needed to save power
PT.idle_timeout(2)

#Blinking LEDs to show controller not connected
ready = False
while not ready:
    led1_pi.on()
    led2_pi.on()
    time.sleep(0.5)
    led1_pi.off()
    led2_pi.off()
    time.sleep(0.5)
    pygame.init()
    if pygame.joystick.get_count() == 0:
        pygame.joystick.quit()
    elif pygame.joystick.get_init() == 1 and pygame.joystick.get_count() == 1:
        led1_pi.off()
        led2_pi.off()
        ready = True

#Create joystick object
joystick = pygame.joystick.Joystick(0)
joystick.init()

#Light LEDs to show controller working
led1_pi.on()
led2_pi.on()

#create robot object
#Set-up the thunderborg object
TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x0a
TB.Init()

# Power settings
voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
voltageOut = 7.0                       # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

#create flag object to exit main program loop
done = False

#Constants for text to speak function call
cmd_beg= 'espeak '
cmd_end= ' | aplay /home/pi/RaspberryPiRobot/robot/sound/goodbye.wav  2>/dev/null' # To play back the stored .wav file and to dump the std errors to /dev/null
cmd_out= '--stdout > /home/pi/RaspberryPiRobot/robot/sound/goodbye.wav ' # To store the voice file
goodbye = "i am leaving now robot camera signing off goodbye"

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
                    forward = 0 - joystick.get_axis(1)
                    TB.SetMotors(forward*maxPower)
                
                elif joystick.get_axis(1) < 0: #and backwards
                    backward = 0 - (joystick.get_axis(1)) #To positive values
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

        elif event.type == pygame.JOYHATMOTION: #move the pan tilt servors with d-pad

            if joystick.get_hat(0) == (1, 0):

                if PT.get_pan() > 75 and PT.get_pan() < -75:
                    pan = 0
                    PT.pan(pan)
     
                elif PT.get_pan() <= 75 and PT.get_pan() >= -75
                    pan = PT.get_pan()
                    pan -= 5
                    PT.pan(pan)

            elif joystick.get_hat(0) == (-1, 0):
                
                if PT.get_pan() > 75 and PT.get_pan() < -75:
                    pan = 0
                    PT.pan(pan)
     
                elif PT.get_pan() <= 75 and PT.get_pan() >= -75
                    pan = PT.get_pan()
                    pan += 5
                    PT.pan(pan)


            elif joystick.get_hat(0) == (0, 1):
                
                if PT.get_tilt() > 75 and PT.get_tilt() < -75:
                    tilt = 0
                    PT.tilt(tilt)
     
                elif PT.get_tilt() <= 75 and PT.get_tilt() >= -75
                    tilt = PT.get_tilt()
                    tilt -= 5
                    PT.tilt(tilt)

            elif joystick.get_hat(0) == (0, -1):
                
                if PT.get_tilt() > 75 and PT.get_tilt() < -75:
                    tilt = 0
                    PT.tilt(tilt)
     
                elif PT.get_tilt() <= 75 and PT.get_tilt() >= -75
                    tilt = PT.get_tilt()
                    tilt += 5
                    PT.tilt(tilt)

        elif event.type == pygame.JOYBUTTONDOWN:
             if joystick.get_button(0) == True: #when share pressed quit loop
                 call(["aplay", "/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/car_horn.wav"])

    

#Quit program sequence            
PT.pan(0)
PT.tilt(0)
print(goodbye) #print quit message
goodbye = goodbye.replace(' ', '_') #put in underscores to distinguish words
call([cmd_beg+cmd_out+goodbye+cmd_end], shell=True) #Calls the Espeak TTS Engine to read aloud the Text
time.sleep(5)
led1_pi.off()
led2_pi.off()
os.system("sudo shutdown -h now")                































































                

