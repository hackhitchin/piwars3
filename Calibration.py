import core
import time
import cwiid
import launcher

import os.path
from ConfigParser import SafeConfigParser


class Calibration:
    def __init__(self, core_module, wm, launcher_app):
        """Class Constructor"""
        self.filename = "motors.ini"
        self.killed = False
        self.core = core_module
        self.wiimote = wm
        self.launcher = launcher_app

        self.ticks = 0

        # Define mode enums
        self.mode_none = 0
        self.mode_left = 1
        self.mode_right = 2

        self.mode_left_aux_1 = 3
        self.mode_right_aux_1 = 4

        # Default current mode to NONE
        self.mode = self.mode_none

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """ Main Challenge method. Has to exist and is the
            start point for the threaded challenge. """
        adjust_value = 5

        # Loop indefinitely, or until this thread is flagged as stopped.
        while self.wiimote and not self.killed:

            # While in RC mode, get joystick states and pass speeds to motors.
            classic_buttons_state = self.wiimote.get_classic_buttons()
            if classic_buttons_state is not None:
                if (classic_buttons_state & cwiid.CLASSIC_BTN_UP):
                    print("KEY_UP")
                    self.mode = self.mode_left_aux_1
                if (classic_buttons_state & cwiid.CLASSIC_BTN_DOWN):
                    print("KEY_DOWN")
                    self.mode = self.mode_right_aux_1

                if (classic_buttons_state & cwiid.CLASSIC_BTN_LEFT):
                    print("KEY_LEFT")
                    self.mode = self.mode_left
                if (classic_buttons_state & cwiid.CLASSIC_BTN_RIGHT):
                    print("KEY_RIGHT")
                    self.mode = self.mode_right

                if (classic_buttons_state & cwiid.CLASSIC_BTN_A):
                    print("KEY_A")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_B):
                    print("KEY_B")

                if (classic_buttons_state & cwiid.CLASSIC_BTN_X):
                    print("KEY_X")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_Y):
                    print("KEY_Y")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_L):
                    print("KEY_L")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_R):
                    print("KEY_R")

                if (classic_buttons_state & cwiid.CLASSIC_BTN_PLUS):
                    print("KEY_PLUS")
                    if self.mode == self.mode_left:
                        self.core.left_servo.adjust_range(adjust_value)
                    if self.mode == self.mode_right:
                        self.core.right_servo.adjust_range(adjust_value)
                    if self.mode == self.mode_left_aux_1:
                        self.core.left_aux_1_servo.adjust_range(adjust_value)
                    if self.mode == self.mode_right_aux_1:
                        self.core.right_aux_1_servo.adjust_range(adjust_value)

                if (classic_buttons_state & cwiid.CLASSIC_BTN_MINUS):
                    print("KEY_MINUS")
                    if self.mode == self.mode_left:
                        self.core.left_servo.adjust_range(-adjust_value)
                    if self.mode == self.mode_right:
                        self.core.right_servo.adjust_range(-adjust_value)
                    if self.mode == self.mode_left_aux_1:
                        self.core.left_aux_1_servo.adjust_range(-adjust_value)
                    if self.mode == self.mode_right_aux_1:
                        self.core.right_aux_1_servo.adjust_range(-adjust_value)

                if (classic_buttons_state & cwiid.CLASSIC_BTN_HOME):
                    print("KEY_HOME")

            # Show current config
            if self.launcher:
                if self.mode == self.mode_left:
                    self.launcher.show_motor_config(True)
                elif self.mode == self.mode_right:
                    self.launcher.show_motor_config(False)
                elif self.mode == self.mode_left_aux_1:
                    self.launcher.show_aux_1_config(True)
                elif self.mode == self.mode_right_aux_1:
                    self.launcher.show_aux_1_config(False)
                else:
                    self.launcher.show_mode()

            # Sleep between loops to allow other stuff to
            # happen and not over burden Pi and Arduino.
            time.sleep(0.05)

    def read_config(self):
        """ Read the motor defaults from the config file. """

        print("Reading Config")

        # Only bother reading if file exists
        if os.path.isfile(self.filename):
            # Get config file
            config = SafeConfigParser()
            config.read(self.filename)

            # Read the motor min/mid/max servo ranges
            if self.core is not None:
                # Read Wheel motor ESC ranges
                self.core.left_servo.servo_min =\
                    int(config.get('motors', 'LEFT_MIN'))
                self.core.left_servo.servo_mid =\
                    int(config.get('motors', 'LEFT_MID'))
                self.core.left_servo.servo_max =\
                    int(config.get('motors', 'LEFT_MAX'))

                self.core.right_servo.servo_min =\
                    int(config.get('motors', 'RIGHT_MIN'))
                self.core.right_servo.servo_mid =\
                    int(config.get('motors', 'RIGHT_MID'))
                self.core.right_servo.servo_max =\
                    int(config.get('motors', 'RIGHT_MAX'))

                # Read Auxilery ESC ranges
                self.core.left_aux_1_servo.servo_min = \
                    int(config.get('motors', 'LEFT_AUX_1_MIN'))
                self.core.left_aux_1_servo.servo_mid = \
                    int(config.get('motors', 'LEFT_AUX_1_MID'))
                self.core.left_aux_1_servo.servo_max = \
                    int(config.get('motors', 'LEFT_AUX_1_MAX'))

                self.core.right_aux_1_servo.servo_min = \
                    int(config.get('motors', 'RIGHT_AUX_1_MIN'))
                self.core.right_aux_1_servo.servo_mid = \
                    int(config.get('motors', 'RIGHT_AUX_1_MID'))
                self.core.right_aux_1_servo.servo_max = \
                    int(config.get('motors', 'RIGHT_AUX_1_MAX'))
        print("Finished Reading Config")

    def write_config(self):
        """ Read the motor defaults from the config file. """
        self.filename = "motors.ini"

        # Get config file
        config = SafeConfigParser()
        # Only bother reading if file exists
        if os.path.isfile(self.filename):
            config.read(self.filename)

        # *** Server Settings ***
        try:
            config.add_section('motors')
        except:
            print("Failed to add, could already exist")

        # Write out the wheel motor ESC ranges
        config.set('motors', 'LEFT_MIN', str(self.core.LEFT_MIN))
        config.set('motors', 'LEFT_MID', str(self.core.LEFT_MID))
        config.set('motors', 'LEFT_MAX', str(self.core.LEFT_MAX))

        config.set('motors', 'RIGHT_MIN', str(self.core.RIGHT_MIN))
        config.set('motors', 'RIGHT_MID', str(self.core.RIGHT_MID))
        config.set('motors', 'RIGHT_MAX', str(self.core.RIGHT_MAX))

        # Write out the Auxilery ESC ranges
        config.set('motors', 'LEFT_AUX_1_MIN', str(self.core.LEFT_AUX_1_MIN))
        config.set('motors', 'LEFT_AUX_1_MID', str(self.core.LEFT_AUX_1_MID))
        config.set('motors', 'LEFT_AUX_1_MAX', str(self.core.LEFT_AUX_1_MAX))

        config.set('motors', 'RIGHT_AUX_1_MIN', str(self.core.RIGHT_AUX_1_MIN))
        config.set('motors', 'RIGHT_AUX_1_MID', str(self.core.RIGHT_AUX_1_MID))
        config.set('motors', 'RIGHT_AUX_1_MAX', str(self.core.RIGHT_AUX_1_MAX))


if __name__ == "__main__":
    core = core.Core()
    calibration = Calibration(core)
    try:
        calibration.run_auto()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        calibration.stop()
        core.set_neutral()
        print("Quitting")
