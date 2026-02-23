from machine import Pin
import time

# Leatherback motor enable pin is each for left and right, but TurtlePico has one motor enable pin.

# for Leatherback model
#enable_right = Pin("MOTOR_ENR", Pin.OUT)
#enable_left = Pin("MOTOR_ENL", Pin.OUT)

# for TurtlePico model
enable = Pin("MOTOR_EN", Pin.OUT)

left = Pin("MOTOR_L", Pin.OUT)
right = Pin("MOTOR_R", Pin.OUT)

led_r = Pin("LED_R", Pin.OUT)
led_l = Pin("LED_L", Pin.OUT)

while True:

    # for Leatherback model
    # enable_right.value(1)
    # enable_left.value(1)

    # for TurtlePico model
    enable.value(1)
    
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
    # for Leatherback model
    # enable_right.value(0)
    # enable_left.value(0)

    # for TurtlePico model
    enable.value(0)
    
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
