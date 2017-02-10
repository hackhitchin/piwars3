# Import triangula module to interact with SixAxis
import core
import time
# import sounds


class WallFollower:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0
        self.tick_time = 0.1 # How many seconds per control loop
        self.time_limit = 10 # How many seconds to run for
        self.left_motor_scale = 0.3  # What proportion of full throttle to use
        self.right_motor_scale = 0.3

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """Read a sensor and set motor speeds accordingly"""
        self.core.enable_motors(True)
        
        tick_limit = self.tick_time * self.time_limit
        
        while not self.killed and self.ticks < tick_limit:
            prox = self.drive.read_sensor()

            # sensor measures distance to left wall (0 - 20cm)
            # so lower sensor value means more left motor needed
            self.leftspeed = ((20 - prox) / 20) * self.left_motor_scale
            self.rightspeed = (prox / 20) * self.right_motor_scale

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
