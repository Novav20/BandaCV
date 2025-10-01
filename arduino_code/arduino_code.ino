#include "Motor.h"
#include "ClassifierServo.h"
#include "RpmSensor.h"
#include "ObstacleSensor.h"
#include "Communication.h"

// --- Pin Definitions ---
const int CONVEYOR_MOTOR_PWM_PIN = 11;   // PWM pin for conveyor motor speed (moved from 9 due to timer conflict)
const int CLASSIFIER_SERVO_PIN = 10;     // PWM pin for the classification servo
const int OBSTACLE_IR_SENSOR_PIN = 7;    // Digital pin for the infrared obstacle sensor
const int CONVEYOR_ENCODER_PIN = 2;      // Interrupt pin for the conveyor's RPM encoder

// --- Constants ---
const long SERIAL_BAUD_RATE = 9600;
const int ENCODER_PULSES_PER_REVOLUTION = 20;

// --- Component Objects ---
Motor conveyorMotor(CONVEYOR_MOTOR_PWM_PIN);
ClassifierServo classifierServo(CLASSIFIER_SERVO_PIN);
RpmSensor rpmSensor(CONVEYOR_ENCODER_PIN, ENCODER_PULSES_PER_REVOLUTION);
ObstacleSensor obstacleSensor(OBSTACLE_IR_SENSOR_PIN);
Communication serialCommunicator(SERIAL_BAUD_RATE, &conveyorMotor, &classifierServo);

void setup() {
    conveyorMotor.setup();
    classifierServo.setup();
    rpmSensor.setup();
    obstacleSensor.setup();
    serialCommunicator.setup();
}

void loop() {
    rpmSensor.update();
    serialCommunicator.update(rpmSensor.getRpm(), obstacleSensor.getState());
}