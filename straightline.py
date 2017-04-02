import core
import time
import PID


class StraightLine:
    def __init__(self, core_module, wiimote, oled):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0
        self.tick_time = 0.05  # How many seconds per control loop
        self.time_limit = 1.0  # How many seconds to run for
        self.follow_left = False

        # Initial speed
        self.left_speed = 0.0
        self.right_speed = 0.0

        # self.speed_mid = 0.4  # Starting speed; will speed up as it goes
        self.speed_range = -0.4
        # self.skew_left = 0.87  # for driving blind or speed 0.5
        self.skew_left = 1  # for guided driving

        # Initial constants for straight line mode
        self.pidc = PID.PID(0.33, 0.0, 0.1)  # works well at 0.4

        # Create dictionary for left/right speed
        self.speed_dict = dict()
        # p, i, d, left_speed, right_speed
        # NOTE: 5 ticks per 1/4 second.
        # 0 tick = starting pid/speeds

        # self.speed_dict[5] = (0.33, 0.0, 0.15, 0.4, 0.4, 0.4) works well all the way  

        # Somehow this set just worked like magic and I'm not questioning it
        #self.speed_dict[0] = (0.0, 0.0, 0.0, 0.4, 0.4, 0.4)
        #self.speed_dict[5] = (0.20, 0.0, 0.12, 0.5, 0.5, 0.4)
        #self.speed_dict[15] = (0.20, 0.0, 0.09, 0.5, 0.5, 0.4)
        #self.speed_dict[22] = (0.33, 0.0, 0.1, 0.2, 0.2, 0.0)                

        self.speed_dict[0] = (0.0, 0.0, 0.0, 0.4, 0.4, 0.4)
        self.speed_dict[5] = (0.20, 0.0, 0.12, 0.5, 0.5, 0.4)
        self.speed_dict[15] = (0.20, 0.0, 0.09, 0.8, 0.8, 1.2)
        # self.speed_dict[20] = (0.33, 0.0, 0.1, 0.5, 0.5, 0.4)
        self.speed_dict[22] = (0.33, 0.0, 0.1, 0.2, 0.2, 0.0)

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
        distance_range = 200.0  # works for 0.4 speed
        error = (sensorvalue - distance_midpoint)
        self.pidc.update(error, False)  # don't ignore D

        deviation = self.pidc.output / distance_range
        c_deviation = max(-1.0, min(1.0, deviation))

        print("PID out: %f" % deviation)

        if self.follow_left:
            leftspeed = (self.left_speed + (c_deviation * self.speed_range))
            rightspeed = (self.right_speed - (c_deviation * self.speed_range))
        else:
            leftspeed = (self.left_speed - (c_deviation * self.speed_range))
            rightspeed = (self.right_speed + (c_deviation * self.speed_range))

        return leftspeed, rightspeed

    def run(self):
        print("Start run")
        """Read a sensor and set motor speeds accordingly"""
        self.ticks = 0
        self.core.enable_motors(True)
        tick_limit = self.time_limit / self.tick_time
        side_prox = 0

        self.core.throttle(0, 0, core.ServoEnum.LEFT_AUX_ESC, core.ServoEnum.RIGHT_AUX_ESC)
        time.sleep(1.0)
        self.core.throttle(1, 1, core.ServoEnum.LEFT_AUX_ESC, core.ServoEnum.RIGHT_AUX_ESC)

        while not self.killed and self.ticks < tick_limit and side_prox != -1:
            d_left = self.core.read_sensor(2)
            # d_front = self.core.read_sensor(1)
            d_right = self.core.read_sensor(0)

            # Which wall are we following?
            if self.follow_left:
                side_prox = d_left  # 0:Left, 2: right
            else:
                side_prox = d_right
                # front_prox = d_front

            # Have we fallen out of the end of the course?
            # if d_left > 500 and d_right > 400:
            #    self.killed = True
            #    break

            # Try to get new PID values for current time.
            try:
                kp, ki, kd, ls, rs, self.speed_range = self.speed_dict[self.ticks]
                print("Speed Change L" + str(ls) + " R" + str(rs))
                self.pidc.setKp(kp)
                self.pidc.setKi(ki)
                self.pidc.setKd(kd)
                self.left_speed = ls
                self.right_speed = rs
            except IndexError:
                # Not really an error, just no
                # new PID values for current time slot.
                print("Index Error")
            except KeyError:
                print("")

            print("Distance is %d" % (side_prox))

            leftspeed, rightspeed = self.decide_speeds(side_prox)

            # Safety
            # if use_lidar and front_prox < 300:
            #    print("Safety stop")
            #    self.killed = True

            self.core.throttle(leftspeed, rightspeed)
            print("Motors %f, %f" % (leftspeed, rightspeed))

            self.ticks = self.ticks + 1
            time.sleep(self.tick_time)

        print("Stop after %d seconds, %r ".format(
            self.ticks * self.tick_time,
            self.killed)
        )

        self.core.stop()
        self.core.throttle(-1, -1, core.ServoEnum.LEFT_AUX_ESC, core.ServoEnum.RIGHT_AUX_ESC)


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
