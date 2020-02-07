import pygame

pygame.init()

#Create joystick object
joystick = pygame.joystick.Joystick(0)
joystick.init()

events = pygame.event.get()

print(events)
