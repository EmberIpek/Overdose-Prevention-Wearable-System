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
# from datetime import datetime
import time
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

#######################################################################
# signal processing
#######################################################################

def rms(window):
    '''Returns RMS value of window of samples.'''
    return np.sqrt(np.mean(window**2))

# Wn: The critical frequency or frequencies.
# For lowpass and highpass filters, Wn is a scalar;
# for bandpass and bandstop filters, Wn is a length-2 sequence.
def lowpass_filter(samples, order=4, cutoff=0.4, fs=float):
    b, a = signal.butter(N=order, Wn=cutoff, btype="lowpass", fs=freq)
    filtered_signal = signal.filtfilt(b, a, samples)
    
    return filtered_signal

def bandpass_filter(samples, order=4, low=0.5, high=4.5, fs=float):
    b, a = signal.butter(N=order, Wn=(low, high), btype="bandpass", fs=freq)
    filtered_signal = signal.filtfilt(b, a, samples)
    
    return filtered_signal

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

# initialize UDP
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
        
        if(count < 2000):
            count += 1
            red_samples.append(red)
            ir_samples.append(ir)
            time_received.append(time.time())
        else:
            break
        
    except struct.error:
        print("Packet unpacking failed")

# compute average sampling rate using time received
dt = np.diff(time_received)
freq = 1 / np.mean(dt)

# TO DO: error if transmission rate drops

# put samples into np array and remove DC component
np_red_samples = np.array(red_samples, dtype=float)
np_red_DC = lowpass_filter(np_red_samples, fs=freq)
# np_red_DC = np.mean(np_red_samples)
np_red_AC = np_red_samples - np_red_DC

np_ir_samples = np.array(ir_samples, dtype=float)
np_ir_DC = lowpass_filter(np_ir_samples, fs=freq)
# np_ir_DC = np.mean(np_ir_samples)
np_ir_AC = np_ir_samples - np_ir_DC

# compute spectrum
# spectrum = np.fft.fftshift(np.fft.fft(np_red_samples))
# plot_spectrum(spectrum, fs=100, doStem=False)
# bp_filter = signal.butter(N=4, Wn=(0.5, 7), btype="bandpass", output="sos", fs=freq)
# filtered_red = signal.sosfilt(bp_filter, red_samples)

filtered_red_AC = bandpass_filter(np_red_AC, fs=freq)
filtered_ir_AC = bandpass_filter(np_ir_AC, fs=freq)

# Ratio: oxygen saturation to be calculated with (AC_ir/DC_ir)/(AC_red/DC_red)
# TO DO: This should be RMS values
ratio_red = filtered_red_AC/np_red_DC
ratio_ir = filtered_ir_AC/np_ir_DC
o2_sat = ratio_ir/ratio_red

##################################################################
# Plotting signals
##################################################################

# plot_spectrum(filtered_red_AC, fs=freq)
t = np.arange(len(filtered_red_AC)) / freq

# AC component
# plt.plot(t, filtered_red_AC, label='Filtered Red Samples')
# plt.plot(t, np_red_AC, label='Red Samples')
# plt.plot(t, filtered_ir_AC, label='Filtered IR Samples')
# plt.plot(t, np_ir_AC, label='IR Samples')

# DC component
# plt.plot(t, np_red_DC, label='Red DC')
# plt.plot(t, np_ir_DC, label='IR DC')

# Ratio
plt.plot(t, ratio_red, label='Red Ratio')
plt.plot(t, ratio_ir, label='IR Ratio')
# plt.plot(t, o2_sat, label='O2 Saturation')

plt.legend()
plt.title("LED Samples")
plt.xlabel("time")
plt.ylabel("ADC value")

plt.show()
