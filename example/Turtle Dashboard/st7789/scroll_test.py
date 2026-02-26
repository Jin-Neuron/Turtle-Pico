import st7789
import tft_config
import fonts.vga1_16x32 as font
import fonts.vga1_bold_16x32 as font_bold
import time
import screens
from machine import Pin
from wifi_config import wifi_config
import utime


tft = tft_config.config(0)


def cycle(p):
    try:
        len(p)
    except TypeError:
        cache = []
        for i in p:
            yield i
            cache.append(i)
        p = cache
    while p:
        yield from p


def main():

    tft.init()
    tft.offset(35,0)
    
    tft.fill(0x0000)

main()