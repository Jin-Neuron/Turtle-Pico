import time
import st7789
import tft_config
from machine import Pin, PWM, I2C
from lib.TurtlePico import Leatherback
from lib.bme280 import Bme_280

bme = Bme_280(Leatherback.I2C_ID, Leatherback.I2C_SCL, Leatherback.I2C_SDA)

for i in range(5):
    print(bme.read_data())
    time.sleep(3)