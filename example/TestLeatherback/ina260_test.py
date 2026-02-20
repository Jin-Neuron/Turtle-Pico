from lib.ina260 import INA260
from lib.TurtlePico import Leatherback
from machine import I2C

ina260 = INA260(I2C(Leatherback.I2C_ID, scl=Leatherback.I2C_SCL, sda=Leatherback.I2C_SDA, freq=400000))

print("Current:", ina260.current, "mA")
print("Voltage:", ina260.voltage, "V")
print("Power:", ina260.power, "mW")