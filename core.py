from __future__ import division
import servo_control
# import arduino
import sensor


class Core():
    """ Instantiate a 2WD drivetrain, utilising 2x ESCs,
        controlled using a 2 axis (throttle, steering)
        system + skittle accessories """

    def __init__(self):
        """ Constructor """

        # Minimum and maximum theoretical pulse widths. Ignore reversing here
        # ESC "DB1" midpoint is about 1440
        # ESC "DB2" midpoint is 1500
        self.LEFT_MIN = 940
        self.LEFT_MID = 1440
        self.LEFT_MAX = 1940

        self.RIGHT_MIN = 1000
        self.RIGHT_MID = 1500
        self.RIGHT_MAX = 2000

        self.LEFT_AUX_1_MIN = 940
        self.LEFT_AUX_1_MID = 1440
        self.LEFT_AUX_1_MAX = 1940

        self.RIGHT_AUX_1_MIN = 1000
        self.RIGHT_AUX_1_MID = 1500
        self.RIGHT_AUX_1_MAX = 2000

        self.left_servo = servo_control.Servo_Controller(
            self.LEFT_MIN, self.LEFT_MID, self.LEFT_MAX, True)
        self.right_servo = servo_control.Servo_Controller(
            self.RIGHT_MIN, self.RIGHT_MID, self.RIGHT_MAX, False)

        # self.left_channel = 1
        # self.right_channel = 2

        # Proximity sensor: roughly cm from closest measurable point
        self.prox = sensor.Sensor(0, 450, 20, 0)

        # self.arduino = arduino.Arduino()
        self.arduino = None

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
            sensor_value = None
        return sensor_value
