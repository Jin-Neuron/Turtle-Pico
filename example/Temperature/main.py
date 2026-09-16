from machine import Pin, I2C
import time

i2c = I2C(0, scl=Pin("I2C_SCL"), sda=Pin("I2C_SDA"), freq=100000)

# デバイスのアドレスをスキャンします
addr = i2c.scan()
print( "address is :" + str(addr) )

addr_temp = 56

while True:
    #測定コマンドを送信
    i2c.writeto(addr_temp, b'\xAC\x33\x00')

    #測定結果を読み込む
    data = i2c.readfrom(addr_temp, 6)
    status = data[0] >> 7
    while status == 1:

        #測定中は待機
        data = i2c.readfrom(addr_temp, 6)
        status = data[0] >> 7
        time.sleep_ms(10)
    
    #温湿度データを取得
    hum = data[1] << 12 | data[2] << 4 | (data[3] & 0xF0) >> 4
    temp = ((data[3] & 0x0F) << 16) | data[4] << 8 | data[5]

    hum = hum / 2**20 * 100
    temp = temp / 2**20 * 200 - 50

    print("hum: " + str(hum))
    print("temp: " + str(temp))