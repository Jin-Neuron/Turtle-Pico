from machine import Pin, PWM
import time, _thread
from lib.TurtlePico import Leatherback

servo1 = PWM(Pin(Leatherback.ESC_SERVO_RR))
servo1.freq(50)

enable_right = Pin(Leatherback.MOTOR_ENR, Pin.OUT)
enable_left = Pin(Leatherback.MOTOR_ENL, Pin.OUT)
left = Pin(Leatherback.MOTOR_L, Pin.OUT)
right = Pin(Leatherback.MOTOR_R, Pin.OUT)

led_r = Pin(Leatherback.LED_R, Pin.OUT)
led_l = Pin(Leatherback.LED_L, Pin.OUT)

def servo_control():
    global servo1
    max_duty = 65025
    dig_min = 0.025   # -90°
    dig_max = 0.12    # 90°

    i = 0
    status = 0

    while True:
        if i > 180:
            status = 1
        elif i < 0:
            status = 0
        deg = dig_min + i * (dig_max - dig_min) / 180
        #print(i)
        if status > 0:
            i -= 1
        else:
            i += 1
        servo1.duty_u16(int(deg * max_duty))
        time.sleep_ms(10)

_thread.start_new_thread(servo_control, ())

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
