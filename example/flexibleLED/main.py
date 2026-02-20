import machine
from machine import PWM, Pin
import time
from lib.TurtlePico import Leatherback

RSW = Pin(Leatherback.SW_R, Pin.IN, Pin.PULL_DOWN)
LSW = Pin(Leatherback.SW_L, Pin.IN, Pin.PULL_DOWN)

LEDR = Pin(Leatherback.LED_R, Pin.OUT)
LEDL = Pin(Leatherback.LED_L, Pin.OUT)

i = 0
status = 0

while True:
    print("Button R:", RSW.value(), "Button L:", LSW.value())
    time.sleep(0.1)