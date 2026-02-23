import machine
from machine import PWM, Pin
import time

RSW = Pin("SW_R", Pin.IN, Pin.PULL_DOWN)
LSW = Pin("SW_L", Pin.IN, Pin.PULL_DOWN)

LEDR = Pin("LED_R", Pin.OUT)
LEDL = Pin("LED_L", Pin.OUT)

while True:
    LEDL.value(LSW.value())
    LEDR.value(RSW.value())
    time.sleep(0.1)