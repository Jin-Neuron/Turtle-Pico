import _thread
import machine
from machine import Pin, I2C, SPI
import time
import ustruct
import math
from lib.ssd1306 import SSD1306_SPI
from lib.img_lib import img_lib
import framebuf
import network
import socket
from wifi_config import wifi_config

#i2c設定
i2c = I2C(0, scl=Pin("I2C_SCL"), sda=Pin("I2C_SDA"), freq=100000)
#spi設定
spi = SPI(1, baudrate = 100000, sck = Pin("SPI_SCK"), mosi = Pin("SPI_MOSI"))

#アドレスを設定
addr_ag = 0x6a
addr_m = 0x1c
addr_temp = 0x38
#自宅Wi-FiのSSIDとパスワードを入力
ssid = wifi_config.ssid
password = wifi_config.pw

#ピンを設定
trig = Pin("TRIG_TX", Pin.OUT)
echo = Pin("ECHO_RX", Pin.IN)
cs = Pin("OLED_CS", Pin.OUT)
dc = Pin("OLED_DC", Pin.OUT)
rst = Pin("OLED_RST", Pin.OUT)

#OLEDを初期化
display = SSD1306_SPI(128, 64, spi, dc, rst, cs)
fb = framebuf.FrameBuffer(img_lib.techring, 74, 64, framebuf.MONO_HLSB)

#加速度・ジャイロセンサのレジスタ
CTRL_REG1_G = 0x10
CTRL_REG2_G = 0x11
CTRL_REG3_G = 0x12
ORIENT_CFG_G = 0x13
CTRL_REG4 = 0x1E
CTRL_REG5_XL = 0x1F
CTRL_REG6_XL = 0x20
CTRL_REG7_XL = 0x21

#センサの設定
i2c.writeto_mem(addr_ag, CTRL_REG1_G, b'\x60')  #0110 0000
i2c.writeto_mem(addr_ag, CTRL_REG2_G, b'\x00')  #0000 0000
i2c.writeto_mem(addr_ag, CTRL_REG3_G, b'\x41')  #0100 0001
i2c.writeto_mem(addr_ag, ORIENT_CFG_G, b'\x40') #0100 0000
i2c.writeto_mem(addr_ag, CTRL_REG4, b'\x3a')    #0011 1010
i2c.writeto_mem(addr_ag, CTRL_REG5_XL, b'\x38') #0011 1000
i2c.writeto_mem(addr_ag, CTRL_REG6_XL, b'\x3c') #0011 1100
i2c.writeto_mem(addr_ag, CTRL_REG7_XL, b'\x00') #0000 0000

#磁気センサのレジスタ
CTRL_REG1_M = 0x20
CTRL_REG2_M = 0x21
CTRL_REG3_M = 0x22
CTRL_REG4_M = 0x23
CTRL_REG5_M = 0x24

#センサの設定
i2c.writeto_mem(addr_m, CTRL_REG1_M, b'\x14')  #0001 0100
i2c.writeto_mem(addr_m, CTRL_REG2_M, b'\x40')  #0100 0000
i2c.writeto_mem(addr_m, CTRL_REG3_M, b'\x00')  #0000 0000
i2c.writeto_mem(addr_m, CTRL_REG4_M, b'\x0c')  #0000 1100
i2c.writeto_mem(addr_m, CTRL_REG5_M, b'\x00')  #0000 0000

#加速度、ジャイロ、磁気の変数
AccX, AccY, AccZ = 0, 0, 0
GyrX, GyrY, GyrZ = 0, 0, 0
MagX, MagY, MagZ = 0, 0, 0
text_hum, text_temp, text_distance = "", "", ""

#Wi-Fiに接続
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

#HTMLを定義
html = """<!DOCTYPE html><html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">
    <style> html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
        .buttonGreen { background-color: #4CAF50; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
        .buttonRed { background-color: #D11D53; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
        .buttonBlue { background-color: #191970; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
        .contents { overflow: hidden; padding: auto; width: 100%%; margin: 0 auto; }
        .item { width: 33%%; float: left; text-align: center; }
    </style>
</head>
<body>
    <center>
        <h1>Get Sensors Value</h1>
    </center><br><br>
    <div class="contents">
        <h2 style="color: red;">Acceleration</h2>
        <div class="item">
            <h3>Acceleration_X</h3>
            <p>%s</p>
        </div>
        <div class="item">
            <h3>Acceleration_Y</h3>
            <p>%s</p>
        </div>
        <div class="item">
            <h3>Acceleration_Z</h3>
            <p>%s</p>
        </div>
    </div>
    <div class="contents">
        <h2 style="color: red;">Gyro</h2>
        <div class="item">
            <h3>Gyro_Z</h3>
            <p>%s</p>
        </div>
        <div class="item">
            <h3>Gyro_Y</h3>
            <p>%s</p>
        </div>
        <div class="item">
            <h3>Gyro_Z</h3>
            <p>%s</p>
        </div>
    </div>
    <div class="contents">
        <h2 style="color: red;">Magnetic</h2>
        <div class="item">
            <h3>Magnetic_X</h3>
            <p>%s</p>
        </div>
        <div class="item">
            <h3>Magnetic_Y</h3>
            <p>%s</p>
        </div>
        <div class="item">
            <h3>Magnetic_Z</h3>
            <p>%s</p>
        </div>
    </div>
    <center>
        <h2 style="color: red;">Humidity</h2>
        <p>%s</p><br><br>
        <h2 style="color: red;">Temperature</h2>
        <p>%s</p><br><br>
        <h2 style="color: red;">Distance</h2>
        <p>%s</p><br><br>
    </center>
</body>
</html>"""

#起動アニメーションの表示
display.fill(0)
display.blit(fb, int((128-74) / 2), 0)
display.show()
#time.sleep(3)
for i in range(1, 64):
    display.fill(0)
    display.blit(fb, int((128-74) / 2), -i)
    display.show()
    time.sleep(0.01)

#wifiの接続を待機
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    display.fill(0)
    display.text('waiting for connection...', 0, 0, 1)
    display.show()
    time.sleep(1)

#接続できなかった場合はエラーを表示
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
#接続できた場合はIPアドレスを表示
else:
    print('Connected')
    print(wlan.ifconfig()[0])

#ソケットを作成
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

def task():
    global AccX, AccY, AccZ, GyrX, GyrY, GyrZ, MagX, MagY, MagZ, text_hum, text_temp, text_distance

    while True:#ディスプレイ初期化
        display.fill(0)
        display.text('Connected', int(128 / 2 - len('Connected') * 4), 0, 1)
        display.text(wlan.ifconfig()[0], int(128 / 2 - len(wlan.ifconfig()[0]) * 4), 8, 1)

        print("=======================================================")
        #アドレス0x27のstatusレジスタの下から1ビット目が加速度のデータ更新状態
        status = i2c.readfrom_mem(addr_ag, 0x27, 1)
        if status and 0x01 != 0x00:
            #加速度センサのデータの読み込み
            data = b''
            for i in range(0x28, 0x2e):
                data += i2c.readfrom_mem(addr_ag, i, 1)
            AccX = ustruct.unpack("<h", data[0:2])[0]
            AccY = ustruct.unpack("<h", data[2:4])[0]
            AccZ = ustruct.unpack("<h", data[4:6])[0]
            AccX = AccX * 0.000244
            AccY = AccY * 0.000244
            AccZ = AccZ * 0.000244
            print("AccX:" + '{:.2f}'.format(AccX) + " AccY:" + '{:.2f}'.format(AccY) + " AccZ:" + '{:.2f}'.format(AccZ))
            phi = math.atan(-AccY/AccX)
            thete = math.atan(AccX/math.sqrt(AccY*AccY+AccZ*AccZ))
            print("phi:" + '{:.2f}'.format(phi) + " thete:" + '{:.2f}'.format(thete))
        
        #アドレス0x27のstatusレジスタの下から2ビット目がジャイロのデータ更新状態
        if status and 0x02 != 0x00:
            data = b''
            for i in range(0x18, 0x1e):
                data += i2c.readfrom_mem(addr_ag, i, 1)
            GyrX = ustruct.unpack("<h", data[0:2])[0]
            GyrY = ustruct.unpack("<h", data[2:4])[0]
            GyrZ = ustruct.unpack("<h", data[4:6])[0]
            GyrX = GyrX * 0.00875
            GyrY = GyrY * 0.00875
            GyrZ = GyrZ * 0.00875
            print("GyrX:" + '{:.2f}'.format(GyrX) + " GyrY:" + '{:.2f}'.format(GyrY) + " GyrZ:" + '{:.2f}'.format(GyrZ))
        
        status = i2c.readfrom_mem(addr_m, 0x27, 1)
        #アドレス0x27のstatusレジスタの下から4ビット目が磁気のデータ更新状態
        if status and 0x08 != 0x00:
            data = i2c.readfrom_mem(addr_m, 0x28, 6)
            MagX = ustruct.unpack("<h", data[0:2])[0]
            MagY = ustruct.unpack("<h", data[2:4])[0]
            MagZ = ustruct.unpack("<h", data[4:6])[0]
            MagX = MagX * 0.00043
            MagY = MagY * 0.00043
            MagZ = MagZ * 0.00043
            print("MagX:" + '{:.2f}'.format(MagX) + " MagY:" + '{:.2f}'.format(MagY) + " MagZ:" + '{:.2f}'.format(MagZ))

        #測定コマンドを送信
        i2c.writeto(addr_temp, b'\xAC\x33\x00')

        #測定結果を読み込む
        data = i2c.readfrom(addr_temp, 6)

        #温湿度データを取得
        hum = data[1] << 12 | data[2] << 4 | (data[3] & 0xF0) >> 4
        temp = ((data[3] & 0x0F) << 16) | data[4] << 8 | data[5]

        hum = hum / 2**20 * 100
        temp = temp / 2**20 * 200 - 50
        text_hum = "hum : " + '{:.2f}'.format(hum) + "%"
        text_temp = "temp : " + '{:.2f}'.format(temp) + "C"

        print("=======================================================")

        #ディスプレイとログに温湿度を表示
        print(text_hum)
        print(text_temp)
        display.text(text_hum, int(128 / 2 - len(text_hum) * 4), 24, 1)
        display.text(text_temp, int(128 / 2 - len(text_temp) * 4), 32, 1)

        #トリガ波形を出力
        trig.low()
        time.sleep_us(2)
        trig.high()
        time.sleep_us(10)
        trig.low()

        #エコーの立ち下がりから立ち上がりまでの時間を計測
        signaloff, signalon = 0, 0
        while echo.value() == 0:
            signaloff = time.ticks_us()
        while echo.value() == 1:
            signalon = time.ticks_us()
        
        #エコーの時間差から距離を計算
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        text_distance = "dist : " + '{:.2f}'.format(distance) + "cm"

        print(text_distance)
        display.text(text_distance, int(128 / 2 - len(text_distance) * 4), 40, 1)

        display.show()
        time.sleep(1)

_thread.start_new_thread(task,())

while True:
    cl, addr = s.accept()
    try:
        #クライアントからのリクエストを解析
        print('client connected from', addr)
        
        #HTMLをクライアントに送信
        response = html % ('{:.2f}'.format(AccX) + "g", '{:.2f}'.format(AccY) + "g", '{:.2f}'.format(AccZ) + "g",
                        '{:.2f}'.format(GyrX) + "dps", '{:.2f}'.format(GyrY) + "dps", '{:.2f}'.format(GyrZ) + "dps",
                        '{:.2f}'.format(MagX) + "gauss", '{:.2f}'.format(MagY) + "gauss", '{:.2f}'.format(MagZ) + "gauss",
                        text_hum, text_temp, text_distance)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        
    except Exception as e:
        cl.close()
        print(e)

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        machine.reset()