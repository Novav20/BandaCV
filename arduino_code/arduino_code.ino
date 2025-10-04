#include "config.h"
#include "Motor.h"
#include "ClassifierServo.h"
#include "RpmSensor.h"
#include "ObstacleSensor.h"
#include "Communication.h"

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
