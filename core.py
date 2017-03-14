from __future__ import division
import servo_control
import arduino
# import sensor
import i2c_lidar
# from RPIO import PWM
from ctypes import *

LIDAR_PIN = 4
LEFT_SERVO_PIN = 17
RIGHT_SERVO_PIN = 27


""" Initialisation code for I2C Time Of Flight sensor """


def i2c_read(address, reg, data_p, length):
    """ i2c bus read callback """
    ret_val = 0
    result = []

    try:
        result = i2cbus.read_i2c_block_data(address, reg, length)
    except IOError:
        ret_val = -1

    if (ret_val == 0):
        for index in range(length):
            data_p[index] = result[index]

    return ret_val


def i2c_write(address, reg, data_p, length):
    """ i2c bus write callback """
    ret_val = 0
    data = []

    for index in range(length):
        data.append(data_p[index])
    try:
        i2cbus.write_i2c_block_data(address, reg, data)
    except IOError:
        ret_val = -1

    return ret_val


# Load VL53L0X shared lib
tof_lib = CDLL("./VL53L0X_rasp_python/bin/vl53l0x_python.so")

# Create read function pointer
READFUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
read_func = READFUNC(i2c_read)

# Create write function pointer
WRITEFUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
write_func = WRITEFUNC(i2c_write)

# pass i2c read and write function pointers to VL53L0X library
tof_lib.VL53L0X_set_i2c(read_func, write_func)


""" End of initialisation code for I2C Time Of Flight sensor """


class Core():
    """ Instantiate a 2WD drivetrain, utilising 2x ESCs,
        controlled using a 2 axis (throttle, steering)
        system + skittle accessories """

    def __init__(self, i2cbus):
        """ Constructor """
        self.i2cbus = i2cbus

        # Minimum and maximum theoretical pulse widths. Ignore reversing here
        # ESC "DB1" midpoint is about 1440
        # ESC "DB2" midpoint is 1500
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
            self.LEFT_MIN,
            self.LEFT_MID,
            self.LEFT_MAX, True)
        self.right_servo = servo_control.Servo_Controller(
            self.RIGHT_MIN,
            self.RIGHT_MID,
            self.RIGHT_MAX, False)

        self.left_aux_1_servo = servo_control.Servo_Controller(
            self.LEFT_AUX_1_MIN,
            self.LEFT_AUX_1_MID,
            self.LEFT_AUX_1_MAX, False)
        self.right_aux_1_servo = servo_control.Servo_Controller(
            self.RIGHT_AUX_1_MIN,
            self.RIGHT_AUX_1_MID,
            self.RIGHT_AUX_1_MAX, False)

        self.left_channel = 1
        self.right_channel = 2

        # Proximity sensor: roughly cm from closest measurable point
        # self.tof_left = sensor.Sensor(0, 450, 20, 0)
        # self.PWMservo = PWM.Servo(pulse_incr_us=1)

        # Always set these to None for initialisation
        self.PWMservo = None
        self.arduino = None

        self.arduino_mode = 0  # Not using Arduino

        if (self.arduino_mode == 1):
            self.arduino = arduino.Arduino()
        else:
            self.arduino = None
            # self.PWMservo = PWM.Servo(pulse_incr_us=1)
            # i2c_lidar.xshut([LIDAR_PIN])
            # self.tof_left = i2c_lidar.create(LIDAR_PIN, tof_lib, 0x2a)

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
            if self.PWMservo:
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
            if self.PWMservo:
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
            if self.PWMservo:
                self.PWMservo.set_servo(LEFT_SERVO_PIN, self.LEFT_MID)
                self.PWMservo.set_servo(RIGHT_SERVO_PIN, self.RIGHT_MID)
