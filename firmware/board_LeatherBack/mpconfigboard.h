// Board and hardware specific configuration
#define MICROPY_HW_BOARD_NAME "TurtlePico Leatherback model"
#define PICO_FLASH_SIZE_BYTES (16 * 1024 * 1024)
#define MICROPY_HW_FLASH_STORAGE_BYTES (PICO_FLASH_SIZE_BYTES - (2 * 1024 * 1024))
#define MICROPY_HW_MCU_NAME "RP2350B"

// I2Cのデフォルト設定
#define MICROPY_HW_I2C0_SCL             (15)
#define MICROPY_HW_I2C0_SDA             (14)

// SPIのデフォルト設定
#define MICROPY_HW_SPI1_SCK             (10)
#define MICROPY_HW_SPI1_MOSI            (11)
#define MICROPY_HW_SPI1_MISO            (12) 

