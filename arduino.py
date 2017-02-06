import serial
from time import sleep

MESSAGE_THROTTLE = 1
MESSAGE_DIRECT = 2
MESSAGE_CALIBRATE = 3


class Arduino():
    def __init__(self):
        
        self.ser = serial.Serial(
            "/dev/ttyUSB0",
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            writeTimeout=0,
            timeout=10,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False)

        while (self.ser.readline() == ""):
             print("Waiting for serial")
        print ("Got serial input, now we can continue")
        self.ser.write("Hello")            
            
    def throttle(self, left_micros, right_micros):
        command = "[%d, %d, %d]\n" % (MESSAGE_THROTTLE, left_micros, right_micros)
        self.ser.write(command)
        print("Writing %s" % command )

    def direct_micros(self, left_micros, right_micros):
        command = "[%d, %d, %d]\n" % (MESSAGE_DIRECT, left_micros, right_micros)
        print("Writing %s" % command )
        self.ser.write(command)
        
    def calibrate_motors(self, left_mid, right_mid):
        command = "[%d, %d, %d]\n" % (MESSAGE_CALIBRATE, left_mid, right_mid)
        self.ser.write(command)
        print("Writing %s" % command )

    def read_sensor(self):
        command = "[4]"
        self.ser.write(command)
        print("Writing %s" % command )
        s = self.ser.readline() # Of the format "(A,xxx)\n"
        s_value = s
        print("Read sensor %s" % s_value )
        try:
            i_value = int(s_value)
            return i_value
        except:
            print( "Cannot parse message %s as number, returning 0" % s_value) 
            return 0
