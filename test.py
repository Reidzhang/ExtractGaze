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
sphero.set_heading(0, False);
time.sleep(2)
sphero.set_rgb_led(255,0,0,0,False)
time.sleep(1)
sphero.set_rgb_led(0,255,0,0,False)
time.sleep(1)
sphero.set_rgb_led(0,0,255,0,False)
time.sleep(3)
sphero.roll(100, 0, 1, True)
time.sleep(2)
# sphero.roll(100, 15, 1, False)
# time.sleep(2)
# sphero.roll(100, 15, 1, False)
# time.sleep(2)
# sphero.roll(100, 15, 1, False)
# time.sleep(2)
# sphero.roll(100, 15, 1, False)
# time.sleep(2)
# sphero.roll(100, 15, 1, False)
# time.sleep(2)
# sphero.join()
sphero.disconnect()
sys.exit(1)



