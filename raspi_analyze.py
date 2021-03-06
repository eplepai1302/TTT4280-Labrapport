from cProfile import label
from cmath import cos
import math
from turtle import xcor
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import signal
import scipy.signal as signal 
from scipy.signal import butter, lfilter, freqz



def raspi_import(path, channels=5):
    """
    Import data produced using adc_sampler.c.
    Returns sample period and ndarray with one column per channel.
    Sampled data for each channel, in dimensions NUM_SAMPLES x NUM_CHANNELS.
    """

    with open(path, 'r') as fid:
        sample_period = np.fromfile(fid, count=1, dtype=float)[0]
        data = np.fromfile(fid, dtype=np.uint16)
        data = data.reshape((-1, channels))
    return sample_period, data

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Import data from bin file
sample_period, data = raspi_import('C6 30grader.bin')

data = signal.detrend(data, axis=0)  # removes DC component for each channel
sample_period *= 1e-6  # change unit to micro seconds

# Generate time axis
num_of_samples = data.shape[0]  # returns shape of matrix
t = np.linspace(start=0, stop=num_of_samples*sample_period, num=num_of_samples)

# Generate frequency axis and take FFT
freq = np.fft.fftfreq(n=num_of_samples, d=sample_period)
spectrum = np.fft.fft(data, axis=0)  # takes FFT of all channels


# Plot the results in two subplots
# NOTICE: This lazily plots the entire matrixes. All the channels will be put into the same plots.
# If you want a single channel, use data[:,n] to get channel n
plt.subplot(2, 1, 1)
plt.title("Time domain signal")
plt.xlabel("Time [us]")
plt.ylabel("Voltage")
plt.plot(t, data)

plt.subplot(2, 1, 2)
plt.title("Power spectrum of signal")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Power [dB]")
plt.plot(freq, 20*np.log10(np.abs(spectrum))) # get the power spectrum

plt.show()


#Dataene fra de forskjellige mikrofonene

mic_1 = data[2000:,1] 
mic_2 = data[2000:,0]
mic_3 = data[2000:,4]


#F??rst b??ndpassfilter over data
order = 6
fs = 31250
cutoff = 500

b, a = butter_lowpass(cutoff, fs, order)

#Plotting freq respons
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()
plt.show()

filter_1 = butter_lowpass_filter(mic_1, cutoff, fs, order)
filter_2 = butter_lowpass_filter(mic_2, cutoff, fs, order)
filter_3 = butter_lowpass_filter(mic_3, cutoff, fs, order)

t2 = t[2000:]
plt.subplot(2, 1, 1)
plt.plot(t2, mic_1, 'b-', label='data')
plt.plot(t2, filter_1, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(t2, mic_2, 'b-', label='data')
plt.plot(t2, filter_2, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(t2, mic_3, 'b-', label='data')
plt.plot(t2, filter_3, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.show()

#s?? krysskorelasjon mellom dataen og finn st??rste verdi

mic_12 = np.correlate(mic_1, mic_2, 'full')
mic_13 = np.correlate(mic_1, mic_3, 'full')
mic_23 = np.correlate(mic_2, mic_3, 'full')
mic_11 = np.correlate(mic_1, mic_1, 'full')

#Plot av alle krysskorrelasjonene:
fig = plt.figure()
ax1 = fig.add_subplot(411)
ax1.xcorr(mic_1, mic_2, usevlines=True, maxlags=29)
ax1.grid(True)

ax2 = fig.add_subplot(412)
ax2.xcorr(mic_1, mic_3, usevlines=True, maxlags=29)
ax2.grid(True)

ax3 = fig.add_subplot(413)
ax3.xcorr(mic_2, mic_3, usevlines=True, maxlags=29)
ax3.grid(True)

ax3 = fig.add_subplot(414)
ax3.xcorr(mic_1, mic_1, usevlines=True, maxlags=29)
ax3.grid(True)

plt.show()

#Finner hvilken lag som gir maksveridene p?? krysskorrelasjonene:
max_11 = np.argmax(mic_11)
max_1 = np.argmax(mic_12) - max_11
max_2 = np.argmax(mic_13) - max_11
max_3 = np.argmax(mic_23) - max_11

print(max_1)
print(max_2)
print(max_3)
print(max_11)

#Beregner vinkel utifra forskyvningen i lag.
vinkel = math.degrees(np.arctan2(np.sqrt(3)*(max_1 + max_2),(max_1 - max_2 - 2*max_3)))

print(f"Vinkelen: {vinkel}")