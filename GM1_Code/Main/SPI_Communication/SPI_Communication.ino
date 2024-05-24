#include <SPI.h>;

char buff[] = "Hello Slave\n";

void setup() {
  Serial.begin(9600);
  SPI.begin();
}

void loop() {
  for (int i = 0; i < sizeof buff; i++) {
    SPI.transfer(buff[i]);
  }
  Serial.println("Hello Slave__");
  delay(2000);
}