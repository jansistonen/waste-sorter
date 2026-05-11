from gpiozero import OutputDevice, DistanceSensor, Servo
from time import sleep

# -----------------------------
# PINNIT
# -----------------------------
STEP_PIN = 27
DIR_PIN = 17
ENABLE_PIN = 22

TRIGGER_PIN = 5
ECHO_PIN = 6

SERVO_PIN = 23

# -----------------------------
# LAITTEET
# -----------------------------
step = OutputDevice(STEP_PIN)
direction = OutputDevice(DIR_PIN)
enable = OutputDevice(
    ENABLE_PIN,
    active_high=False,
    initial_value=False
)

sensor = DistanceSensor(
    echo=ECHO_PIN,
    trigger=TRIGGER_PIN,
    max_distance=2.0
)

# Servon asetukset kuvan mukaisesti
my_servo = Servo(
    SERVO_PIN, 
    initial_value=1, 
    min_pulse_width=0.0005, 
    max_pulse_width=0.0024
)

# -----------------------------
# ASETUKSET
# -----------------------------
FORWARD = False
BACKWARD = True

STEP_DELAY = 0.001       

# Pysäytysetäisyys palautuksessa
STOP_DISTANCE_CM = 10.0

# -----------------------------
# FUNKTIOT
# -----------------------------
def move_steps(amount):
    """
    Liikuttaa moottoria eteenpäin annetun määrän steppejä.
    """
    for _ in range(amount):
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)

def move_until_distance(stop_distance_cm):
    """
    Liikuttaa moottoria kunnes sensorin mittaama etäisyys
    on pienempi tai yhtä suuri kuin stop_distance_cm.
    """
    while True:
        distance_cm = sensor.distance * 100
        
        # Pysäytetään, jos raja alittuu
        if distance_cm <= stop_distance_cm:
            print(f"Raja saavutettu ({distance_cm:.1f} cm), pysäytetään")
            break

        # Otetaan askel
        step.on()
        sleep(STEP_DELAY)
        step.off()
        sleep(STEP_DELAY)

def operate_servo():
    """
    Ajaa servon liitetiedoston servo.py logiikan mukaisesti.
    """
    print("--- Servon ajo alkaa ---")
    print("Suljetaan servo...")
    my_servo.value = 0.9    # Minimiasento (kiinni)
    sleep(1)
    my_servo.detach()
    print("Valmis!")

    print("Avataan servo...")
    my_servo.value = -0.06  # Maksimiasento (auki)
    sleep(1)
    my_servo.detach()
    
    print("Pidetään tauko (3 sekuntia)...")
    sleep(3)
    print("--- Servon ajo valmis ---")

def run_motor_sequence(rounds, steps_per_round):
    """
    Ajaa askelmoottoria eteenpäin, käyttää servoa ja
    palauttaa askelmoottorin takaisin sensorin antamaan rajaan asti.
    """
    total_steps = rounds * steps_per_round
    print(f"\nAloitetaan ajo: {rounds} kierrosta, {steps_per_round} askelta/kierros (yhteensä {total_steps} askelta)")
    
    enable.on() # Laitetaan askelmoottori päälle
    
    # 1. Liike eteenpäin
    direction.value = FORWARD
    print("Liikutaan eteenpäin...")
    move_steps(total_steps)
    
    # 2. Servon ajo
    operate_servo()
    
    # 3. Liike taaksepäin (palautus)
    print("Palautetaan askelmoottori taaksepäin sensorin perusteella...")
    direction.value = BACKWARD
    sleep(0.1) # Pieni tauko suunnanvaihdon yhteydessä
    move_until_distance(STOP_DISTANCE_CM)
    
    enable.off() # Askelmoottori lepotilaan
    print("Koko sekvenssi valmis.\n")

# -----------------------------
# PÄÄOHJELMA
# -----------------------------
try:
    print("\n==================================")
    print("Ohjelma käynnistyy...")
    
    # ALKUASETUS (Homing): Ajetaan heti alkuun moottori oikeaan paikkaan
    print("Kalibroidaan aloitusasento: Etsitään sensori < 10 cm...")
    enable.on()
    direction.value = BACKWARD
    sleep(0.1)
    move_until_distance(STOP_DISTANCE_CM)
    enable.off()
    print("Aloitusasento saavutettu!")
    print("==================================\n")
    
    print("Paina Ctrl+C lopettaaksesi milloin tahansa.\n")
    
    # KÄYTTÄJÄN VALINTALUUPPI
    while True:
        print("Valitse haluamasi toiminto:")
        print("1) Rounds: 5,  Steps: 95")
        print("2) Rounds: 10, Steps: 95")
        print("3) Rounds: 15, Steps: 95")
        print("4) Rounds: 19, Steps: 92")
        valinta = input("Syötä numero (1-4) tai 'q' lopettaaksesi: ")
        
        if valinta == '1':
            run_motor_sequence(rounds=5, steps_per_round=95)
        elif valinta == '2':
            run_motor_sequence(rounds=10, steps_per_round=95)
        elif valinta == '3':
            run_motor_sequence(rounds=15, steps_per_round=95)
        elif valinta == '4':
            run_motor_sequence(rounds=19, steps_per_round=92)
        elif valinta.lower() == 'q':
            print("Lopetetaan ohjelma...")
            break
        else:
            print("Virheellinen valinta, yritä uudelleen.\n")

except KeyboardInterrupt:
    print("\nOhjelma lopetettu käyttäjän toimesta (Ctrl+C)")

finally:
    enable.off()
    print("Turvallinen lopetus tehty (moottorit pois päältä).")
