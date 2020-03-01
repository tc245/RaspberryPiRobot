#!/usr/bin/env python3

import time
import math
from lsm303d import LSM303D
import csv
import datetime

def raw_heading(zero=0):
    """Return a raw compass heading calculated from the magnetometer data."""

    X = 0
    Y = 2  # Change to 1 if you have the breakout flat

    # Get the magnetometer's values
    mag = list(lsm.magnetometer())

    # Scale and shift values
    for i in range(len(mag)):
        mag[i] = mag[i] - offsets[i]

    # Calculate the heading from the vector
    heading = math.atan2(mag[Y], mag[X])

    if heading < 0:
        heading += (2 * math.pi)

    # Convert radian value to degrees
    heading_degrees = (round(math.degrees(heading), 2) - zero) % 360

    return heading_degrees


lsm = LSM303D(0x1d)  # Change to 0x1e if you have soldered the address jumper

# Python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass

# Precalculated offsets from calibration exercise
offsets = [0.08085445, 0, 0.08645489]

# Zero point for the compass
# Get the magnetometer's values
gauss_zero = [-0.029379361249846976, 0.3781368588566532, -0.14215326189374466]

# Calculate the heading from the vector
zero_heading = math.atan2(gauss_zero[0], gauss_zero[2])

if zero_heading < 0:
    zero_heading += (2 * math.pi)

# Convert radian value to degrees
zero = (round(math.degrees(zero_heading), 2)) % 360

input("Press a key to begin readings!\n")

while True:
    rh = raw_heading(zero=zero)
    print(rh)
    time.sleep(0.2)
