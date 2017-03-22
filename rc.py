import core
from core import ServoEnum
import time
import sys
# from lib_oled96 import ssd1306


class rc:
    def __init__(self, core_module, wm, oled):
        """Class Constructor"""
        self.killed = False
        self.core_module = core_module
        self.wiimote = wm
        self.oled = oled

        self.ticks = 0

        # Store Max joystick values for left/right
        self.l_max_x = -1
        self.l_min_x = -1
        self.l_max_y = -1
        self.l_min_y = -1
        self.r_max_x = -1
        self.r_min_x = -1
        self.r_max_y = -1
        self.r_min_y = -1

    def show_motor_speeds(self, left_motor, right_motor):
        """ Show motor/aux config on OLED display """
        if self.oled is not None:
            # Format the speed to 2dp
            message = "[L: %0.2f] [R: %0.2f]" % (left_motor, right_motor)

            self.oled.cls()  # Clear Screen
            self.oled.canvas.text((10, 10), message, fill=1)
            # Now show the mesasge on the screen
            self.oled.display()

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def show_joystick_calibration(self, l_joystick_state, r_joystick_state):
        """ Shows the Min/Max raw joystick values to the prompt. """
        # Get raw joystick values. Using it to calibrate min/max range
        l_joystick_raw_pos = l_joystick_state['state']['raw']
        l_joystick_y, l_joystick_x = l_joystick_raw_pos
        # min/max [X]
        if self.l_max_x == -1:
            self.l_max_x = l_joystick_x
        else:
            self.l_max_x = max(self.l_max_x, l_joystick_x)
        if self.l_min_x == -1:
            self.l_min_x = l_joystick_x
        else:
            self.l_min_x = min(self.l_min_x, l_joystick_x)
        # min/max [Y]
        if self.l_max_y == -1:
            self.l_max_y = l_joystick_y
        else:
            self.l_max_y = max(self.l_max_y, l_joystick_y)
        if self.l_min_y == -1:
            self.l_min_y = l_joystick_y
        else:
            self.l_min_y = min(self.l_min_y, l_joystick_y)

        r_joystick_raw_pos = r_joystick_state['state']['raw']
        r_joystick_y, r_joystick_x = r_joystick_raw_pos
        # min/max [X]
        if self.r_max_x == -1:
            self.r_max_x = r_joystick_x
        else:
            self.r_max_x = max(self.r_max_x, r_joystick_x)
        if self.r_min_x == -1:
            self.r_min_x = r_joystick_x
        else:
            self.r_min_x = min(self.r_min_x, r_joystick_x)
        # min/max [Y]
        if self.r_max_y == -1:
            self.r_max_y = r_joystick_y
        else:
            self.r_max_y = max(self.r_max_y, r_joystick_y)
        if self.r_min_y == -1:
            self.r_min_y = r_joystick_y
        else:
            self.r_min_y = min(self.r_min_y, r_joystick_y)

        print("Left raw X[{},{}] Y[{},{}]".format(
            self.l_min_x,
            self.l_max_x,
            self.l_min_y,
            self.l_max_y)
        )
        print("Right raw X[{},{}] Y[{},{}]".format(
            self.r_min_x,
            self.r_max_x,
            self.r_min_y,
            self.r_max_y)
        )

    def run(self):
        print(sys.argv)
        """ Main Challenge method. Has to exist and is the
            start point for the threaded challenge. """
        nTicksSinceLastMenuUpdate = -1
        nTicksBetweenMenuUpdates = 10  # 10*0.05 seconds = every half second

        # Grab original motor scale factors
        left_motor_esc = self.core_module.servos[ServoEnum.LEFT_MOTOR_ESC][0]
        right_motor_esc = self.core_module.servos[ServoEnum.RIGHT_MOTOR_ESC][0]
        left_motor_orig_scale_factor = left_motor_esc.scale_factor
        right_motor_orig_scale_factor = right_motor_esc.scale_factor

        # Change motors to 1/4 speed
        speed_factor = 0.25
        left_motor_esc.set_scale_factor(speed_factor)
        right_motor_esc.set_scale_factor(speed_factor)

        # Loop indefinitely, or until this thread is flagged as stopped.
        while self.wiimote and not self.killed:
            # While in RC mode, get joystick states and pass speeds to motors.
            try:
                l_joystick_state = \
                    self.wiimote.get_classic_joystick_state(True)
                r_joystick_state = \
                    self.wiimote.get_classic_joystick_state(False)
            except:
                print("Failed to get Joystick")

            # Annotate joystick states to screen
            # if l_joystick_state:
            #     print("l_joystick_state: {}".format(l_joystick_state))
            # if r_joystick_state:
            #     print("r_joystick_state: {}".format(r_joystick_state))

            # Grab normalised x,y / steering,throttle
            # from left and right joysticks.
            l_joystick_pos = l_joystick_state['state']['normalised']
            l_steering, l_throttle = l_joystick_pos
            r_joystick_pos = r_joystick_state['state']['normalised']
            r_steering, r_throttle = r_joystick_pos

            # I'm assuming "normalised" means [-1, 1]
            # If it doesn't we'll have to do some division by self.l_max_x etc.

            self.tank = False

            # How much expo to apply to throttle
            # 1 = linear response (twitchy)
            # 3 = very slow in central portion of stick movement
            # At 2.0, half the stick travel means 25% throttle
            y_exp = 2.0

            # How much expo to apply to steering input
            x_exp = 1.5

            # What proportion of full speed to use
            speed_scale = 1.0

            # What proportion of full steering speed to use at throttle = 0
            steer_scale = 1.0

            # What proportion of full steering speed to use at full throttle
            steer_softening = 0.5

            # speed_input and steer_input are expo'd values of stick movement,
            if( l_throttle >= 0 ):
                speed_input = pow(l_throttle, y_exp)
            else:
                speed_input = 0 - (pow(0-l_throttle, y_exp))
            speed_input = speed_input * speed_scale

            if( r_steering >= 0 ):
                steer_input = pow(r_steering, x_exp)
            else:
                steer_input = 0 - (pow(0-r_steering, x_exp))
            steer_input = steer_input * steer_scale

            # Reduce steering input at high speed to avoid crazy behaviour
            # At throttle=0.0, steering_reduction = 1
            # At throttle=0.5, steering_reduction = 0.75
            # At throttle=-0.5, steering_reduction = 0.75 (not -0.75)
            # At throttle=1.0, steering_reduction = 0.5
            
            steering_reduction = (steer_softening * abs(speed_input))
            steer_input = steer_input * (1-steering_reduction)
            # Change to -1 if the steering is backwards :)
            steering_rev = 1.0

            # delta: the difference in throttle between the motors
            steering_delta = (steer_input * steer_scale) * steering_rev;

            l_motor = speed_input + steering_delta
            r_motor = speed_input - steering_delta

            # Cap the motor speeds: if one motor speed is above 1.0,
            # reduce both to maintain steering input
            if (l_motor > 1):
                c_r_motor = r_motor - (l_motor - 1)
                c_l_motor = 1
            elif (l_motor < -1):
                c_r_motor = r_motor + (l_motor + 1)
                c_l_motor = -1
            else:
                c_l_motor = l_motor

            if (r_motor > 1):
                c_l_motor = l_motor - (r_motor - 1)
                c_r_motor = 1
            elif (r_motor < -1):
                c_l_motor = l_motor + (r_motor + 1)
                c_r_motor = -1
            else:
                c_r_motor = r_motor

            if self.core_module:
                if self.tank:
                    self.core_module.throttle(c_l_motor, c_r_motor)
                else:
                    self.core_module.throttle(l_throttle, r_throttle)

            print("Motors %0.2f, %0.2f" % (c_l_motor, c_r_motor))

            # Show motor speeds on LCD
            if (nTicksSinceLastMenuUpdate == -1 or
               nTicksSinceLastMenuUpdate >= nTicksBetweenMenuUpdates):
                self.show_motor_speeds(c_l_motor, c_r_motor)
                nTicksSinceLastMenuUpdate = 0
            else:
                nTicksSinceLastMenuUpdate = nTicksSinceLastMenuUpdate + 1

            # Sleep between loops to allow other stuff to
            # happen and not over burden Pi and Arduino.
            time.sleep(0.05)

        # Reset motors to previous speed
        left_motor_esc.set_scale_factor(left_motor_orig_scale_factor)
        right_motor_esc.set_scale_factor(right_motor_orig_scale_factor)

if __name__ == "__main__":
    core = core.Core()
    rc = rc(core, None, None)
    try:
        rc.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        rc.stop()
        core.set_neutral()
        print("Quitting")
