#ifndef CLASSIFIER_SERVO_H
#define CLASSIFIER_SERVO_H

#include <Arduino.h>
#include <Servo.h>

class ClassifierServo {
public:
    ClassifierServo(int servoPin);
    void setup();
    void setPosition(int servoCode);

private:
    int _servoPin;
    Servo _servo;
};

#endif
