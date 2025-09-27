#ifndef RPM_SENSOR_H
#define RPM_SENSOR_H

#include <Arduino.h>

class RpmSensor {
public:
    RpmSensor(int sensorPin, int pulsesPerRevolution);
    void setup();
    void update();
    float getRpm();
    static void countPulse(); // Needs to be static for ISR

private:
    int _sensorPin;
    int _pulsesPerRevolution;
    unsigned long _lastRpmTime;
    float _currentRpm;
    static volatile unsigned long _pulseCount; // Static for ISR
};

#endif
