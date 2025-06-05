#include "SmartServoBus.hpp"
#include "RBCX.h"
#include <Arduino.h>
//#include <thread>
auto &man = rb::Manager::get(); // pro fungovani RBCX
#include "Grabber.hpp"
#include "Comunication.hpp"
#include "Movement.hpp"
#include "Sensors.hpp"

Grabber grab;
Movement move;
Communication comm;
Sensors sens;

void WaitForStart()
{
    while (true)
    {
        if (man.buttons().on() == 1)
        {
            break;
        }
        delay(10);
    }
}

void CheckBattery()
{
    const auto &bat = man.battery();
    static const uint32_t VOLTAGE_MAX = 7500; //%edit
    static const uint32_t VOLTAGE_MIN = 6600; //%edit
    int i = 0;
    int voltage = 0;
    for (i = 0; i < 2; ++i)
    {
        voltage = bat.voltageMv();
        // Vypočítej procenta (omez na 0-100)
        int pct = (voltage - VOLTAGE_MIN) * 100 / (VOLTAGE_MAX - VOLTAGE_MIN);
        if (pct > 100)
            pct = 100;
        if (pct < 0)
            pct = 0;

        if (i > 0)
        {
            printf("Battery at %d%%, %dmv\n", pct, voltage);
            if (voltage < VOLTAGE_MIN)
            {
                printf("Je třeba nabít baterii!\n");
            }
        }
        delay(1000);
    }
}

// #define LED_PIN 15
// #define NUM_LEDS 8
// CRGB leds[NUM_LEDS];

void setup()
{
    Serial.begin(115200);

    auto &man = rb::Manager::get(); // get manager instance as singleton
    man.install();                  // install manager

    // servoBus.begin(2, UART_NUM_1, GPIO_NUM_27);
    // servoBus.setAutoStop(0, false); // vypne autostop leveho serva
    // servoBus.setAutoStop(1, false); // vypne autostop praveho serva
    // man.leds().yellow(true);

    // comm.WaitForDistanceData();

    // if (comm.distance_px == 1)
    // {
    //     man.leds().red(true);
    // }

    //  cekani na zpravu z Raspberry
    // while (true)
    // {
    //     Serial.printf(" US_Right %i \n", sens.GetUS(sens.RIGHT));
    //     Serial.printf(" US_Left %i \n", sens.GetUS(sens.LEFT));
    //     Serial.printf(" US_Back %i \n", sens.GetUS(sens.BACK));
    //     delay(1000);
    // }

    // comm.WaitForData(); // cekani na zpravu z Raspberry
    // CheckBattery();

    // WaitForStart();

    // move.Straight(1000, 1000, 1000);
    //  move.BackwardUntillWall();
    //       grab.Close();
    //       delay(2000);
    //       grab.Open();
    //       delay(2000);
    //       grab.Close();
}

bool cekamNaData = true;

void loop() {
    static bool cervenaLed = false;

    if (cekamNaData) {
        if (Serial.available() > 0) {
            String data = Serial.readStringUntil('\n');
            comm.distance_px = std::atoi(data.c_str());
            cekamNaData = false;

            if (comm.distance_px == 1) {
                man.leds().red(true);
                cervenaLed = true;
            }
        }
    }

    // LEDky zůstanou svítit
    man.leds().yellow(true);
    if (cervenaLed) man.leds().red(true);

}