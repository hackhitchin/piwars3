from __future__ import division
# import logging
import servo_control
import arduino
import sensor

# Minimum and maximum theoretical pulse widths. Ignore reversing here
# ESC "DB1" midpoint is about 1440
# ESC "DB2" midpoint is 1500
LEFT_MIN = 940
RIGHT_MIN = 1000

LEFT_MID = 1440
RIGHT_MID = 1500

LEFT_MAX = 1940
RIGHT_MAX = 2000


class Core():
    """ Instantiate a 2WD drivetrain, utilising 2x ESCs,
        controlled using a 2 axis (throttle, steering)
        system + skittle accessories """

    def __init__(self):
        """ Constructor """
        self.left_servo = servo_control.Servo_Controller(
            LEFT_MIN, LEFT_MID, LEFT_MAX, True)
        self.right_servo = servo_control.Servo_Controller(
            RIGHT_MIN, RIGHT_MID, RIGHT_MAX, False)
        self.left_channel = 1
        self.right_channel = 2
        # Proximity sensor: roughly cm from closest measurable point
        self.prox = sensor.Sensor(0, 450, 20, 0)
        self.arduino = arduino.Arduino()

    def enable_motors(self, enable):
        """ Called when we want to enable/disable the motors.
            When disabled, will ignore any new motor commands. """

        # Send motor neutral if disabling.
        if not enable:
            self.stop()

        # AFTER we have sent neutral, enable/disable motors
        self.arduino.enable_motors(enable)

    def throttle(self, left_speed, right_speed):
        """ Send motors speed value in range [-1,1]
            where 0 = neutral """

        # Calculate microseconds from command speed
        left_micros = self.left_servo.micros(left_speed)
        right_micros = self.right_servo.micros(right_speed)

        # Tell the Arduino to move to that speed (eventually)
        self.arduino.throttle(left_micros, right_micros)

    def direct_speed(self, left_speed, right_speed):
        """ Send motors speed value in range [-1,1]
            where 0 = neutral.
            WARNING: this method tells the motors
            to change speed IMEDIATELY without ramping. """

        # Calculate microseconds from command speed
        left_micros = self.left_servo.micros(left_speed)
        right_micros = self.right_servo.micros(right_speed)

        # Tell the Arduino to set motors to that speed immediately
        self.arduino.direct_micros(left_micros, right_micros)

    def stop(self):
        """ Send neutral to the motors IMEDIATELY. """
        self.arduino.direct_micros(LEFT_MID, RIGHT_MID)

    def read_sensor(self):
        """ Read a sensor value and return it. """
        sensor_voltage = self.arduino.read_sensor()
        sensor_value = self.prox.translate(sensor_voltage)
        return sensor_value
