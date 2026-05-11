from gpiozero import OutputDevice, DistanceSensor
from time import sleep

# -----------------------------
# PINNIT
# -----------------------------
STEP_PIN = 17
DIR_PIN = 27
ENABLE_PIN = 22

TRIGGER_PIN = 5
ECHO_PIN = 6

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

# -----------------------------
# ASETUKSET
# -----------------------------
FORWARD = False
BACKWARD = True

STEP_DELAY = 0.003       # isompi = hitaampi moottori
SENSOR_DELAY = 0.02      # tauko sensorin lukujen välissä

# Pysäytysetäisyys palautuksessa
STOP_DISTANCE_CM = 10.0

# -----------------------------
# FUNKTIOT
# -----------------------------
def read_distance_cm():
    """
    Lukee sensorin etäisyyden senttimetreinä.
    Palauttaa None, jos lukema vaikuttaa virheelliseltä.
    """
    distance_cm = sensor.distance * 100

    if distance_cm <= 0:
        return None

    return distance_cm

def one_step():
    """
    Tekee yhden step-pulssin A4988-ajurille.
    """
    step.on()
    sleep(STEP_DELAY)
    step.off()
    sleep(STEP_DELAY)

def move_steps(amount):
    """
    Liikuttaa moottoria annetun määrän steppejä.
    """
    for _ in range(amount):
        one_step()

def move_until_distance(stop_distance_cm):
    """
    Liikuttaa moottoria kunnes sensorin mittaama etäisyys
    on pienempi tai yhtä suuri kuin stop_distance_cm.
    """
    while True:
        distance_cm = read_distance_cm()

        if distance_cm is None:
            print("Virheellinen sensorilukema")
            sleep(SENSOR_DELAY)
            continue

        print(f"Etäisyys: {distance_cm:.1f} cm")

        if distance_cm <= stop_distance_cm:
            print("Raja saavutettu, pysäytetään")
            break

        one_step()
        sleep(SENSOR_DELAY)

def run_motor_sequence(rounds, steps_per_round):
    """
    Ajaa moottoria eteenpäin annettujen kierrosten ja askeleiden verran,
    minkä jälkeen palauttaa taaksepäin sensorin antamaan rajaan asti.
    """
    total_steps = rounds * steps_per_round
    print(f"\n--- Aloitetaan ajo: {rounds} kierrosta, {steps_per_round} askelta/kierros (yhteensä {total_steps} askelta) ---")
    
    enable.on() # Laitetaan moottori päälle
    
    # Liike eteenpäin
    direction.value = FORWARD
    print("Liikutaan eteenpäin...")
    move_steps(total_steps)
    
    # Liike taaksepäin (palautus)
    print("Palautetaan taaksepäin sensorin perusteella...")
    direction.value = BACKWARD
    sleep(0.1) # Pieni tauko suunnanvaihdon yhteydessä
    move_until_distance(STOP_DISTANCE_CM)
    
    enable.off() # Moottori lepotilaan
    print("Ajo valmis. Moottori lepotilassa.\n")

# -----------------------------
# PÄÄOHJELMA
# -----------------------------
try:
    print("Ohjelma käynnistetty. Paina Ctrl+C lopettaaksesi milloin tahansa.")
    
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
    print("Turvallinen lopetus tehty (enable.off).")
