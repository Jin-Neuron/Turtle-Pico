from lib.ina260 import INA260
from machine import I2C, Pin

ina260 = INA260(I2C(1, scl=Pin("I2C_SCL"), sda=Pin("I2C_SDA"), freq=400000))

print("Current:", ina260.current, "mA")
print("Voltage:", ina260.voltage, "V")
print("Power:", ina260.power, "mW")