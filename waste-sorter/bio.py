from servo import open_and_close
from gpiozero import OutputDevice, Servo
from time import sleep

# Adjust needed pins and settings (Step counts, direction, servo and on/off pin)
STEP_PIN = 27
DIR_PIN = 17
ENABLE_PIN = 22
my_servo = Servo(23)

step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
enable = OutputDevice(ENABLE_PIN, active_high=False, initial_value=False)

# Adding the motors direction (True or False)
direction.value = True

# Motor running settings
rounds = 10
steps = 100
delay = 0.001

total_steps = steps * rounds
print("starting")

# Doing needed steps

try:
    enable.on()
    # Running bascket up to right bin
    for i in range(total_steps):
        print("on")
        step.on()
        sleep(delay)
        step.off()
        sleep(delay)
        print("off")
    
    # Dropping thrash
    open_and_close(my_servo)
    direction.value = False

    # 
    for i in range(total_steps):
        print("on")
        step.on()
        sleep(delay)
        step.off()
        sleep(delay)
        print("off")

except KeyboardInterrupt:
    print("\nOhjelma lopetettu")

finally:
    enable.off()
    step.off()
    print("motor off")