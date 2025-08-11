import RPi.GPIO as GPIO
import time

class stepper_control :
    def __init__(self, enable_pin, step_pin, direction_pin):
        self._enable_pin = enable_pin
        self._step_pin = step_pin
        self._direction_pin = direction_pin
    