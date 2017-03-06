# Import triangula module to interact with SixAxis
import core
import time
import PID
# import sounds

''' 10-2-2017: This code is completely untested; don't be surprised when it 
doesn't compile, run or do anything sensible.'''


class WallFollower:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0
        self.tick_time = 0.1 # How many seconds per control loop
        self.time_limit = 3 # How many seconds to run for

#known good for straight line, underdamped
#        self.pidc = PID.PID(0.5, 0.0, 0.2)
        self.pidc = PID.PID(0.5, 0.0, 0.2)

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def set_control_mode(self, mode):
        self.control_mode = mode

    def decide_speeds(self, sensorvalue):
        """ Set up return values at the start"""
        leftspeed = 0
        rightspeed = 0

        if self.control_mode == "LINEAR":
            speed_mid = -0.2
            speed_range = 0.06
            """ Deviation is distance from intended midpoint.
                Right is positive, left is negative
                Rate is how much to add/subtract from motor speed """

            distance_midpoint = 200.0  # mm
            distance_range = 100.0  # mm
            deviation = (sensorvalue - distance_midpoint) / distance_range  # [-1, 1]

            # Gate value to [-1,1] for the sake of not driving backwards
            if (deviation < -1):
                deviation = -1
            if (deviation > 1):
                deviation = 1

            leftspeed = (speed_mid - (deviation * speed_range))
            rightspeed = (speed_mid + (deviation * speed_range))

            return leftspeed, rightspeed

        elif self.control_mode == "EXPO":
            speed_mid = 0.05
            speed_range = 0.05

            distance_midpoint = 200.0  # mm
            distance_range = 100.0  # mm
            deviation = (sensorvalue - distance_midpoint) / distance_range  # [-1, 1]

            if (deviation < 0):
                deviation = 0 - (deviation * deviation)
            else:
                deviation = deviation * deviation

            leftspeed = (speed_mid - (deviation * speed_range))
            rightspeed = (speed_mid + (deviation * speed_range))

        elif self.control_mode == "PID":
            speed_mid = -0.2
            speed_range = -0.2

            distance_midpoint = 200.0
            distance_range = 150.0
            error = (sensorvalue - distance_midpoint)
            self.pidc.update(error)

            deviation = self.pidc.output / distance_range
            c_deviation = max( -1.0, min(1.0, deviation)) 

            print("PID out: %f" % deviation)

            leftspeed = (speed_mid - (c_deviation * speed_range))
            rightspeed = (speed_mid + (c_deviation * speed_range))

        else:
            leftspeed = speed_mid
            leftspeed = speed_mid

        return leftspeed, rightspeed

    def run(self):
        print("Start run")
        """Read a sensor and set motor speeds accordingly"""
        self.core.enable_motors(True)

        tick_limit = self.time_limit / self.tick_time

        self.set_control_mode("PID")

        prox = 0

        while not self.killed and self.ticks < tick_limit and prox != -1:
            prox = self.core.read_sensor()
            print("Distance is %d" % (prox) )
            leftspeed = 0
            rightspeed = 0

            # sensor measures distance to left wall (0 - 20cm)
            # so lower sensor value means more left motor needed

            leftspeed, rightspeed = self.decide_speeds(prox)

            self.core.throttle(leftspeed, rightspeed)
            print("Motors %f, %f" % (leftspeed, rightspeed))

            self.ticks = self.ticks + 1
            time.sleep(0.1)

        print("Ticks %d" % self.ticks)


if __name__ == "__main__":
    core = core.Core()
    follower = WallFollower(core)
    try:
        follower.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        follower.stop()
        core.stop()
        print("Quitting")
