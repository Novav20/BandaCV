#ifndef CONFIG_H
#define CONFIG_H

// =================================================================
// ==                PROJECT CONFIGURATION FILE                   ==
// =================================================================
// This file centralizes all hardware and firmware configuration
// for the project. Modify the values here to adapt to your setup.
// =================================================================


// --- Pin Definitions ---
// Assigns microcontroller pins to different hardware components.
// IMPORTANT: CONVEYOR_MOTOR_PWM_PIN was moved from 9 to 11 to avoid a timer conflict with the Servo library.
const int CONVEYOR_MOTOR_PWM_PIN = 11;
const int CLASSIFIER_SERVO_PIN = 10;
const int OBSTACLE_IR_SENSOR_PIN = 7;
const int CONVEYOR_ENCODER_PIN = 2;      // Must be an interrupt-capable pin (e.g., 2 or 3 on Arduino Uno)


// --- Serial Communication ---
// Configuration for the serial connection with the host computer.
const long SERIAL_BAUD_RATE = 9600;
const unsigned long SERIAL_SEND_INTERVAL_MS = 100;    // How often to send data (RPM, sensor state) to the PC.
const unsigned long HEARTBEAT_TIMEOUT_MS = 2000;      // If no command is received from PC in this time, enter safe mode.


// --- Encoder & Motor Configuration ---
// YOU MUST CONFIGURE THIS SECTION TO MATCH YOUR MOTOR.
// The datasheet for Pololu 37D motors specifies 64 CPR for the encoder using
// 4x decoding. Since we are only using a single rising edge interrupt (1x decoding),
// the base CPR is 64 / 4 = 16.
const int ENCODER_BASE_CPR = 16;

// Find the gear ratio written on your motor's gearbox (e.g., 19:1, 50:1, 70:1).
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// !!                  CHANGE THIS VALUE                        !!
const int MOTOR_GEAR_RATIO = 30; // <-- CHANGE THIS TO MATCH YOUR MOTOR
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

// Final calculation for pulses per full revolution of the output shaft.
const int ENCODER_PULSES_PER_REVOLUTION = ENCODER_BASE_CPR * MOTOR_GEAR_RATIO;


// --- Servo Positions ---
// Defines the angle (in degrees) for the servo arm for each classification.
// You may need to calibrate these values for your specific setup.
const int SERVO_POS_TRIANGLE = 30;
const int SERVO_POS_SQUARE = 90;
const int SERVO_POS_CIRCLE = 150;
const int SERVO_POS_UNKNOWN = 0;   // Home/default position.


#endif // CONFIG_H
