from gpiozero import Servo
from time import sleep

# Define the GPIO pin your servo's signal wire (usually yellow or orange) is connected to.
# We are using GPIO 23
servo_pin = 23
my_servo = Servo(servo_pin)

def open_and_close():
    print("Opening the servo...")
    my_servo.max()  # Moves the servo to its maximum position (open)
    
    print("Pausing...")
    sleep(2)        # Pauses the script for 2 seconds
    
    print("Closing the servo...")
    my_servo.min()  # Moves the servo to its minimum position (closed)
    
    # Optional: pause briefly before the program ends to give it time to finish moving
    sleep(1)
    print("Done!")

# Run the sequence once
open_and_close()