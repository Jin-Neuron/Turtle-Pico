from machine import Pin, SPI
import st7789

TFA = 0	# top free area when scrolling
BFA = 0	# bottom free area when scrolling

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=62_500_000, sck=Pin("SPI_SCK"), mosi=Pin("SPI_MOSI")),
        240,
        320,
        reset=Pin("LCD_RST", Pin.OUT),
        cs=Pin("LCD_CS", Pin.OUT),
        dc=Pin("LCD_DC", Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)