from __future__ import division
# import logging
import servo_control
import arduino
#import sensor
import i2c_lidar
from RPIO import PWM

# Minimum and maximum theoretical pulse widths. Ignore reversing here
# ESC "DB1" midpoint is about 1440
# ESC "DB2" midpoint is 1500

LIDAR_PIN = 4
LEFT_SERVO_PIN = 17
RIGHT_SERVO_PIN = 27


class Core():
    """ Instantiate a 2WD drivetrain, utilising 2x ESCs,
        controlled using a 2 axis (throttle, steering)
        system + skittle accessories """

    def __init__(self):
        """ Constructor """

        self.LEFT_MIN = 800
        self.LEFT_MID = 1300
        self.LEFT_MAX = 1800

        self.RIGHT_MIN = 800
        self.RIGHT_MID = 1300
        self.RIGHT_MAX = 1800

        self.LEFT_AUX_1_MIN = 800
        self.LEFT_AUX_1_MID = 1300
        self.LEFT_AUX_1_MAX = 1800

        self.RIGHT_AUX_1_MIN = 800
        self.RIGHT_AUX_1_MID = 1300
        self.RIGHT_AUX_1_MAX = 1800

        self.left_servo = servo_control.Servo_Controller(
            self.LEFT_MIN, self.LEFT_MID, self.LEFT_MAX, True)
        self.right_servo = servo_control.Servo_Controller(
            self.RIGHT_MIN, self.RIGHT_MID, self.RIGHT_MAX, False)

        self.left_channel = 1
        self.right_channel = 2

        # Proximity sensor: roughly cm from closest measurable point
        # self.tof_left = sensor.Sensor(0, 450, 20, 0)
        self.PWMservo = PWM.Servo(pulse_incr_us=1)

        self.arduino_mode = 0  # Not using Arduino

        if (self.arduino_mode == 1):
            self.arduino = arduino.Arduino()
        else:
            self.arduino = None
            self.PWMservo = PWM.Servo(pulse_incr_us=1)
            i2c_lidar.xshut([LIDAR_PIN])
            self.tof_left = i2c_lidar.create(LIDAR_PIN, 0x2a)

    def enable_motors(self, enable):
        """ Called when we want to enable/disable the motors.
            When disabled, will ignore any new motor commands. """

        # Send motor neutral if disabling.
        if not enable:
            self.set_neutral()

        # AFTER we have sent neutral, enable/disable motors
        if self.arduino:
            self.arduino.enable_motors(enable)

    def throttle(self, left_speed, right_speed):
        """ Send motors speed value in range [-1,1]
            where 0 = neutral """

        # Calculate microseconds from command speed
        left_micros = self.left_servo.micros(left_speed)
        right_micros = self.right_servo.micros(right_speed)

        # Tell the Arduino to move to that speed (eventually)
        if self.arduino:
            self.arduino.throttle(left_micros, right_micros)
        else:
            # TODO: make this ramp speeds using RPIO
            self.PWMservo.set_servo(LEFT_SERVO_PIN, left_micros)
            self.PWMservo.set_servo(RIGHT_SERVO_PIN, right_micros)
            print("Set PWM servos to %d, %d" % (left_micros, right_micros))

    def direct_speed(self, left_speed, right_speed):
        """ Send motors speed value in range [-1,1]
            where 0 = neutral.
            WARNING: this method tells the motors
            to change speed IMEDIATELY without ramping. """

        # Calculate microseconds from command speed
        left_micros = self.left_servo.micros(left_speed)
        right_micros = self.right_servo.micros(right_speed)

        # Tell the Arduino to set motors to that speed immediately
        if self.arduino:
            self.arduino.direct_micros(left_micros, right_micros)
        else:
            self.PWMservo.set_servo(LEFT_SERVO_PIN, left_micros)
            self.PWMservo.set_servo(RIGHT_SERVO_PIN, right_micros)

    def set_neutral(self):
        """ Send neutral to the motors IMEDIATELY. """
        if self.arduino:
            self.arduino.direct_micros(self.LEFT_MID, self.RIGHT_MID)

    def read_sensor(self):
        """ Read a sensor value and return it. """
        if self.arduino:
            sensor_voltage = self.arduino.read_sensor()
            sensor_value = self.prox.translate(sensor_voltage)
        else:
            sensor_value = self.tof_left.get_distance()
        return sensor_value

    def stop(self):
        if self.arduino:
            self.arduino.direct_micros(self.LEFT_MID, self.RIGHT_MID)
        else:
            self.PWMservo.set_servo(LEFT_SERVO_PIN, self.LEFT_MID)
            self.PWMservo.set_servo(RIGHT_SERVO_PIN, self.RIGHT_MID)
