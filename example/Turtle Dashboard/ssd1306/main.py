from machine import Pin, SPI, I2C
import framebuf, os
import lib, network, time
from lib.fdrawer import FontDrawer
from wifi_config import wifi_config

led1 = Pin("LED_R", Pin.OUT)
led2 = Pin("LED_L", Pin.OUT)

SW_Sel = Pin("SW_L", Pin.IN, Pin.PULL_DOWN)
SW_Up = Pin("SW_R", Pin.IN, Pin.PULL_DOWN)

led1.high()
led2.high()

button_sel_clicked = False
button_up_clicked = False

#spi設定
#spi = SPI(1, baudrate = 100000, sck = Pin("SPI_SCK"), mosi = Pin("SPI_MOSI"))
#i2c設定
i2c = I2C(0, sda = Pin("I2C_SDA"), scl = Pin("I2C_SCL"))

#pin設定(SPI)
#oled_cs = Pin("LCD_CS",Pin.OUT)
#dc = Pin("LCD_DC",Pin.OUT)
#rst = Pin("LCD_RST",Pin.OUT)
#display宣言(I2C)
display = lib.SSD1306_I2C(128, 64, i2c)
#display宣言(SPI)
#display = SSD1306_SPI(128, 64, spi, dc, rst, oled_cs)

#スクリーンオブジェクト
menu = lib.screens.menu(display)
cl = lib.screens.clock(display)
#wt = lib.screens.weather(display)
sc = menu

#WiFiに接続
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())
wlan.connect(wifi_config.ssid, wifi_config.pw)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('接続待ち...')
    time.sleep(1)

if wlan.status() != 3:
    print(wlan.status())
    raise RuntimeError('ネットワーク接続失敗')
else:
    print('接続完了')
    status = wlan.ifconfig()
    print( 'IPアドレス = ' + status[0] )

while(True):

    if(SW_Sel.value() == 1 and not button_sel_clicked):
        button_sel_clicked = True
        if(sc == menu):
            if(menu.menu_item_char[menu.item_selected] == 'Clock'):
                sc = cl
                if(not sc.isTimeset):
                    sc.setTimeThread()
            elif(menu.menu_item_char[menu.item_selected] == 'Weather'):
                sc = wt
            else:
                raise Exception( "Invalid Menu Item!" )
        else:
            #return menu screen
            if(sc.selMenu() < 0):
                sc = menu
                continue

    if(SW_Up.value() == 1 and not button_up_clicked):
        sc.upMenu()
        button_up_clicked = True
    
    if(SW_Sel.value() == 0 and button_sel_clicked):
        button_sel_clicked = False
    if(SW_Up.value() == 0 and button_up_clicked):
        button_up_clicked = False

    sc.showDisplay()