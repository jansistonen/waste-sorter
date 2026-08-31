import cv2
from pathlib import Path
from ultralytics import YOLO
from gpiozero import OutputDevice, DistanceSensor, Servo
from time import sleep

# ==========================================
# 1. HARDWARE SETTINGS AND PINS
# ==========================================
STEP_PIN = 27
DIR_PIN = 17
ENABLE_PIN = 22
TRIGGER_PIN = 5
ECHO_PIN = 6
SERVO_PIN = 23

# Stepper motor control
step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
enable = OutputDevice(ENABLE_PIN, active_high=False, initial_value=False)

# Distance sensor
sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIGGER_PIN, max_distance=2.0)

# Servo (note: initial_value=None prevents twitching on startup)
my_servo = Servo(
    SERVO_PIN, 
    initial_value=None, 
    min_pulse_width=0.0005, 
    max_pulse_width=0.0024
)

FORWARD = False
BACKWARD = True
STEP_DELAY = 0.001       
STOP_DISTANCE_CM = 6.0

# ==========================================
# 2. SORTING SETTINGS (Combines prefix and steps)
# ==========================================
ROUTING = {
    "bio": {"rounds": 5, "steps": 95},
    "cardb": {"rounds": 10, "steps": 95},
    "plastic": {"rounds": 15, "steps": 95},
    "metal": {"rounds": 19, "steps": 92}, 
    "mix": {"rounds": 0, "steps": 0},
    "paper": {"rounds": 0, "steps": 0}
}

# ==========================================
# 3. MOTOR FUNCTIONS
# ==========================================
def move_steps(amount):
    """Drives the stepper motor forward a specific number of steps."""
    enable.on()
    for _ in range(amount):
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)
    enable.off()

def move_until_distance(stop_distance_cm):
    """Drives the stepper motor until the sensor measures less than the target distance."""
    enable.on()
    while True:
        distance_cm = sensor.distance * 100
        if distance_cm <= stop_distance_cm:
            break
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)
    enable.off()

def init_servo():
    """Safely drives the servo to the closed home position at program startup."""
    print("Calibrating servo (closed position)...")
    my_servo.value = 0.9  
    sleep(1)
    my_servo.detach() 
    
    my_servo.value = -0.06  # Open
    sleep(1)
    my_servo.detach()
    print("Servo calibrated!")

def operate_servo():
    """Opens and closes the servo hatch mechanism after sorting."""
    my_servo.value = 0.9    # Closed
    sleep(1)
    my_servo.detach()
    my_servo.value = -0.06  # Open
    sleep(1)
    my_servo.detach()

def run_motor_sequence(rounds, steps_per_round):
    """Full sorting sequence: drive to correct position, servo movement, and return."""
    total_steps = rounds * steps_per_round
    enable.on()
    
    # 1. Forward to the correct bin
    direction.value = FORWARD
    move_steps(total_steps)
    enable.off()
    
    # 2. Servo drops the trash
    operate_servo()
    
    # 3. Backward return to home position
    enable.on()
    direction.value = BACKWARD
    sleep(0.1)
    move_until_distance(STOP_DISTANCE_CM)
    
    enable.off()

# ==========================================
# 4. IMAGE RECOGNITION PROCESSING
# ==========================================
def process_detected_item(item_name):
    """Parses the detected class name and drives the motor according to the routing dictionary."""
    prefix = item_name.split("_")[0]
    
    if prefix in ROUTING:
        print(f"--> PROCESSING: {prefix.upper()}")
        params = ROUTING[prefix]
        run_motor_sequence(params["rounds"], params["steps"])
    else:
        print(f"--> Unknown category: {prefix}, skipping.")

# ==========================================
# 5. MAIN PROGRAM AND CAMERA LOOP
# ==========================================
if __name__ == "__main__":
    print("\n==================================")
    print("Hardware calibration starting...")
    
    # A. Servo calibration
    init_servo()

    # B. Stepper motor calibration (Homing)
    print("Calibrating stepper motor home position (sensor < 10 cm)...")
    enable.on()
    direction.value = BACKWARD
    sleep(0.1)
    move_until_distance(STOP_DISTANCE_CM)
    enable.off()
    
    print("Hardware calibrated and ready to use!")
    print("==================================\n")

    # C. YOLO and opening camera
    # NOTE: Make sure the model path (best_ncnn_model) is correct!
    repo_root = Path(__file__).resolve().parent.parent
    model_path = repo_root / "models" / "best_ncnn_model"
    model = YOLO(str(model_path))  # previously YOLO(r"best.pt") 
    cap = cv2.VideoCapture(0)
    current_object = None
    
    # New camera speedups
    frame_count = 0
    annotated_frame = None

    print("Camera started, waiting for trash... (Press 'q' to quit)")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("No image from camera.")
                break
            
            frame_count += 1
            detected_class_name = None
            highest_conf = 0.0
            
            if frame_count % 3 == 0:
                results = model(frame, verbose=False)

                # D. Find the most confident detection on screen
                for result in results:
                    boxes = result.boxes
                    if len(boxes) > 0:
                        for box in boxes:
                            conf = float(box.conf[0])
                            if conf > highest_conf and conf > 0.7:
                                highest_conf = conf
                                class_id = int(box.cls[0])
                                detected_class_name = model.names[class_id]
                        annotated_frame = result.plot()
                    else:
                        annotated_frame = frame
            
            if annotated_frame is None:
                annotated_frame = frame
                
            # E. If there is a NEW object on camera, sort it
            if detected_class_name != current_object:
                if detected_class_name is not None:
                    print(f"\nNEW OBJECT DETECTED: {detected_class_name} (Confidence: {highest_conf:.2f})")
                    # Run sorting. The video frame stops during motor drive preventing double detections.
                    process_detected_item(detected_class_name)
                    
                    # ----------------------------------------------------
                    # NEW: 0.5s cooldown and flush camera buffer
                    # ----------------------------------------------------
                    print("Cooling down for 0.5s to prevent instant re-detection...")
                    sleep(0.5)
                    # Read and discard a few frames to clear the OpenCV buffer
                    for _ in range(5):
                        cap.read()
                    # ----------------------------------------------------
                    
                    print("Waiting for new trash...")
                
                # Update variable so the same trash isn't sorted continuously
                current_object = detected_class_name
                
            # F. Show video frame
            cv2.imshow("Robot Sorting", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        enable.off()
        print("\nProgram interrupted by user!")

    finally:
        enable.off()
        cap.release()
        cv2.destroyAllWindows()
        print("Hardware and camera closed safely.")