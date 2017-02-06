import serial


# Mixer and serial comms
class DriveTrain:
    def __init__(self):
        """Constructor"""
        self.enabled = False
        self.motor_left = 0
        self.motor_right = 0

        # self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.ser = serial.Serial(
            "/dev/ttyUSB0",
            baudrate=57600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            writeTimeout=0,
            timeout=10,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False)
        data = self.ser.readline()
        print(data)

    def stop(self):
        """Called when we want to shut down."""
        if self.ser:
            self.ser.close()

    def mix_tank(self, lx, ly, rx, ry):
        """Mix [-1,1] values for Left and Right X,Y axis"""
        # Worlds simplest mixer, for tank driving only
        # need to send ly and ry direct to motors.
        self.motor_left = ly
        self.motor_right = ry

    def mix_channels_and_send(self, lx, ly, rx, ry):
        """Mix axis and send the motors"""
        # Send left and right axis values to appropriate mixer
        self.mix_tank(lx, ly, rx, ry)
        # Left and Right motor values will
        # have been updated by above method
        self.send_to_motors()

    def send_neutral_to_motors(self):
        if self.ser:
            # Can send neutral even when motors disabled
            command = "[0]\n"
            print(command)
            self.ser.write(command)
            # result = self.ser.readline()
            # print(result)

    def fire_laser(self):
        """Send laser on value to arduino.
           Laser will fire for pre-determined time."""
        if self.ser:
            command = "[2]\n"
            print(command)
            self.ser.write(command)

    def send_to_motors(self):
        """Send motor Left and Right values to arduino"""
        if self.enabled and self.ser:
            command = "[1,%f,%f]\n" % (self.motor_left, self.motor_right)
            print(command)
            self.ser.write(command)
            # esult = self.ser.readline()
            # print(result)

    def set_neutral(self):
        """Set motors to neutral"""
        self.motor_left = 0
        self.motor_right = 0
        self.send_neutral_to_motors()
        # self.send_to_motors()

    def enable_motors(self, enable):
        """Enable or disable motors"""
        self.enabled = enable
        # If now disabled, send neutral to motors
        if not self.enabled:
            self.set_neutral()

    def send_command_motors(self, command):
        """Send motor Left and Right values to arduino"""
        if self.ser:
            print(command)
            self.ser.write(command)
            # Retrieve result straight away
            data = self.ser.readline()
            print(data)
