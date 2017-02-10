# Import triangula module to interact with SixAxis
import core
import time
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
        self.time_limit = 10 # How many seconds to run for

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def decide_speeds(self, sensorvalue):
        """ Set up return values at the start"""
        leftspeed = 0
        rightspeed = 0

        if self.control_mode == "LINEAR":
            """ Deviation is distance from intended midpoint.
                Right is positive, left is negative
                Rate is how much to add/subtract from motor speed """

            distance_midpoint = 10
            deviation = (sensorvalue - 10) / 10.0 # [-1, 1]

            speed_mid = 0.3
            speed_range = 0.3

            leftspeed = (speed_mid - (deviation * speed_range) )
            rightspeed = (speed_mid + (deviation * speed_range) )

            return leftspeed, rightspeed

        elif self.control_mode == "EXPO":
            distance_midpoint = 10
            deviation = (sensorvalue - 10) / 10.0 # [-1, 1]

            if (deviation < 0):
                deviation = 0 - (deviation * deviation)
            else:
                deviation = deviation * deviation

            speed_mid = 0.3
            speed_range = 0.3

            leftspeed = (speed_mid - (deviation * speed_range) )
            rightspeed = (speed_mid + (deviation * speed_range) )
            
        else:
            leftspeed = speed_mid
            leftspeed = speed_mid

        return leftspeed, rightspeed


    def run(self):
        """Read a sensor and set motor speeds accordingly"""
        self.core.enable_motors(True)
        
        tick_limit = self.tick_time * self.time_limit
        
        while not self.killed and self.ticks < tick_limit:
            prox = self.drive.read_sensor()

            # sensor measures distance to left wall (0 - 20cm)
            # so lower sensor value means more left motor needed
            
            leftspeed, rightspeed = decide_speeds(prox, "EXPO")

            self.core.throttle(self.leftspeed, self.rightspeed)
            print ("Motors %f, %f" % (self.leftspeed, self.rightspeed))

            self.ticks = self.ticks + 1
            time.sleep(0.1)


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
