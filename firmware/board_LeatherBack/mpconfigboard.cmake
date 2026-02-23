# The Core is powered by an RP2350B with 48 GPIOs
set(PICO_PLATFORM "rp2350")
set(PICO_NUM_GPIOS 48)

set(PICO_BOARD "leatherback_rp2350b_core")
list(APPEND PICO_BOARD_HEADER_DIRS ${MICROPY_BOARD_DIR})

# Board specific version of the frozen manifest
set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)
