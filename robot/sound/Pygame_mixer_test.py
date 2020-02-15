import pygame
import os
import time

pygame.mixer.init()
os.chdir("/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/")
goodbye = pygame.mixer.Sound("time2die.wav")
horn = pygame.mixer.Sound("car_horn.wav")
camera_shutter = pygame.mixer.Sound("camer_shutter.wav")

horn.play()
time.sleep(3)
goodbye.play()
time.sleep(60)
camera_shutter.play()
time.sleep(3)