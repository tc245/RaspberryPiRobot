import pygame
import time

pygame.init()

#Create joystick object
joystick = pygame.joystick.Joystick(0)
joystick.init()

while True:
    events = pygame.event.get()
    print(events)
    time.sleep(1)
