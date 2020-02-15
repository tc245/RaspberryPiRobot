import pygame
import time

done = False
loop = False

pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

while not done:
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(9) == True: #when share pressed quit loop
                done = True
            elif joystick.get_button(1) == True:
                print("Button pressed")
                loop = True
                while loop:
                    print ("in a while loop")
                    time.sleep(1)
                    if pygame.event.peek(pygame.JOYBUTTONDOWN):
                        loop = False
            elif joystick.get_button(4) == True:
                print("Button pressed")            
                
Print("exited loop")
