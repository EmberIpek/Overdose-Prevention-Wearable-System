import socket
import struct
from datetime import datetime
import matplotlib.pyplot as plt
import scipy as sp
import numpy as np

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

count = 0
red_samples = []
ir_samples = []
time_received = []


print("Listening on port", UDP_PORT)

while True:
    packet, addr = sock.recvfrom(1024)
    print("Received", len(packet), "bytes from", addr)
    
    # > = big endian, f = float, i = signed int
    try:
        data = struct.unpack(">fiiH", packet)
        temperature = data[0]
        red = data[1]
        ir = data[2]
        checksum = data[3]
        
        print("UDP received! Temperature: ", temperature,
              ", Red LED: ", red,
              ", IR LED: ", ir,
              ", checksum: ", checksum)
        
        if(count < 1000):
            count += 1
            red_samples.append(red)
            ir_samples.append(ir)
            time_received.append(datetime.now())
        else:
            break
        
    except struct.error:
        print("Packet unpacking failed")
        

plt.plot(time_received, red_samples, label='Red Samples')
plt.plot(time_received, ir_samples,  label='IR Samples')
plt.legend()
plt.title("LED Samples")
plt.xlabel("time")
plt.ylabel("ADC value")

plt.show()
