import time
import st7789
import tft_config
from machine import Pin, PWM
from lib.TurtlePico import Leatherback
import vga2_bold_16x32 as font

led_r = Pin(Leatherback.LED_R, Pin.OUT)
led_l = Pin(Leatherback.LED_L, Pin.OUT)

tft = tft_config.config(rotation=3)
tft.init()

tft.jpg('/img/jin.jpg', 0, 0, st7789.SLOW)

def center(text):
    length = 1 if isinstance(text, int) else len(text)
    tft.text(
        font,
        text,
        tft.width() // 2 - length // 2 * font.WIDTH,
        tft.height() // 2 - font.HEIGHT //2,
        st7789.WHITE,
        st7789.RED)
    
center(b'\xAEHello\xAF')