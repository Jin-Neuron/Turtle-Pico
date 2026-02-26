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

    colors = cycle([0xe000, 0xece0, 0xe7e0, 0x5e0, 0x00d3, 0x7030])
    foreground = next(colors)
    background = st7789.BLACK

    tft.fill(background)
    utime.sleep(1)

    height = tft.height()
    width = tft.width()
    last_line = height - font.HEIGHT

    tfa = tft_config.TFA        # top free area
    bfa = tft_config.BFA        # bottom free area

    tft.vscrdef(tfa, height, bfa)

    scroll = 0
    character = font.FIRST

    while True:
        # clear top line before scrolling off display
        tft.fill_rect(0, scroll, width, 1, background)

        # Write new line when we have scrolled the height of a character
        if scroll % font.HEIGHT == 0:
            line = (scroll + last_line) % height

            # write character hex value as a string
            tft.text(
                font,
                'x{:02x}'.format(character),
                16,
                line,
                foreground,
                background)

            # write character using a integer (could be > 0x7f)
            tft.text(
                font,
                character,
                90,
                line,
                foreground,
                background)

            # change color for next line
            foreground = next(colors)

            # next character with rollover at 256
            character += 1
            if character > font.LAST:
                character = font.FIRST

        # scroll the screen up 1 row
        tft.vscsad(scroll+tfa)
        scroll += 1
        scroll %= height

        utime.sleep(0.01)


main()