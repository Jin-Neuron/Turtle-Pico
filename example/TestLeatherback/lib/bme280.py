from machine import Pin,I2C
import time
class Bme_280:
    DEVICE_ADDR = 0x77
    digT = []
    digP = []
    digH = []
    t_fine = 0.0
    def __init__(self, id1=0,scl_pin = 1,sda_pin = 0):
        self.i2c = I2C(id1,scl=Pin(scl_pin),sda=Pin(sda_pin),freq=400000)
        self.int280()
        self.get_calib_param()
    def int280(self):
        self.i2c.writeto_mem(self.DEVICE_ADDR, 0xF2, bytes([0x01]))
        self.i2c.writeto_mem(self.DEVICE_ADDR, 0xF4, bytes([0x27]))
        self.i2c.writeto_mem(self.DEVICE_ADDR, 0xF5, bytes([0xA0]))
        time.sleep_ms(50)
    def get_calib_param(self):
        calib_t = bytearray(6)
        self.i2c.readfrom_mem_into(self.DEVICE_ADDR, 0x88, calib_t)
        self.digT.append((calib_t[1] << 8) | calib_t[0])
        self.digT.append((calib_t[3] << 8) | calib_t[2])
        self.digT.append((calib_t[5] << 8) | calib_t[4])
        calib_p = bytearray(0x12)
        self.i2c.readfrom_mem_into(self.DEVICE_ADDR, 0x8E, calib_p)
        self.digP.append((calib_p[1] << 8) | calib_p[0])
        self.digP.append((calib_p[3] << 8) | calib_p[2])
        self.digP.append((calib_p[5] << 8) | calib_p[4])
        self.digP.append((calib_p[7] << 8) | calib_p[6])
        self.digP.append((calib_p[9] << 8) | calib_p[8])
        self.digP.append((calib_p[11] << 8) | calib_p[10])
        self.digP.append((calib_p[13] << 8) | calib_p[12])
        self.digP.append((calib_p[15] << 8) | calib_p[14])
        self.digP.append((calib_p[17] << 8) | calib_p[16])
        calibh=bytearray(1)
        self.i2c.readfrom_mem_into(self.DEVICE_ADDR, 0xA1, calibh)
        self.digH.append(calibh[0])
        calib_h = bytearray(8)
        self.i2c.readfrom_mem_into(self.DEVICE_ADDR, 0xE1, calib_h)
        self.digH.append((calib_h[1] << 8) | calib_h[0])
        self.digH.append(calib_h[2])
        self.digH.append((calib_h[3] << 4) | (0x0F & calib_h[4]))
        self.digH.append((calib_h[5] << 4) | ((calib_h[4] >> 4) & 0x0F))
        self.digH.append(calib_h[6])
        for i in range(1,2):
            if self.digT[i] & 0x8000:
                self.digT[i] = (-self.digT[i] ^ 0xFFFF) + 1
        for i in range(1,8):
            if self.digP[i] & 0x8000:
                self.digP[i] = (-self.digP[i] ^ 0xFFFF) + 1
        for i in range(0,6):
            if self.digH[i] & 0x8000:
                self.digH[i] = (-self.digH[i] ^ 0xFFFF) + 1
    def read_data(self):
        data1 = bytearray(0x08)
        self.i2c.readfrom_mem_into(self.DEVICE_ADDR,0xF7,data1)
        prse_raw = (data1[0] << 16 | data1[1] << 8 | data1[2]) >> 4
        temp_raw = (data1[3] << 16 | data1[4] << 8 | data1[5]) >> 4
        hum_raw = data1[6] << 8 | data1[7]
        comp_t = self.compensate_T(temp_raw)
        comp_p = self.compensate_P(prse_raw)
        comp_h = self.compensate_H(hum_raw)
        return comp_t , comp_p , comp_h
    def compensate_P(self,adc_P):
        #global  t_fine
        pressure = 0.0
        v1 = (self.t_fine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.digP[5]
        v2 = v2 + ((v1 * self.digP[4]) * 2.0)
        v2 = (v2 / 4.0) + (self.digP[3] * 65536.0)
        v1 = (((self.digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8)  + ((self.digP[1] * v1) / 2.0)) / 262144
        v1 = ((32768 + v1) * self.digP[0]) / 32768
        if v1 == 0:
            return 0
        pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2
        v1 = (self.digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * self.digP[7]) / 8192.0
        pressure = pressure + ((v1 + v2 + self.digP[6]) / 16.0)
        return  pressure/100
    def compensate_T(self,adc_T):
        #self.t_fine
        v1 = (adc_T / 16384.0 - self.digT[0] / 1024.0) * self.digT[1]
        v2 = (adc_T / 131072.0 - self.digT[0] / 8192.0) * (adc_T / 131072.0 - self.digT[0] / 8192.0) * self.digT[2]
        self.t_fine = v1 + v2
        temperature = self.t_fine / 5120.0
        return  temperature
    def compensate_H(self,adc_H):
        #global t_fine
        var_h = self.t_fine - 76800.0
        if var_h != 0:
            var_h = (adc_H - (self.digH[3] * 64.0 + self.digH[4]/16384.0 * var_h)) * (self.digH[1] / 65536.0 * (1.0 + self.digH[5] / 67108864.0 * var_h * (1.0 + self.digH[2] / 67108864.0 * var_h)))
        else:
            return 0
        var_h = var_h * (1.0 - self.digH[0] * var_h / 524288.0)
        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0
        return var_h