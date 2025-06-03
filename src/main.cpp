#include "SmartServoBus.hpp"
#include "RBCX.h"
#include <Arduino.h>
#include <thread>
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

void setup()
{
    Serial.begin(115200);

    auto &man = rb::Manager::get(); // get manager instance as singleton
    man.install();                  // install manager

    servoBus.begin(2, UART_NUM_1, GPIO_NUM_27);
    servoBus.setAutoStop(0, false); // vypne autostop leveho serva
    servoBus.setAutoStop(1, false); // vypne autostop praveho serva

    sens.InitRGB(); // inicializace
    sens.LEDsSetColor(CRGB::White); // nastav LED na cernou
    
    while (true)
    {
        Serial.printf(" US_Right %i \n", sens.GetUS(sens.RIGHT));
        Serial.printf(" US_Left %i \n", sens.GetUS(sens.LEFT));
        Serial.printf(" US_Back %i \n", sens.GetUS(sens.BACK));
        delay(1000);
    }
    
    
    comm.WaitForData(); // cekani na zpravu z Raspberry

    //WaitForStart();
    //man.leds().red(true);
    // move.Straight(1000, 1000, 1000);
    // move.BackwardUntillWall();
    //grab.Close();
    //delay(2000);
    //grab.Open();
    //delay(2000);
    //grab.Close();
}
void loop() {}