from __future__ import division
import servo_control
import arduino
# import sensor
import i2c_lidar

from RPIO import PWM
from ctypes import *
from enum import Enum

LIDAR_PINS = [18, 15, 14]
LIDAR_LEFT = 0
LIDAR_FRONT = 1
LIDAR_RIGHT = 2

LEFT_MOTOR_ESC_PIN = 17
RIGHT_MOTOR_ESC_PIN = 27

LEFT_AUX_ESC_PIN = 0
RIGHT_AUX_ESC_PIN = 0

LEFT_FLINGER_ESC_PIN = 0
RIGHT_FLINGER_ESC_PIN = 0

LEFT_FLINGER_SERVO_PIN = 0
RIGHT_FLINGER_SERVO_PIN = 0

WINCH_SERVO_PIN = 0


class ServoEnum(Enum):
    # Enum listing each servo that we can control
    SERVO_NONE = 0
    LEFT_MOTOR_ESC = 1
    RIGHT_MOTOR_ESC = 2
    LEFT_AUX_ESC = 3
    RIGHT_AUX_ESC = 4
    LEFT_FLINGER_ESC = 5
    RIGHT_FLINGER_ESC = 6
    LEFT_FLINGER_SERVO = 7
    RIGHT_FLINGER_SERVO = 8
    WINCH_SERVO = 9


class Core():
    """ Instantiate a 2WD drivetrain, utilising 2x ESCs,
        controlled using a 2 axis (throttle, steering)
        system + skittle accessories """

    def __init__(self, tof_lib):
        """ Constructor """

        self.tof_lib = tof_lib
        # Create a list of servo's
        self.servos = dict()
        # Add Motor Servo's. NOTE: Left motor esc is reversed.
        self.servos[ServoEnum.LEFT_MOTOR_ESC] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=True
            ), LEFT_MOTOR_ESC_PIN, 'Left Motor']
        self.servos[ServoEnum.RIGHT_MOTOR_ESC] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=False
            ), RIGHT_MOTOR_ESC_PIN, 'Right Motor']

        # Add Auxilary servo's. NOTE: Aux esc's are not reversed.
        self.servos[ServoEnum.LEFT_AUX_ESC] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=False
            ), LEFT_AUX_ESC_PIN, 'Left Aux']
        self.servos[ServoEnum.RIGHT_AUX_ESC] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=False
            ), RIGHT_AUX_ESC_PIN, 'Right Aux']

        # Add Auxilary servo's. NOTE: Ball Flinger esc's are not reversed.
        self.servos[ServoEnum.LEFT_FLINGER_ESC] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=False
            ), LEFT_FLINGER_ESC_PIN, 'Left Flinger ESC']
        self.servos[ServoEnum.RIGHT_FLINGER_ESC] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=False
            ), RIGHT_FLINGER_ESC_PIN, 'Right Flinger ESC']

        # Add Auxilary servo's. NOTE: Ball Flinger esc's are not reversed.
        self.servos[ServoEnum.LEFT_FLINGER_SERVO] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=False
            ), LEFT_FLINGER_SERVO_PIN, 'Left Flinger Servo']
        self.servos[ServoEnum.RIGHT_FLINGER_SERVO] = [
            servo_control.Servo_Controller(
                min=800, mid=1300, max=1800, bReverse=False
            ), RIGHT_FLINGER_SERVO_PIN, 'Right Flinger Servo']

        # Add Auxilary servo's. NOTE: Aux 4 servo is not reversed.
        self.servos[ServoEnum.WINCH_SERVO] = [servo_control.Servo_Controller(
            min=800, mid=1300, max=1800, bReverse=False
        ), WINCH_SERVO_PIN, 'Winch']

        # Always set these to None for initialisation
        self.PWMservo = None
        self.arduino = None

        self.arduino_mode = 0  # Not using Arduino
        self.lidars = []

        if (self.arduino_mode == 1):
            self.arduino = arduino.Arduino()
        else:
            self.arduino = None
            self.PWMservo = PWM.Servo(pulse_incr_us=1)

        self.enable_lidar()

    def enable_motors(self, enable):
        """ Called when we want to enable/disable the motors.
            When disabled, will ignore any new motor commands. """
        # Send motor neutral if disabling.
        if not enable:
            self.set_neutral()

        # AFTER we have sent neutral, enable/disable motors
        if self.arduino:
            self.arduino.enable_motors(enable)

    def throttle(self,
                 left_speed,
                 right_speed,
                 left_servo=ServoEnum.LEFT_MOTOR_ESC,
                 right_servo=ServoEnum.RIGHT_MOTOR_ESC):
        """ Send motors speed value in range [-1,1]
            where 0 = neutral """

        # Calculate microseconds from command speed
        left_micros = 0
        right_micros = 0
        try:
            if left_servo != ServoEnum.SERVO_NONE:
                left_micros = self.servos[left_servo][0].micros(left_speed)
            if right_servo != ServoEnum.SERVO_NONE:
                right_micros = self.servos[right_servo][0].micros(right_speed)
        except:
            print("Failed to get servo throttle micros")

        # Tell the Arduino to move to that speed (eventually)
        if self.arduino:
            self.arduino.throttle(left_micros, right_micros)
        else:
            if self.PWMservo:
                # TODO: make this ramp speeds using RPIO
                try:
                    if left_servo != ServoEnum.SERVO_NONE:
                        self.PWMservo.set_servo(
                            self.servos[left_servo][1],
                            left_micros)
                    if right_servo != ServoEnum.SERVO_NONE:
                        self.PWMservo.set_servo(
                            self.servos[right_servo][1],
                            right_micros)
                except:
                    print("Failed to set servo throttle micros")

    def set_neutral(self,
                    left_servo=ServoEnum.LEFT_MOTOR_ESC,
                    right_servo=ServoEnum.RIGHT_MOTOR_ESC):
        """ Send neutral to the motors IMEDIATELY. """
        try:
            if left_servo != ServoEnum.SERVO_NONE:
                left_mid = self.servos[left_servo][0].servo_mid
            if right_servo != ServoEnum.SERVO_NONE:
                right_mid = self.servos[right_servo][0].servo_mid
        except:
            print("Failed to get servo enum values")

        if self.arduino:
            self.arduino.direct_micros(left_mid, right_mid)
        else:
            # Need to send 0 speed to motors if neutral selected.
            try:
                if left_servo != ServoEnum.SERVO_NONE:
                    self.PWMservo.set_servo(
                        self.servos[left_servo][1],
                        left_mid)
                if right_servo != ServoEnum.SERVO_NONE:
                    self.PWMservo.set_servo(
                        self.servos[right_servo][1],
                        right_mid)
            except:
                print("Failed to set servo neutral PWM values")

    def read_sensor(self, pin):
        """ Read a sensor value and return it. """
        if self.arduino:
            sensor_voltage = self.arduino.read_sensor()
            sensor_value = self.prox.translate(sensor_voltage)
        else:
            sensor_value = self.lidars[pin].get_distance()
        return sensor_value

    def stop(self):
        self.set_neutral()

    def enable_lidar(self):
        # I2C lidar sensors should be enabled
        # in both Arduino mode or direct pi mode.
        # I know this is all kinds of redundant but it worked on the hardware
        # so it's staying
        for pin in range(0, 3):
            i2c_lidar.xshut([LIDAR_PINS[pin]])
        for pin in range(0, 3):
            self.lidars.append(
                i2c_lidar.create(LIDAR_PINS[pin], self.tof_lib, 0x2a + pin)
            )
