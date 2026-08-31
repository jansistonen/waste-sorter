from gpiozero import OutputDevice, DistanceSensor
from time import sleep

STEP_PIN = 27
DIR_PIN = 17
ENABlE_PIN = 22
sensor = DistanceSensor(echo=6, trigger=5)

step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
enable = OutputDevice(ENABlE_PIN, active_high=False, initial_value=False)

# 1 = clockwise Wokwin A4988-dokumentaation mukaan
direction.value = False

# Alkuarvo
rounds = 19
steps = 92
delay = 0.001

total_steps = steps * rounds
print("starting")
try:
    enable.on()
    
    for i in range(total_steps):
        print("on")
        step.on()
        sleep(delay)
        step.off()
        sleep(delay)
        print("off")
	
        etaisyys = sensor.distance * 100
        print(f"etäisyys: {etaisyys:.1f} cm")

except KeyboardInterrupt:
    print("\nOhjelma lopetettu")
    
finally:
    direction.value = True
    while True:
        etaisyys = sensor.distance * 100
        print(sensor.distance * 100)
        if etaisyys <= 7:
            break
        step.on()
        sleep(delay)
        step.off()
        sleep(delay)
	
    enable.off()
    step.off()
    print("motor off")
    
