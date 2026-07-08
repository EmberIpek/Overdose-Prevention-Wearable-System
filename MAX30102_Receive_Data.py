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
from collections import deque

UDP_IP = "0.0.0.0"
PICO_IP = "172.20.10.10"
TX_PORT = 5006
RX_PORT = 5005

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
    # clamp range if sampling below nyquist rate
    if(freq < (2 * cutoff)):
        cutoff = (freq/2) * 0.99
        print("****************FREQ = ", freq, "*****************")
    
    b, a = signal.butter(N=order, Wn=cutoff, btype="lowpass", fs=freq)
    filtered_signal = signal.filtfilt(b, a, samples)
    
    return filtered_signal

def bandpass_filter(samples, order=4, low=0.5, high=4.5, fs=float):
	# clamp range if sampling below nyquist rate
    if(freq < (2 * high)):
        high = (freq/2) * 0.99
        print("****************FREQ = ", freq, "*****************")
    if(high < low):
        low = 0.1
        print("****************FREQ = ", freq, "*****************")
    
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
	axp.set_ylabel('Phase (rad/$pi$)')
	axp.grid()

	plt.show()

#############################################################
# SpO2
#############################################################

def get_ratio(fs=float):
	ratio = []
	window = int(fs * 2)
	
	for i in range(window, len(np_red_samples)):
		red_seg = filtered_red_AC[i-window:i]
		ir_seg  = filtered_ir_AC[i-window:i]
		# find RMS value of AC segment in window
		AC_red = rms(red_seg)
		AC_ir  = rms(ir_seg)
		# find average DC component in window
		DC_red = np.mean(np_red_samples[i-window:i])
		DC_ir  = np.mean(np_ir_samples[i-window:i])
		
		ratio.append((AC_red/DC_red)/(AC_ir/DC_ir))
	
	return ratio

################################################################
# Heart rate
################################################################

# signal.find_peaks returns indices of peaks that satisfy conditions
# use to find times and calculate heart rate with a rolling window
def get_heartrate():
	peak_indices, _ = signal.find_peaks(filtered_red_AC, distance=int(freq * 0.4))
	window = 5
	peak_times = np.array(time_received)[peak_indices]
	heartrate_list = []

	for i in range(window, len(peak_indices)):
		t = peak_times[i-window:i]
		dt = np.diff(t)
		
		if len(dt) > 0:
			heartrate = 60 / np.mean(dt)
			heartrate_list.append(heartrate)

	return heartrate_list

# initialize UDP
tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rx_sock.bind((UDP_IP, RX_PORT))

count = 0
# red_samples = []
# ir_samples = []
# time_received = []
red_samples = deque(maxlen=2000)
ir_samples = deque(maxlen=2000)
time_received = deque(maxlen=2000)
current_hr = 0
current_spo2 = 0
# filter for initial conditions
low = 0.5
high = 4.5

print("Listening on port", RX_PORT)


#################################################################
# Processing loop
#################################################################

while True:
	packet, addr = rx_sock.recvfrom(1024)
	print("Received", len(packet), "bytes from", addr)
	
	# > = big endian, f = float, i = signed int
	try:
		data = struct.unpack(">fiiH", packet)
		temperature = data[0]
		red = data[1]
		ir = data[2]
		checksum = data[3]
		
		# print("UDP received! Temperature: ", temperature,
		# 	  ", Red LED: ", red,
		# 	  ", IR LED: ", ir,
		# 	  ", checksum: ", checksum)
		
		# receive first 2000 packets then graph
		if(count < 100):
			count += 1
			red_samples.append(red)
			ir_samples.append(ir)
			time_received.append(time.time())
			if(not count % 10):
				hr_data = int(current_hr)
				spo2_data = int(current_spo2)
				packet = struct.pack(">ii", hr_data, spo2_data)
				tx_sock.sendto(packet, ("172.20.10.10", TX_PORT))
		else:
			# compute average sampling rate using time received
			dt = np.diff(time_received)
			freq = 1 / np.mean(dt)
			# TO DO: error if transmission rate drops
			# put samples into np array and remove DC component
			np_red_samples = np.array(red_samples, dtype=float)
			np_red_DC = lowpass_filter(np_red_samples)
			# np_red_DC = np.mean(np_red_samples)
			np_red_AC = np_red_samples - np_red_DC
			np_ir_samples = np.array(ir_samples, dtype=float)
			np_ir_DC = lowpass_filter(np_ir_samples)
			# np_ir_DC = np.mean(np_ir_samples)
			np_ir_AC = np_ir_samples - np_ir_DC
			# compute spectrum
			# spectrum = np.fft.fftshift(np.fft.fft(np_red_samples))
			# plot_spectrum(spectrum, fs=100, doStem=False)
			# bp_filter = signal.butter(N=4, Wn=(0.5, 7), btype="bandpass", output="sos", fs=freq)
			# filtered_red = signal.sosfilt(bp_filter, red_samples)

			# Digital filter critical frequencies must be 0 < Wn < fs/2
			filtered_red_AC = bandpass_filter(np_red_AC, fs=freq)
			filtered_ir_AC = bandpass_filter(np_ir_AC, fs=freq)

			# these should be RMS values within a windowed segment (2s)

			##################################################################
			# Plotting signals
			##################################################################

			ratio = np.array(get_ratio(freq))
			spo2 = 104.0 - (17.0 * ratio)
			heartrate_list = get_heartrate()

			# make sure input length > padlen
			if len(spo2) > 15:
				spo2_filtered = lowpass_filter(spo2, cutoff=0.4, fs=freq)
				current_spo2 = spo2_filtered[len(spo2_filtered) - 1]
			
			if len(heartrate_list) > 15:
				heartrate_filtered = lowpass_filter(heartrate_list, cutoff=0.4, fs=freq)
				current_hr = heartrate_filtered[len(heartrate_filtered) - 1]

			if(not count % 10):
				hr_data = int(current_hr)
				spo2_data = int(current_spo2)
				packet = struct.pack(">ii", hr_data, spo2_data)
				tx_sock.sendto(packet, ("172.20.10.10", TX_PORT))
				print(".............................Data sent: ", current_hr)
    
			# spo2_filtered = lowpass_filter(spo2, cutoff=0.4, fs=freq)
			# heartrate_filtered = lowpass_filter(heartrate_list, cutoff=10, fs=freq)
			# heartrate_convolved= np.convolve(heartrate_list, np.ones(5)/5, mode="same")
			# current_hr = heartrate_convolved[len(heartrate_convolved) - 1]
			
			# plot_spectrum(filtered_red_AC, fs=freq)

			# time axis
			# t = np.arange(len(filtered_red_AC)) / freq
			# t_o2 = t[window:] - (window / (2 * freq))

			# plt.figure(figsize=(10, 6))

			# AC component
			# plt.plot(t, filtered_red_AC, label='Filtered Red Samples')
			# plt.plot(t, np_red_AC, label='Red Samples')
			# plt.plot(t, filtered_ir_AC, label='Filtered IR Samples')
			# plt.plot(t, np_ir_AC, label='IR Samples')

			# DC component
			# plt.plot(t, np_red_DC, label='Red DC')
			# plt.plot(t, np_ir_DC, label='IR DC')

			# Ratio
			# plt.plot(t, ratio_red, label='Red Ratio')
			# plt.plot(t, ratio_ir, label='IR Ratio')
			# plt.plot(t_R, ratio, label='ratio')

			# SpO2 saturation
			# plt.subplot(3, 1, 1)
			# plt.plot(spo2_filtered, label='oxygen saturation')
			# plt.title("Oxygen Saturation")
			# plt.xlabel("time")
			# plt.ylabel("%")

			# plt.subplot(3, 1, 2)
			# plt.plot(heartrate_filtered, label='heartrate')
			# plt.title("Heart Rate (Lowpass Filter)")
			# plt.xlabel("time")
			# plt.ylabel("BPM")

			# plt.subplot(3, 1, 3)
			# plt.plot(heartrate_convolved, label='heartrate')
			# plt.title("Heart Rate (Convolved)")
			# plt.xlabel("time")
			# plt.ylabel("BPM")

			# plt.tight_layout()
			# plt.show()

			# update initial conditions for next batch
			if(current_hr > 0 and (((1/current_hr) - 0.5) > 0.5)):
				low = (1/current_hr) - 0.5
			if(current_hr > 0 and (((1/current_hr) + 0.5) < 4.5)):
				high = (1/current_hr) + 0.5
			count = 0
	except struct.error:
		print("Packet unpacking failed")
