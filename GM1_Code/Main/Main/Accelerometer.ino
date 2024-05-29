// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>


Adafruit_MPU6050 mpu;

/* 
  MPU6050_RANGE_2_G = +/- 2g (default value)
  MPU6050_RANGE_4_G = +/- 4g
  MPU6050_RANGE_8_G = +/- 8g
  MPU6050_RANGE_16_G = +/- 16g

  MPU6050_RANGE_250_DEG = +/- 250 deg/s (default value)
  MPU6050_RANGE_500_DEG = +/- 500 deg/s
  MPU6050_RANGE_1000_DEG = +/- 1000 deg/s
  MPU6050_RANGE_2000_DEG = +/- 2000 deg/s

  MPU6050_BAND_260_HZ < Docs imply this disables the filter
  MPU6050_BAND_184_HZ < 184 Hz
  MPU6050_BAND_94_HZ  < 94 Hz
  MPU6050_BAND_44_HZ  < 44 Hz
  MPU6050_BAND_21_HZ  < 21 Hz
  MPU6050_BAND_10_HZ  < 10 Hz
  MPU6050_BAND_5_HZ   < 5 Hz
*/
void set_accel (void){
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

// Get accel, gyro and temp by using a.acceleration.x(y,z), g.gyro.x(y,z), temp.temperatur
double get_accel (void){

  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  double mag = (sqrt(sq(a.acceleration.x)+sq(a.acceleration.y)+sq(a.acceleration.z)));
  return mag;
  // Serial.print("AccelX:");
  // Serial.print(a.acceleration.x);
  // Serial.print(",");
  // Serial.print("AccelY:");
  // Serial.print(a.acceleration.y);
  // Serial.print(",");
  // Serial.print("AccelZ:");
  // Serial.print(a.acceleration.z);
  // Serial.print(", ");
  // Serial.print("GyroX:");
  // Serial.print(g.gyro.x);
  // Serial.print(",");
  // Serial.print("GyroY:");
  // Serial.print(g.gyro.y);
  // Serial.print(",");
  // Serial.print("GyroZ:");
  // Serial.print(g.gyro.z);
  // Serial.println("");

}

