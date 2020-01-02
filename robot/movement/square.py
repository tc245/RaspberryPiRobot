from  gpiozero import Robot
from time import sleep 

robot = Robot(left=(4, 17), right=(27, 22))

for i in range(4):
	robot.forward()
	sleep(0.5)
	robot.right()
	sleep(0.25)
