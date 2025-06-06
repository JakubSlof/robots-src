import cv2
import numpy as np
import math

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


# Převodní funkce
def px_to_cm_y(distance_px):
    return 2.06666720 * np.exp(0.0138075444 * distance_px) + 32.6886470

def px_to_cm_x_offset(offset_px, distance_cm, frame_width=960, fov_deg=45):
    # Každý pixel představuje určitý úhel
    deg_per_px = fov_deg / frame_width
    angle_rad = math.radians(offset_px * deg_per_px)

    # Přepočet offsetu na cm pomocí tangensu a hloubky
    cm_offset = math.tan(angle_rad) * distance_cm
    return cm_offset


# Hlavní smyčka
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(3, 960)
cap.set(4, 640)

if not cap.isOpened():
    print("Nepodařilo se otevřít kameru.")
    exit()

print("Stiskni 'q' pro ukončení.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Chyba při čtení z kamery.")
        break

    result = get_nearest_red_info(frame)
    if result:
        (x, y, w, h), distance_px, offset_x = result

        # Přepočet do cm
        cm_y = px_to_cm_y(distance_px)
        cm_x = px_to_cm_x_offset(offset_x, cm_y, frame_width=960)

        # Vykresli výsledky
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        text = f"X: {cm_x:.1f} cm | Y: {cm_y:.1f} cm"
        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        print(f"Odsazení X: {offset_x}px → {cm_x:.1f} cm, Spodní vzdálenost: {distance_px}px → {cm_y:.1f} cm")
    else:
        cv2.putText(frame, "Zadny cerveny objekt nenalezen", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Detekce červeného objektu", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
