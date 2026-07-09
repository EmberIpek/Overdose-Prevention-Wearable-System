# Overdose Prevention Wearable System
## Pilot Proposal

Individuals at high risk of overdose often experience prolonged respiratory depression long before help arrives. Studies indicate that individuals involved in the criminal justice system are significantly more likely to die of overdose than the general population [1], [2], with those on probation up to 15 times more likely to die of opioid-related overdose [2]. Additional risk factors identified for those on probation included age >45, prior positive drug screen result for opioids or cocaine, and prior placement in drug treatment programs [2]. This pilot proposal evaluates whether wearable devices that includes voluntary healthcare-managed heartrate monitor and oxygen saturation monitor combined with rapid outreach programs reliably reduce fatal overdoses in high-risk populations. The program prioritizes protection of healthcare data, early detection of overdose, and non-punitive medical response.

Current GPS monitoring programs are designed for location tracking and compliance monitoring and provide no mechanism for detecting medical emergencies. This program aims to bridge the gap through an optional HIPAA compliant healthcare-managed biometric monitoring program for participants already required to wear GPS tracking device. Participants who opt in would receive a tracker device that integrates heartrate and oxygen saturation monitors, with health data accessible only to healthcare providers. No probation violation is triggered from medical alerts.

Eligible participants for the program must meet one of the following criteria:

- Adults with ≥1 non-fatal overdose incidents within the past 12 months
- Individuals referred through diversion programs
- Prior placement in a drug/alcohol treatment program
- Documented history of substance use disorder

## Protocol

1.	Device detects one of the following: 

- Oxygen saturation < 90% for 30 seconds 
- Abnormal heart rate (< 50 or > 240)

2.	Device vibrates and displays: 
"Health Check Required. Press button within 60 seconds."

3.	If user presses button:
- Log event
- Clear alert

4.	Else if no response:
- Device sounds alarm
- Send text message to designated contact

5.	If still no response and high-risk pattern after additional timeout:
- EMS dispatched
- Connection to peer support specialist/behavioral services

## Principle of Operation

The MAX30102 is an optical sensor that measures heart rate and oxygen saturation through the pulsing of blood from blood vessels after emitting two wavelengths of light. The module houses a red LED and an infrared (IR) LED, which are shined onto blood vessels through the skin, and the amount of reflected light is measured using a photodetector.

As the heart beats, it pushes blood into the capillaries. This localized increase in blood volume absorbs more light. Between beats, less blood is present, allowing more light to bounce back to the sensor. The peaks of the resulting sinusoidal waveform are measured to determine the frequency of pulses and obtain heart rate.

Oxygenated and deoxygenated blood absorb different ratios of red and IR light: oxygenated blood absorbs more infrared light, and deoxygenated blood absorbs more red light. The sensor alternates with shining the red and IR LEDs, and measures the absorption ratio of both wavelengths. By comparing the ratio of red and IR light absorbed by the photodetector, the sensor estimates the percentage of oxygenated blood in the blood vessels.


## Circuit Diagram

<img width="975" height="806" alt="image" src="https://github.com/user-attachments/assets/cac3f5f1-e251-45e0-ab24-3a77753f9c4e" />

## Outcomes

The program will measure the following outcomes:

Primary:
- Reduction in emergency response time to overdose events
- Reduction in fatal overdoses

Secondary:
- Initiation of substance abuse treatment
- Hospital admission reduction
- EMS activation accuracy (false positive, true positive, and false negative rates)

## Works Cited

[1] I. A. Binswanger, A. P. Nguyen, J. D. Morenoff, S. Xu, and D. J. Harding, “The association of criminal justice supervision setting with overdose mortality: a longitudinal cohort study,” Addiction, vol. 115, no. 12, pp. 2329–2338, Dec. 2020, doi: 10.1111/add.15077. PMID: 32267585.

[2] J. K. Boulger, K. Hinami, T. Lyons, and J. Nowinski Konchak, “Prevalence and risk factors for opioid related mortality among probation clients in an American city,” Journal of Substance Abuse Treatment, vol. 137, p. 108712, Jun. 2022, doi: 10.1016/j.jsat.2021.108712. PMID: 35067401.

# Progress Notes

### 6/19/2026

MAX30102 heart rate/oxygen saturation module obtained. Communicates through I2C protocol, sigma-delta ADC is integrated within module. Since the module supports IRQ and interrupts (active low INT pin), it is possible to use an ISR when an interrupt flag is raised by a low oxygen/heart rate event. Connect Vdd with bypass capacitor to GND.

Measured data is stored in FIFO register within the device. 18-bit data stored in big-endian format (MSB first) in register 0x07.

<img width="975" height="335" alt="image" src="https://github.com/user-attachments/assets/492c5260-e86a-4d07-914d-4bc889b1cdd9" />

MAX30102 datasheet: [https://www.analog.com/media/en/technical-documentation/data-sheets/max30102.pdf]

### Relevant registers:

Interrupt Enable: 0x02-0x03

Interrupt Status: 0x00-0x01

FIFO Data: 0x04-0x07

Mode Configuration: 0x09

Part ID: 0xFF

Device address: 0x57

### 6/23/2026

Soldered pins onto Pi Pico board, will use Pico to send biometric data to Pi. Machine.I2C documentation read: [https://docs.micropython.org/en/latest/library/machine.I2C.html]
Wired sensor and set up I2C communication on Pi Pico. Will use upython MAX30102 library.

bash:
```bash 
import mip
mip.install("micropython-max30102")
```

Updated schematic:
<img width="975" height="414" alt="image" src="https://github.com/user-attachments/assets/d322f0c4-a48e-4ec4-8c53-13cf37722e81" />

Available at: [https://www.circuitlab.com/editor/#?id=hh6msg7vwy5q]


Mode configuration reg (0x09) starts in power down, must be set to 0x03 for SpO2 mode. Read Part ID reg (0xFF) to test I2C bus.

To do: read MAX30102 upython documentation, set up polling for FIFO buffer reg (0x07)

### 6/24/2026

Initialized sensor to use MAX30102 library and added a loop to continuously read temperature. Pressing sensor against skin results in readings steadily increasing to body temperature, verifying operation.


<img width="464" height="414" alt="image" src="https://github.com/user-attachments/assets/d1403b7e-9d56-4867-b6a0-80748bf2a82f" />


MAX30102 micropython library is poorly documented and leads to unpredictable behavior. Will use direct access to registers instead. SpO2 config register (0x0A):

<img width="975" height="155" alt="image" src="https://github.com/user-attachments/assets/430ef721-b813-4c2e-862c-1eb3f77ef096" />

Bits 4:2 define sample rate, will use 400 samples/s

<img width="975" height="285" alt="image" src="https://github.com/user-attachments/assets/a891848b-b9c8-4ceb-869d-853548af4382" />

### Temperature registers: 

Die Temp Integer: 0x1F [7:0]

Die Temp Fraction: 0x20 [3:0]

Die Temp Config: 0x21 [0]

To do: read red and IR LED values, plot using matplotlib, pass through numpy butterworth low pass filter to filter out electrical jitter/high freq noise

### 6/25/2026

LED pulse width setter function created (register 0x0A bits 1:0). **Sample rate sets upper limit on pulse width time and ADC resolution is determined by pulse width:** 

<img width="975" height="214" alt="image" src="https://github.com/user-attachments/assets/bccba845-543a-4934-9f07-6077e4e4dce9" />

 
Helper function to set LED pulse amplitudes created (registers 0x0C and 0x0D). To tune pulse amplitude, check raw ADC values. IR signal should be ~20-80% ADC range. Function created to set ADC range (register 0x0A bits 6:5).

Temperature data registers 0x1F-0x21:

<img width="975" height="194" alt="image" src="https://github.com/user-attachments/assets/dd2a1748-fe63-4783-81bc-3bcd92cfc916" />

 
Temperature integer value represented in big endian 2’s complement format. Fractional value incremented in multiples of 0.0625. Temperature config register bit 0 set to 1 to read temperature and is automatically cleared.

### 6/26/2026

Modified code to connect to send packets through UDP. Made socket and wlan global and initialized outside of sensor for better separation of concerns. 
Reading the FIFO_DATA register (0x07) does not automatically increment the register address. Maximum sample rate for ADC depends on pulse width. For 118us, ADC resolution is 16 bits. FIFO register should be read in 3-byte bursts. For SpO2 mode, one sample requires 6-byte reads.

FIFO config register (0x08) bits 7:5 determine the number of samples averaged:

<img width="975" height="145" alt="image" src="https://github.com/user-attachments/assets/c4bc2bd8-1b2c-4397-947b-35b4286650da" />

Setter function for sample averaging implemented and set to 8 by default. Bit 4 set for FIFO rollover enable by default.

To do: eventually move all SpO2 functions to a separate file. Accidentally ended up writing an entire driver for this module, so might as well use it as one.

### 6/29/2026

Refactored code to create a MAX30102 class for future driver implementation. Created function to read FIFO data in 6-byte bursts for SpO2 mode. Samples are transmitted in a 24-bit field, with the upper six bits unused. When operating at less than 18-bit resolution, the valid ADC bits remain aligned to the most significant end of the 18-bit field:

<img width="975" height="175" alt="image" src="https://github.com/user-attachments/assets/67d7b14d-7878-40cf-bb57-89854bfe1e38" />

FIFO read and write pointers cleared upon setting SpO2 mode, as instructed in the data sheet. FIFO read function returns red and IR LED values, which spike when pressed against thumb. Values are out of range of the 16-bit ADC resolution (0 – (2^16 – 1)). Must clear top 6 bits and shift right by 18 – resolution. Added code to append checksum to packet. 

To do: use matplotlib to graph red and IR LED data, apply low pass filter.

### 6/30/2026

Sensor receiver code modified to graph first 1000 samples of IR and LED data received. Graph shows small, consistent spikes in data values when heart beats. Will verify further by increasing data transmission rate and testing for changes after exercise. Increasing transmission rate results in cleaner readings:

<img width="440" height="357" alt="image" src="https://github.com/user-attachments/assets/24f87c49-1c10-436d-9f0d-cbd609ae3751" />
<img width="440" height="357" alt="image" src="https://github.com/user-attachments/assets/de6625d8-df0e-4720-bef0-6414ce08fffc" />


Np.mean subtracted from signal to normalize signal, np.fft used to analyze signal frequencies and plot spectrum:

<img width="882" height="561" alt="image" src="https://github.com/user-attachments/assets/d492784b-e620-46f8-91f3-fbc5f180a884" />

Signal is passed through butterworth bandpass filter (0.5 – 7Hz) to filter out noise. Sampling rate is estimated using time_received. Filtered signal looks more stable but should parameterize filter coefficients later:

<img width="534" height="392" alt="image" src="https://github.com/user-attachments/assets/43682724-b52a-4386-b1bf-70fe0276172d" />
 
To do: throw exception if transmission rate drops below threshold. Try filtfilt, narrower bandpass range.

Acknowledgements: plot_spectrum() function from ECE201 Signals and Systems, Dr. Bernd-Peter Paris, George Mason University.

### 7/1/2026

Bandpass filter moved to separate function, filtered signal plotted against normalized raw values, passed through SciPy filtfilt to obtain clean AC sample:

<img width="560" height="438" alt="image" src="https://github.com/user-attachments/assets/6f2f47a7-d447-4cc9-a529-7e1b456247e3" />

Read SciPy buttord documentation to determine how to find optimal order for butterworth filter. To compute SpO2, red and IR samples will be filtered and the ratio calculated with R=(AC_ir/DC_ir)/(AC_red/DC_red).
Real-time DC component of signal obtained through lowpass filter (0.4Hz):
 
<img width="572" height="439" alt="image" src="https://github.com/user-attachments/assets/bcdf6512-0920-41d9-8f96-1a913d676c10" />

Plotting red and IR ratios give similar values, trying using unfiltered DC signal with np.mean:

<img width="535" height="413" alt="image" src="https://github.com/user-attachments/assets/198eca51-57ea-4bfb-a02b-ee9a480b6caf" />

RMS value function written. Calculating ratio requires RMS values of signals within a window:

$$
V_{\mathrm{RMS}} = \sqrt{\frac{1}{N} \sum_{n=1}^{N} V_n^2}
$$

To do: find peak values to calculate bpm, read SciPy signal.find_peaks documentation, calculate ratio correctly, use np.mean for DC component.

### 7/2/2026

Signal.find_peaks documentation read. Np.mean used for calculating DC component of ratio and RMS for AC, lowpass filter result kept for extracting AC data. Cast list into np array and used formula to convert ratio to SpO2 estimation:

<img width="470" height="374" alt="image" src="https://github.com/user-attachments/assets/6d9e8084-eb61-44c1-88dc-18b6f4c2ff2c" />
<img width="470" height="374" alt="image" src="https://github.com/user-attachments/assets/feef65db-4bf3-49c4-82e9-440ba087c3d8" />

Measured peaks with signal.find_peaks and plotted. Light exercise while holding module verifies heart rate increase:

<img width="975" height="583" alt="image" src="https://github.com/user-attachments/assets/d280d08c-6736-4be1-9325-6d75f6c33c26" />

To do: Use np.convolve or apply lowpass filter to resulting ratio to smooth before calculating SpO2.

### 7/3/2026

O2 and heart rate signal cleaned up with further signal processing, low pass filter compared with convolution:

<img width="975" height="572" alt="image" src="https://github.com/user-attachments/assets/af2b7a7e-8770-4918-ae71-441eb0553f73" />
 
Setting up 7-segment displays to show heart rate and SpO2 data in real time, with green and red LEDs showing safe and unsafe range, respectively:

<img width="640" height="493" alt="image" src="https://github.com/user-attachments/assets/a714b300-6877-4576-aa47-06670df7b0c3" />

Use PC to send data back to Pico (dummy data for now). Turned sample lists into FIFO buffers and implemented 2-way communication with the Pico. **Sometimes the sample rate dips below the Nyquist rate for the high end of the bandpass filter. Clamped frequency value passed into filters to ensure program does not crash.**

To do: Define packet, with status bits for low SpO2, tachycardia, and bradycardia. Unpack on Pico and update 7-seg displays and LEDs

### 7/6/2026

Updated circuit diagram for 7-seg display:

<img width="1043" height="755" alt="image" src="https://github.com/user-attachments/assets/6685b549-b4ad-48be-97f6-1b9fb29d4b5c" />

Created separate file for 7-seg function. Wired and initialized segments. Filtfilt padlen is 15 by default, created check to make sure input signal length > 15 before passing through.

To do: split UDP and sensor code into separate files, define range for LEDs, PC still sending back dummy values to Pico, send back the heart rate and SpO2 data. Average heart rate and SpO2 and send back every 100 iterations. Unpack on Pico and use to update display: truncate float to 4 significant digits

### 7/7/2026

Fixed UDP send bug when sending heart rate back to Pico (cast to int before sending). Pico now receives accurate averaged heart rate data and 7-seg display shows heart rate. Refactored code to handle SSEG display in separate file.

Youtube demonstration:

[![Watch the video](https://img.youtube.com/vi/7sWadJel9nA/default.jpg)](https://www.youtube.com/watch?v=7sWadJel9nA)

To do: processing lags behind sent/received data, must resync at regular intervals.

### 7/8/2026

Added second SSEG display and added code to send SpO2 data back to Pico. Circuit diagram updated for second SSEG display and LEDs:

<img width="975" height="806" alt="image" src="https://github.com/user-attachments/assets/8fe98517-f34a-4280-9174-ecf2bca64714" />

Debugging with print statements to determine if sampling rate goes below Nyquist rate for filters. Display 10s and 100s place is very dim and flickering, wiring for digits mixed up. Fix in next iteration.

To do: add code to light LEDs based on heart rate and SpO2. Professor suggested using stateful filters with previous batch values to determine bandpass filter cutoffs, experiment with using initial conditions based on previous states.

### 7/9/2026

Fixed 7-segment display bug and updated circuit diagram. Implemented LED functionality.

<img width="975" height="816" alt="image" src="https://github.com/user-attachments/assets/47dd6b3f-cdb4-44d9-9f57-0572c3805ffd" />

Youtube demonstration:

[![Watch the video](https://img.youtube.com/vi/-ZItoqglV_4/default.jpg)](https://www.youtube.com/watch?v=-ZItoqglV_4)

<p align="center">
  <a href="https://www.youtube.com/watch?v=-ZItoqglV_4" target="_blank">
    <img src="https://youtube.com" alt="Watch the video" width="600">
  </a>
</p>
