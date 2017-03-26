import core
import time
import PID

class Maze:
    def __init__(self, core_module, wm, oled):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0
        self.tick_time = 0.1 # How many seconds per control loop
        self.time_limit = 16 # How many seconds to run for
        self.follow_left = True
        self.switched_wall = False

# sensible defaults for maze: 
#        self.pidc = PID.PID(0.5, 0.0, 0.1)
        self.pidc = PID.PID(0.5, 0.0, 0.1)

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def decide_speeds(self, sensorvalue, ignore_d):
        """ Set up return values at the start"""
        leftspeed = 0
        rightspeed = 0

# straight line, cautious: mid -0.2, range -0.2
# maze, cautious: mid -0.1, range -0.2
# maze, tuned: mid -0.14, range -0.2

        speed_mid = -0.13
        speed_range = -0.2

        distance_midpoint = 200.0
        distance_range = 150.0
        error = (sensorvalue - distance_midpoint)
        self.pidc.update(error, ignore_d)

        deviation = self.pidc.output / distance_range
        c_deviation = max( -1.0, min(1.0, deviation))

        print("PID out: %f" % deviation)

        if self.follow_left:
            leftspeed = (speed_mid - (c_deviation * speed_range))
            rightspeed = (speed_mid + (c_deviation * speed_range))
        else:
            leftspeed = (speed_mid + (c_deviation * speed_range))
            rightspeed = (speed_mid - (c_deviation * speed_range))

        return leftspeed, rightspeed

    def run(self):
        print("Start run")
        """Read a sensor and set motor speeds accordingly"""
        # self.core.enable_lidar()
        self.core.enable_motors(True)

        tick_limit = self.time_limit / self.tick_time

        side_prox = 0
        prev_prox = 100 # Make sure nothing bad happens on startup

        while not self.killed and self.ticks < tick_limit:

            prev_prox = side_prox
            d_left = self.core.read_sensor(0)
            d_front = self.core.read_sensor(1) - 150
            d_right = self.core.read_sensor(2)

            # Which wall are we following?
            if self.follow_left:
                side_prox = d_left # 0:Left, 2: right
            else:
                side_prox = d_right
            front_prox = d_front

            # Have we fallen out of the end of the course?
            if d_left > 400 and d_right > 400:
                print("End of course, of course")
                self.killed = True
                break

            print("Distance is %d" % (side_prox) )

            ignore_d = False
            # Have we crossed over the middle of the course?
            if side_prox > 350 and (side_prox-100 > prev_prox) and self.switched_wall == False:
                print("Distance above threshold, follow right")
                self.follow_left = False
                self.switched_wall = True
                # Tell PID not to wig out too much
                ignore_d = True
            leftspeed = 0
            rightspeed = 0

            leftspeed, rightspeed = self.decide_speeds(min(side_prox, front_prox), ignore_d)

            self.core.throttle(leftspeed, rightspeed)
            print("Motors %f, %f" % (leftspeed, rightspeed))

            self.ticks = self.ticks + 1
            time.sleep(0.1)

        print("End of course, ran for %d seconds" % self.ticks / 10.0)

        self.core.stop()


if __name__ == "__main__":
    core = core.Core()
    follower = Maze(core, None, None)
    try:
        follower.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        follower.stop()
        core.stop()
        print("Quitting")
