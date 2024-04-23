import time
from machine import Pin
from machine import PWM
import neopixel
import _thread

pixelNum = 15

#ピンを設定
trig = Pin(1, Pin.OUT)
echo = Pin(0, Pin.IN)

np1 = neopixel.NeoPixel(Pin(13), pixelNum)

red = Pin(4, Pin.OUT)
blue = Pin(18, Pin.OUT)

sig_red = PWM(red)
sig_blue = PWM(blue)

sig_red.freq(1000)
sig_blue.freq(1000)

def main():
    status = False

    while True:
        #トリガから超音波出力
        trig.low()
        time.sleep_us(2)
        trig.high()
        time.sleep_us(10)
        trig.low()
        signaloff, signalon = 0, 0
        #echoに返ってくるまでの時間を計測
        while echo.value() == 0:
            signaloff = time.ticks_us()
        while echo.value() == 1:
            signalon = time.ticks_us()
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        #logging
        print("dinstance: ",distance,"cm")

        if distance < 15 and status == False:
            status = True
            for i in range(pixelNum):
                sig_red.duty_u16(int(16384/pixelNum*i))
                sig_blue.duty_u16(int(16384/pixelNum*i))
                np1[i] = (0, 16, 32)
                np1.write()
                time.sleep_ms(25)
        elif distance > 15 and status == True:
            status = False
            sig_red.duty_u16(0)
            sig_blue.duty_u16(0)
            for i in range(15):
                np1[i] = (0, 0, 0)
            np1.write()

        time.sleep(0.5)

main()