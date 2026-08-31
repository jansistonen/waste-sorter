from gpiozero import Servo
from time import sleep

# Define the GPIO pin your servo's signal wire (usually yellow or orange) is connected to.
# We are using GPIO 23
servo_pin = 23
my_servo = Servo(servo_pin, initial_value=1, min_pulse_width=0.0005, max_pulse_width=0.0024)

def open_and_close():
    
    print("Closing the servo...")
    my_servo.value = 0.9  # Moves the servo to its minimum position (closed)
    
    # Optional: pause briefly before the program ends to give it time to finish moving
    sleep(1)
    my_servo.detach()
    print("Done!")


    
    print("Opening the servo...")
    #my_servo.value = 0.0  # Moves the servo to its maximum position (open)
    my_servo.value = -0.06
    sleep(1)
    my_servo.detach()
    print("Pausing...")
    sleep(3)        # Pauses the script for 2 seconds
    
    '''print("Closing the servo...")
    my_servo.value = 0.9  # Moves the servo to its minimum position (closed)
    
    # Optional: pause briefly before the program ends to give it time to finish moving
    sleep(1)
    my_servo.detach()
    print("Done!")'''

# Run the sequence once
open_and_close()
