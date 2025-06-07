#include "SmartServoBus.hpp"
#include "RBCX.h"
#include <Arduino.h>
struct Communication
{
  int angle_deg;
  int distance_px;

  void WaitForOffSetData()
  {
    while (true)
    {
      if (Serial.available() > 0)
      {
        int num;
        String data = Serial.readStringUntil('\n');
        const char *daata = data.c_str();
        num = std::atoi(daata);
        angle_deg = num;
        man.leds().yellow(true); // rozsviti zelenou diodu
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
        int num;
        String data = Serial.readStringUntil('\n');
        const char *daata = data.c_str();
        num = std::atoi(daata);
        distance_px = num;

        man.leds().green(true); // rozsviti zelenou diodu

        break;
      }
      delay(10);
    }
  }
};
