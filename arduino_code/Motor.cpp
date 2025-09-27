#include "Motor.h"

Motor::Motor(int pwmPin, int dirPin) {
    _pwmPin = pwmPin;
    _dirPin = dirPin;
}

void Motor::setup() {
    pinMode(_pwmPin, OUTPUT);
    pinMode(_dirPin, OUTPUT);
    // Set a default direction
    digitalWrite(_dirPin, HIGH);
}

void Motor::setSpeed(int pwmValue) {
    analogWrite(_pwmPin, pwmValue);
}
