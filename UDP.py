# Author: Ember Ipek
#
# MAX30102 SpO2 and heartrate monitor UDP class for sending
# and receiving data.

import network
import socket
import ustruct
import utime

class UDP:
    
    def __init__(self, tx_sock=None, rx_sock=None,
                 tx_port=5005, rx_port=5006, udp_ip=None):
        self.tx_sock = tx_sock
        self.rx_sock = rx_sock
        self.udp_ip = udp_ip
        self.tx_port = tx_port
        self.rx_port = rx_port
        
        if(rx_sock is not None):
            rx_sock.bind(("0.0.0.0", 5006))
            rx_sock.setblocking(False)
    
    def connect_wifi(self):
        # connect to hotspot
        ssid = "SSID"
        password = "PASSWORD"
        timeout = 20
        self.wlan = network.WLAN(network.WLAN.IF_STA)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)
        
        while not self.wlan.isconnected() and timeout > 0:
            utime.sleep(0.5)
            timeout -= 1
            
        if self.wlan.isconnected():
            print("Connected to Wi-Fi: ", self.wlan.ifconfig())
        
        return self.wlan

    # maintain wifi connection
    def maintain_wifi(self, wlan):
        if not self.wlan.isconnected():
            print("Wi-Fi lost, reconnecting...")
            self.wlan = self.connect_wifi()
        
        return self.wlan

    def calc_checksum(self, data):
        checksum = 0
        for byte in data:
            checksum ^= byte
        
        return checksum

    def receive_packet(self):
        while True:
            try:
                packet, addr = self.rx_sock.recvfrom(32)
                ## update display and LEDs
                # make unpack data/update display functions
                data = ustruct.unpack(">ii", packet)
                heartrate = data[0]
                spo2 = data[1]
                print(".................................Heart rate received: ", heartrate)
                print(".................................SpO2 received: ", spo2)
                
                return heartrate, spo2
                
            except OSError:
                return None, None

    # packs data for transmission over UDP and appends checksum
    # > = big endian, f = float, i = signed int
    def pack_data(self, temperature, red, ir):
        packet = ustruct.pack(">fii", temperature, red, ir)
        checksum = self.calc_checksum(packet)
        packet += ustruct.pack(">H", checksum)
        
        return packet
    
    def send_data(self, packet):
        if self.wlan.isconnected():
            self.tx_sock.sendto(packet, (self.udp_ip, self.tx_port))
