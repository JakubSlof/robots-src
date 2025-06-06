import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import math
import serial
import time

RED_PIN = 17
GREEN_PIN = 24
BUTTON1_PIN = 27
BUTTON2_PIN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Defaultně svítí červená
GPIO.output(RED_PIN, GPIO.HIGH)
GPIO.output(GREEN_PIN, GPIO.LOW)

state_field = "red" #stav strany hriste

#######################################################
def ComunictionSetup():
    port = '/dev/ttyACM0' # port pro komunikaci s Raspberry Pi /dev/ttyACM0
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

def WaitForData():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            return line

########################################################
def px_to_cm_y(distance_px):
    return 2.06666720 * np.exp(0.0138075444 * distance_px) + 32.6886470

def px_to_cm_x_offset(offset_px, distance_cm, frame_width=960, fov_deg=45):
    # Každý pixel představuje určitý úhel
    deg_per_px = fov_deg / frame_width
    angle_rad = math.radians(offset_px * deg_per_px)

    # Přepočet offsetu na cm pomocí tangensu a hloubky
    cm_offset = math.tan(angle_rad) * distance_cm
    return cm_offset

########################################################
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
            blue_centers.append((x, y, w, h, cx, cy))

    if not blue_centers:
        return None  # žádný modrý objekt nenalezen

    # Najdi objekt nejblíže spodnímu okraji
    closest = max(blue_centers, key=lambda c: c[1])
    image_height = image.shape[0]
    image_width = image.shape[1]

    distance_from_bottom = image_height - closest[1]  # px ve svislém směru (čím nižší, tím menší)
    offset_x = closest[0] - (image_width // 2)        # px vlevo/zprava od středu (může být záporný)

    return (x, y, w, h),distance_from_bottom, offset_x


def get_nearest_red_info(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Detekce červené
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    red_info = []

    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > 400:
            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            red_info.append((x, y, w, h, cx, cy))

    if not red_info:
        return None

    closest = max(red_info, key=lambda item: item[1] + item[3])  # Nejnižší objekt

    x, y, w, h, cx, cy = closest
    image_width = image.shape[1]
    image_height = image.shape[0]

    distance_from_bottom = image_height - (y + h)
    offset_x = cx - image_width // 2

    return (x, y, w, h), distance_from_bottom, offset_x

#######################################################

while True:
	if GPIO.input(BUTTON1_PIN) == GPIO.LOW:  # Tlačítko 1 stisknuto
		# Prohoď LEDky
		if GPIO.input(RED_PIN):
			GPIO.output(RED_PIN, GPIO.LOW)
			GPIO.output(GREEN_PIN, GPIO.HIGH)
			state_field = "blue"
		else:
			GPIO.output(RED_PIN, GPIO.HIGH)
			GPIO.output(GREEN_PIN, GPIO.LOW)
			state_field = "red"
		time.sleep(0.2)  # Debounce

	if GPIO.input(BUTTON2_PIN) == GPIO.LOW:  # Tlačítko 2 stisknuto
		GPIO.output(RED_PIN, GPIO.LOW)
		GPIO.output(GREEN_PIN, GPIO.LOW)
		time.sleep(0.01)  # Debounce
		break

	time.sleep(0.01)

time.sleep(1)

ComunictionSetup()
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(3, 960)
cap.set(4, 640)
print("camdone")

if state_field == "red":
	GPIO.output(RED_PIN, GPIO.HIGH)
	while True:
		if WaitForData() == "sendnudes":
                    for i in range(5):
                        h, j = cap.read()
                    ret, frame = cap.read()
                    result = get_nearest_red_info(frame)
                    if result:
                        (x, y, w, h), distance_px, offset_x = result
                # Přepočet do cm
                        cm_y = px_to_cm_y(distance_px)
                        cm_x = px_to_cm_x_offset(offset_x, cm_y, frame_width=960)
                        SendData(int(distance_px))
                        time.sleep(0.1)  # Krátká prodleva pro stabilitu
                        SendData(int(offset_x))
                        print(f"Odsazení X: {offset_x}px → {cm_x:.1f} cm, Spodní vzdálenost: {distance_px}px → {cm_y:.1f} cm")
else:
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    while True:
        if WaitForData() == "sendnudes":
            for i in range(5):
                h, j = cap.read()
            ret, frame = cap.read()
            result = get_nearest_blue_info(frame)
            if result:
                (x, y, w, h), distance_px, offset_x = result
                cm_y = px_to_cm_y(distance_px)
                cm_x = px_to_cm_x_offset(offset_x, cm_y, frame_width=960)
                SendData(int(distance_px))
                time.sleep(0.1)  # Krátká prodleva pro stabilitu
                SendData(int(offset_x))
                print(f"Odsazení X: {offset_x}px → {cm_x:.1f} cm, Spodní vzdálenost: {distance_px}px → {cm_y:.1f} cm")

