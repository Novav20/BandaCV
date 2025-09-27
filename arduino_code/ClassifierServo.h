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
    // Servo positions - these should be calibrated
    const int SERVO_POS_TRIANGLE = 30;
    const int SERVO_POS_SQUARE = 90;
    const int SERVO_POS_CIRCLE = 150;
    const int SERVO_POS_UNKNOWN = 0;
};

#endif
