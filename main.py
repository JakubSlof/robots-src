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
        
ComunictionSetup()
SendData(1)