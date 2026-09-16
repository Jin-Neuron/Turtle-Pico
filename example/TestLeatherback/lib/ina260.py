from micropython import const

_REG_CONFIG = const(0x00)  # CONFIGURATION REGISTER (R/W)
_REG_CURRENT = const(0x01)  # SHUNT VOLTAGE REGISTER (R)
_REG_BUSVOLTAGE = const(0x02)  # BUS VOLTAGE REGISTER (R)
_REG_POWER = const(0x03)  # POWER REGISTER (R)
_REG_MASK_ENABLE = const(0x06)  # MASK ENABLE REGISTER (R/W)
_REG_ALERT_LIMIT = const(0x07)  # ALERT LIMIT REGISTER (R/W)
_REG_MFG_UID = const(0xFE)  # MANUFACTURER UNIQUE ID REGISTER (R)
_REG_DIE_UID = const(0xFF)  # DIE UNIQUE ID REGISTER (R)
_REG_CALIBRATION = const(0x05)

class RWBits:
    """
    Multibit register (less than a full byte) that is readable and writeable.
    This must be within a byte register.

    Values are `int` between 0 and 2 ** ``num_bits`` - 1.

    :param int num_bits: The number of bits in the field.
    :param int register_address: The register address to read the bit from
    :param type lowest_bit: The lowest bits index within the byte at ``register_address``
    :param int register_width: The number of bytes in the register. Defaults to 1.
    :param bool lsb_first: Is the first byte we read from I2C the LSB? Defaults to true
    :param bool signed: If True, the value is a "two's complement" signed value.
                        If False, it is unsigned.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        num_bits,
        register_address,
        lowest_bit,
        register_width=1,
        lsb_first=True,
        signed=False,
    ):
        self.bit_mask = ((1 << num_bits) - 1) << lowest_bit
        # print("bitmask: ",hex(self.bit_mask))
        if self.bit_mask >= 1 << (register_width * 8):
            raise ValueError("Cannot have more bits than register size")
        self.lowest_bit = lowest_bit
        self.buffer = bytearray(1 + register_width)
        self.buffer[0] = register_address
        self.lsb_first = lsb_first
        self.sign_bit = (1 << (num_bits - 1)) if signed else 0

    def __get__(self, obj, objtype=None):
        with obj.i2c_device as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
        # read the number of bytes into a single variable
        reg = 0
        order = range(len(self.buffer) - 1, 0, -1)
        if not self.lsb_first:
            order = reversed(order)
        for i in order:
            reg = (reg << 8) | self.buffer[i]
        reg = (reg & self.bit_mask) >> self.lowest_bit
        # If the value is signed and negative, convert it
        if reg & self.sign_bit:
            reg -= 2 * self.sign_bit
        return reg

    def __set__(self, obj, value):
        value <<= self.lowest_bit  # shift the value over to the right spot
        with obj.i2c_device as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
            reg = 0
            order = range(len(self.buffer) - 1, 0, -1)
            if not self.lsb_first:
                order = range(1, len(self.buffer))
            for i in order:
                reg = (reg << 8) | self.buffer[i]
            # print("old reg: ", hex(reg))
            reg &= ~self.bit_mask  # mask off the bits we're about to change
            reg |= value  # then or in our new value
            # print("new reg: ", hex(reg))
            for i in reversed(order):
                self.buffer[i] = reg & 0xFF
                reg >>= 8
            i2c.write(self.buffer)

class ROBits(RWBits):
    """
    Multibit register (less than a full byte) that is read-only. This must be
    within a byte register.

    Values are `int` between 0 and 2 ** ``num_bits`` - 1.

    :param int num_bits: The number of bits in the field.
    :param int register_address: The register address to read the bit from
    :param type lowest_bit: The lowest bits index within the byte at ``register_address``
    :param int register_width: The number of bytes in the register. Defaults to 1.
    """

    def __set__(self, obj, value):
        raise AttributeError()

class RWBit:
    """
    Single bit register that is readable and writeable.

    Values are `bool`

    :param int register_address: The register address to read the bit from
    :param type bit: The bit index within the byte at ``register_address``
    :param int register_width: The number of bytes in the register. Defaults to 1.
    :param bool lsb_first: Is the first byte we read from I2C the LSB? Defaults to true

    """

    def __init__(self, register_address, bit, register_width=1, lsb_first=True):
        self.bit_mask = 1 << (bit % 8)  # the bitmask *within* the byte!
        self.buffer = bytearray(1 + register_width)
        self.buffer[0] = register_address
        if lsb_first:
            self.byte = bit // 8 + 1  # the byte number within the buffer
        else:
            self.byte = register_width - (bit // 8)  # the byte number within the buffer

    def __get__(self, obj, objtype=None):
        with obj.i2c_device as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
        return bool(self.buffer[self.byte] & self.bit_mask)

    def __set__(self, obj, value):
        with obj.i2c_device as i2c:
            i2c.write_then_readinto(self.buffer, self.buffer, out_end=1, in_start=1)
            if value:
                self.buffer[self.byte] |= self.bit_mask
            else:
                self.buffer[self.byte] &= ~self.bit_mask
            i2c.write(self.buffer)

class ROBit(RWBit):
    """Single bit register that is read only. Subclass of `RWBit`.

    Values are `bool`

    :param int register_address: The register address to read the bit from
    :param type bit: The bit index within the byte at ``register_address``
    :param int register_width: The number of bytes in the register. Defaults to 1.

    """

    def __set__(self, obj, value):
        raise AttributeError()

class Mode:
    """Modes avaible to be set

    +--------------------+---------------------------------------------------------------------+
    | Mode               | Description                                                         |
    +====================+=====================================================================+
    | ``Mode.CONTINUOUS``| Default: The sensor will continuously measure the bus voltage and   |
    |                    | shunt voltage across the shunt resistor to calculate ``power`` and  |
    |                    | ``current``                                                         |
    +--------------------+---------------------------------------------------------------------+
    | ``Mode.TRIGGERED`` | The sensor will immediately begin measuring and calculating current,|
    |                    | bus voltage, and power. Re-set this mode to initiate another        |
    |                    | measurement                                                         |
    +--------------------+---------------------------------------------------------------------+
    | ``Mode.SHUTDOWN``  |  Shutdown the sensor, reducing the quiescent current and turning off|
    |                    |  current into the device inputs. Set another mode to re-enable      |
    +--------------------+---------------------------------------------------------------------+

    """

    SHUTDOWN = const(0x0)
    TRIGGERED = const(0x3)
    CONTINUOUS = const(0x7)

class ConversionTime:
    """Options for ``current_conversion_time`` or ``voltage_conversion_time``

    +----------------------------------+------------------+
    | ``ConversionTime``               | Time             |
    +==================================+==================+
    | ``ConversionTime.TIME_140_us``   | 140 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_204_us``   | 204 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_332_us``   | 332 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_588_us``   | 588 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_1_1_ms``   | 1.1 ms (Default) |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_2_116_ms`` | 2.116 ms         |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_4_156_ms`` | 4.156 ms         |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_8_244_ms`` | 8.244 ms         |
    +----------------------------------+------------------+

    """

    TIME_140_us = const(0x0)
    TIME_204_us = const(0x1)
    TIME_332_us = const(0x2)
    TIME_588_us = const(0x3)
    TIME_1_1_ms = const(0x4)
    TIME_2_116_ms = const(0x5)
    TIME_4_156_ms = const(0x6)
    TIME_8_244_ms = const(0x7)

    @staticmethod
    def get_seconds(time_enum):
        """Retrieve the time in seconds giving value read from register"""
        conv_dict = {
            0: 140e-6,
            1: 204e-6,
            2: 332e-6,
            3: 588e-6,
            4: 1.1e-3,
            5: 2.116e-3,
            6: 4.156e-3,
            7: 8.244e-3,
        }
        return conv_dict[time_enum]


class AveragingCount:
    """Options for ``averaging_count``

    +-------------------------------+------------------------------------+
    | ``AveragingCount``            | Number of measurements to average  |
    +===============================+====================================+
    | ``AveragingCount.COUNT_1``    | 1 (Default)                        |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_4``    | 4                                  |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_16``   | 16                                 |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_64``   | 64                                 |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_128``  | 128                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_256``  | 256                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_512``  | 512                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_1024`` | 1024                               |
    +-------------------------------+------------------------------------+

    """

    COUNT_1 = const(0x0)
    COUNT_4 = const(0x1)
    COUNT_16 = const(0x2)
    COUNT_64 = const(0x3)
    COUNT_128 = const(0x4)
    COUNT_256 = const(0x5)
    COUNT_512 = const(0x6)
    COUNT_1024 = const(0x7)

    @staticmethod
    def get_averaging_count(avg_count):
        """Retrieve the number of measurements giving value read from register"""
        conv_dict = {0: 1, 1: 4, 2: 16, 3: 64, 4: 128, 5: 256, 6: 512, 7: 1024}
        return conv_dict[avg_count]


# pylint: enable=too-few-public-methods

def _to_signed(num):
    if num > 0x7FFF:
        num -= 0x10000
    return num

class INA260:
    """Driver for the INA260 power and current sensor.

    :param ~busio.I2C i2c_device: The I2C bus the INA260 is connected to.
    :param address: The I2C device address for the sensor. Default is ``0x40``.

    """

    def __init__(self, i2c_device, address=0x40):
        self.i2c_device = i2c_device
        self.i2c_addr = address
        self.buf = bytearray(2)
    
    def _write_register(self, reg, value):
        self.buf[0] = (value >> 8) & 0xFF
        self.buf[1] = value & 0xFF
        self.i2c_device.writeto_mem(self.i2c_addr, reg, self.buf)

    def _read_register(self, reg):
        self.i2c_device.readfrom_mem_into(self.i2c_addr, reg & 0xff, self.buf)
        value = (self.buf[0] << 8) | (self.buf[1])
        return value

    # MASK_ENABLE fields
    overcurrent_limit = RWBit(_REG_MASK_ENABLE, 15, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the current measurement
       following a conversion exceeds the value programmed in the Alert Limit Register.
    """
    under_current_limit = RWBit(_REG_MASK_ENABLE, 14, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the current measurement
       following a conversion drops below the value programmed in the Alert Limit Register.
    """
    bus_voltage_over_voltage = RWBit(_REG_MASK_ENABLE, 13, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the bus voltage measurement
       following a conversion exceeds the value programmed in the Alert Limit Register.
    """
    bus_voltage_under_voltage = RWBit(_REG_MASK_ENABLE, 12, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the bus voltage measurement
       following a conversion drops below the value programmed in the Alert Limit Register.
    """
    power_over_limit = RWBit(_REG_MASK_ENABLE, 11, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the Power calculation
       made following a bus voltage measurement exceeds the value programmed in the
       Alert Limit Register.
    """
    conversion_ready = RWBit(_REG_MASK_ENABLE, 10, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted when the Conversion Ready Flag,
        Bit 3, is asserted indicating that the device is ready for the next conversion.
    """
    # from 5 to 9 are not used
    alert_function_flag = ROBit(_REG_MASK_ENABLE, 4, 2, False)
    """While only one Alert Function can be monitored at the ALERT pin at time, the
       Conversion Ready can also be enabled to assert the ALERT pin.
       Reading the Alert Function Flag following an alert allows the user to determine if the Alert
       Function was the source of the Alert.

       When the Alert Latch Enable bit is set to Latch mode, the Alert Function Flag bit
       clears only when the Mask/Enable Register is read.
       When the Alert Latch Enable bit is set to Transparent mode, the Alert Function Flag bit
       is cleared following the next conversion that does not result in an Alert condition.
    """
    _conversion_ready_flag = ROBit(_REG_MASK_ENABLE, 3, 2, False)
    """Bit to help coordinate one-shot or triggered conversion. This bit is set after all
        conversion, averaging, and multiplication are complete.
        Conversion Ready flag bit clears when writing the configuration register or
        reading the Mask/Enable register.
    """
    math_overflow_flag = ROBit(_REG_MASK_ENABLE, 2, 2, False)
    """This bit is set to 1 if an arithmetic operation resulted in an overflow error.
    """
    alert_polarity_bit = RWBit(_REG_MASK_ENABLE, 1, 2, False)
    """Active-high open collector when True, Active-low open collector when false (default).
    """
    alert_latch_enable = RWBit(_REG_MASK_ENABLE, 0, 2, False)
    """Configures the latching feature of the ALERT pin and Alert Flag Bits.
    """

    reset_bit = RWBit(_REG_CONFIG, 15, 2, False)
    """Setting this bit t 1 generates a system reset. Reset all registers to default values."""
    averaging_count = RWBits(3, _REG_CONFIG, 9, 2, False)
    """The window size of the rolling average used in continuous mode"""
    voltage_conversion_time = RWBits(3, _REG_CONFIG, 6, 2, False)
    """The conversion time taken for the bus voltage measurement"""
    current_conversion_time = RWBits(3, _REG_CONFIG, 3, 2, False)
    """The conversion time taken for the current measurement"""

    mode = RWBits(3, _REG_CONFIG, 0, 2, False)
    """The mode that the INA260 is operating in. Must be one of
    ``Mode.CONTINUOUS``, ``Mode.TRIGGERED``, or ``Mode.SHUTDOWN``
    """

    mask_enable = RWBits(16, _REG_MASK_ENABLE, 0, 2, False)
    """The Mask/Enable Register selects the function that is enabled to control the ALERT pin as
        well as how that pin functions.
        If multiple functions are enabled, the highest significant bit
        position Alert Function (D15-D11) takes priority and responds to the Alert Limit Register.
    """
    alert_limit = RWBits(16, _REG_ALERT_LIMIT, 0, 2, False)
    """The Alert Limit Register contains the value used to compare to the register selected in the
        Mask/Enable Register to determine if a limit has been exceeded.
        The format for this register will match the format of the register that is selected for
        comparison.
    """

    @property
    def current(self):
        """The current (between V+ and V-) in mA"""
        raw_current = self._read_register(_REG_CURRENT)

        return raw_current * 1.25

    @property
    def voltage(self):
        """The bus voltage in V"""
        raw_voltage = self._read_register(_REG_BUSVOLTAGE)
        return raw_voltage * 0.00125

    @property
    def power(self):
        """The power being delivered to the load in mW"""
        raw_power = _to_signed(self._read_register(_REG_POWER))
        return raw_power * 10