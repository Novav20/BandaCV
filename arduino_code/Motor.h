#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor {
public:
    Motor(int pwmPin);
    void setup();
    void setSpeed(int speed);

private:
    int pwmPin;
};

#endif