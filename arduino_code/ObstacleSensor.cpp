#include "ObstacleSensor.h"

ObstacleSensor::ObstacleSensor(int sensorPin) {
    _sensorPin = sensorPin;
}

void ObstacleSensor::setup() {
    pinMode(_sensorPin, INPUT_PULLUP); // Use internal pull-up
}

int ObstacleSensor::getState() {
    // Assuming the sensor is LOW when an obstacle is present
    return digitalRead(_sensorPin) == LOW ? 1 : 0;
}
