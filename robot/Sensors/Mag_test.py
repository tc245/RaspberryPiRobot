#!/usr/bin/env python

import time
from lsm303d import LSM303D
import csv

lsm = LSM303D(0x1d) # Change to 0x1e if you have soldered the address jumper

with open('gauss.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(["X", "Y", "Z"])

while True:
    xyz = list(lsm.magnetometer())
    print(("{:+06.2f} : {:+06.2f} : {:+06.2f}").format(*xyz))
    with open('gauss.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(xyz[0], xyz[1], xyz[2])
    time.sleep(0.2)

