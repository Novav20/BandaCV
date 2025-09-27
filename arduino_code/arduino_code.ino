#include "Motor.h"
#include "ClassifierServo.h"
#include "RpmSensor.h"
#include "ObstacleSensor.h"
#include "Communication.h"

// --- Pin Definitions ---
const int MOTOR_PWM_PIN = 9;
const int MOTOR_DIR_PIN = 8;
const int SERVO_PIN = 10;
const int OBSTACLE_SENSOR_PIN = 7;
const int RPM_SENSOR_PIN = 2;

// --- Constants ---
const long BAUD_RATE = 9600;
const int PULSES_PER_REVOLUTION = 20;

// --- Component Objects ---
Motor motor(MOTOR_PWM_PIN, MOTOR_DIR_PIN);
ClassifierServo classifierServo(SERVO_PIN);
RpmSensor rpmSensor(RPM_SENSOR_PIN, PULSES_PER_REVOLUTION);
ObstacleSensor obstacleSensor(OBSTACLE_SENSOR_PIN);
Communication communication(BAUD_RATE, &motor, &classifierServo);

void setup() {
    motor.setup();
    classifierServo.setup();
    rpmSensor.setup();
    obstacleSensor.setup();
    communication.setup();
}

void loop() {
    rpmSensor.update();
    communication.update(rpmSensor.getRpm(), obstacleSensor.getState());
}
