import socket
import struct
import time
import matplotlib
import scipy

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

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
    except struct.error:
        print("Packet unpacking failed")import socket
import struct
import time
import matplotlib
import scipy

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening on port", UDP_PORT)

while True:
    packet, addr = sock.recvfrom(1024)
    print("Received", len(packet), "bytes from", addr)
    
    # > = big endian, f = float
    try:
        data = struct.unpack("<f", packet)
        temperature = data[0]
        
        print("UDP received! Unpacked data: ", temperature)
    except struct.error:
        print("Packet unpacking failed")
