import gpiozero
import time

TRIG = 23
ECHO = 24

trigger = gpiozero.OutputDevice(TRIG)
echo = gpiozero.DigitalInputDevice(ECHO)

robot = gpiozero.Robot(left=(18, 17), right=(27,22))

trigger.off()
time.sleep(3)

def get_distance(trigger, echo):
	trigger.on()
	time.sleep(0.00001)
	trigger.off()

	while echo.is_active == False:
		pulse_start = time.time()

	while echo.is_active == True:
		pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start

	distance = 34300 * (pulse_duration/2)

	round_distance = round(distance,1)

	return(round_distance)

while True:
	dist = get_distance(trigger,echo)
	if dist <= 15:
		robot.right(0.5)
		time.sleep(0.25)
	else:
		robot.forward(0.3)
		time.sleep(0.1)
