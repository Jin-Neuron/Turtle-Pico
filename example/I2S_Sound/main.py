import os
from machine import Pin
from machine import SoftSPI as SPI
from lib.wavplayer import WavPlayer
from lib.sdcard import SDCard

cs = Pin("SD_CS")

spi = SPI( baudrate = 25_000_000,
           polarity=0,
           phase=0,
           bits=8,
           firstbit=SPI.MSB,
           sck  = Pin("SPI_SCK"),
           mosi = Pin("SPI_MOSI"),
           miso = Pin("SPI_MISO"))

sd = SDCard(spi, cs)
sd.init_spi(25_000_000)  # increase SPI bus speed to SD card
os.mount(sd, "/sd")
list = os.listdir("/sd")
print(list)

WAV_FILE = "09-Someday-My-Prince-Will-Come.wav"

wp = WavPlayer(
    id=0,
    sck_pin=Pin("I2S_BCLK"),
    ws_pin=Pin("I2S_LRCLK"),
    sd_pin=Pin("I2S_SDATA"),
    ibuf=40000,
    volume=-2
)
print("==========  START PLAYBACK ==========")
try:
    wp.play(WAV_FILE)
except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))

while wp.isplaying():
    pass