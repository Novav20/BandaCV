#include "config.h"
#include "ClassifierServo.h"

ClassifierServo::ClassifierServo(int servoPin) {
    _servoPin = servoPin;
}

void ClassifierServo::setup() {
    _servo.attach(_servoPin);
    _servo.write(SERVO_POS_UNKNOWN); // Start at home position
}

void ClassifierServo::setPosition(int servoCode) {
    switch (servoCode) {
        case 0: // Corresponds to 'TRIANGLE' or 'RED' or 'SMALL'
            _servo.write(SERVO_POS_TRIANGLE);
            break;
        case 1: // Corresponds to 'SQUARE' or 'YELLOW' or 'MEDIUM'
            _servo.write(SERVO_POS_SQUARE);
            break;
        case 2: // Corresponds to 'CIRCLE' or 'GREEN' or 'LARGE'
            _servo.write(SERVO_POS_CIRCLE);
            break;
        default: // 'UNKNOWN'
            _servo.write(SERVO_POS_UNKNOWN);
            break;
    }
}