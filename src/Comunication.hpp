#include "SmartServoBus.hpp"
#include "RBCX.h"
#include <Arduino.h>
struct Communication
{
  int angle_deg;
  int distance_px;

  void WaitForAngleData()
  {
    while (true)
    {
      if (Serial.available() > 0)
      {
        man.leds().red(true);
        String data = Serial.readStringUntil('\n');
        const char *daata = data.c_str();
        int num = std::atoi(daata);
        angle_deg = num;
        break;
      }
    }
  }

  void WaitForDistanceData()
  {
    while (true)
    {
      if (Serial.available() > 0)
      {
        String data = Serial.readStringUntil('\n');
        const char *daata = data.c_str();
        int num = std::atoi(daata);
        distance_px = num;
        break;
      }
      delay(10);
    }
  }
};
