#!/usr/bin/env python3

import time
import math
from lsm303d import LSM303D
import csv
import datetime

lsm = LSM303D(0x1d)  # Change to 0x1e if you have soldered the address jumper

X = 0
Y = 2  # Change to 1 if you have the breakout flat

# Precalculated offsets from calibration exercise
offsets = [0.08085445, 0, 0.08645489]

# Get the magnetometer's values
mag = list(lsm.magnetometer())

# Scale and shift values
for i in range(len(mag)):
    mag[i] = mag[i] - offsets[i]

print(mag)


# Calculate the heading from the vector
heading = math.atan2(mag[Y], mag[X])

if heading < 0:
    heading += (2 * math.pi)

# Convert radian value to degrees
heading_degrees = (round(math.degrees(heading), 2)) % 360

print(heading_degrees)





