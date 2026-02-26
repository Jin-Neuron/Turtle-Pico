import st7789
import fonts.vga1_16x32 as font
import fonts.vga1_bold_16x32 as font_bold
import fonts.vga1_8x16 as font_small   
import time, network, screens, tft_config
from machine import Pin, Timer
from wifi_config import wifi_config

led1 = Pin("LED_R", Pin.OUT)
led2 = Pin("LED_L", Pin.OUT)

SW_Sel = Pin("SW_L", Pin.IN, Pin.PULL_DOWN)
SW_Up = Pin("SW_R", Pin.IN, Pin.PULL_DOWN)

button_sel_clicked = False
button_up_clicked = False

disp_width = 170
disp_height = 320
disp_offset = int((240 - disp_width) / 2)

tft = tft_config.config(rotation=0)
tft.init()
tft.offset(35,0)

tft.png('/img/JinTurtle.png', 0, 0)
time.sleep(1.5)

menu = screens.menu(font, font_bold, tft)
sc = menu

load_cnt = 0
tft.fill_rect(0, 310, 170, 10, 0x0000)
tft.text(font_small, ' Connecting...', 0, 310 - 8, 0xFFFF) # 白文字

def loadingAnimation():
    global load_cnt
    path = '/img/loadingIcon/spinner'+str(load_cnt)+'.png'
    tft.fill_rect(0, 240, 64, 64, 0x0000) # 白い枠
    tft.png(path, 0, 220) # スピナーアイコン

    load_cnt += 1
    if load_cnt > 7:
        load_cnt = 0

loadTimer = Timer(period=150, callback=lambda t: loadingAnimation())

#WiFiに接続
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())
wlan.connect(wifi_config.ssid, wifi_config.pw)

max_reconnect = 3
max_wait = 20

while max_reconnect > 0:
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('接続待ち...')
        time.sleep(1)

    if wlan.status() == 3:
        break
    else:
        print(wlan.status())
        print('接続失敗、再試行します...')
        wlan.connect(wifi_config.ssid, wifi_config.pw)
        max_reconnect -= 1

if wlan.status() != 3:
    print(wlan.status())
    raise RuntimeError('ネットワーク接続失敗')
else:
    print('接続完了')
    status = wlan.ifconfig()
    print( 'IPアドレス = ' + status[0] )

loadTimer.deinit() # ローディングアニメーション停止

sc.showDisplay()

while(True):
    if(SW_Sel.value() == 1 and not button_sel_clicked):
        button_sel_clicked = True
        '''
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
        '''

    if(SW_Up.value() == 1 and not button_up_clicked):
        sc.upMenu()
        button_up_clicked = True
    
    if(SW_Sel.value() == 0 and button_sel_clicked):
        button_sel_clicked = False
    if(SW_Up.value() == 0 and button_up_clicked):
        button_up_clicked = False
