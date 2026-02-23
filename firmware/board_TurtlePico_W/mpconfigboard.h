// Board and hardware specific configuration
#define MICROPY_HW_BOARD_NAME "TurtlePico PICO_W model"
// todo: We need something to check our binary size
#define MICROPY_HW_FLASH_STORAGE_BYTES          (848 * 1024)
#define MICROPY_HW_MCU_NAME "RP2040"

// Enable networking.
#define MICROPY_PY_NETWORK 1
#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT     "TurtlePico"

// CYW43 driver configuration.
#define CYW43_USE_SPI (1)
#define CYW43_LWIP (1)
#define CYW43_GPIO (1)
#define CYW43_SPI_PIO (1)

// For debugging mbedtls - also set
// Debug level (0-4) 1=warning, 2=info, 3=debug, 4=verbose
// #define MODUSSL_MBEDTLS_DEBUG_LEVEL 1

#define MICROPY_HW_PIN_EXT_COUNT    CYW43_WL_GPIO_COUNT

// I2Cのデフォルト設定
#define MICROPY_HW_I2C0_SCL             (9)
#define MICROPY_HW_I2C0_SDA             (8)

// SPIのデフォルト設定
#define MICROPY_HW_SPI1_SCK             (10)
#define MICROPY_HW_SPI1_MOSI            (11)
#define MICROPY_HW_SPI1_MISO            (12) 

// If this returns true for a pin then its irq will not be disabled on a soft reboot
int mp_hal_is_pin_reserved(int n);
#define MICROPY_HW_PIN_RESERVED(i) mp_hal_is_pin_reserved(i)