import time
import RPi.GPIO as GPIO

LED11 = 11
LED13 = 13
LED15 = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED11, GPIO.OUT)
GPIO.setup(LED13, GPIO.OUT)
GPIO.setup(LED15, GPIO.OUT)

while True:
	time.sleep(1)
	GPIO.output(LED11, False)
	time.sleep(1)

	time.sleep(1)
	GPIO.output(LED13, False)
	time.sleep(1)

	time.sleep(1)
	GPIO.output(LED15, False)
	time.sleep(1)

GPIO.output(LED11, False)
GPIO.output(LED13, False)
GPIO.output(LED15, False)
