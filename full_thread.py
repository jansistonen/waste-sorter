import cv2
from ultralytics import YOLO
from gpiozero import OutputDevice, DistanceSensor, Servo
from time import sleep
import threading  # Tuodaan säikeistyskirjasto

# ==========================================
# 1. LAITTEISTON ASETUKSET JA PINNIT
# ==========================================
STEP_PIN = 27
DIR_PIN = 17
ENABLE_PIN = 22
TRIGGER_PIN = 5
ECHO_PIN = 6
SERVO_PIN = 23

step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
enable = OutputDevice(ENABLE_PIN, active_high=False, initial_value=False)
sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIGGER_PIN, max_distance=2.0)
my_servo = Servo(SERVO_PIN, initial_value=None, min_pulse_width=0.0005, max_pulse_width=0.0024)

FORWARD = False
BACKWARD = True
STEP_DELAY = 0.001       
STOP_DISTANCE_CM = 10.0

# Lippu, joka kertoo onko moottorioperaatio käynnissä
is_motor_running = False

ROUTING = {
    "bio": {"rounds": 5, "steps": 95},
    "cardb": {"rounds": 10, "steps": 95},
    "paper": {"rounds": 15, "steps": 95},
    "plastic": {"rounds": 19, "steps": 92},
    "metal": {"rounds": 19, "steps": 92}, 
    "mix": {"rounds": 19, "steps": 92}
}

# ==========================================
# 2. MOOTTORIFUNKTIOT
# ==========================================
def move_steps(amount):
    for _ in range(amount):
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)

def move_until_distance(stop_distance_cm):
    while True:
        distance_cm = sensor.distance * 100
        if distance_cm <= stop_distance_cm:
            break
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)

def init_servo():
    print("Kalibroidaan servo...")
    my_servo.value = 0.9  
    sleep(1)
    my_servo.detach()     

def operate_servo():
    my_servo.value = 0.9    # Kiinni
    sleep(1)
    my_servo.detach()
    my_servo.value = -0.06  # Auki
    sleep(1)
    my_servo.detach()
    sleep(3)

def run_motor_sequence(rounds, steps_per_round):
    """Tämä funktio ajetaan omassa säikeessään."""
    global is_motor_running
    try:
        is_motor_running = True
        total_steps = rounds * steps_per_round
        enable.on()
        
        # 1. Ajo lokerolle
        direction.value = FORWARD
        move_steps(total_steps)
        
        # 2. Pudotus
        operate_servo()
        
        # 3. Palautus
        direction.value = BACKWARD
        sleep(0.1)
        move_until_distance(STOP_DISTANCE_CM)
        
        enable.off()
    finally:
        is_motor_running = False # Vapautetaan lippu, kun työ on tehty
        print("--- Lajittelu valmis, otetaan vastaan uusia kohteita ---")

# ==========================================
# 3. PÄÄOHJELMA JA KAMERALOOPPI
# ==========================================
if __name__ == "__main__":
    # Kalibroinnit
    init_servo()
    print("Kalibroidaan askelmoottori...")
    enable.on()
    direction.value = BACKWARD
    move_until_distance(STOP_DISTANCE_CM)
    enable.off()

    # YOLO ja Kamera
    model = YOLO(r"best.pt") 
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    current_object = None
    frame_count = 0
    annotated_frame = None

    print("Käynnissä! Paina 'q' lopettaaksesi.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            frame_count += 1
            
            # SUORITETAAN TUNNISTUS VAIN JOS MOOTTORI EI OLE KÄYNNISSÄ
            if not is_motor_running:
                # Ajetaan YOLO vain joka 3. ruutu suorituskyvyn takia
                if frame_count % 3 == 0:
                    results = model(frame, verbose=False)
                    
                    detected_class_name = None
                    highest_conf = 0.0

                    if len(results[0].boxes) > 0:
                        for box in results[0].boxes:
                            conf = float(box.conf[0])
                            if conf > highest_conf:
                                highest_conf = conf
                                class_id = int(box.cls[0])
                                detected_class_name = model.names[class_id]
                        
                        annotated_frame = results[0].plot()
                    else:
                        annotated_frame = frame
                        detected_class_name = None

                    # Jos uusi kohde tunnistettiin, käynnistetään moottorisäie
                    if detected_class_name and detected_class_name != current_object:
                        prefix = detected_class_name.split("_")[0]
                        if prefix in ROUTING:
                            print(f"\nKOHDE: {prefix.upper()}. Käynnistetään moottorit.")
                            params = ROUTING[prefix]
                            
                            # KÄYNNISTETÄÄN MOOTTORI OMASSAN SÄIKEESSÄÄN
                            motor_thread = threading.Thread(
                                target=run_motor_sequence, 
                                args=(params["rounds"], params["steps"])
                            )
                            motor_thread.start()
                            
                            current_object = detected_class_name
            else:
                # Jos moottori on käynnissä, näytetään vain peruskuvaa tai viimeisintä analyysia
                # Lisätään ruudulle teksti kertomaan tilasta
                cv2.putText(frame, "MOOTTORI AJOSSA - Tunnistus tauolla", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                annotated_frame = frame
                current_object = None # Nollataan esine, jotta se voidaan tunnistaa uudestaan paluun jälkeen

            # Päivitetään kuva ruudulle aina (ei jäädy enää)
            display_frame = annotated_frame if annotated_frame is not None else frame
            cv2.imshow("Robottilajittelu", display_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nKeskeytetty.")
    finally:
        enable.off()
        cap.release()
        cv2.destroyAllWindows()
