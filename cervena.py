import cv2
import numpy as np
import math
import serial
import time

def ComunictionSetup():
    port = 'COM4' # port pro komunikaci s Raspberry Pi /dev/ttyACM0
    baund_rate = 115200 # rychlost komunikace
    global ser
    ser = serial.Serial(port,baund_rate,timeout=1)
    time.sleep(2)
    ser.reset_input_buffer()
    print("serial comunication setup done")

def SendData(data):
    command = f"{data}\n"
    ser.write(command.encode('utf-8'))
    print('data send')

def waitForResponse():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            return line

def get_nearest_red_info(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definice červené barvy ve dvou rozsazích
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Maska pro červenou
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # Najdi kontury červených objektů
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    red_centers = []
    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            red_centers.append((cx, cy))

    if not red_centers:
        return None  # žádný červený objekt nenalezen

    # Najdi nejblíže spodnímu okraji
    closest = max(red_centers, key=lambda c: c[1])
    image_height = image.shape[0]
    image_width = image.shape[1]
    distance_from_bottom = image_height - closest[1]

    # Výpočet úhlu vzhledem ke středu (osa x)
    dx = closest[0] - image_width // 2
    dy = image_height - closest[1]
    angle = round(math.degrees(math.atan2(dy, dx)))  # Zaokrouhlený úhel

    return distance_from_bottom, angle


# Hlavní část

ComunictionSetup()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(3, 960)
cap.set(4, 640)

ret, frame = cap.read()
cap.release()

if not ret:
    print("Nepodařilo se načíst obraz.")
else:
    result = get_nearest_red_info(frame)
    if result:
        distance_px, angle_deg = result
        # Odeslání dat na Raspberry Pi
        SendData(distance_px)
        print(f"Vzdálenost od spodní hrany: {distance_px} px")
        print(f"Úhel od středu (osa X): {angle_deg:.2f}°")
    else:
        print("Nebyly nalezeny žádné červené objekty.")

    # Volitelně zobrazit obraz
    cv2.imshow("Frame", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
