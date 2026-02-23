from machine import Pin, SoftSPI
import machine
import os
from lib.sdcard import SDCard
from lib.TurtlePico import Leatherback as TurtlePico

cs = Pin(TurtlePico.SD_CS)

spi = SoftSPI(baudrate = 100000,
           sck  = machine.Pin(TurtlePico.SPI_SCK),
           mosi = machine.Pin(TurtlePico.SPI_MOSI),
           miso = machine.Pin(TurtlePico.SPI_MISO))

sd = SDCard(spi, cs)

os.mount(sd, '/sd')
os.chdir('sd')

list = os.listdir("/sd")
print(list)