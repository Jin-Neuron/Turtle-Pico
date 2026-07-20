from lib.bno08x import *
from lib.bno08x_i2c import BNO08X_I2C
from machine import I2C, Pin

import time 

I2C_ADDR = 0x4a
i2c = I2C(1, scl=Pin("I2C_SCL"), sda=Pin("I2C_SDA"), freq=400_000)

bno = BNO08X_I2C(i2c, address=I2C_ADDR)

bno.acceleration.enable()
bno.linear_acceleration.enable()
bno.magnetic.enable()
bno.gyro.enable()
bno.quaternion.enable()
bno.geomagnetic_quaternion.enable()
bno.game_quaternion.enable()

bno.steps.enable()
bno.stability_classifier.enable()
bno.activity_classifier.enable()

while True:

    bno.update_sensors()
    accel_x, accel_y, accel_z = bno.acceleration

    print("Acceleration: X={:.2f} Y={:.2f} Z={:.2f} m/s^2 \n".format(accel_x, accel_y, accel_z))

    lin_accel_x, lin_accel_y, lin_accel_z = bno.linear_acceleration
    print("Linear Acceleration: X={:.2f} Y={:.2f} Z={:.2f} m/s^2 \n".format(lin_accel_x, lin_accel_y, lin_accel_z))

    mag_x, mag_y, mag_z = bno.magnetic
    print("Magnetic Field: X={:.2f} Y={:.2f} Z={:.2f} uT \n".format(mag_x, mag_y, mag_z))

    gyro_x, gyro_y, gyro_z = bno.gyro
    print("Gyro: X={:.2f} Y={:.2f} Z={:.2f} dps \n".format(gyro_x, gyro_y, gyro_z))

    yaw, pitch, roll = bno.quaternion.euler
    print("Quaternion Euler Angles: Yaw={:.2f} Pitch={:.2f} Roll={:.2f} degrees \n\n".format(yaw, pitch, roll))

    time.sleep(1)