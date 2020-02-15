import pygame
import os

pygame.mixer.init()
os.chdir("/home/pi/RaspberryPiRobot/robot/sound/SoundsRepository/")
goodbye = pygame.mixer.Sound("time2die.wav")
horn = pygame.mixer.Sound("horn.wav")

horn.play()
goodbye.play()
