from machine import Pin
import time

STEP_PIN = 16
DIR_PIN = 17

step = Pin(STEP_PIN, Pin.OUT)
direction = Pin(DIR_PIN, Pin.OUT)

# 1 = clockwise Wokwin A4988-dokumentaation mukaan
direction.value(1)
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
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(pulse_delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(pulse_delay)
except KeyboardInterrupt:
    GPIO.cleanup()
# Alkuarvo
step.value(0)

# Pulssitahti:
# 1 askel per pulssi
# 200 askelta = 1 kierros full-step moodissa
pulse_delay_us = 1000  # 1 ms high + 1 ms low => noin 500 steps/s

while True:
    step.value(1)
    time.sleep_us(pulse_delay_us)
    step.value(0)
    time.sleep_us(pulse_delay_us)
