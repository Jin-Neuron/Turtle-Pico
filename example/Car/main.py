import time
import st7789
import tft_config
from machine import Pin, PWM

servo_rr = PWM("ESC_SERVO_RR")
servo_rr.freq(50)

max_duty = 65025
dig_min = 0.025   #-90°
dig_max = 0.12     #90°

led_r = Pin("LED_R", Pin.OUT)
led_l = Pin("LED_L", Pin.OUT)

led_r.value(1)
led_l.value(1)

# Leatherback motor enable pin is each for left and right, but TurtlePico has one motor enable pin.

# for Leatherback model
#motor_len = Pin("MOTOR_ENL", Pin.OUT)
#motor_ren = Pin("MOTOR_ENR", Pin.OUT)
# for TurtlePico model
enable = Pin("MOTOR_EN", Pin.OUT)

motor_l = Pin("MOTOR_L", Pin.OUT)
motor_r = Pin("MOTOR_R", Pin.OUT)

trig = Pin("TRIG_TX", Pin.OUT)
echo = Pin("ECHO_RX", Pin.IN)

MotorStatus_R = 0
MotorStatus_L = 0

tft = tft_config.config(rotation=3)
tft.init()

# 0: TurnRight
# 1: TurnLeft
currentStatus = 0

degs = [30, 110]
pic = ['/img/TUT_2.jpg', '/img/JinNeuron.jpg']

led_l.value(0)
led_r.value(1)

deg = dig_min + degs[0] * (dig_max - dig_min) / 180
servo_rr.duty_u16(int(deg * max_duty))
time.sleep_ms(10)

tft.jpg(pic[0], 0, 0, st7789.SLOW)

motor_l.value(0)
motor_r.value(0)

#motor_len.value(1)
#motor_ren.value(1)

time.sleep(2)

print("Start")

while True:
    # for Leatherback model
    # motor_len.value(0)
    # motor_ren.value(0)
    # for TurtlePico model
    enable.value(0)

    while True:
        trig.low()
        time.sleep_us(2)
        trig.high()
        time.sleep_us(10)
        trig.low()
        signaloff, signalon = 0, 0
        while echo.value() == 0:
            signaloff = time.ticks_us()
        while echo.value() == 1:
            signalon = time.ticks_us()
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        if distance < 3:
            print("Hand detected at %.2f cm" % distance)
            break
        time.sleep(0.1)

    if currentStatus == 0:
        currentStatus = 1
        rotation = 0
        led_l.value(1)
        led_r.value(0)
    else:
        currentStatus = 0
        rotation = 3
        led_l.value(0)
        led_r.value(1)
    
    tft.fill(st7789.WHITE)

    deg = dig_min + degs[currentStatus] * (dig_max - dig_min) / 180
    servo_rr.duty_u16(int(deg * max_duty))
    time.sleep_ms(10)

    tft.rotation(rotation)

    tft.jpg(pic[currentStatus], 0, 0, st7789.SLOW)

    
    motor_l.value(currentStatus)
    motor_r.value(currentStatus)

    #motor_len.value(1)
    #motor_ren.value(1)

    time.sleep(2)