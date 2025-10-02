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

// --- Encoder Configuration ---
// NOTE: You must configure this section to match your specific motor.
// The datasheet for Pololu 37D motors specifies 64 CPR for the encoder using
// 4x decoding. Since we are only using a single rising edge interrupt (1x decoding),
// the base CPR is 64 / 4 = 16.
const int ENCODER_BASE_CPR = 16;

// Find the gear ratio written on your motor's gearbox (e.g., 19:1, 50:1, 70:1).
// YOU MUST CHANGE THIS VALUE.
const int MOTOR_GEAR_RATIO = 50; // <-- CHANGE THIS TO MATCH YOUR MOTOR

const int ENCODER_PULSES_PER_REVOLUTION = ENCODER_BASE_CPR * MOTOR_GEAR_RATIO;

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