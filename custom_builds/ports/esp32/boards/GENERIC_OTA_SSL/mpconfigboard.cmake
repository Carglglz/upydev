set(SDKCONFIG_DEFAULTS
    boards/sdkconfig_ssl.base
    boards/sdkconfig.ble_off
    boards/GENERIC_OTA/sdkconfig.board
)

if(NOT MICROPY_FROZEN_MANIFEST)
    set(MICROPY_FROZEN_MANIFEST ${MICROPY_PORT_DIR}/boards/manifest_ota.py)
endif()
