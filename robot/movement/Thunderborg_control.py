#Thunderborg board to control robot

import sys
import time

sys.path.append('/home/pi/thunderborg')
import ThunderBorg

TB = ThunderBorg.ThunderBorg()
TB.i2cAddress = 0x0a
TB.Init()

TB.SetMotors(0.2)
time.sleep(2)
TB.SetMotors(0)
