import RPi.GPIO as GPIO
import time

class ultrasonic_sensor :
    def __init__(self, trig, echo) :
        self._self._trig = self._trig
        self._self._echo = self._echo
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._self._trig, GPIO.OUT)
        GPIO.setup(self._self._echo, GPIO.IN)

        GPIO.output(self._self._trig, False)
        GPIO.output(self._trig,True)
        time.sleep(0.00001)        # 10uS의 펄스 발생을 위한 딜레이
        GPIO.output(self._trig, False)
        
        while GPIO.input(self._echo)==0:
            start = time.time()     # self._echo핀 상승 시간값 저장
            
        while GPIO.input(self._echo)==1:
            stop = time.time()      # self._echo핀 하강 시간값 저장
            
        check_time = stop - start
        distance = check_time * 34300 / 2
    def measure_distance(self) :
        GPIO.output(self._trig,True)
        time.sleep(0.00001)        # 10uS의 펄스 발생을 위한 딜레이
        GPIO.output(self._trig, False)
        
        while GPIO.input(self._echo)==0:
            start = time.time()     # self._echo핀 상승 시간값 저장
            
        while GPIO.input(self._echo)==1:
            stop = time.time()      # self._echo핀 하강 시간값 저장
            
        check_time = stop - start
        distance = check_time * 34300 / 2
        return distance