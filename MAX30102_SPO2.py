# Author: Ember Ipek
#
# 6/23/2026
#
# This initializes an I2C bus for a MAX30102 sensor, puts it in SpO2 mode,
# and gets a temperature reading every 0.5 seconds. Helper functions are
# included to set SpO2 sample rate, pulse width, ADC range, FIFO register,
# and get temperature readings and red/IR LED data. Data is packed, checksum
# is appended, and sent to PC for unpacking/processing over UDP. Processed
# heart rate data received from PC and displayed on 7-seg display

import machine
import utime
import network
import socket
import ustruct
import SSEG_CC
# from max30102 import MAX30102

SPO2_SDA = machine.Pin(4)
SPO2_SCL = machine.Pin(5)

UDP_IP = "172.20.10.3"
TX_PORT = 5005
RX_PORT = 5006

dig_1 = machine.Pin(0, machine.Pin.OUT)
dig_2 = machine.Pin(1, machine.Pin.OUT)
dig_3 = machine.Pin(2, machine.Pin.OUT)
dig_4 = machine.Pin(3, machine.Pin.OUT)

seg_a = machine.Pin(6, machine.Pin.OUT)
seg_b = machine.Pin(7, machine.Pin.OUT)
seg_c = machine.Pin(8, machine.Pin.OUT)
seg_d = machine.Pin(9, machine.Pin.OUT)
seg_e = machine.Pin(10, machine.Pin.OUT)
seg_f = machine.Pin(11, machine.Pin.OUT)
seg_g = machine.Pin(12, machine.Pin.OUT)

digits = [dig_1,
          dig_2,
          dig_3,
          dig_4]

segments = [seg_a,
            seg_b,
            seg_c,
            seg_d,
            seg_e,
            seg_f,
            seg_g]

###################################################################
# UDP setup
###################################################################

def connect_wifi():
    # connect to hotspot
    ssid = "SSID"
    password = "PASSWORD"
    timeout = 20
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected() and timeout > 0:
        utime.sleep(0.5)
        timeout -= 1
        
    if wlan.isconnected():
        print("Connected to Wi-Fi: ", wlan.ifconfig())
    
    return wlan

# maintain wifi connection
def maintain_wifi(wlan):
    if not wlan.isconnected():
        print("Wi-Fi lost, reconnecting...")
        wlan = connect_wifi()
    
    return wlan

def calc_checksum(data):
    checksum = 0
    for byte in data:
        checksum ^= byte
    
    return checksum


def receive_packet():
    while True:
        try:
            packet, addr = rx_sock.recvfrom(32)
            ## update display and LEDs
            # make unpack data/update display functions
            data = ustruct.unpack(">i", packet)
            heartrate = data[0]
            print(".................................Heart rate received: ", heartrate)
            
            return heartrate
            
        except OSError:
            break

# packs data for transmission over UDP and appends checksum
# > = big endian, f = float, i = signed int
def pack_data(temperature, red, ir):
    packet = ustruct.pack(">fii", temperature, red, ir)
    checksum = calc_checksum(packet)
    packet += ustruct.pack(">H", checksum)
    
    return packet

###################################################################
# SpO2 class
# make this a driver eventually...
###################################################################

class MAX30102:
    ADDR = 0x57
    FIFO_WRITE_POINTER = 0x04
    FIFO_OVERFLOW_COUNTER = 0x05
    FIFO_READ_POINTER = 0x06
    FIFO_REG = 0x07
    FIFO_CONFIG_REG = 0x08
    MODE_REG = 0x09
    CONFIG_REG = 0x0A
    LED1_REG = 0x0C
    LED2_REG = 0x0D
    TEMP_INT_REG = 0x1F
    TEMP_FRAC_REG = 0x20
    TEMP_CONFIG_REG = 0x21
    DEVID_REG = 0xFF
    
    def __init__(self, i2c):
        self.i2c = i2c
        self.resolution = 16
        self.mode = "spo2"

    # helper function to set SpO2 pulse width
    # set bits 1:0, default 118us
    def set_led_pulse_width(self, width=118):
        """
        Sets LED pulse width in CONFIG_REG bits 1:0.
        Determines ADC resolution (15 - 18 bits).
        
        Args:
            width: pulse width
                   valid pulse widths: 69, 118, 215, 411
        """
        BITS = {
            69: 0x00,
            118: 0x01,
            215: 0x02,
            411: 0x03
            }
        RES = {
            69: 15,
            118: 16,
            215: 17,
            411: 18
            }
        
        data = self.i2c.readfrom_mem(self.ADDR, self.CONFIG_REG, 1)[0]
        value = BITS.get(width)
        if value is None:
            raise ValueError("Invalid pulse width")
        self.resolution = RES.get(width)
        # clear bits 1:0 first
        data &= 0xFC
        data |= value
        
        self.i2c.writeto_mem(self.ADDR, self.CONFIG_REG, bytearray([data]))
        
        return

    # helper function to set SpO2 sample rate
    # set bits 4:2, default 100Hz
    def set_sample_rate(self, rate=100):
        """
        Sets sample rate in CONFIG_REG bits 4:2.
        
        Args:
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
        
        data = self.i2c.readfrom_mem(self.ADDR, self.CONFIG_REG, 1)[0]
        value = BITS.get(rate)
        if value is None:
            raise ValueError("Invalid sample rate")
        # clear bits 4:2 then set them
        data &= 0xE3
        data |= value
        
        self.i2c.writeto_mem(self.ADDR, self.CONFIG_REG, bytearray([data]))
        
        return

    # helper function to set ADC range
    # set bits 6:5, default 4096nA
    def set_adc_range(self, adc_range=4096):
        """
        Sets ADC operational range in CONFIG_REG bits 6:5.
        
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
        
        data = self.i2c.readfrom_mem(self.ADDR, self.CONFIG_REG, 1)[0]
        value = BITS.get(adc_range)
        if value is None:
            raise ValueError("Invalid range")
        # clear and set bits 6:5
        data &= 0x9F
        data |= value
        
        self.i2c.writeto_mem(self.ADDR, self.CONFIG_REG, bytearray([data]))
        
        return

    # helper function to set LED amplitude, default 0x24
    def set_led_pulse_amplitude(self, amplitude=0x24):
        """
        Sets LED pulse amplitude in LED registers
        
        Args:
            i2c: I2C bus
            rate: LED pulse amplitude
                  valid range: 0x00-0xFF
        """
        if (amplitude > 0xFF or amplitude < 0x00):
            raise ValueError("Invalid amplitude")
        
        # set LED registers
        self.i2c.writeto_mem(self.ADDR, self.LED1_REG, bytearray([amplitude]))
        self.i2c.writeto_mem(self.ADDR, self.LED2_REG, bytearray([amplitude]))
        
        return

    # setter function for number of samples per FIFO entry
    def set_sample_average(self, samples=8):
        """
        Sets number of samples to average per FIFO entry in FIFO_CONFIG_REG
        bits 7:5
        
        Args:
            i2c: I2C bus
            samples: number of samples to average
                  valid samples: 1, 2, 4, 8, 16, 32
        """
        BITS = {
            1: 0x00,
            2: 0x10,
            4: 0x20,
            8: 0x30,
            16: 0x40,
            32: 0x50
            }
        
        data = self.i2c.readfrom_mem(self.ADDR, self.FIFO_CONFIG_REG, 1)[0]
        value = BITS.get(samples)
        if value is None:
            raise ValueError("Invalid sample number")
        # clear and set bits 7:5
        data &= 0x1F
        data |= value
        
        self.i2c.writeto_mem(self.ADDR, self.FIFO_CONFIG_REG, bytearray([data]))
        
        return

    def set_fifo_rollover(self, rollover=1):
        """
        Sets/clears FIFO rollover in FIFO_CONFIG_REG bit 4. On by default.
        
        Args:
            rollover: enabled if >= 1, disabled otherwise
        """
        data = self.i2c.readfrom_mem(self.ADDR, self.FIFO_CONFIG_REG, 1)[0]
        if (rollover >= 1):
            data |= 0x10
        else:
            data &= 0xEF
        self.i2c.writeto_mem(self.ADDR, self.FIFO_CONFIG_REG, bytearray([data]))
        
        return

    def get_temp(self):
        """
        Gets temperature in C. Integer is represented in 2's complement in
        TEMP_INT_REG, fraction is represented in increments of 0.0625 in
        TEMP_FRAC_REG, TEMP_CONFIG_REG bit 0 is set to get reading and is
        cleared automatically.
        
        Returns:
            Temperature in C
        """
        self.i2c.writeto_mem(self.ADDR, self.TEMP_CONFIG_REG, bytearray([0x01]))
        # wait for conversion to finish
        while self.i2c.readfrom_mem(self.ADDR, self.TEMP_CONFIG_REG, 1)[0] & 0x01:
            utime.sleep_ms(1)
        
        temp_int = self.i2c.readfrom_mem(self.ADDR, self.TEMP_INT_REG, 1)[0]
        temp_frac = self.i2c.readfrom_mem(self.ADDR, self.TEMP_FRAC_REG, 1)[0]
        
        if temp_int & 0x80:
            temp_int -= 256
        
        return temp_int + (temp_frac * 0.0625)
    
    def get_fifo_data(self):
        """
        Gets red and IR LED FIFO data.
        
        Returns:
            red and IR LED values
        """
        r = self.i2c.readfrom_mem(self.ADDR, self.FIFO_READ_POINTER, 1)[0]
        w = self.i2c.readfrom_mem(self.ADDR, self.FIFO_WRITE_POINTER, 1)[0]
        while(r == w):
            r = self.i2c.readfrom_mem(self.ADDR, self.FIFO_READ_POINTER, 1)[0]
            w = self.i2c.readfrom_mem(self.ADDR, self.FIFO_WRITE_POINTER, 1)[0]
            if(r != w):
                break
        
        data = self.i2c.readfrom_mem(self.ADDR, self.FIFO_REG, 6)
        # split data into 3-byte chunks to get red and IR readings
        # discard upper 6 bits
        red = (data[0] << 16 | data[1] << 8 | data[2]) & 0x03FFFF
        ir = (data[3] << 16 | data[4] << 8 | data[5]) & 0x03FFFF
        
        # adjust alignment for ADC resolution
        shift = 18 - self.resolution
        red = red >> shift
        ir = ir >> shift
        
        return red, ir

    def spo2_setup(self):
        self.i2c.writeto_mem(self.ADDR, self.MODE_REG, bytearray([0x03]))
        # The FIFO write/read pointers should be cleared upon entering
        # SpO2 mode or HR mode, so that there is no old data represented
        # in the FIFO.
        self.i2c.writeto_mem(self.ADDR, self.FIFO_OVERFLOW_COUNTER, bytearray([0x00]))
        self.i2c.writeto_mem(self.ADDR, self.FIFO_READ_POINTER, bytearray([0x00]))
        self.i2c.writeto_mem(self.ADDR, self.FIFO_WRITE_POINTER, bytearray([0x00]))
        
        self.mode = "spo2"
        
        self.set_sample_rate(rate=100)
        self.set_led_pulse_width(width=118)
        self.set_adc_range(adc_range=4096)
        self.set_led_pulse_amplitude(amplitude=0x24)
        self.set_sample_average(samples=8)
        # small delay needed after mode change
        utime.sleep_ms(50)
        self.set_fifo_rollover(rollover=1)
        
        # debugging: make sure CONFIG_REG is set & print device ID
        cfg = self.i2c.readfrom_mem(self.ADDR, self.CONFIG_REG, 1)[0]
        print(bin(cfg), hex(cfg))
        data = self.i2c.readfrom_mem(self.ADDR, self.DEVID_REG, 1)
        print(data)
        utime.sleep_ms(100)
        
        return

#############################################################
# init variables/objects
#############################################################

# use standard i2c speed 100kHz, set mode to SpO2 mode
i2c0 = machine.I2C(0, scl=SPO2_SCL, sda=SPO2_SDA, freq=100000)
sensor = MAX30102(i2c0)
sensor.spo2_setup()

tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

rx_sock.bind(("0.0.0.0", 5006))
rx_sock.setblocking(False)

wlan = connect_wifi()
current_hr = 0
while True:
    wlan = maintain_wifi(wlan)
    
    # receive heartrate from packet
    count = 0
    while(count<10):
        new_hr = receive_packet()
        if(new_hr != None):
            current_hr = new_hr
        count += 1
        
    # read the die temperature in Celsius
    temp_C = sensor.get_temp()
    red, ir = sensor.get_fifo_data()
    print("Die temperature: ", temp_C, "C")
#     # debugging: print raw LED bytes
#     print("LED bytes hex: ", data.hex())
#     print("LED bytes bin: ", bin(red), bin(ir))
    print("LED value red: ", red, ", IR: ", ir)
    packet = pack_data(temp_C, red, ir)
    
    if wlan.isconnected():
        tx_sock.sendto(packet, (UDP_IP, TX_PORT))
        print("Packet sent! IP: ", wlan.ifconfig())
        
    new_hr = receive_packet()
    if(new_hr != None):
            current_hr = new_hr
    ones = current_hr % 10
    tens = (current_hr // 10) % 10
    hundreds = (current_hr // 100) % 10
    # show received heart rate on sseg display
    seg, dig = SSEG_CC.show_sseg(ones, 3)
#     seg, dig = SSEG_CC.show_sseg(0, 0)
    for i in range(len(seg)):
        segments[i].value(seg[i])
    for i in range(len(dig)):
        digits[i].value(dig[i])
    utime.sleep_ms(5)
    
    if(tens > 0):
        seg, dig = SSEG_CC.show_sseg(tens, 2)
        for i in range(len(seg)):
            segments[i].value(seg[i])
        for i in range(len(dig)):
            digits[i].value(dig[i])
    utime.sleep_ms(5)
    
    if(hundreds > 0):
        seg, dig = SSEG_CC.show_sseg(hundreds, 1)
        for i in range(len(seg)):
            segments[i].value(seg[i])
        for i in range(len(dig)):
            digits[i].value(dig[i])
    utime.sleep_ms(5)
#     utime.sleep_ms(10)
