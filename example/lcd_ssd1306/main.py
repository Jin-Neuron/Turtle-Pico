from machine import Pin, SPI, I2C
import framebuf, time
from lib.ssd1306 import SSD1306_SPI, SSD1306_I2C
from lib.img_lib import img_lib

led1 = Pin("LED_R", Pin.OUT)
led2 = Pin("LED_L", Pin.OUT)

SW_Up = Pin("SW_L", Pin.IN, Pin.PULL_DOWN)
SW_Down = Pin("SW_R", Pin.IN, Pin.PULL_DOWN)

led1.high()
led2.high()

item_selected = 0
item_sel_previous = 0
item_sel_next = 0

button_up_clicked = False
button_down_clicked = True

num_items = len(img_lib.menu_item_fb)

#spi設定
#spi = SPI( TurtlePico.SPI_ID, baudrate = 100000, sck = Pin(TurtlePico.SPI_SCK), mosi = Pin(TurtlePico.SPI_MOSI))
#i2c設定
i2c = I2C(0, sda = Pin("I2C_SDA"), scl = Pin("I2C_SCL"))

#pin設定(SPI)
#oled_cs = Pin("OLED_CS",Pin.OUT)
#dc = Pin("OLED_DC",Pin.OUT)
#rst = Pin("OLED_RST",Pin.OUT)
#display宣言(I2C)
display = SSD1306_I2C(128, 64, i2c)
#display宣言(SPI)
#display = SSD1306_SPI(128, 64, spi, dc, rst, oled_cs)

while(True):

    if(SW_Up.value() == 1 and not button_up_clicked):
        item_selected = item_selected - 1
        button_up_clicked = True
        if(item_selected < 0):
            item_selected = num_items - 1
    if(SW_Down.value() == 1 and not button_down_clicked):
        item_selected = item_selected + 1
        button_down_clicked = True
        if(item_selected >= num_items):
            item_selected = 0
    
    if(SW_Up.value() == 0 and button_up_clicked):
        button_up_clicked = False
    if(SW_Down.value() == 0 and button_down_clicked):
        button_down_clicked = False

    item_sel_previous = item_selected - 1
    if(item_sel_previous < 0):
        item_sel_previous = num_items - 1
    item_sel_next = item_selected + 1
    if(item_sel_next >= num_items):
        item_sel_next = 0

    #backgroundを表示
    display.fill(0)
    #display.blit(img_lib.item_sel_background 0, 22)
    #display.blit(img_lib.scrollbar_background, 125, 0)

    #previous item
    display.blit(img_lib.menu_item_fb[item_sel_previous], 5, 2)
    display.text(img_lib.menu_item_char[item_sel_previous], 29, 7, 1)

    #selected item
    display.blit(img_lib.menu_item_fb[item_selected], 5, 24)
    display.text(img_lib.menu_item_char[item_selected], 29, 27, 1)

    #next item
    display.blit(img_lib.menu_item_fb[item_sel_next], 5, 46)
    display.text(img_lib.menu_item_char[item_sel_next], 29, 50, 1)

    display.show()