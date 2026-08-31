import RPi.GPIO as GPIO
import time

DIR = 17
STEP = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

GPIO.output(DIR, GPIO.HIGH)
GPIO.output(STEP, GPIO.LOW)

pulse_delay = 0.01  # 10 ms high + 10 ms low = hyvin hidas

try:
    while True:
        print("STEP high")
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(pulse_delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(pulse_delay)
        print("STEP low")
except KeyboardInterrupt:
    GPIO.cleanup()
