#include <Arduino.h>
#include <avr/wdt.h>
#include "gpio_router.h"

int i;
String data;
String relay_state = "0000";
unsigned char relay_pin[4] = {4, 7, 8, 12};

void (*resetFunc)(void) = 0;  //declare reset function at address 0

void setRelays(String relay_data) {
  bool is_valid = true;
  if (relay_data.length() != 4) {
    Serial.println("problem in set command");
    return;
  }

  for (i = 0; i < 4; i++) {
    if (relay_data[i] != '0' && relay_data[i] != '1') is_valid = false;
  }

  if (is_valid) {
    for (i = 0; i < 4; i++) {
      digitalWrite(relay_pin[i], int(relay_data[i]) - '0');
    }
    relay_state = relay_data;
    Serial.println("success");
  }
  else Serial.println("problem in set command");
}

void softwareReset(uint8_t prescaller) {
  // start watchdog with the provided prescaller
  wdt_enable(prescaller);
  // wait for the prescaller time to expire
  // without sending the reset signal by using
  // the wdt_reset() method
  while (1) {}
}

void setup() {
  Serial.setTimeout(10);
  Serial.begin(BAUDRATE);  // Start the Serial monitor with speed of 9600 Bauds
  delay(1);
  Serial.print(GPIO_ROUTER_NAME);
  Serial.print(' ');
  Serial.println(GPIO_ROUTER_VERSION);
  delay(5);
  for (i = 0; i < 4; i++) {
    pinMode(relay_pin[i], OUTPUT);
    digitalWrite(relay_pin[i], 0);
  }
}

void loop() {
  while (Serial.available() > 0) {  // Check if values are available in the Serial Buffer
    data = Serial.readString();     //Read the incoming data & store into data
    if (data == GET_NAME) Serial.println(GPIO_ROUTER_NAME);
    else if (data == GET_VERSION) Serial.println(GPIO_ROUTER_VERSION);
    else if (data == RESET) softwareReset(WDTO_60MS);  //call reset
    else if (data.startsWith(SET_GPIO)) setRelays(data.substring(strlen(SET_GPIO)));
    else if (data == GET_GPIO) Serial.println(relay_state);
    else Serial.println("command not supported");
  }
}
