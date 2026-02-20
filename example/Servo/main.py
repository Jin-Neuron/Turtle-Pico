from machine import PWM, Pin
import time
from lib.TurtlePico import Leatherback

servo1 = PWM(Pin(Leatherback.ESC_SERVO_RR))
servo1.freq(50)

max_duty = 65025
dig_min = 0.025   #-90°
dig_max = 0.12     #90°

i = 0
status = 0

while True:
    if i > 180:
        status = 1
    elif i < 0:
        status = 0
    deg = dig_min + i * (dig_max - dig_min) / 180
    print(i)
    if status > 0:
        i -= 1
    else:
        i += 1
    servo1.duty_u16(int(deg * max_duty))
    time.sleep_ms(10)