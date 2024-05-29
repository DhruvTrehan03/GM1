#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>



int32_t SPO2; //SPO2
int8_t SPO2Valid; //Flag to display if SPO2 calculation is valid
int32_t heartRate; //Heart-rate
int8_t heartRateValid; //Flag to display if heart-rate calculation is valid 

void setup() {
  Serial.begin(115200);
  set_spo2();
  set_accel();
  
}

void loop() {
  
  get_spo2();
  Serial.print(SPO2Valid);
  Serial.print(", ");
  Serial.print(SPO2);
  Serial.print(", ");
  Serial.print(heartRateValid);
  Serial.print(", ");
  Serial.print(heartRate);
  Serial.print(", ");
  /* Get new sensor events with the readings */
  Serial.println(get_accel());
  delay(10);
  
}
