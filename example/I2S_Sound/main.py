import os
from machine import Pin
from machine import SPI
from lib.wavplayer import WavPlayer
from lib.sdcard import SDCard
from lib.TurtlePico import TurtlePico

cs = Pin(TurtlePico.SD_CS)

spi = SPI( 1,
           baudrate = 25_000_000,
           polarity=0,
           phase=0,
           bits=8,
           firstbit=SPI.MSB,
           sck  = Pin(TurtlePico.SPI_SCK),
           mosi = Pin(TurtlePico.SPI_MOSI),
           miso = Pin(TurtlePico.SPI_MISO))

sd = SDCard(spi, cs)
sd.init_spi(25_000_000)  # increase SPI bus speed to SD card
os.mount(sd, "/sd")
list = os.listdir("/sd")
print(list)

WAV_FILE = "09-Someday-My-Prince-Will-Come.wav"

wp = WavPlayer(
    id=TurtlePico.I2S_ID,
    sck_pin=TurtlePico.I2S_BCLK,
    ws_pin=TurtlePico.I2S_LRCLK,
    sd_pin=TurtlePico.I2S_SDATA,
    ibuf=40000,
    volume=-2
)
print("==========  START PLAYBACK ==========")
wp.play(WAV_FILE)

try:
    while wp.isplaying():
        pass
except (KeyboardInterrupt, Exception) as e:
    wp.wav.close()
    wp.audio_out.deinit()