import machine
import utime
import network
import socket
import ustruct
from max30102 import MAX30102

SPO2_ADDR = 0x57
SPO2_FIFO_REG = 0x07
SPO2_MODE_REG = 0x09
SPO2_DEVID_REG = 0xFF

SPO2_SDA = machine.Pin(4)
SPO2_SCL = machine.Pin(5)

# use standard i2c speed 100kHz, set mode to SpO2 mode
i2c0 = machine.I2C(0, scl=SPO2_SCL, sda=SPO2_SDA, freq = 100000)
i2c0.writeto_mem(SPO2_ADDR, SPO2_MODE_REG, bytearray([0x03]))

data = i2c0.readfrom_mem(SPO2_ADDR, SPO2_DEVID_REG, 1)
print(data)