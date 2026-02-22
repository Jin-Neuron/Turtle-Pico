from machine import Pin
import time
from lib.TurtlePico import Leatherback

enable_right = Pin(Leatherback.MOTOR_ENR, Pin.OUT)
enable_left = Pin(Leatherback.MOTOR_ENL, Pin.OUT)
left = Pin(Leatherback.MOTOR_L, Pin.OUT)
right = Pin(Leatherback.MOTOR_R, Pin.OUT)

led_r = Pin(Leatherback.LED_R, Pin.OUT)
led_l = Pin(Leatherback.LED_L, Pin.OUT)

while True:

    enable_right.value(1)
    enable_left.value(1)
    led_r.value(1)
    led_l.value(1)
    left.value(1)
    right.value(1)
    print("forward")

    time.sleep(5)
    led_l.value(1)
    led_r.value(0)
    left.value(1)
    right.value(0)
    print("turn right")

    time.sleep(5)
    led_l.value(0)
    led_r.value(1)
    left.value(0)
    right.value(1)
    print("turn left")

    time.sleep(5)
    led_l.value(0)
    led_r.value(0)
    left.value(0)
    right.value(0)
    print("backward")

    time.sleep(5)
    enable_right.value(0)
    enable_left.value(0)
    led_l.value(0)
    led_r.value(1)
    time.sleep(1)
    led_l.value(1)
    led_r.value(0)
    time.sleep(1)
    led_l.value(0)
    led_r.value(1)
    time.sleep(1)
    led_l.value(1)
    led_r.value(0)
    time.sleep(1)
    print("stop")
