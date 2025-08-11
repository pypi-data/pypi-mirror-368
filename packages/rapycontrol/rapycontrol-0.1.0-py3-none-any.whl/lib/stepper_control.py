import RPi.GPIO as GPIO
import time

class stepper_control :
    def __init__(self, enable_pin, step_pin, direction_pin):
        self._enable_pin = enable_pin
        self._step_pin = step_pin
        self._direction_pin = direction_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._enable_pin,GPIO.OUT)
        GPIO.setup(self._step_pin,GPIO.OUT)
        GPIO.setup(self._direction_pin,GPIO.OUT)
        GPIO.output(self._enable_pin,False)
        GPIO.output(self._step_pin,False)
        GPIO.output(self._direction_pin,False)

    def turn_stepper_one_step(self, direction, step_delay):
        if direction == 1:
            GPIO.output(self._direction_pin,True)
        elif direction == 0:
            GPIO.output(self._direction_pin,False)
        GPIO.output(self._step_pin,False)
        time.sleep(0.0001)
        GPIO.output(self._step_pin,True)
        time.sleep(step_delay)
    def disable_stepper(self):
        GPIO.output(self._enable_pin,True)
    def enable_stepper(self):
        GPIO.output(self._enable_pin,False)