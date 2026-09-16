from machine import PWM, Pin, SPI, reset
from lib.wavplayer import WavPlayer
import os
from lib.sdcard import SDCard
from lib.ssd1306 import SSD1306_SPI
from lib.img_lib import img_lib
import framebuf
import time

#Pin設定
orange = PWM(Pin("LED_R", Pin.OUT))
green = PWM(Pin("LED_L", Pin.OUT))
playSW = Pin("SW_R", Pin.IN, Pin.PULL_DOWN)
stopSW = Pin("SW_L", Pin.IN, Pin.PULL_DOWN)
#oled
oled_cs = Pin("LCD_CS")
dc = Pin("LCD_DC")
rst = Pin("LCD_RST")
#sd
sd_cs = Pin("SD_CS")
#i2s
sck_pin = Pin("I2S_BCLK")   # シリアルクロック出力
ws_pin = Pin("I2S_LRCLK")    # ワードクロック出力
sd_pin = Pin("I2S_SDATA")    # シリアルデータ出力
#ultrasonic
trig = Pin("TRIG_TX", Pin.OUT)
echo = Pin("ECHO_RX", Pin.IN)

orange.freq(1000)
green.freq(1000)

spi = SPI( 1,
           baudrate = 100000,
           sck  = Pin("SPI_SCK"),
           mosi = Pin("SPI_MOSI"),
           miso = Pin("SPI_MISO"))

sd = SDCard(spi, sd_cs)
display = SSD1306_SPI(128, 64, spi, dc, rst, oled_cs)
fb = framebuf.FrameBuffer(img_lib.techring, 74, 64, framebuf.MONO_HLSB)

def main():

    os.mount(sd, '/sd')
    os.chdir('sd')
    list = os.listdir("/sd")

    #jin_imgを表示
    display.fill(0)
    display.blit(fb, int((128-74) / 2), 0)
    display.show()
    time.sleep(3)

    try: 
        for i in range(1, 64):
            display.fill(0)
            display.blit(fb, int((128-74) / 2), -i)
            display.show()
            time.sleep(0.01)
        
        for i in range(0, len(list)):
            green.duty_u16(65535)
            orange.duty_u16(0)

            if(list[i].find(".wav") == -1):
                continue
            
            wp = WavPlayer(
                id=0,
                sck_pin=sck_pin,
                ws_pin=ws_pin,
                sd_pin=sd_pin,
                ibuf=40000,
            )
            wp.play(list[i], loop=False)
            display.fill(0)
            display.text(list[i], 0, 0)
            display.show()

            j = 0
            while wp.isplaying():
                distance = messure_distance()
                print(distance,"cm")
                if(j > 128):
                    j = 0
                else:
                    j += 1

                display.fill(0)
                display.text(list[i], -j, 0)
                display.show()

                if distance < 5:
                    print("skip")
                    wp.stop()
                    green.duty_u16(0)
                    orange.duty_u16(65535)
                    time.sleep(0.5)
                    break
                if stopSW.value() == 1:
                    #print("pause")
                    #wp.pause()
                    wp.increase_volume()
                    #green.duty_u16(0)
                    #orange.duty_u16(65535)
                if playSW.value() == 1:
                    #print("resume")
                    #wp.resume()
                    wp.decrease_volume()
                    #green.duty_u16(65535)
                    #orange.duty_u16(0)
                time.sleep(0.15)
                pass
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        reset()

def messure_distance():
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
    dis = (timepassed * 0.0343) / 2
    return dis

if __name__ == "__main__":
    main()
    display.fill(0)
    display.text("end", 0, 0)
    display.show()
    reset()