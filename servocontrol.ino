#include <Servo.h>

#define SERIAL_BOARD_RATE 9600

// Millisecond timeout. If timeout reached, neutral is automatically kicked in.v
#define SAFETY_TIMEOUT 5000
#define FULL_ACCEL_SECONDS 0.5

#define LEFT_MOTOR 0
#define RIGHT_MOTOR 1

// Pin possibilities [PWM: 3, 5, 6, 9, 10, and 11]
// WARNING: pins 5 and 6 share internal timer with 
// millis() and delay() functions so aren't a great choice.

// BLACK CABLE
#define LEFT_REVERSE_PIN 8
// BLUE CABLE
#define LEFT_MOTOR_PIN 9

// BROWN CABLE
#define RIGHT_MOTOR_PIN 10
// PINK CABLE
#define RIGHT_REVERSE_PIN 11

#define VSENSE_PIN A0

#define MAX_PARAMS 3

#define LED 2

int SERVO_MAX = 2100;
int SERVO_NEUTRALS[2] = {1450,1500};
int SERVO_MIN = 900;
bool m_bDebugMessages = false;
String m_szString;
double m_dMotors_Current_uS[2] = {SERVO_NEUTRALS[0], SERVO_NEUTRALS[1]};
double m_dMotors_Target_uS[2] = {SERVO_NEUTRALS[0], SERVO_NEUTRALS[1]};
int m_nLastMilli = 0;
int m_nLastMilliSerial = 0;
double m_duSPerMilliSec = 0.0;
double dRangeuS = (SERVO_MAX - SERVO_MIN) / 2.0;
bool LEDdebug = false;

// Servo-style motor controllers
Servo lServo;
Servo rServo;

void setup()
{
  // Configure USB serial
  Serial.begin(SERIAL_BOARD_RATE, SERIAL_8N1); // SERIAL_8N1
  while (!Serial) {
  }

  Serial.println("Marco");

  // Setup LED flash pin
  pinMode(LED, OUTPUT);

  pinMode(LEFT_MOTOR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_PIN, OUTPUT);
  pinMode(LEFT_REVERSE_PIN, OUTPUT);
  pinMode(RIGHT_REVERSE_PIN, OUTPUT);
  pinMode(VSENSE_PIN, INPUT);
  // Calculate acceleration based on number of seconds from zero to full throttle.
  calculate_acceleration(FULL_ACCEL_SECONDS);

  if (!LEDdebug) {
    lServo.attach(LEFT_MOTOR_PIN);
    rServo.attach(RIGHT_MOTOR_PIN);
  }
}

void calculate_acceleration(float fSeconds)
{
  // Calculate acceleration based on number of seconds from zero to full throttle.
  // [ratio of volts per second]
  m_duSPerMilliSec = dRangeuS / (fSeconds*1000.0);
}

void set_motor_target_speed( int nMotor, int targetuS )
{
  int capped_targetUS = targetuS;
  // Ensure speed is within [900,2100]
  if (capped_targetUS < SERVO_MIN)
    capped_targetUS = SERVO_MIN;
  if (capped_targetUS > SERVO_MAX)
    capped_targetUS = SERVO_MAX;
    
  // nMotor is index (L/R) and the speed is in range [-1,1]
  m_dMotors_Target_uS[nMotor] = capped_targetUS;
}

void set_motor_ACTUAL_speed( int nMotor, int targetuS )
{
  int capped_targetUS = targetuS;
  // Ensure speed is within [900,2100]
  if (capped_targetUS < SERVO_MIN)
    capped_targetUS = SERVO_MIN;
  if (capped_targetUS > SERVO_MAX)
    capped_targetUS = SERVO_MAX;
    
  // nMotor is index (L/R) and the speed is in range [-1,1]
  m_dMotors_Target_uS[nMotor] = capped_targetUS;
  m_dMotors_Current_uS[nMotor] = capped_targetUS;
}

int micros_to_byte( int imicros, boolean reverse )
{
  int zmicros = imicros - 900; // 0 - ~1200
  float f_speed = ((float)(zmicros)) / 1200; // 0-1
  if( !reverse) { f_speed = 1.0 - f_speed; }
  int b_speed = f_speed * 128;
  return b_speed;
}

void blink_LED(int nTimes)
{
  // Blink LED a set number of times.
  for (int i=0; i<nTimes; i++)
  {
    digitalWrite(LED, HIGH);
    delay(100);    
    digitalWrite(LED, LOW);
    delay(100);
  }
}

void parse_command()
{
  // Parse the command just read in and enact on it.

  // Parse command type from string
  int nParam = 0;
  String szParams[MAX_PARAMS];
  bool bReading = false;
  int nStrLength = m_szString.length();
  for (int i=0; i<nStrLength; i++)
  {
    char chChar = m_szString[i];
    if (chChar == '[')
      bReading = true; // Found start of command string
    else if (chChar == ',')
      nParam++; // Comma means we move to next parameter index.
    else if (chChar == ']' || chChar == '\0')
      i=nStrLength; // Stop parsing string
    else if (bReading)
      szParams[nParam] += chChar;
  }
  // Convert found string to command index
  int nCommand = 0;
  if (szParams[0].length())
    nCommand = szParams[0].toInt();
  else
    nCommand = -1; // If no command read, set to -1 so we know its not a valid command

  // Blink LED to count command index
  //blink_LED(nCommand);
  
  // Based on command type, read command parameters
  switch(nCommand)
  {
    // CHANGE MOTOR SPEED
    case 1:
    {
      // Blink when command recognised
      //blink_LED(nParam+1);
      
      if (nParam == 2) // NOTE, nParam is zero based index so 2 == 3 parameters.
      {
        // Pull left and right motor speeds from command string.
        int iLeftMotor = SERVO_NEUTRALS[0], iRightMotor = SERVO_NEUTRALS[1];
        if (szParams[1].length()) // Only convert to int if string has a length.
          iLeftMotor = szParams[1].toInt();
        if (szParams[2].length()) // Only convert to int if string has a length.
          iRightMotor = szParams[2].toInt();

        // Set new TARGET speed. Note, doesn't actually set motor voltages here.
        set_motor_target_speed(LEFT_MOTOR, iLeftMotor);
        set_motor_target_speed(RIGHT_MOTOR, iRightMotor);
      }
    }break;

    case 2:
    {
      // Set motor pulse width directly without the ramp-up faff.
      if (nParam == 2) // NOTE, nParam is zero based index so 2 == 3 parameters.
      {
        // Pull left and right motor speeds from command string.
        int iLeftMotor = SERVO_NEUTRALS[0], iRightMotor = SERVO_NEUTRALS[1];
        if (szParams[1].length()) // Only convert to int if string has a length.
          iLeftMotor = szParams[1].toInt();
        if (szParams[2].length()) // Only convert to int if string has a length.
          iRightMotor = szParams[2].toInt();

        // Set new TARGET speed. Note, doesn't actually set motor voltages here.
        set_motor_target_speed(LEFT_MOTOR, iLeftMotor);
        set_motor_target_speed(RIGHT_MOTOR, iRightMotor);

        set_motor_ACTUAL_speed(LEFT_MOTOR, iLeftMotor);
        set_motor_ACTUAL_speed(RIGHT_MOTOR, iRightMotor);        
      }      
    } break;

    case 3:
    {
      // Set servo controller midpoints
      if (nParam == 2) // need three numbers: [3, left servo mid, right servo mid]
      {
        SERVO_NEUTRALS[0] = szParams[1].toInt();
        SERVO_NEUTRALS[1] = szParams[2].toInt();
      }
    } break;

    case 4:
    {
      // Read analog sensor on A0, return value over serial
      long v_in = analogRead(VSENSE_PIN);  
      delay(20);
      Serial.println( v_in );
    }
  }
}

void read_command()
{
  // Read serial comms if available
  bool bReadCMDEnd = false;
  while (Serial.available()>0)
  {
    // Blink for each character read
    //blink_LED(1);

    char chChar = Serial.read();
    m_szString += chChar;

    if (chChar == ']')
      bReadCMDEnd = true;
  }
  
  // If we have read a command, attempt to parse out the details
  if (bReadCMDEnd)
  {
    // Blink when end of command read
    //blink_LED(1);
    
    parse_command();
    m_szString = ""; // clear out string
    // Store time when we last recieved a command over serial comms.
    m_nLastMilliSerial = millis();
  }
}

void loop()
{
  // Read serial comms if available
  read_command();

  // First time ever into this loop.
  // Ensure millis is time NOW.
  int nMillis = millis();
  if (m_nLastMilli == 0)
    m_nLastMilli = nMillis;

  // Safety cutout timer
  int nSerialDiff = nMillis-m_nLastMilliSerial;
  if (nSerialDiff>SAFETY_TIMEOUT)
  {
    // Serial comms last sent recognised message over a second ago, can't 
    // be sure comms have failed so set motors into neutral.
    m_dMotors_Target_uS[LEFT_MOTOR] = SERVO_NEUTRALS[0];
    m_dMotors_Target_uS[RIGHT_MOTOR] = SERVO_NEUTRALS[1];

    // Turn on LED when in safety cutout mode
    digitalWrite(LED, HIGH);
  }
  else
    digitalWrite(LED, LOW);

  // Loop motors [L/R] and update current voltage value based on acceleration ramps.
  int nMilliDiff = nMillis-m_nLastMilli;
  if (nMilliDiff>0)
  {
    int nMotor = 0;
    int nMotors = 2;
    for (nMotor = 0; nMotor < nMotors; nMotor++)
    {
      // Calculate difference from current value and target value.
      int iDiff = m_dMotors_Target_uS[nMotor] - m_dMotors_Current_uS[nMotor];
      if (fabs(iDiff) > 1)
      {
        double duSIncrease = m_duSPerMilliSec * ((double)nMilliDiff);
        if (iDiff<0.0)
          duSIncrease = -duSIncrease; // Invert difference to decelerate
        m_dMotors_Current_uS[nMotor] += (int)duSIncrease;

        // Ensure voltage is capped to min/max
        if (m_dMotors_Current_uS[nMotor]<SERVO_MIN)
          m_dMotors_Current_uS[nMotor] = SERVO_MIN;
        if (m_dMotors_Current_uS[nMotor]>SERVO_MAX)
          m_dMotors_Current_uS[nMotor] = SERVO_MAX;
      }
    }
  }
  
  if (!LEDdebug) {
    lServo.writeMicroseconds( m_dMotors_Current_uS[LEFT_MOTOR] );
    rServo.writeMicroseconds( m_dMotors_Current_uS[RIGHT_MOTOR] );
  }
  else
  {
    analogWrite(LEFT_MOTOR_PIN, micros_to_byte(m_dMotors_Current_uS[LEFT_MOTOR], true));
    analogWrite(RIGHT_MOTOR_PIN, micros_to_byte(m_dMotors_Current_uS[RIGHT_MOTOR], false));
  }

  // Blink once each time round loop for status.
  //blink_LED(1);
    
  // Must always update nLastMilli!
  m_nLastMilli = nMillis;
}
