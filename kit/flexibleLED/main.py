import machine
from machine import PWM
import time
 
blue=PWM(machine.Pin(28, machine.Pin.OUT))
red = PWM(machine.Pin(27, machine.Pin.OUT))

blue.freq(1000)
red.freq(1000)

i = 0
status = 0

while True:
    if i > 65536:
        status = 1
    elif i < 0:
        status = 0
    red.duty_u16(i)
    blue.duty_u16(65536-i)
    print(i)

    if status == 0:
        i += 30
    else:
        i -= 30
    
    time.sleep(0.001)