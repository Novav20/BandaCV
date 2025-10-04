#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <Arduino.h>
#include "Motor.h"
#include "ClassifierServo.h"

class Communication {
public:
    Communication(long baudRate, Motor* motor, ClassifierServo* servo);
    void setup();
    void update(float rpm, int obstacleState);

private:
    long _baudRate;
    String _inputString;
    unsigned long _lastSerialSendTime;
    unsigned long _lastHeartbeatTime;
    Motor* _motor;
    ClassifierServo* _servo;

    void handleSerial();
    void processCommand(String command);
    void sendDataToPC(float rpm, int obstacleState);
    void _checkHeartbeat();
};

#endif
