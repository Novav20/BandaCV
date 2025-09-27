#ifndef OBSTACLE_SENSOR_H
#define OBSTACLE_SENSOR_H

#include <Arduino.h>

class ObstacleSensor {
public:
    ObstacleSensor(int sensorPin);
    void setup();
    int getState();

private:
    int _sensorPin;
};

#endif
