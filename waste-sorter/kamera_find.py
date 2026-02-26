import cv2

print("Etsitään kameroita...")
for i in range(20):
    # Pyydetään OpenCV:tä olemaan tulostamatta omia virheitään konsoliin
    cap = cv2.VideoCapture(i, cv2.CAP_V4L2) 
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"-> TOIMIVA KAMERA LÖYTYI INDEKSISTÄ: {i}")
        else:
            print(f"-> Indeksi {i} aukesi, mutta ei antanut kuvaa (todennäköisesti syvyyssensori tai virtuaalikamera)")
        cap.release()

print("Etsintä valmis!")