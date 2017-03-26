import core
import time
import PID

class LineFollow:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0
        self.tick_time = 0.1 # How many seconds per control loop
        self.time_limit = 60 # How many seconds to run for
        self.follow_left = True

# Initial constants for line following mode
#        self.pidc = PID.PID(0.5, 0.0, 0.1)
        self.pidc = PID.PID(0.5, 0.0, 0.1)

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def decide_speeds(self, sensorvalue):
        """ Set up return values at the start"""
        leftspeed = 0
        rightspeed = 0

# line follow, cautious: mid -0.2, range -0.2

        speed_mid = -0.2
        speed_range = -0.2

        # Sensorvalue should be deviation from the centre point
        error = sensorvalue
        self.pidc.update(error, False)  # don't ignore D

        deviation = self.pidc.output
        c_deviation = max(-1.0, min(1.0, deviation))

        print("PID out: %f" % deviation)

        leftspeed = (speed_mid - (c_deviation * speed_range))
        rightspeed = (speed_mid + (c_deviation * speed_range))

        return leftspeed, rightspeed

    def run(self):
        print("Start run")
        """Read a sensor and set motor speeds accordingly"""
        self.core.enable_motors(True)

        tick_limit = self.time_limit / self.tick_time

        side_prox = 0

        while not self.killed and self.ticks < tick_limit and side_prox != -1:
            # SENSOR LOGIC HERE
            # READ THE EIGHT ANALOG VALUES AND FIGURE OUT WHERE THE LINE IS?

            lineposition = core.read_line_sensor()

            print("Line is %d" % (lineposition) )

            leftspeed = 0
            rightspeed = 0

            leftspeed, rightspeed = self.decide_speeds(side_prox)

            self.core.throttle(leftspeed, rightspeed)
            print("Motors %f, %f" % (leftspeed, rightspeed))

            self.ticks = self.ticks + 1
            time.sleep(self.tick_time)

        print("Timeout after %d seconds" % (self.ticks * self.tick_time))

        self.core.stop()


if __name__ == "__main__":
    core = core.Core()
    follower = LineFollow(core)
    try:
        follower.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        follower.stop()
        core.stop()
        print("Quitting")
