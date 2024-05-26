#include <AccelStepper.h>

#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11

AccelStepper stepper(AccelStepper::HALF4WIRE, IN1, IN3, IN2, IN4);

int motorSpeed = 100; // Швидкість двигуна (кроків за секунду)
int stepsPerRevolution = 2000;

void setup() {
  stepper.setMaxSpeed(motorSpeed);
  stepper.setSpeed(motorSpeed);
}

void loop() {
  static long currentPosition = 0;
  static bool forward = true;
  static int revolutionsCounter = 0;

  if (forward) {
    stepper.setSpeed(motorSpeed);
  } else {
    stepper.setSpeed(-motorSpeed);
  }

  stepper.runSpeed();

  if (stepper.distanceToGo() == 0) {
    if (revolutionsCounter < 1) {
      currentPosition += forward ? stepsPerRevolution : -stepsPerRevolution;
      revolutionsCounter++;
    } else {
      forward = !forward;
      revolutionsCounter = 0;
    }
    stepper.moveTo(currentPosition);
  }
}