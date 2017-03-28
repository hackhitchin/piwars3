#include <Wire.h>
#define uchar unsigned char
uchar t;
//void send_data(short a1,short b1,short c1,short d1,short e1,short f1);
uchar data[16];
String m_szString;

void setup()
{
  Wire.begin();        // join i2c bus (address optional for master)
  Serial.begin(9600);  // start serial for output
  t = 0;
  m_szString = ""; // clear out string
}

bool read_command()
{
  // Read command from serial
  m_szString = ""; // clear out string
  bool bReadCMDEnd = false;
  while (Serial.available()>0)
  {
    char chChar = Serial.read();
    m_szString += chChar;

    if (chChar == ']')
      bReadCMDEnd = true;
  }
  return bReadCMDEnd;
}

void loop()
{
  Wire.requestFrom(9, 16);    // request 16 bytes from slave device #9
  while (Wire.available())   // slave may send less than requested
  {
    data[t] = Wire.read(); // receive a byte as character
    if (t < 15)
      t++;
    else
      t = 0;
  }

  // Attempt to read command from serial
  if (read_command())
  {
    for (int i=0; i<8; i++)
    {
      //unsigned int word = ((unsigned int)data[(i*2)+1] << 8) + data[i*2];
      unsigned int word = ((unsigned int)data[(i*2)] << 8) + data[(i*2)+1];
      Serial.print(word);
      // Append splitter character between channels (but don't add one to the end)
      if (i < 7)
        Serial.print(",");
    }
    // Send string back through serial
    Serial.println("");
  }
  
  // Short 10ms delay between readings
  delay(10);
}
