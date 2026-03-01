import cv2
from ultralytics import YOLO
import time

# 1. Ladataan kevyt YOLOv11-malli (n-versio on nopea videokuvalle)
model = YOLO("best_ncnn_model") #nyt käytössä kevyempi ncnn, vaihda "best.pt" pytorch mallia käyttääksesi

# 2. Avataan kamera (indeksi 0, 1 webc, 6=Intel RGB)
cap = cv2.VideoCapture(0)

# Muuttuja muistaa mikä esine kuvassa on juuri nyt
current_object = None 

# Jono käsiteltäville objekteille
handle_queue = []

# Käsittelyfunktio, jos tietorakenteessa on jotain
def item_handler(handle_queue: list):
    item = str(handle_queue.pop())
    item_class = item.split("_")

    if item_class[0] == "bio":
        print("BIOJÄTETTÄ, KÄSITELLÄÄN BIOJÄTETTÄ")
        time.sleep(3)
    
    elif item_class[0] == "cardb":
        print("KÄSITELLÄÄN KARTONKIA")
        time.sleep(3)

    elif item_class[0] == "paper":
        print("KÄSITELLÄÄN PAPERIA")
        time.sleep(3)
    
    elif item_class[0] == "plastic":
        print("KÄSITELLÄÄN PAPERIA")
        time.sleep(3)
    
    elif item_class[0] == "metal":
        print("KÄSITELLÄÄN METALLIA")
        time.sleep(3)
    
    handle_queue.remove

    
print("Kamera käynnistetty. Odotetaan esineitä...")

############################
#
#     "PÄÄOHJELMA ALKAA"
#
##############################

while True:

    print(handle_queue)

    ret, frame = cap.read()
    if not ret:
        print("Ei kuvaa kameralta.")
        break

    # 3. Tehdään tunnistus. 
    # HUOM: verbose=False on kriittinen, estää YOLOa spammaamasta terminaalia!
    results = model(frame, verbose=False)

    detected_class_name = None
    highest_conf = 0.0

    # 4. Etsitään ruudun selkein tunnistus
    for result in results:
        boxes = result.boxes
        if len(boxes) > 0:
            # Käydään läpi kaikki löydökset ja valitaan se, jolla on suurin varmuus
            for box in boxes:
                conf = float(box.conf[0])
                if conf > highest_conf:
                    highest_conf = conf
                    class_id = int(box.cls[0])
                    detected_class_name = model.names[class_id]
            
            # Piirretään laatikko kuvaan visuaalista testausta varten
            frame = result.plot()

    # 5. TARKISTETAAN ONKO ESINE VAIHTUNUT
    if detected_class_name != current_object:
        if detected_class_name is not None:
            # Uusi esine tunnistettu! 
            print(f"-> UUSI ESINE: {detected_class_name} (Varmuus: {highest_conf:.2f})")
            # TÄHÄN TULEE ROBOTIN MEKAANINEN LAJITTELUKÄSKY (esim. Serial write tai pyynnön lähetys)

            handle_queue.append(detected_class_name)
            
        else:
            # Kuva on tyhjä, esine meni jo
            print("-> Linjasto tyhjä. Odotetaan...")
        
        # Päivitetään nykyinen tila
        current_object = detected_class_name

        # Jonossa on jotain, kutsutaan lajittelu lajittelufunktio
        if len(handle_queue) > 0:
            item_handler(handle_queue)

    # 6. Näytetään videokuva
    cv2.imshow("Robottilajittelu", frame)

    # Lopeta painamalla 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Siivotaan lopuksi
cap.release()
cv2.destroyAllWindows()