from machine import Pin, SPI
from lib.TurtlePico import Leatherback
import st7789

TFA = 0	 # top free area when scrolling
BFA = 0	 # bottom free area when scrolling

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(Leatherback.SPI_ID, baudrate=10_000_000, sck=Pin(Leatherback.SPI_SCK), mosi=Pin(Leatherback.SPI_MOSI), miso=Pin(Leatherback.SPI_MISO)),
        240,
        320,
        reset=Pin(Leatherback.Display_RST, Pin.OUT),
        cs=Pin(Leatherback.Display_CS, Pin.OUT),
        dc=Pin(Leatherback.Display_DC, Pin.OUT),
        backlight=Pin(Leatherback.Display_BL, Pin.OUT),
        options=options,
        buffer_size=buffer_size)