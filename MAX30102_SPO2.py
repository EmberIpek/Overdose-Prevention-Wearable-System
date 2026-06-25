# Author: Ember Ipek
#
# This initializes an I2C bus for a MAX30102 sensor, puts it in SpO2 mode,
# and gets a temperature reading every 0.5 seconds. Helper functions are
# included to set SpO2 sample rate and pulse width.

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

# helper function to set SpO2 pulse width, bits 1:0
# set bits 1:0 with bitwise OR, default 118us
def set_spo2_pulse_width(i2c, width=118):
    """Sets SpO2 pulse width. Valid pulse widths: 69, 118, 215, 411
    Determines ADC resolution (15 - 18 bits)
    
    Args:
        i2c (machine.I2C object): I2C bus
        width (integer): pulse width
    """
    data = i2c.readfrom_mem(SPO2_ADDR, SPO2_CONFIG_REG, 1)[0]
    BITMASK = {
        69: 0x00,
        118: 0x01,
        215: 0x02,
        411: 0x03
        }
    
    if BITMASK.get(width) is None:
        raise ValueError("Invalid pulse width")
    data |= BITMASK.get(width)
    
    i2c.writeto_mem(SPO2_ADDR, SPO2_CONFIG_REG, bytearray([data]))
    
    return

# helper function to set SpO2 sample rate, bits 4:2 define sample rate
# set bits 4:2 with bitwise OR, default 100Hz
def set_spo2_sample_rate(i2c, rate=100):
    """Sets SpO2 sample rate. Valid sample rates: 50, 100, 200, 400, 800,
    1000, 1600, 3200
    
    Args:
        i2c (machine.I2C object): I2C bus
        rate (integer): sample rate
    """
    data = i2c.readfrom_mem(SPO2_ADDR, SPO2_CONFIG_REG, 1)[0]
    BITMASK = {
        50: 0x00,
        100: 0x04,
        200: 0x08,
        400: 0x0C,
        800: 0x10,
        1000: 0x14,
        1600: 0x18,
        3200: 0x1C
        }
    
    if BITMASK.get(rate) is None:
        raise ValueError("Invalid sample rate")
    data |= BITMASK.get(rate)
    
    i2c.writeto_mem(SPO2_ADDR, SPO2_CONFIG_REG, bytearray([data]))
    
    return

i2c0, sensor = spo2_setup()
set_spo2_sample_rate(i2c0, rate=100)
set_spo2_pulse_width(i2c0, width=118)

while True:
    
    # the internal die temperature sensor is intended for calibrating
    # the temperature dependence of the SpO2 subsystem
    # read the die temperature in Celsius
    temperature_C = sensor.read_temperature()
    print("Die temperature: ", temperature_C, "°C")
    
    utime.sleep(0.5)
