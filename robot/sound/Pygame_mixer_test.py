import pygame
import os
import time

pygame.mixer.init()
os.chdir("/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/")
goodbye = pygame.mixer.Sound("time2die.wav")
horn = pygame.mixer.Sound("horn.wav")

horn.play()
time.sleep(5)
goodbye.play()
time.sleep(120)
