from machine import Pin, SoftSPI
import machine
import os
from lib.sdcard import SDCard

cs = Pin("SD_CS")

spi = SoftSPI(baudrate = 100000,
           sck  = machine.Pin("SPI_SCK"),
           mosi = machine.Pin("SPI_MOSI"),
           miso = machine.Pin("SPI_MISO"))

sd = SDCard(spi, cs)

os.mount(sd, '/sd')
os.chdir('sd')

list = os.listdir("/sd")
print(list)