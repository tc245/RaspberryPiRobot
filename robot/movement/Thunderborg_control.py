#Thunderborg board to control robot

import sys
import time
import pantilthat
import pygame

sys.path.append('/home/pi/thunderborg')
import ThunderBorg

TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x0a
TB.Init()

#Motor control code
TB.SetMotors(-0.5)
time.sleep(3)
TB.SetMotors(0)
TB.SetMotors(0.5)
time.sleep(2)
TB.SetMotors(0)
