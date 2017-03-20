import core
import time
import cwiid
from lib_oled96 import ssd1306
import os.path
from ConfigParser import SafeConfigParser
from enum import Enum


class CalibrationMode(Enum):
    CM_NONE = 0
    CM_LEFT = 1
    CM_RIGHT = 2
    CM_LEFT_AUX_1 = 3
    CM_RIGHT_AUX_1 = 4


class Calibration:
    def __init__(self, core_module, wm, oled):
        """Class Constructor"""
        self.filename = "motors.ini"
        self.killed = False
        self.core = core_module
        self.wiimote = wm
        self.oled = oled

        self.ticks = 0

        # Default current mode to NONE
        self.mode = CalibrationMode.CM_NONE

    def show_motor_config(self, left):
        """ Show motor/aux config on OLED display """
        if self.oled is not None:
            if left:
                title = "Left Motor:"
                message = str(self.core.left_servo.servo_min) + '/'\
                    + str(self.core.left_servo.servo_mid) + '/'\
                    + str(self.core.left_servo.servo_max)
            else:
                title = "Right Motor:"
                message = str(self.core.right_servo.servo_min) + '/'\
                    + str(self.core.right_servo.servo_mid) + '/'\
                    + str(self.core.right_servo.servo_max)

            self.oled.cls()  # Clear Screen
            self.oled.canvas.text((10, 10), title, fill=1)
            self.oled.canvas.text((10, 30), message, fill=1)
            # Now show the mesasge on the screen
            self.oled.display()

    def show_aux_1_config(self, left):
        """ Show motor/aux config on OLED display """
        if self.oled is not None:
            if left:
                title = "Left Aux 1:"
                message = str(self.core.left_aux_1_servo.servo_min) + '/'\
                    + str(self.core.left_aux_1_servo.servo_mid) + '/'\
                    + str(self.core.left_aux_1_servo.servo_max)
            else:
                title = "Right Aux 1:"
                message = str(self.core.right_aux_1_servo.servo_min) + '/'\
                    + str(self.core.right_aux_1_servo.servo_mid) + '/'\
                    + str(self.core.right_aux_1_servo.servo_max)

            self.oled.cls()  # Clear Screen
            self.oled.canvas.text((10, 10), title, fill=1)
            self.oled.canvas.text((10, 30), message, fill=1)
            # Now show the mesasge on the screen
            self.oled.display()

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """ Main Challenge method. Has to exist and is the
            start point for the threaded challenge. """
        adjust_value = 5

        # Loop indefinitely, or until this thread is flagged as stopped.
        while self.wiimote and not self.killed:

            value_adjusted = False

            # While in RC mode, get joystick states and pass speeds to motors.
            classic_buttons_state = self.wiimote.get_classic_buttons()
            if classic_buttons_state is not None:
                if (classic_buttons_state & cwiid.CLASSIC_BTN_UP):
                    self.mode = CalibrationMode.CM_LEFT_AUX_1
                    value_adjusted = True
                if (classic_buttons_state & cwiid.CLASSIC_BTN_DOWN):
                    self.mode = CalibrationMode.CM_RIGHT_AUX_1
                    value_adjusted = True

                if (classic_buttons_state & cwiid.CLASSIC_BTN_LEFT):
                    self.mode = CalibrationMode.CM_LEFT
                    value_adjusted = True
                if (classic_buttons_state & cwiid.CLASSIC_BTN_RIGHT):
                    self.mode = CalibrationMode.CM_RIGHT_AUX_1
                    value_adjusted = True

                if (classic_buttons_state & cwiid.CLASSIC_BTN_PLUS):
                    value_adjusted = True
                    if self.mode == CalibrationMode.CM_LEFT:
                        self.core.left_servo.adjust_range(adjust_value)
                    if self.mode == CalibrationMode.CM_RIGHT:
                        self.core.right_servo.adjust_range(adjust_value)
                    if self.mode == CalibrationMode.CM_LEFT_AUX_1:
                        self.core.left_aux_1_servo.adjust_range(adjust_value)
                    if self.mode == CalibrationMode.CM_RIGHT_AUX_1:
                        self.core.right_aux_1_servo.adjust_range(adjust_value)

                if (classic_buttons_state & cwiid.CLASSIC_BTN_MINUS):
                    value_adjusted = True
                    if self.mode == CalibrationMode.CM_LEFT:
                        self.core.left_servo.adjust_range(-adjust_value)
                    if self.mode == CalibrationMode.CM_RIGHT:
                        self.core.right_servo.adjust_range(-adjust_value)
                    if self.mode == CalibrationMode.CM_LEFT_AUX_1:
                        self.core.left_aux_1_servo.adjust_range(-adjust_value)
                    if self.mode == CalibrationMode.CM_RIGHT_AUX_1:
                        self.core.right_aux_1_servo.adjust_range(-adjust_value)

            # Show current config
            if value_adjusted:
                if self.mode == CalibrationMode.CM_LEFT:
                    self.show_motor_config(True)
                elif self.mode == CalibrationMode.CM_RIGHT:
                    self.show_motor_config(False)
                elif self.mode == CalibrationMode.CM_LEFT_AUX_1:
                    self.show_aux_1_config(True)
                elif self.mode == CalibrationMode.CM_RIGHT_AUX_1:
                    self.show_aux_1_config(False)

                # Send motors "stick neutral" so that we can test centre value
                self.core.throttle(0.0, 0.0)

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
        config.set('motors', 'LEFT_MIN', str(self.core.left_servo.servo_min))
        config.set('motors', 'LEFT_MID', str(self.core.left_servo.servo_mid))
        config.set('motors', 'LEFT_MAX', str(self.core.left_servo.servo_max))

        config.set('motors', 'RIGHT_MIN', str(self.core.right_servo.servo_min))
        config.set('motors', 'RIGHT_MID', str(self.core.right_servo.servo_mid))
        config.set('motors', 'RIGHT_MAX', str(self.core.right_servo.servo_max))

        # Write out the Auxilery ESC ranges
        config.set(
            'motors',
            'LEFT_AUX_1_MIN',
            str(self.core.left_aux_1_servo.servo_min))
        config.set(
            'motors',
            'LEFT_AUX_1_MID',
            str(self.core.left_aux_1_servo.servo_mid))
        config.set(
            'motors',
            'LEFT_AUX_1_MAX',
            str(self.core.left_aux_1_servo.servo_max))
        # And now the right
        config.set(
            'motors',
            'RIGHT_AUX_1_MIN',
            str(self.core.right_aux_1_servo.servo_min))
        config.set(
            'motors',
            'RIGHT_AUX_1_MID',
            str(self.core.right_aux_1_servo.servo_mid))
        config.set(
            'motors',
            'RIGHT_AUX_1_MAX',
            str(self.core.right_aux_1_servo.servo_max))


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
