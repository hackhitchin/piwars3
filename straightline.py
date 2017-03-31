import core
import time
import PID

class StraightLine:
    def __init__(self, core_module, wiimote, oled):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0
        self.tick_time = 0.05 # How many seconds per control loop
        self.time_limit = 1.9 # How many seconds to run for
        self.follow_left = False

        self.speed_mid = 0.4  # Starting speed; will speed up as it goes
        self.speed_range = -0.4    
        # self.skew_left = 0.87  # for driving blind or speed 0.5
        self.skew_left = 1  # for guided driving    

# Initial constants for straight line mode
#        self.pidc = PID.PID(0.5, 0.0, 0.1)
        self.pidc = PID.PID(0.33, 0.0, 0.1)  # works well at 0.4
        # self.pidc = PID.PID(0.045, 0.0, 0.06)  # 0.5 speed?

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def decide_speeds(self, sensorvalue):
        """ Set up return values at the start"""
        leftspeed = 0
        rightspeed = 0

# straight line, cautious: mid -0.2, range -0.2
# straight line, fast: mid -0.5, range -0.2
# straight line, batsh*t crazy: mid -0.9, range -0.1



        distance_midpoint = 190.0
        distance_range = 150.0  # works for 0.4 speed
        error = (sensorvalue - distance_midpoint)
        self.pidc.update(error, False)  # don't ignore D

        deviation = self.pidc.output / distance_range
        c_deviation = max(-1.0, min(1.0, deviation))

        print("PID out: %f" % deviation)

        if self.follow_left:
            leftspeed = (self.speed_mid - (c_deviation * self.speed_range))
            rightspeed = (self.speed_mid + (c_deviation * self.speed_range))
        else:
            leftspeed = (self.speed_mid + (c_deviation * self.speed_range))
            rightspeed = (self.speed_mid - (c_deviation * self.speed_range))

        return leftspeed, rightspeed

    def run(self):
        print("Start run")
        """Read a sensor and set motor speeds accordingly"""
        self.core.enable_motors(True)

        tick_limit = self.time_limit / self.tick_time

        side_prox = 0

        # speedup = [2,3,4,5,6,7,8]
        speedup = []

        use_lidar = True

        self.core.throttle(0.4, 0.4)
        print("Motors %f, %f" % (leftspeed, rightspeed))

        time.sleep(0.2)

        while not self.killed and self.ticks < tick_limit and side_prox != -1:
            prev_prox = side_prox
            if use_lidar:
                d_left = self.core.read_sensor(2)
                d_front = self.core.read_sensor(1)
                d_right = self.core.read_sensor(0)

                # Which wall are we following?
                if self.follow_left:
                    side_prox = d_left  # 0:Left, 2: right
                else:
                    side_prox = d_right
                front_prox = d_front
            else:
                side_prox = 123
                front_prox = 123

            # Have we fallen out of the end of the course?
            # if d_left > 500 and d_right > 400:
            #    self.killed = True
            #    break

            # Speed up as we go
            if self.ticks in speedup:
                self.speed_mid += 0.1
                self.speed_range += 0.1

            print("Distance is %d" % (side_prox))

            leftspeed = 0
            rightspeed = 0

            if use_lidar:
                leftspeed, rightspeed = self.decide_speeds(side_prox)
            else:
                leftspeed = min(self.speed_mid * self.skew_left, 1.0)
                rightspeed = min(self.speed_mid, 1.0)

            # Safety
            #if use_lidar and front_prox < 300:
            #    print("Safety stop")
            #    self.killed = True

            self.core.throttle(leftspeed, rightspeed)
            print("Motors %f, %f" % (leftspeed, rightspeed))

            self.ticks = self.ticks + 1
            time.sleep(self.tick_time)

        print("Stop after %d seconds, %r " % (self.ticks * self.tick_time, self.killed))

        self.core.stop()


if __name__ == "__main__":
    core = core.Core()
    follower = StraightLine(core)
    try:
        follower.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        follower.stop()
        core.stop()
        print("Quitting")
