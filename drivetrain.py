from __future__ import division
import logging
from numpy import interp, clip
import servo_control, arduino, sensor

# Minimum and maximum theoretical pulse widths. Ignore reversing here
# ESC "DB1" midpoint is about 1440
# ESC "DB2" midpoint is 1500
LEFT_MIN = 940
RIGHT_MIN = 1000

LEFT_MID = 1440
RIGHT_MID = 1500

LEFT_MAX = 1940
RIGHT_MAX = 2000


class DriveTrain():
    """Instantiate a 2WD drivetrain, utilising 2x ESCs,
    controlled using a 2 axis (throttle, steering)
    system + skittle accessories"""
    def __init__(
        self,
    ):
        self.left_servo = servo_control.Servo_Controller(LEFT_MIN, LEFT_MID, LEFT_MAX, True)
        self.right_servo = servo_control.Servo_Controller(RIGHT_MIN, RIGHT_MID, RIGHT_MAX, False)
        self.left_channel = 1
        self.right_channel = 2
        # Proximity sensor: roughly cm from closest measurable point
        self.prox = sensor.Sensor(0, 450, 20, 0)
        self.arduino = arduino.Arduino()
        
    def enable_motors(self, enable):
        # Do nothing for now, only send pulse train once motors driven
        print("Motors enabled, clibrating %d, %d" % ( LEFT_MID, RIGHT_MID ))
        self.arduino.calibrate_motors(LEFT_MID, RIGHT_MID);
        
    def throttle(self, left_speed, right_speed):
        # Calculate microseconds from command speed
        left_micros = self.left_servo.micros(left_speed)
        right_micros = self.right_servo.micros(right_speed)

        # Tell the Arduino to move to that speed (eventually)
        self.arduino.throttle(left_micros, right_micros)
        
    def direct_speed(self, left_speed, right_speed):
        # Calculate microseconds from command speed
        left_micros = self.left_servo.micros(left_speed)
        right_micros = self.right_servo.micros(right_speed)
        
        # Tell the Arduino to set motors to that speed immediately
        self.arduino.direct_micros(left_micros, right_micros)
        
    def stop(self):
        self.arduino.direct_micros(LEFT_MID, RIGHT_MID)

    def read_sensor(self):
        sensor_voltage = self.arduino.read_sensor()
        sensor_value = self.prox.translate(sensor_voltage)
        return sensor_value
