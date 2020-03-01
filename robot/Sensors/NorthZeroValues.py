#!/usr/bin/env python3

import time
import math
from lsm303d import LSM303D
import csv
import datetime

X = 0
Y = 2  # Change to 1 if you have the breakout flat

# Precalculated offsets from calibration exercise
offsets = [0.08085445, 0, 0.08645489]

input("Set a zero (North) point, then turn your breakout to that point and press a key...\n")

# Get the magnetometer's values
mag = list(lsm.magnetometer())

# Scale and shift values
for i in range(len(mag)):
    mag[i] = mag[i] - offsets[i]

print(mag)

