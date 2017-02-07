import core
import time


class rc:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.core_module = core_module
        self.ticks = 0

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        self.core_module.enable_motors(True)
        """Read a sensor and set motor speeds accordingly"""
        while not self.killed:
            # While in RC mode, get joystick states and pass speeds to motors.
            self.core_module.throttle(self.leftspeed, self.rightspeed)
            print ("Motors %f, %f" % (self.leftspeed, self.rightspeed))

            # Sleep between loops to allow other stuff to
            # happen and not over burden Pi and Arduino.
            time.sleep(0.5)
