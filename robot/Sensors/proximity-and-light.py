#!/usr/bin/env python

import time
from ltr559 import LTR559

ltr559 = LTR559()

try:
    while True:
        ltr559.update_sensor()
        lux = ltr559.get_lux()

        print("Lux: {:06.2f}".format(lux))

        time.sleep(0.05)
except KeyboardInterrupt:
    pass
