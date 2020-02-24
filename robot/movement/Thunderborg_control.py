#!/usr/bin/env python

#Stuff still to do:
#Install the text to speak stuff from here: https://www.dexterindustries.com/howto/make-your-raspberry-pi-speak/
#Including installling num2words package using; sudo pip3 install num2words
#Adjust wiring on PI to add another GPIO LED (pin 5)

#Thunderborg board to control robot

"""Button mapping:
Axis 0 - Left stick horizontal
Axis 1 - Left stick vertical
Axis 2 - Left trigger
Axis 3 - Right stick horizontal
Axis 4 - Right stick vertical
Axis 5 - Right trigger
Button 0 cross
Button 1 circle (camera)
Button 2 triangle (disco mode)
Button 3 square (light)
Button 4 Left Shoulder
Button 5 Right Shoulder
Button 8 Share
Button 9 Options (quit)
Button 10 Playstation
Button 11 Left stick button
Button 12 Right stick button (horn)

Joy hat buttons:
(-1,0) = Left button and move camera left
(1,0) = Right and move camera right
(0,-1) = Down and move camera down
(0,1) = Up and move camera up

Global values
axisUpDown = 1          # Joystick axis to read for up / down position
axisLeftRight = 3       # Joystick axis to read for left / right position
buttonSlow = 4          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 5      # Joystick button number for turning fast (R2)
camera = 1              # Button number for camera shutter
horn = 12               # Button number for Horn
disco = 2               # Button number for disco mode
light = 3               # Button to turn light on and off
quit_button = 9         # Button to quit and shutdown robot
interval = 0.00         # Time between updates in seconds, smaller responds faster but uses more processor time
"""

import time
import pygame
import gpiozero
import numpy
import math
import os
import pantilthat
import sys
from subprocess import call
import picamera
from datetime import datetime

sys.path.append('/home/pi/thunderborg')
import ThunderBorg

#mount NAS
call(["sudo", "mount", "-a"])

#Sound test
#call(["aplay", "/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/car_horn.wav"])

#Indicators to confirm ok to turn motors on
led1_pi = gpiozero.LED(26)
led2_pi = gpiozero.LED(13)
led1_pi.off()
led2_pi.off()

#Create instance of the pantilthat class
PT = pantilthat.PanTilt()
#create counter variables for the pantilt
pan_to = 0
tilt_to = 0
#Set up the camera light
PT.light_mode(pantilthat.WS2812)
PT.light_type(pantilthat.GRBW)

#Centre the camera
PT.pan(pan_to)
PT.tilt(tilt_to)

#disable servo until needed to save power
PT.idle_timeout(2)

#create robot object
#Set-up the thunderborg object
TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x0a
TB.Init()

#create camera object and set up neopixels
camera = picamera.PiCamera()
camera.rotation = 180

# Power settings
voltageIn = 12.0                        # Total battery voltage to the ThunderBorg
voltageOut = 7.0                       # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Show battery monitoring settings
battMin, battMax = TB.GetBatteryMonitoringLimits()
battCurrent = TB.GetBatteryReading()
print 'Battery monitoring settings:'
print '    Minimum  (red)     %02.2f V' % (battMin)
print '    Half-way (yellow)  %02.2f V' % ((battMin + battMax) / 2)
print '    Maximum  (green)   %02.2f V' % (battMax)
print
print '    Current voltage    %02.2f V' % (battCurrent)
print

# Setup pygame and wait for the joystick to become available
TB.MotorsOff()
TB.SetLedShowBattery(False)
TB.SetLeds(0,0,1)
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()
#and the pygame mixer
pygame.mixer.init()
os.chdir("/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/")
goodbye = pygame.mixer.Sound("time2die.wav")
horn = pygame.mixer.Sound("car_horn.wav")
camera_shutter = pygame.mixer.Sound("camera_shutter.wav")

#Blinking LEDs to show controller not connected
ready = False
while not ready:
    TB.SetLeds(0,0,1)
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
TB.SetLedShowBattery(True)
ledBatteryMode = True

#Light LEDs to show controller working
led1_pi.on()
led2_pi.on()

#Joystick settings
#Axes
axisUpDown = 1          # Joystick axis to read for up / down position
axisLeftRight = 3       # Joystick axis to read for left / right position
#buttons
buttonSlow = 4          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 5      # Joystick button number for turning fast (R2)
camera_button = 1       # Button number for camera shutter
horn_button = 12        # Button number for Horn
disco_button = 2        # Button number for disco mode
light_button = 3        # Button to turn light on and off
quit_button = 9         # Button to quit and shutdown robot
#Other settings
interval = 0.00         # Time between updates in seconds, smaller responds faster but uses more processor time

#create flag object to exit main program loop
done = False

#other flag variables
PT.set_all(0, 0, 0, 0)
PT.show()
light_on = False

# -------- Main Program Loop -----------
while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.JOYBUTTONDOWN:
            
            if joystick.get_button(quit_button) == True: #when share pressed quit loop
                print("User Quit")
                done = True
                

            elif joystick.get_button(horn_button): #Horn
                horn.play()
                print("horn button pressed")


            elif joystick.get_button(camera_button): #camera and 
                os.chdir("/home/pi/Pictures")
                d = datetime.now() #Collect time stamp when picture taken
                year = str(d.year)
                month = str(d.month)
                day = str(d.day)
                hour = str(d.hour)
                mins = str(d.minute)
                secs = str(d.second)
                camera_shutter.play() #shutter noise
                camera.capture("{0}_{1}_{2}_{3}_{4}_{5}.jpeg".format(day, month, year, hour, mins, secs), format="jpeg") #Image capture

            elif joystick.get_button(light_button): #Light on and off
                if light_on:
                    PT.set_all(0, 0, 0, 0)
                    PT.show()
                    light_on = False

                elif light_on == False:
                    PT.set_all(255, 255, 255, 255)
                    PT.show()
                    light_on = True

        elif event.type == pygame.JOYAXISMOTION: #Grab forward axis values
            
            if joystick.get_axis(axisUpDown) != 0:
                
                if joystick.get_axis(axisUpDown) > 0:
                    forward = 0 - joystick.get_axis(1)
                    TB.SetMotors(forward*maxPower)
                
                elif joystick.get_axis(axisUpDown) < 0: #and backwards
                    backward = 0 - (joystick.get_axis(1)) #To positive values
                    TB.SetMotors(backward*maxPower)
            
            elif joystick.get_axis(axisLeftRight) !=0: #axis values for robot left
                
                if joystick.get_axis(axisLeftRight) < 0:
                    rightMotorForward = joystick.get_axis(axisLeftRight)
                    leftMotorReverse = (-1) + (1-joystick.get_axis(axisLeftRight))
                    TB.SetMotor2(leftMotorForward*maxPower)
                    TB.SetMotor1(rightMotorReverse*maxPower)                    
                
                elif joystick.get_axis(axisLeftRight) > 0: #and right
                    rightMotorReverse = joystick.get_axis(axisLeftRight)
                    leftMotorForward = 1 - (1 + joystick.get_axis(axisLeftRight))
                    TB.SetMotor2(leftMotorReverse*maxPower)
                    TB.SetMotor1(rightMotorForward*maxPower) 
                    
            elif joystick.get_axis(axisUpDown) == 0 or joystick.get_axis(axisLeftRight) == 0:
                TB.MotorsOff() #stop robot with axis values = 0

        elif event.type == pygame.JOYHATMOTION: #move the pan tilt servors with d-pad

            if joystick.get_hat(0) == (1, 0):

                if PT.get_pan() > 75 or PT.get_pan() < -75:
                    pan = 0
                    print(pan)
                    PT.pan(pan)
     
                elif PT.get_pan() <= 75 or PT.get_pan() >= -75:
                    pan = PT.get_pan()
                    pan -= 5
                    print(pan)
                    PT.pan(pan)

            elif joystick.get_hat(0) == (-1, 0):
                
                if PT.get_pan() > 75 or PT.get_pan() < -75:
                    pan = 0
                    print(pan)
                    PT.pan(pan)
     
                elif PT.get_pan() <= 75 or PT.get_pan() >= -75:
                    pan = PT.get_pan()
                    pan += 5
                    print(pan)
                    PT.pan(pan)


            elif joystick.get_hat(0) == (0, 1):
                
                if PT.get_tilt() > 75 or PT.get_tilt() < -75:
                    tilt = 0
                    print(tilt)
                    PT.tilt(tilt)
     
                elif PT.get_tilt() <= 75 or PT.get_tilt() >= -75:
                    tilt = PT.get_tilt()
                    tilt -= 5
                    print(tilt)
                    PT.tilt(tilt)

            elif joystick.get_hat(0) == (0, -1):
                
                if PT.get_tilt() > 75 or PT.get_tilt() < -75:
                    tilt = 0
                    print(tilt)
                    PT.tilt(tilt)
     
                elif PT.get_tilt() <= 75 or PT.get_tilt() >= -75:
                    tilt = PT.get_tilt()
                    tilt += 5
                    print(tilt)
                    PT.tilt(tilt)

    

#Quit program sequence            
PT.pan(0)
PT.tilt(0)
print(goodbye) #print quit message
goodbye_length=goodbye.get_length()
goodbye.play()
time.sleep(goodbye_length)
led1_pi.off()
led2_pi.off()
os.system("sudo shutdown -h now")              































































                

