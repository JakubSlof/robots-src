import cv2
import numpy as np
import math
import serial
import time

def ComunictionSetup():
    port = '/dev/ttyACM0' # port pro komunikaci s Raspberry Pi
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

def waitForData():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            return line
                

def get_nearest_blue_info(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definice modré barvy v HSV
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])

    # Maska pro modrou
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Najdi kontury modrých objektů
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blue_centers = []
    for cnt in contours_blue:
        area = cv2.contourArea(cnt)
        if area > 400:
            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            blue_centers.append((cx, cy))

    if not blue_centers:
        return None  # žádný modrý objekt nenalezen

    # Najdi objekt nejblíže spodnímu okraji
    closest = max(blue_centers, key=lambda c: c[1])
    image_height = image.shape[0]
    image_width = image.shape[1]
    distance_from_bottom = image_height - closest[1]

    # Výpočet úhlu vzhledem ke středu
    dx = closest[0] - image_width // 2
    dy = image_height - closest[1]
    angle = round(math.degrees(math.atan2(dy, dx)))

    return distance_from_bottom, angle

# Hlavní část programu
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(3, 960)
cap.set(4, 640)

while True:
    if waitForData() == "sendnudes":
        for i in range(5):
            h,j = cap.read()
        ret, frame = cap.read()
        if not ret:
            print("Nepodařilo se načíst obraz.")
        else:
            result = get_nearest_blue_info(frame)
            if result:
                distance_px, angle_deg = result
                SendData(int(distance_px))
                time.sleep(0.1)  # Krátká prodleva pro stabilitu
                SendData(int(angle_deg))
                print(f"Vzdálenost od spodní hrany: {distance_px} px")
                print(f"Úhel od středu (osa X): {angle_deg}°")
            else:
                print("Nebyly nalezeny žádné modré objekty.")
    time.sleep(0.1)  # Krátká prodleva pro stabilitu
