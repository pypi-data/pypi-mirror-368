import RPi.GPIO as GPIO
import time

class servo_control :
    def __init__ (self, servo_pin) :
        self._servo_pin = servo_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._servo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self._servo_pin, 50)
        self.pwm.start(3.0)
        self.duty = 0.0
        self.pwm.ChangeDutyCycle(self.duty)
        self.pwm.stop()
        GPIO.cleanup()
    def turn_servo (self, angle) :
        self.duty = (1.0+(angle/180)/20.0)*100.0
        self.pwm.ChangeDutyCycle(self.duty)
    def servo_off(self) :
        self.pwm.stop()
        GPIO.cleanup()
    def servo_on(self) :
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._servo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self._servo_pin, 50)
        self.pwm.start(3.0)