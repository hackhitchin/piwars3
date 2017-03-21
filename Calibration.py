import core
import time
import cwiid
import os.path
from ConfigParser import SafeConfigParser
from enum import Enum
# from lib_oled96 import ssd1306
from core import ServoEnum
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

# class CalibrationMode(Enum):
#     CM_NONE = 0
#     CM_LEFT = 1
#     CM_RIGHT = 2
#     CM_LEFT_AUX_1 = 3
#     CM_RIGHT_AUX_1 = 4


class Calibration:
    def __init__(self, core_module, wm, oled):
        """Class Constructor"""
        self.filename = "motors.ini"
        self.killed = False
        self.core = core_module
        self.wiimote = wm
        self.oled = oled

        self.ticks = 0

        # Note: string desciptions on the right are for
        # reference only. Not currently used in this code.
        self.menu_list = OrderedDict((
            (ServoEnum.LEFT_MOTOR_ESC, "Left Motor ESC"),
            (ServoEnum.RIGHT_MOTOR_ESC, "Right Motor ESC"),
            (ServoEnum.LEFT_AUX_ESC, "Left Aux ESC"),
            (ServoEnum.RIGHT_AUX_ESC, "Right Aux ESC"),
            (ServoEnum.LEFT_FLINGER_ESC, "Left Flinger ESC"),
            (ServoEnum.RIGHT_FLINGER_ESC, "Right Flinger ESC"),
            (ServoEnum.LEFT_FLINGER_SERVO, "Left Flinger Servo"),
            (ServoEnum.RIGHT_FLINGER_SERVO, "Right flinger Servo"),
            (ServoEnum.WINCH_SERVO, "Winch Servo")
        ))

        # Default current mode to NONE
        self.mode = ServoEnum.LEFT_MOTOR_ESC

    def get_next_mode(self, mode):
        """ Find the previous menu item """
        mode_index = self.menu_list.keys().index(mode)
        next_index = mode_index + 1
        if next_index >= len(self.menu_list):
            next_index = 0  # Wrapped round to end
        return self.menu_list.keys()[next_index]

    def get_previous_mode(self, mode):
        """ Find the previous menu item """
        mode_index = self.menu_list.keys().index(mode)
        previous_index = mode_index - 1
        if previous_index < 0:
            previous_index = len(self.menu_list) - 1  # Wrapped round to end
        return self.menu_list.keys()[previous_index]

    def show_servo_config(self, servo_id):
        """ Show servo config """
        if self.oled is not None:
            servo = self.core.servos[servo_id]
            title = "{}:".format(servo[2])
            message = "{} / {} / {}".format(
                str(servo[0].servo_min),
                str(servo[0].servo_mid),
                str(servo[0].servo_max)
            )

            # Clear Screen
            self.oled.cls()
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

        # Show servo config for current item.
        self.show_servo_config(self.mode)

        # Loop indefinitely, or until this thread is flagged as stopped.
        while self.wiimote and not self.killed:

            value_adjusted = False

            # While in RC mode, get joystick states and pass speeds to motors.
            classic_buttons_state = self.wiimote.get_classic_buttons()
            if classic_buttons_state is not None:

                if (classic_buttons_state & cwiid.CLASSIC_BTN_LEFT):
                    self.mode = self.get_previous_mode(self.mode)
                    value_adjusted = True
                if (classic_buttons_state & cwiid.CLASSIC_BTN_RIGHT):
                    self.mode = self.get_next_mode(self.mode)
                    value_adjusted = True

                if (classic_buttons_state & cwiid.CLASSIC_BTN_PLUS):
                    self.core.servos[self.mode][0].adjust_range(adjust_value)
                    value_adjusted = True
                if (classic_buttons_state & cwiid.CLASSIC_BTN_MINUS):
                    self.core.servos[self.mode][0].adjust_range(-adjust_value)
                    value_adjusted = True

            # Show current config
            if value_adjusted:
                self.show_servo_config(self.mode)

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
                # Read in min/mid/max of menu items that we can change.
                for item in self.menu_list.items():
                    item_enum_str = str(item[0]).split('.')
                    item_min_str = "{}_MIN".format(item_enum_str[0])
                    item_mid_str = "{}_MID".format(item_enum_str[0])
                    item_max_str = "{}_MAX".format(item_enum_str[0])
                    try:
                        self.core.servos[item[0]][0].servo_min = \
                            int(config.get('motors', item_min_str))
                        self.core.servos[item[0]][0].servo_mid = \
                            int(config.get('motors', item_mid_str))
                        self.core.servos[item[0]][0].servo_max = \
                            int(config.get('motors', item_max_str))
                    except:
                        print("Failed to read item from ini.")

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

        # Write out min/mid/max of menu items that we can change.
        for item in self.menu_list.items():
            item_enum_str = str(item[0]).split('.')
            item_min_str = "{}_MIN".format(item_enum_str[0])
            item_mid_str = "{}_MID".format(item_enum_str[0])
            item_max_str = "{}_MAX".format(item_enum_str[0])
            config.set(
                'motors',
                item_min_str,
                str(self.core.servos[item[0]][0].servo_min))
            config.set(
                'motors',
                item_mid_str,
                str(self.core.servos[item[0]][0].servo_mid))
            config.set(
                'motors',
                item_max_str,
                str(self.core.servos[item[0]][0].servo_max))


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
