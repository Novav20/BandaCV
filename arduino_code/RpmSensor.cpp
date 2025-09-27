#include "RpmSensor.h"

// Initialize static members
volatile unsigned long RpmSensor::_pulseCount = 0;

RpmSensor::RpmSensor(int sensorPin, int pulsesPerRevolution) {
    _sensorPin = sensorPin;
    _pulsesPerRevolution = pulsesPerRevolution;
    _lastRpmTime = 0;
    _currentRpm = 0.0;
}

void RpmSensor::setup() {
    pinMode(_sensorPin, INPUT);
    attachInterrupt(digitalPinToInterrupt(_sensorPin), countPulse, RISING);
}

void RpmSensor::update() {
    unsigned long currentTime = millis();
    if (currentTime - _lastRpmTime >= 1000) { // Calculate RPM every second
        detachInterrupt(digitalPinToInterrupt(_sensorPin)); // Safely read pulseCount
        
        _currentRpm = (_pulseCount / (float)_pulsesPerRevolution) * 60.0;
        _pulseCount = 0; // Reset for the next second
        
        _lastRpmTime = currentTime;
        attachInterrupt(digitalPinToInterrupt(_sensorPin), countPulse, RISING); // Re-attach interrupt
    }
}

float RpmSensor::getRpm() {
    return _currentRpm;
}

void RpmSensor::countPulse() {
    _pulseCount++;
}
