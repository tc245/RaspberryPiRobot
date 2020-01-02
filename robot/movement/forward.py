import  gpiozero
import time

robot = gpiozero.Robot(left=(4, 17), right=(27, 22))

for i in range(1):
	robot.forward()
	time.sleep(2)
	
