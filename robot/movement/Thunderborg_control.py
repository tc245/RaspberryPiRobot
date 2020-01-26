#Thunderborg board to control robot

import sys
import time

sys.path.append('/home/pi/thunderborg')
import ThunderBorg

TB = ThunderBorg.ThunderBorg()
TB.init

TB.SetMotors(0.1)
time.sleep(2)
TB.SetMotors(0)
