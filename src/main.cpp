#include "SmartServoBus.hpp"
#include "RBCX.h"
#include <Arduino.h>
#include <thread>
#include <atomic>
#include <cmath>
std::atomic<bool> IsEnemy(false);

auto &man = rb::Manager::get(); // pro fungovani RBCX
#include "Grabber.hpp"
#include "Comunication.hpp"
#include "Movement.hpp"
#include "Sensors.hpp"

Grabber grab;
Movement move;
Communication comm;
Sensors sens;

enum Color
{
    RED,
    BLUE,
    NONE
};

Color color = NONE;

uint16_t pixel_to_mm(uint16_t px)
{
    return px * 10;
}

void sensorThread()
{
    while (true)
    {
        int distRight = 0, distLeft = 0;
        for (int i = 0; i < 3; ++i)
        {
            distRight += sens.GetUS(Sensors::RIGHT);
            distLeft += sens.GetUS(Sensors::LEFT);
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
        distRight /= 3;
        distLeft /= 3;

        if (distRight < 250 || distLeft < 250)
        {
            IsEnemy = true;
        }
        else
        {
            IsEnemy = false;
        }
        // Serial.printf("US Right AVG: %d, US Left AVG: %d, IsEnemy: %s\n", distRight, distLeft, IsEnemy.load() ? "true" : "false");
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

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
    static const uint32_t VOLTAGE_MAX = 8400; //%edit
    static const uint32_t VOLTAGE_MIN = 6000; //%edit
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

void setup()
{
    Serial.begin(115200);

    auto &man = rb::Manager::get(); // get manager instance as singleton
    man.install();                  // install manager

    servoBus.begin(2, UART_NUM_1, GPIO_NUM_27);
    servoBus.setAutoStop(0, false); // vypne autostop leveho serva
    servoBus.setAutoStop(1, false); // vypne autostop praveho serva

    /*START MOVEMENT HERE*/
    CheckBattery();
    color = RED;
    while (true)
    {
        // Nastav LED podle barvy
        if (color == RED)
        {
            man.leds().red(true);
            man.leds().blue(false);
        }
        else if (color == BLUE)
        {
            man.leds().blue(true);
            man.leds().red(false);
        }

        if (man.buttons().up())
        {
            color = (color == RED) ? BLUE : RED;
            delay(300);
        }

        if (man.buttons().on())
        {
            break;
        }
        delay(50);
    }
    // const char *colorStr = (color == RED) ? "RED" : (color == BLUE) ? "BLUE"
    //                                                                 : "NONE";

    const int N = 5;
    int distArr[N];
    int angleArr[N];

    WaitForStart();

    std::thread t1(sensorThread);

    grab.Open();
    delay(1000);

    for (int i = 0; i < N; ++i)
    {
        Serial.println("sendnudes");
        comm.WaitForDistanceData();
        delay(1);
        comm.WaitForOffSetData();
        distArr[i] = comm.distance_px;
        angleArr[i] = comm.angle_deg;
        delay(10);
    }

    // Seřadit pole
    std::sort(distArr, distArr + N);
    std::sort(angleArr, angleArr + N);

    // Průměr prostředních 3 hodnot
    int distSum = distArr[1] + distArr[2] + distArr[3];
    int angleSum = angleArr[1] + angleArr[2] + angleArr[3];

    comm.distance_px = distSum / 3;
    comm.angle_deg = angleSum / 3;

    // while (true)
    // {
    //     Serial.printf("AVG Angle: %d, AVG Distance: %d\n", comm.angle_deg, comm.distance_px);
    // }

    double angle_rad = std::atan2(comm.angle_deg, comm.distance_px);
    double angle = angle_rad * 180.0 / M_PI;

    if (comm.angle_deg < 0)
    {
        move.TurnLeft(angle);
    }
    else
    {
        move.TurnRight(angle);
    }

    move.Straight(5000, pixel_to_mm(comm.distance_px) + 60, 10000);
    delay(100);
    grab.Close();
    delay(100);
    move.BackwardUntillWall();
    delay(100);
    move.Straight(2000, 150, 10000);
    grab.Open();
    move.TurnRight(90);
    t1.join();
}

void loop()
{
}