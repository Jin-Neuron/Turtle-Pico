from machine import Pin, PWM
import time

r_sw = Pin("SW_R", Pin.IN)
l_sw = Pin("SW_L", Pin.IN)

#duty cycle
Max_duty = 0.1 * 65536
Min_duty = 0.05 * 65536

#calibration
def calibration():
    duty = Max_duty
    status = 1
    print("Calibration start")
    for i in range(0, 3):
        for j in range(0, 10):
            if status == 1:
                duty -= 0.005 * 65536
            else:
                duty += 0.005 * 65536
            print(duty / 65536)
            BLDC.duty_u16(int(duty))
            time.sleep(0.1)
        status = status * -1
        time.sleep(3)
    print("Calibration done")

BLDC = PWM(Pin("ESC_SERVO_FR"))
BLDC.freq(50)

duty = Max_duty
BLDC.duty_u16(int(duty))

isCalibrated = False

while True:
    if r_sw.value() == 1:
        if isCalibrated == False:
            calibration()
            isCalibrated = True
            duty = Min_duty
        else:
            if duty < Max_duty:
                duty += 0.001 * 65536
            print(duty / 65536)
            BLDC.duty_u16(int(duty))
            time.sleep(0.5)
    elif l_sw.value() == 1:
        if isCalibrated == True:
            if duty > Min_duty:
                duty -= 0.001 * 65536
            print(duty / 65536)
            BLDC.duty_u16(int(duty))
            time.sleep(0.5)