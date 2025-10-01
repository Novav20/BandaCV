#include "Communication.h"

Communication::Communication(long baudRate, Motor* motor, ClassifierServo* servo) {
    _baudRate = baudRate;
    _motor = motor;
    _servo = servo;
    _inputString = "";
    _lastSerialSendTime = 0;
}

void Communication::setup() {
    Serial.begin(_baudRate);
    _inputString.reserve(20); // Reserve memory for the input string
}

void Communication::update(float rpm, int obstacleState) {
    handleSerial();
    sendDataToPC(rpm, obstacleState);
}

void Communication::handleSerial() {
    while (Serial.available()) {
        char inChar = (char)Serial.read();
        if (inChar == '\n') {
            processCommand(_inputString);
            _inputString = ""; // Clear the string
        } else {
            _inputString += inChar;
        }
    }
}

void Communication::processCommand(String command) {
    command.trim();
    int separatorIndex = command.indexOf('_');
    if (separatorIndex == -1) {
        return; // Invalid command format
    }

    String pwmStr = command.substring(0, separatorIndex);
    String servoStr = command.substring(separatorIndex + 1);

    int pwmValue = pwmStr.toInt();
    int servoCode = servoStr.toInt();

    _motor->setSpeed(pwmValue);
    _servo->setPosition(servoCode);
}

void Communication::sendDataToPC(float rpm, int obstacleState) {
    unsigned long currentTime = millis();
    if (currentTime - _lastSerialSendTime >= SERIAL_SEND_INTERVAL_MS) {
        Serial.print((int)rpm);
        Serial.print("_");
        Serial.println(obstacleState);
        _lastSerialSendTime = currentTime;
    }
}
