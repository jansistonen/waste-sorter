import cv2
from ultralytics import YOLO
import time
import bio

# 1. Load light YOLOv11-model (n-version faster for video)
model = YOLO(r"C:\Users\hjerk\Desktop\Robo\waste-sorter\waste-sorter\best.pt") # Change your model path here!

# 2. Open camera (index 0, 1 webc, 6=Intel RGB)
cap = cv2.VideoCapture(0)

# Variable remembers which object is at video right now
current_object = None

# Queue for object to be prosessed
handle_queue = []

# Handler function if something at queue
def item_handler(handle_queue: list):
    item = str(handle_queue.pop())
    item_class = item.split("_")

    if item_class[0] == "bio":
        print("BIOWASTE")
        bio
        time.sleep(3)
    
    elif item_class[0] == "cardb":
        print("CARDBOARD")
        time.sleep(3)

    elif item_class[0] == "paper":
        print("PAPER")
        time.sleep(3)
    
    elif item_class[0] == "plastic":
        print("PLASTIC")
        time.sleep(3)
    
    elif item_class[0] == "metal":
        print("METAL")
        time.sleep(3)
    
    handle_queue.remove

    print("Camera started, Waiting thrashes...")

# Main program
while True:

    print(handle_queue)

    ret, frame = cap.read()
    if not ret:
        print("Ei kuvaa kameralta.")
        break

    # 1. Make identification. 
    # HOX: verbose=False critical, blocks YOLO spamming terminal!
    results = model(frame, verbose=False)

    detected_class_name = None
    highest_conf = 0.0

    # 2. Find out the most clearest identification from video
    for result in results:
        boxes = result.boxes
        if len(boxes) > 0:
            # Go thrue all findings and pick which is the most valid option
            for box in boxes:
                conf = float(box.conf[0])
                if conf > highest_conf:
                    highest_conf = conf
                    class_id = int(box.cls[0])
                    detected_class_name = model.names[class_id]
            
            # Draw box to the video for visualization
            frame = result.plot()

    # 3. Checks if the object has changed
    if detected_class_name != current_object:
        if detected_class_name is not None:
            # New object detected! 
            print(f"-> NEW OBJECT: {detected_class_name} (Varmuus: {highest_conf:.2f})")

            handle_queue.append(detected_class_name)
            
        else:
            # Video is empty, wating
            print("-> Queue is empty, wating...")
        
        # Update current status
        current_object = detected_class_name

        # If something at queue, call handler functio
        if len(handle_queue) > 0:
            item_handler(handle_queue)

    # 4. Show video
    cv2.imshow("Robottilajittelu", frame)

    # Quit with button 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleaning last
cap.release()
cv2.destroyAllWindows()