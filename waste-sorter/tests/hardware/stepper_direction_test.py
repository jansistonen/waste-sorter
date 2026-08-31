from gpiozero import OutputDevice
from time import sleep

STEP_PIN = 27
DIR_PIN = 17
ENABlE_PIN = 22

step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
enable = OutputDevice(ENABlE_PIN, active_high=False, initial_value=False)

# 1 = clockwise Wokwin A4988-dokumentaation mukaan
direction.value = True

# Alkuarvo
rounds = 5
steps = 95
delay = 0.001

total_steps = steps * rounds

def eteen():
    direction.value = True
    enable.on()
    
    for i in range(total_steps):
        print("on")
        step.on()
        sleep(delay)
        step.off()
        sleep(delay)
        print("off")


def taakse ():
    direction.value = False
    enable.on()
    
    for i in range(total_steps):
        print("on")
        step.on()
        sleep(delay)
        step.off()
        sleep(delay)
        print("off")


print("starting")
try:
    while True:
        i = int(input("Syötä suunta, 1=eteen 2=taakse: "))
        if i == 1:
            eteen()
        elif i == 2:
            taakse()

except KeyboardInterrupt:
    print("\nOhjelma lopetettu")
    
finally:
    enable.off()
    step.off()
    print("motor off")
    
