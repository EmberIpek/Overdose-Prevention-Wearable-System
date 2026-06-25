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
SPO2_LED1_REG = 0x0C
SPO2_LED2_REG = 0x0D
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

# helper function to set SpO2 pulse width
# set bits 1:0, default 118us
def set_spo2_pulse_width(i2c, width=118):
    """
    Sets SpO2 pulse width in SPO2_CONFIG_REG bits 1:0.
    Determines ADC resolution (15 - 18 bits)
    
    Args:
        i2c: I2C bus
        width: pulse width
               valid pulse widths: 69, 118, 215, 411
    """
    BITS = {
        69: 0x00,
        118: 0x01,
        215: 0x02,
        411: 0x03
        }
    
    data = i2c.readfrom_mem(SPO2_ADDR, SPO2_CONFIG_REG, 1)[0]
    value = BITS.get(width)
    if value is None:
        raise ValueError("Invalid pulse width")
    # clear bits 1:0 first
    data &= 0xFC
    data |= value
    
    i2c.writeto_mem(SPO2_ADDR, SPO2_CONFIG_REG, bytearray([data]))
    
    return

# helper function to set SpO2 sample rate
# set bits 4:2, default 100Hz
def set_spo2_sample_rate(i2c, rate=100):
    """
    Sets SpO2 sample rate in SPO2_CONFIG_REG bits 4:2.
    
    Args:
        i2c: I2C bus
        rate: sample rate
              valid sample rates: 50, 100, 200, 400, 800, 1000, 1600, 3200
    """
    BITS = {
        50: 0x00,
        100: 0x04,
        200: 0x08,
        400: 0x0C,
        800: 0x10,
        1000: 0x14,
        1600: 0x18,
        3200: 0x1C
        }
    
    data = i2c.readfrom_mem(SPO2_ADDR, SPO2_CONFIG_REG, 1)[0]
    value = BITS.get(rate)
    if value is None:
        raise ValueError("Invalid sample rate")
    # clear bits 4:2 then set them
    data &= 0xE3
    data |= value
    
    i2c.writeto_mem(SPO2_ADDR, SPO2_CONFIG_REG, bytearray([data]))
    
    return

# helper function to set SpO2 ADC range
# set bits 6:5, default 4096nA
def set_spo2_adc_range(i2c, range=4096):
    """
    Sets SpO2 ADC range in SPO2_CONFIG_REG bits 6:5.
    
    Args:
        i2c: I2C bus
        rate: ADC range
              valid values: 2048, 4096, 8192, 16384
    """
    BITS = {
        2048: 0x00,
        4096: 0x20,
        8192: 0x40,
        16384: 0x60
        }
    
    data = i2c.readfrom_mem(SPO2_ADDR, SPO2_CONFIG_REG, 1)[0]
    value = BITS.get(range)
    if value is None:
        raise ValueError("Invalid range")
    # clear and set bits 6:5
    data &= 0x9F
    data |= value
    
    i2c.writeto_mem(SPO2_ADDR, SPO2_CONFIG_REG, bytearray([data]))
    
    return

# helper function to set LED amplitude, default 0x24
def set_led_pulse_amplitude(i2c, amplitude=0x24):
    """
    Sets LED pulse amplitude in SPO2_LED registers
    
    Args:
        i2c: I2C bus
        rate: LED pulse amplitude
              valid range: 0x00-0xFF
    """
    if (amplitude > 0xFF or amplitude < 0x00):
        raise ValueError("Invalid amplitude")
    
    # set LED registers
    i2c.writeto_mem(SPO2_ADDR, SPO2_LED1_REG, bytearray([amplitude]))
    i2c.writeto_mem(SPO2_ADDR, SPO2_LED2_REG, bytearray([amplitude]))
    
    return

i2c0, sensor = spo2_setup()
set_spo2_sample_rate(i2c0, rate=100)
set_spo2_pulse_width(i2c0, width=118)
set_spo2_adc_range(i2c0, range=4096)
set_led_pulse_amplitude(i2c0, amplitude=0x24)

while True:
    # the internal die temperature sensor is intended for calibrating
    # the temperature dependence of the SpO2 subsystem
    # read the die temperature in Celsius
    temperature_C = sensor.read_temperature()
    print("Die temperature: ", temperature_C, "°C")
    
    utime.sleep(0.5)
