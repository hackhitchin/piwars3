#!/usr/bin/python

# MIT License
#
# Copyright (c) 2017 John Bryan Moore
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# import time
# import smbus
from ctypes import *

VL53L0X_GOOD_ACCURACY_MODE = 0   # Good Accuracy mode
VL53L0X_BETTER_ACCURACY_MODE = 1   # Better Accuracy mode
VL53L0X_BEST_ACCURACY_MODE = 2   # Best Accuracy mode
VL53L0X_LONG_RANGE_MODE = 3   # Longe Range mode
VL53L0X_HIGH_SPEED_MODE = 4   # High Speed mode

# i2cbus = smbus.SMBus(1)


class VL53L0X(object):
    """VL53L0X ToF."""

    object_number = 0

    def __init__(self, tof_lib, address=0x29, **kwargs):
        """Initialize the VL53L0X ToF Sensor from ST"""
        self.device_address = address
        self.my_object_number = VL53L0X.object_number
        VL53L0X.object_number += 1
        self.tof_lib = tof_lib

    def start_ranging(self, mode=VL53L0X_GOOD_ACCURACY_MODE):
        """Start VL53L0X ToF Sensor Ranging"""
        self.tof_lib.startRanging(
            self.my_object_number,
            mode,
            self.device_address
        )

    def stop_ranging(self):
        """Stop VL53L0X ToF Sensor Ranging"""
        self.tof_lib.stopRanging(self.my_object_number)

    def get_distance(self):
        """Get distance from VL53L0X ToF Sensor"""
        return self.tof_lib.getDistance(self.my_object_number)

    # This function included to show how to access the ST library directly
    # from python instead of through the simplified interface
    def get_timing(self):
        Dev = POINTER(c_void_p)
        Dev = tof_lib.getDev(self.my_object_number)
        budget = c_uint(0)
        budget_p = pointer(budget)
        Status = tof_lib.VL53L0X_GetMeasurementTimingBudgetMicroSeconds(
            Dev,
            budget_p
        )
        if (Status == 0):
            return (budget.value + 1000)
        else:
            return 0
