# Author: Ember Ipek
#
# Receives packets from MAX30102 sensor, unpacks temperature and LED
# data, and plots it on graph. Frequency spectrum is analyzed with fft,
# and plotted against magnitude.
#
# plot_spectrum() function from ECE201 Signals and Systems,
# Dr. Bernd-Peter Paris, George Mason University

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

def plot_spectrum(Xv, fs, doStem=False):
    """Plot magnitude and phase of the spectrum"""

    N = len(Xv)
    ff = np.arange(-N/2, N/2, 1) * fs/N

    fig, (axm, axp) = plt.subplots(2, 1, layout='constrained')
    
    if doStem:
        axm.stem(ff, np.abs(Xv))
    else:
        axm.semilogy(ff, np.abs(Xv))
    axm.grid()
    axm.set_ylabel('Magnitude')

    if doStem:
        axp.stem(ff, np.angle(Xv)/np.pi)
    else:
        axp.plot(ff, np.angle(Xv)/np.pi)
    axp.set_xlabel('Frequency (Hz)')
    axp.set_ylabel('Phase (rad/$\pi$)')
    axp.grid()

    plt.show()

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
        
        if(count < 2000):
            count += 1
            red_samples.append(red)
            ir_samples.append(ir)
            time_received.append(datetime.now())
        else:
            break
        
    except struct.error:
        print("Packet unpacking failed")
        
# put samples into np array and remove mean
np_red_samples = np.array(red_samples, dtype=float)
np_red_samples -= np.mean(np_red_samples)
np_ir_samples = np.array(ir_samples, dtype=float)
np_ir_samples -= np.mean(np_ir_samples)

# compute spectrum
spectrum = np.fft.fftshift(np.fft.fft(np_red_samples))
plot_spectrum(spectrum, fs=100, doStem=False)

plt.plot(time_received, red_samples, label='Red Samples')
plt.plot(time_received, ir_samples,  label='IR Samples')
plt.legend()
plt.title("LED Samples")
plt.xlabel("time")
plt.ylabel("ADC value")

plt.show()
