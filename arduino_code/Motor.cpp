#include "Motor.h"

Motor::Motor(int pwmPin) : pwmPin(pwmPin) {}

void Motor::setup() {
    pinMode(pwmPin, OUTPUT);
    digitalWrite(pwmPin, LOW); // Ensure motor is off initially
}

void Motor::setSpeed(int speed) {
    // La interfaz envía un valor directo de 0-255. 
    // Lo limitamos por seguridad y lo escribimos directamente al pin PWM.
    int pwmValue = constrain(speed, 0, 255);
    analogWrite(pwmPin, pwmValue);
}
