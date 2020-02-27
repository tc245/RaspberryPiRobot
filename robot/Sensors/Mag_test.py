#!/usr/bin/env python

import time
from lsm303d import LSM303D
import csv

lsm = LSM303D(0x1d) # Change to 0x1e if you have soldered the address jumper

with open('gauss2.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(["X", "Z", "Y"])

    for _ in range(150):
        xyz = list(lsm.magnetometer())
        print(("{:+06.2f} : {:+06.2f} : {:+06.2f}").format(*xyz))
        with open('gauss2.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(xyz[0:3])
        time.sleep(0.2)


