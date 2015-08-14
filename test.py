#!/usr/bin/python2.7
import struct
import time
import sphero_driver
import sys
import threading
sphero = sphero_driver.Sphero()
sphero.connect()
sphero.set_raw_data_strm(40, 1 , 0, False)

# sphero.start()
sphero.set_stablization(1, False)
sphero.set_back_led(255, False)
time.sleep(1)
# sphero.roll(50, 0, 1, False)
# time.sleep(1)

while True:
	sphero.roll(0, 9, 1, False)
	time.sleep(0.5)
	sphero.set_heading(0, False)

# sphero.roll(100, 15, 1, False)
# time.sleep(2)
# sphero.roll(100, 15, 1, False)
# sphero.join()
sphero.set_back_led(0, False)
sphero.disconnect()
sys.exit(1)



