import machine
import utime
import network
import socket
import ustruct
from max30102 import MAX30102

SPO2_ADDR = 0x57
SPO2_FIFO_REG = 0x07
SPO2_MODE_REG = 0x09
SPO2_CONFIG_REG = 0x0A
SPO2_DEVID_REG = 0xFF

SPO2_SDA = machine.Pin(4)
SPO2_SCL = machine.Pin(5)

def spo2_setup():
    # use standard i2c speed 100kHz, set mode to SpO2 mode
    i2c = machine.I2C(0, scl=SPO2_SCL, sda=SPO2_SDA, freq = 100000)
    i2c.writeto_mem(SPO2_ADDR, SPO2_MODE_REG, bytearray([0x03]))

    sensor = MAX30102(i2c=i2c)

    data = i2c.readfrom_mem(SPO2_ADDR, SPO2_DEVID_REG, 1)
    print(data)
    
    return i2c, sensor

# helper function to set SpO2 sample rate, bits 4:2 define sample rate
# uses bit mask w/ bitwise AND to set bits 4:2, default 100Hz
def set_spo2_sample_rate(i2c, rate=100):
    data = i2c.readfrom_mem(SPO2_ADDR, SPO2_CONFIG_REG, 1)[0]
    BITMASK = {
        50: 0xE3,
        100: 0xE7,
        200: 0xEB,
        400: 0xEF,
        800: 0xF3,
        1000: 0xF7,
        1600: 0xFB,
        3200: 0xFF
        }
    data &= BITMASK.get(rate, 0xE7)
    i2c.writeto_mem(SPO2_ADDR, SPO2_CONFIG_REG, bytearray([data]))
    
    return

i2c0, sensor = spo2_setup()
set_spo2_sample_rate(i2c0, rate=100)

while True:
    
    # the internal die temperature sensor is intended for calibrating
    # the temperature dependence of the SpO2 subsystem
    # read the die temperature in Celsius
    temperature_C = sensor.read_temperature()
    print("Die temperature: ", temperature_C, "°C")
    
    utime.sleep(0.5)
