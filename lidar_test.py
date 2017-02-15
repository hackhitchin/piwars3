#!/usr/bin/python

import time
import i2c_lidar

# Assume 2 devices, connected to GPIOs 17 and 27 (pins 11 and 13 on the GPIO
# header)

# Reset and hold both devices
i2c_lidar.xshut([17,27])

# Initialise the 'left' device and set its address to 0x2a
tof_left = i2c_lidar.create(27, 0x2a)
# Initialise the 'right' device and set its address to 0x2b
tof_right = i2c_lidar.create(17, 0x2b)

# Fetch the amount of time it takes to get a reading. Both TOF devices are
# configured the same so will read at the same rate
timing = tof_left.get_timing()
if (timing < 20000):
    timing = 20000
print ("Timing %d ms" % (timing/1000))

# Do 1000 readings and quit
for count in range(1,1001):
    # Read distance in millimetres
    distance_l = tof_left.get_distance()
    distance_r = tof_right.get_distance()
    print ("%04d    %4d mm, %3d cm <<    >> %4d mm, %3d cm" % (count, distance_l, (distance_l/10), distance_r, (distance_r/10)))

    time.sleep(timing/1000000.00)

# Turn both devices off. This is an optional step, as they get reset every
# time the program runs
tof_left.stop_ranging()
tof_right.stop_ranging()

