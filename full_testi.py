import cv2
from ultralytics import YOLO
from gpiozero import OutputDevice, DistanceSensor, Servo
from time import sleep

# ==========================================
# 1. LAITTEISTON ASETUKSET JA PINNIT
# ==========================================
STEP_PIN = 27
DIR_PIN = 17
ENABLE_PIN = 22
TRIGGER_PIN = 5
ECHO_PIN = 6
SERVO_PIN = 23

# Askelmoottorin ohjaus
step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
enable = OutputDevice(ENABLE_PIN, active_high=False, initial_value=False)

# Sensori
sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIGGER_PIN, max_distance=2.0)

# Servo (huom. initial_value=None estää nykimisen käynnistyksessä)
my_servo = Servo(
    SERVO_PIN, 
    initial_value=None, 
    min_pulse_width=0.0005, 
    max_pulse_width=0.0024
)

FORWARD = False
BACKWARD = True
STEP_DELAY = 0.001       
STOP_DISTANCE_CM = 10.0

# ==========================================
# 2. LAJITTELUASETUKSET (Yhdistää etuliitteen ja askeleet)
# ==========================================
ROUTING = {
    "bio": {"rounds": 5, "steps": 95},
    "cardb": {"rounds": 10, "steps": 95},
    "paper": {"rounds": 15, "steps": 95},
    "plastic": {"rounds": 19, "steps": 92},
    "metal": {"rounds": 19, "steps": 92}, 
    "mix": {"rounds": 19, "steps": 92}
}

# ==========================================
# 3. MOOTTORIFUNKTIOT
# ==========================================
def move_steps(amount):
    """Ajaa askelmoottoria eteenpäin tietyn määrän askeleita."""
    for _ in range(amount):
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)

def move_until_distance(stop_distance_cm):
    """Ajaa askelmoottoria, kunnes sensori mittaa alle tavoite-etäisyyden."""
    while True:
        distance_cm = sensor.distance * 100
        if distance_cm <= stop_distance_cm:
            break
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)

def init_servo():
    """Ajaa servon turvallisesti kiinni-alkuasentoon ohjelman käynnistyessä."""
    print("Kalibroidaan servo (kiinni-asento)...")
    my_servo.value = 0.9  
    sleep(1)
    my_servo.detach()     
    print("Servo kalibroitu!")

def operate_servo():
    """Avaa ja sulkee servon luukkumekanismin lajittelun päätteeksi."""
    my_servo.value = 0.9    # Kiinni
    sleep(1)
    my_servo.detach()
    my_servo.value = -0.06  # Auki
    sleep(1)
    my_servo.detach()
    sleep(3)

def run_motor_sequence(rounds, steps_per_round):
    """Koko lajittelusekvenssi: ajo oikeaan kohtaan, servon liike ja palautus."""
    total_steps = rounds * steps_per_round
    enable.on()
    
    # 1. Eteenpäin oikean lokeron kohdalle
    direction.value = FORWARD
    move_steps(total_steps)
    
    # 2. Servo pudottaa roskan
    operate_servo()
    
    # 3. Taaksepäin palautus alkuasentoon
    direction.value = BACKWARD
    sleep(0.1)
    move_until_distance(STOP_DISTANCE_CM)
    
    enable.off()

# ==========================================
# 4. KUVANTUNNISTUKSEN KÄSITTELY
# ==========================================
def process_detected_item(item_name):
    """Parsii tunnistetun luokan nimen ja ajaa moottoria reitityssanakirjan (ROUTING) mukaan."""
    prefix = item_name.split("_")[0]
    
    if prefix in ROUTING:
        print(f"--> KÄSITELLÄÄN: {prefix.upper()}")
        params = ROUTING[prefix]
        run_motor_sequence(params["rounds"], params["steps"])
    else:
        print(f"--> Tuntematon kategoria: {prefix}, ohitetaan.")

# ==========================================
# 5. PÄÄOHJELMA JA KAMERALOOPPI
# ==========================================
if __name__ == "__main__":
    print("\n==================================")
    print("Laitteiston kalibrointi alkaa...")
    
    # A. Servon kalibrointi
    init_servo()

    # B. Askelmoottorin kalibrointi (Homing)
    print("Kalibroidaan askelmoottorin aloitusasento (sensori < 10 cm)...")
    enable.on()
    direction.value = BACKWARD
    sleep(0.1)
    move_until_distance(STOP_DISTANCE_CM)
    enable.off()
    
    print("Laitteisto kalibroitu ja käyttövalmis!")
    print("==================================\n")

    # C. YOLO ja kameran avaus
    # HUOM: Varmista että mallin polku (best.pt) on oikein!
    model = YOLO(r"best.pt") 
    cap = cv2.VideoCapture(0)
    current_object = None

    print("Kamera käynnistetty, odotetaan roskia... (Paina 'q' lopettaaksesi)")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Ei kuvaa kameralta.")
                break

            results = model(frame, verbose=False)
            detected_class_name = None
            highest_conf = 0.0

            # D. Etsitään varmin tunnistus ruudulta
            for result in results:
                boxes = result.boxes
                if len(boxes) > 0:
                    for box in boxes:
                        conf = float(box.conf[0])
                        if conf > highest_conf:
                            highest_conf = conf
                            class_id = int(box.cls[0])
                            detected_class_name = model.names[class_id]
                    
                    # Piirretään laatikot videokuvaan
                    frame = result.plot()

            # E. Jos kamerassa on UUSI esine, lajitellaan se
            if detected_class_name != current_object:
                if detected_class_name is not None:
                    print(f"\nUUSI KOHDE TUNNISTETTU: {detected_class_name} (Varmuus: {highest_conf:.2f})")
                    # Ajetaan lajittelu. Videokuva pysähtyy moottorin ajon ajaksi estäen tuplatunnistukset.
                    process_detected_item(detected_class_name)
                    print("Odotetaan uusia roskia...")
                
                # Päivitetään muuttuja, jottei samaa roskaa lajitella jatkuvasti
                current_object = detected_class_name

            # F. Näytetään videokuva
            cv2.imshow("Robottilajittelu", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nOhjelma keskeytetty käyttäjän toimesta!")

    finally:
        enable.off()
        cap.release()
        cv2.destroyAllWindows()
        print("Laitteisto ja kamera suljettu turvallisesti.")
