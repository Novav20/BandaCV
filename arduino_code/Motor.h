#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor {
public:
    Motor(int pwmPin, int dirPin);
    void setup();
    void setSpeed(int pwmValue);

private:
    int _pwmPin;
    int _dirPin;
};

#endif
