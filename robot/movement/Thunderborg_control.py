#!/usr/bin/env python

#Stuff still to do:
#Install the text to speak stuff from here: https://www.dexterindustries.com/howto/make-your-raspberry-pi-speak/
#Including installling num2words package using; sudo pip3 install num2words
#Adjust wiring on PI to add another GPIO LED (pin 5)

"""Button mapping:
Axis 0 - Left stick horizontal
Axis 1 - Left stick vertical
Axis 2 - Right stick horizontal
Axis 3 - Left trigger
Axis 4 -Right stick horizontal
Axis 5 - Right stick vertical
Axis 6 - Right trigger

Button 0 cross
Button 1 circle
Button 2 triangle
Button 3 square
Button 4 Left Shoulder
Button 5 Right Shoulder
Button 8 Share
Button 9 Options
Button 10 Playstation
Button 11 Left stick button
Button 12 Right stick button

Joy hat buttons:

(-1,0) = Left button and move camera left
(1,0) = Right and move camera right
(0,-1) = Down and move camera down
(0,1) = Up and move camera up
"""

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
import colorsys

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

#Light LEDs to show controller working
led1_pi.on()
led2_pi.on()

#Create joystick object
joystick = pygame.joystick.Joystick(0)
joystick.init()
TB.SetLedShowBattery(True)
ledBatteryMode = True

#Joystick settings
axisUpDown = 1          # Joystick axis to read for up / down position
axisLeftRight = 4       # Joystick axis to read for left / right position
buttonSlow = 4          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 5      # Joystick button number for turning fast (R2)
camera = 1              # Button number for camera shutter
horn = 12               # Button number for Horn
disco = 2               # Button number for disco mode
light = 1               # Button to turn light on and off
quit_button = 9         # Button to quit and shutdown robot
interval = 0.00         # Time between updates in seconds, smaller responds faster but uses more processor time

#create flag object to exit main program loop
done = False

#Constants for text to speak function call
cmd = 'espeak '
errors = ' 2>/dev/null' # To play back the stored .wav file and to dump the std errors to /dev/null
options = ' -s 120 -v f4 en-sc -p 65 -a 30'
#Different messages
goodbye = "I've seen things you people wouldn't believe. Attack ships on fire off the shoulder of Orion. I watched C-beams glitter in the dark near the Tannhowser Gate. All those moments will be lost in time, like tears in rain. Time to die."
goodbye = goodbye.replace(' ', '_') 
wrong_button = "sorry, this button is not mapped. try another one"
wrong_button = wrong_button.replace(' ', '_') 

# -------- Main Program Loop -----------
while not done:
    driveLeft = 0.0
    driveRight = 0.0
    upDown = 0.0
    leftRight = 0.0
    hadEvent = False
    take_photo = False
    disco_mode = False
    horn_on = False
    cam_up = False
    cam_down = False
    cam_left = False
    Cam_right = False
    unmapped_button = False
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    # Get the latest events from the system
    events = pygame.event.get()
    for event in events: # User did something.
        if joystick.get_button(quit_button): #when share pressed quit loop
                print("User Quit")
                done = True
        elif event.type == pygame.JOYBUTTONDOWN:
            # A button on the joystick just got pushed down
            hadEvent = True
        elif event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved
            hadEvent = True
        elif event.type == pygame.JOYHATMOTION:
            # A d pad button was pushed
            hadEvent = True
        if hadEvent:
            # Read axis positions (-1 to +1)
            upDown = joystick.get_axis(axisUpDown)
            leftRight = joystick.get_axis(axisLeftRight)
            # Apply steering speeds
            if not joystick.get_button(buttonFastTurn):
                leftRight *= 0.5
            # Determine the drive power levels
            driveLeft = -upDown
            driveRight = -upDown
            if leftRight < -0.05:
                # Turning left
                driveLeft *= 1.0 + (2.0 * leftRight)
            elif leftRight > 0.05:
                # Turning right
                driveRight *= 1.0 - (2.0 * leftRight)
            # Check for button presses
            if joystick.get_button(buttonSlow):
                driveLeft *= slowFactor
                driveRight *= slowFactor
            elif joystick.get_button(camera):
                take_photo = True
            elif joystick.get_button(disco):
                disco_mode = True
            elif joystick.get_button(light):
                if light_on = True:
                    light_on = False
                elif light_on = False:
                    light_on = True
            elif joystick.get_button(horn):
                horn_on = True
            # Check for joy hat presses
            if joystick.get_hat(0) == (1, 0):
                cam_right = True
            elif joystick.get_hat(0) == (-1, 0):
                cam_left = True
            elif joystick.get_hat(0) == (0, 1):
                cam_up = True
            elif joystick.get_hat(0) == (0, -1):
                cam_down == True                
            else: #Calls the Espeak TTS Engine to read aloud unmapped button text
                unmapped_button = True

            #Do the actions!
                
            # Set the motors to the new speeds
            TB.SetMotor1(driveRight * maxPower)
            TB.SetMotor2(driveLeft * maxPower)
            # Sound horn
            if horn_on:
                call(["aplay", "/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/car_horn.wav"])
            #Turn on disco mode
            if disco_mode:
                pygame.event.clear()
                while disco_mode:
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
                    events = pygame.event.get()
                    for event in events: # User did something.
                        if event.type == pygame.JOYBUTTONDOWN:
                            disco_mode == False                
            #Take a photo
            if take_photo:
                os.chdir("/home/pi/Pictures")
                d = datetime.now()
                year = str(d.year)
                month = str(d.month)
                day = str(d.day)
                hour = str(d.hour)
                mins = str(d.minute)
                call(["aplay", "/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/camera_shutter.wav"])
                camera.capture("{0}_{1}_{2}_{3}_{4}.jpeg".format(day, month, year, hour, mins), format="jpeg")
            #Turn light on
            if light_on:
                PT.set_all(255, 255, 255, 255)
                PT.show()
            if not light_on:
                PT.set_all(0, 0, 0, 0)
                PT.show()
            #Move the camera
            ## Right and left
            if cam_right or cam_left and PT.get_pan() not in range(-75,75):
                pan_to = PT.get_pan
                PT.pan(pan_to)
            elif cam_right and PT.get_pan() in range(-75,75):
                pan_to = PT.get_pan()+5
                PT.pan(pan_to)
            elif cam_left and PT.get_pan() in range(-75,75):
                pan_to = PT.get_pan()-5
                PT.pan(pan_to)
            ##Up and down
            if cam_up or cam_down and PT.get_tilt() not in range(-75,75):
                tilt_to = PT.get_tilt
                PT.tilt(tilt_to)
            elif cam_up and PT.get_tilt() in range(-75,75):
                tilt_to = PT.get_tilt()+5
                PT.tilt(tilt_to)
            elif cam_down and PT.get_tilt() in range(-75,75):
                tilt_to = PT.get_tilt()-5
                PT.tilt(tilt_to) 
            # Unmapped button
            if unmapped_button:
                   call([cmd+wrong_button+options+errors], shell=True)
                   
        # Wait for the interval period
        time.sleep(interval)
    # Disable all drives
    TB.MotorsOff()

#Quit program sequence            
PT.pan(0)
PT.tilt(0)
print(goodbye) #print quit message
call([cmd+goodbye+options+errors], shell=True) #Calls the Espeak TTS Engine to read aloud the Text
time.sleep(5)
led1_pi.off()
led2_pi.off()
os.system("sudo shutdown -h now")                































































                

