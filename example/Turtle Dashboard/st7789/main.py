import st7789
import tft_config
import fonts.vga1_16x32 as font
import fonts.vga1_bold_16x32 as font_bold
import time
import screens
from machine import Pin
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

tft.jpg('/img/JinNeuron.jpg', 0, 0, st7789.SLOW)
time.sleep(1)

menu = screens.menu(font, font_bold, tft)
sc = menu
tft.fill(0x0000) # 黒でクリア
tft.offset(35,0)
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
