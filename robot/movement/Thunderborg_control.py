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
import picamera
from datetime import datetime

sys.path.append('/home/pi/thunderborg')
import ThunderBorg

#mount NAS
call(["sudo", "mount", "-a"])

#Sound test
call(["aplay", "/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/car_horn.wav"])

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
#Set up the camera light
PT.light_mode(pantilthat.WS2812)
PT.light_type(pantilthat.GRBW)

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

#create camera object and set up neopixels
camera = picamera.PiCamera()
camera.rotation = 180

#Light on flag
light=False

#Disco flag!
disco = False

#Flag to exit horn loop
horn = False

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
cmd = 'espeak '
errors = ' 2>/dev/null' # To play back the stored .wav file and to dump the std errors to /dev/null
#Different messages
goodbye = "i am leaving now, robot camera signing off, goodbye"
goodbye = goodbye.replace(' ', '_') 
wrong_button = "sorry, this button is not mapped. try another one"
wrong_button = wrong_button.replace(' ', '_') 

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
                
            elif joystick.get_button(12): #Horn
                call(["aplay", "/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/car_horn.wav"])
                
            elif joystick.get_button(1): #camera and shutter noise
                os.chdir("/home/pi/Pictures")
                d = datetime.now()
                year = str(d.year)
                month = str(d.month)
                day = str(d.day)
                hour = str(d.hour)
                mins = str(d.minute)
                call(["aplay", "/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/camera_shutter.wav"])
                camera.capture("{0}_{1}_{2}_{3}_{4}.jpeg".format(day, month, year, hour, mins), format="jpeg")

            elif joystick.get_button(11): #Light on and off
                if light:
                    PT.set_all(0, 0, 0, 0)
                    PT.show()
                    light = False

                elif light == False:
                    PT.set_all(255, 255, 255, 255)
                    PT.show()
                    light = True

            elif joystick.get_button(11): #Disco mode!
                disco = True
                while disco:
                    for event in pygame.event.get(): # User did something.
                        if event.type == pygame.JOYBUTTONDOWN:
                            if joystick.get_button(11):
                                disco = False
                    t = time.time()
                    b = (math.sin(t * 2) + 1) / 2
                    b = int(b * 255.0)
                    t = round(time.time() * 1000) / 1000
                    a = round(math.sin(t) * 90)
                    PT.pan(int(a))
                    PT.tilt(int(a))
                    r, g, b = [int(x*255) for x in  colorsys.hsv_to_rgb(((t*100) % 360) / 360.0, 1.0, 1.0)]
                    PT.set_all(r, g, b)
                    PT.show()
                    time.sleep(0.04)
                
            else:
                call([cmd+wrong_button+errors], shell=True) #Calls the Espeak TTS Engine to read aloud the Text

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
     
                elif PT.get_pan() <= 75 and PT.get_pan() >= -75:
                    pan = PT.get_pan()
                    pan -= 5
                    PT.pan(pan)

            elif joystick.get_hat(0) == (-1, 0):
                
                if PT.get_pan() > 75 and PT.get_pan() < -75:
                    pan = 0
                    PT.pan(pan)
     
                elif PT.get_pan() <= 75 and PT.get_pan() >= -75:
                    pan = PT.get_pan()
                    pan += 5
                    PT.pan(pan)


            elif joystick.get_hat(0) == (0, 1):
                
                if PT.get_tilt() > 75 and PT.get_tilt() < -75:
                    tilt = 0
                    PT.tilt(tilt)
     
                elif PT.get_tilt() <= 75 and PT.get_tilt() >= -75:
                    tilt = PT.get_tilt()
                    tilt -= 5
                    PT.tilt(tilt)

            elif joystick.get_hat(0) == (0, -1):
                
                if PT.get_tilt() > 75 and PT.get_tilt() < -75:
                    tilt = 0
                    PT.tilt(tilt)
     
                elif PT.get_tilt() <= 75 and PT.get_tilt() >= -75:
                    tilt = PT.get_tilt()
                    tilt += 5
                    PT.tilt(tilt)

    

#Quit program sequence            
PT.pan(0)
PT.tilt(0)
print(goodbye) #print quit message
call([cmd+goodbye+errors], shell=True) #Calls the Espeak TTS Engine to read aloud the Text
time.sleep(5)
led1_pi.off()
led2_pi.off()
os.system("sudo shutdown -h now")                































































                

