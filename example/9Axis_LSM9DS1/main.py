from machine import Pin, I2C, reset
import time
import ustruct
from lib.fusion import Fusion

calibrate_sw = Pin("SW_R", Pin.IN)
reset_sw = Pin("SW_L", Pin.IN)

fuse = Fusion()
i2c = I2C(0, scl=Pin("I2C_SCL"), sda=Pin("I2C_SDA"), freq=100000)

# デバイスのアドレスをスキャンします
addr = i2c.scan()
print( "address is :" + str(addr) )

addr_ag = 0x6a
addr_m = 0x1c

#センサーレジスタの設定(加速度/ジャイロ)
CTRL_REG1_G = 0x10
CTRL_REG2_G = 0x11
CTRL_REG3_G = 0x12
ORIENT_CFG_G = 0x13
CTRL_REG4 = 0x1E
CTRL_REG5_XL = 0x1F
CTRL_REG6_XL = 0x20
CTRL_REG7_XL = 0x21

i2c.writeto_mem(addr_ag, CTRL_REG1_G, b'\x60')  #0110 0000
i2c.writeto_mem(addr_ag, CTRL_REG2_G, b'\x00')  #0000 0000
i2c.writeto_mem(addr_ag, CTRL_REG3_G, b'\x41')  #0100 0001
i2c.writeto_mem(addr_ag, ORIENT_CFG_G, b'\x40') #0100 0000
i2c.writeto_mem(addr_ag, CTRL_REG4, b'\x3a')    #0011 1010
i2c.writeto_mem(addr_ag, CTRL_REG5_XL, b'\x38') #0011 1000
i2c.writeto_mem(addr_ag, CTRL_REG6_XL, b'\x24') #0010 0100
i2c.writeto_mem(addr_ag, CTRL_REG7_XL, b'\x00') #0000 0000

#センサーレジスタの設定（地磁気）
CTRL_REG1_M = 0x20
CTRL_REG2_M = 0x21
CTRL_REG3_M = 0x22
CTRL_REG4_M = 0x23
CTRL_REG5_M = 0x24

i2c.writeto_mem(addr_m, CTRL_REG1_M, b'\x14')  #0001 0100
i2c.writeto_mem(addr_m, CTRL_REG2_M, b'\x00')  #0000 0000
i2c.writeto_mem(addr_m, CTRL_REG3_M, b'\x00')  #0000 0000
i2c.writeto_mem(addr_m, CTRL_REG4_M, b'\x0c')  #0000 1100
i2c.writeto_mem(addr_m, CTRL_REG5_M, b'\x00')  #0000 0000

accel = 0, 0, 0
gyro = 0, 0, 0
mag = 0, 0, 0

def get9DofData(type="mag"):
    addr = addr_m if type == "mag" else addr_ag
    memAddr = 0x18 if type == "gyro" else 0x28
    scale = 32768
    scale /= 2 if type == "accel" else 245 if type == "gyro" else 4
    enableBit = 0x01 if type == "accel" else 0x02 if type == "gyro" else 0x08

    status = i2c.readfrom_mem(addr, 0x27, 1)
    if status and enableBit != 0x00:
        data = i2c.readfrom_mem(addr, memAddr, 6)

        x = ustruct.unpack("<h", data[0:2])[0]
        y = ustruct.unpack("<h", data[2:4])[0]
        z = ustruct.unpack("<h", data[4:6])[0]
        x /= scale
        y /= scale
        z /= scale

        return (x,y,z)
    return (0,0,0)

print("Calibrating. Press switch when done.")
fuse.calibrate(get9DofData, calibrate_sw, 20)
print(fuse.magbias)

while True:

    #print("=======================================================")
    #statusレジスタのアドレス0x27の下から1ビット目が加速度のデータ更新状態
    status = i2c.readfrom_mem(addr_ag, 0x27, 1)

    accel = get9DofData("accel")
    gyro = get9DofData("gyro")
    mag = get9DofData("mag")

    #print(str(ax) + "," + str(ay) + "," + str(az) + ","  + str(gx) + "," + str(gy) + "," + str(gz) + ","  + str(mx) + "," + str(my) + "," + str(mz))
    
    fuse.update(accel, gyro, mag)
    print("1," + str(gyro[0]) + "," + str(gyro[1]) + "," + str(gyro[2]))
    print("2," + str(accel[0]) + "," + str(accel[1]) + "," + str(accel[2]))
    print("3," + str(mag[0]) + "," + str(mag[1]) + "," + str(mag[2]))
    print("4," + str(fuse.roll) + "," + str(fuse.pitch) + "," + str(fuse.heading))

    if reset_sw.value() == 1:
        reset()

    time.sleep_ms(20)