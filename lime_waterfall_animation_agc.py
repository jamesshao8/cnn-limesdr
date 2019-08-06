import tkinter as tk
import threading
import queue
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as line
import numpy as np
from scipy import fftpack
from scipy import signal
import sys
import os
from ctypes import *
import datetime
import time
import pylab as mpl


SIZE = 1024


#GUI
class Application(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self,master)
        self.grid()
        self.creatWidgets()

    def creatWidgets(self):
        self.quitButton=tk.Button(self,text='quit',command=root.destroy)
        self.quitButton.grid(column=1,row=3)


#Matplotlib
fig = plt.figure()
rt_ax = plt.subplot(212,xlim=(0,SIZE), ylim=(-0.5,0.5))
fft_ax = plt.subplot(211)
fft_ax.set_xlim(0,SIZE)
fft_ax.set_ylim(0.01,100)
rt_ax.set_title("Real Time")
fft_ax.set_title("FFT Time")
rt_line = line.Line2D([],[])
fft_line = line.Line2D([],[])

rt_data=np.arange(0,SIZE,1)
fft_data=np.arange(0,SIZE,1)
rt_x_data=np.arange(0,SIZE,1)
fft_x_data=np.arange(0,SIZE,1)

array_type = (c_int16* 2048)
recv_buf = array_type()


class lms_stream_t(Structure):
    _fields_ = [("handle", c_size_t),
                ("isTx", c_bool),
                ("channel", c_uint32),
                ("fifoSize", c_uint32),
                ("throughputVsLatency", c_float),
                ("dataFmt", c_int)]

def packed_bytes_to_iq(bytes):
    ''' Convenience function to unpack array of bytes to Python list/array
    of complex numbers and normalize range. Called automatically by read_samples()
    '''
    if True:
        # use NumPy array
        iq = np.empty(len(bytes)//2, 'complex')
        iq.real, iq.imag = bytes[::2], bytes[1::2]
        iq /= (255/2)
    return iq


def load_liblimesdr():


    driver_files = []
    driver_files += ['libLimeSuite.so']

    dll = None

    for driver in driver_files:
        print (driver)
        try:
            dll = CDLL(driver)
            print ("normal")
            break
        except:
            print ("exception")
            pass
 

    return dll

liblimesdr = load_liblimesdr()

p_limesdr_dev = c_void_p
p_null = c_void_p

dev_p = p_limesdr_dev(None)
null_p = p_null(None)

bfr = (c_ubyte * 2560)()
lo_freq = (c_double * 1)()
range_p = (c_double * 3)()


f = liblimesdr.LMS_GetDeviceList
f.restype, f.argtypes = c_int, [POINTER(c_ubyte)]

f = liblimesdr.LMS_Open
f.restype, f.argtypes = c_int, [POINTER(p_limesdr_dev), c_char_p , p_null]

f = liblimesdr.LMS_Close
f.restype, f.argtypes = c_int, [p_limesdr_dev]

f = liblimesdr.LMS_GetNumChannels
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool]

f = liblimesdr.LMS_EnableChannel
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t , c_bool]

f = liblimesdr.LMS_SetLOFrequency
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t , c_double]

f = liblimesdr.LMS_GetLOFrequency
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t , POINTER(c_double)]

f = liblimesdr.LMS_SetAntenna
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t , c_size_t]

f = liblimesdr.LMS_GetAntenna
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t]

f = liblimesdr.LMS_SetSampleRate
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_double, c_size_t]

f = liblimesdr.LMS_GetLPFBWRange
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, POINTER(c_double)]

f = liblimesdr.LMS_SetLPFBW
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t, c_double]

f = liblimesdr.LMS_SetNormalizedGain
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t, c_double]

f = liblimesdr.LMS_Calibrate
f.restype, f.argtypes = c_int, [p_limesdr_dev, c_bool, c_size_t, c_double, c_uint]

f = liblimesdr.LMS_AGCStart
f.restype, f.argtypes = c_int, [p_limesdr_dev]

f = liblimesdr.LMS_SetupStream
f.restype, f.argtypes = c_int, [p_limesdr_dev, POINTER(lms_stream_t)]

f = liblimesdr.LMS_StartStream
f.restype, f.argtypes = c_int, [POINTER(lms_stream_t)]


f = liblimesdr.LMS_RecvStream
f.restype, f.argtypes = c_int, [POINTER(lms_stream_t), c_void_p , c_size_t, p_null, c_uint]


def plot_init():
    rt_ax.add_line(rt_line)
    fft_ax.add_line(fft_line)
    return fft_line,rt_line,
    
def plot_update(i):
    global rt_data
    global fft_data
    
    rt_line.set_xdata(rt_x_data)
    rt_line.set_ydata(rt_data)
    
    fft_line.set_xdata(fft_x_data)
    fft_line.set_ydata(fft_data)
    return fft_line,rt_line,


class reading_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global rt_data,fft_data,recv_buf
        self.running = True
        while self.running:
            samplesRead=liblimesdr.LMS_RecvStream(byref(stream), recv_buf, 1024, null_p, 1000)
            samples = packed_bytes_to_iq(recv_buf)
        
            rt_data = np.real(samples)

            samples = samples * window
            fft_temp_data=fftpack.fftshift(fftpack.fft(samples,overwrite_x=True))
            fft_data=np.abs(fft_temp_data)[0:fft_temp_data.size]




ani = animation.FuncAnimation(fig, plot_update,
                              init_func=plot_init, 
                              frames=10,
                              interval=10,
                              blit=True)


num_devices = liblimesdr.LMS_GetDeviceList(bfr)
counter = 0
first_limesdr = ''
num = 0 
for b in bfr:
    first_limesdr = first_limesdr + chr(b)
    counter = counter + 1
    if counter % 256 == 0:
        break

first_limesdr = bytes(first_limesdr, 'UTF-8')
result = liblimesdr.LMS_Open(dev_p, first_limesdr, null_p)
num_channels = liblimesdr.LMS_GetNumChannels(dev_p , False)
result = liblimesdr.LMS_EnableChannel(dev_p, False, 0, True)
result = liblimesdr.LMS_SetLOFrequency(dev_p, False, 0, 433e6)
result = liblimesdr.LMS_GetLOFrequency(dev_p, False, 0, lo_freq)
result = liblimesdr.LMS_SetAntenna(dev_p, False, 0, 2)
result = liblimesdr.LMS_GetAntenna(dev_p, False, 0)
result = liblimesdr.LMS_SetSampleRate(dev_p, 10e6, 4)
result = liblimesdr.LMS_GetLPFBWRange(dev_p, False, range_p)
result = liblimesdr.LMS_SetLPFBW(dev_p, False, 0, 10e6)
result = liblimesdr.LMS_SetNormalizedGain(dev_p, False, 0, 0.7)
result = liblimesdr.LMS_Calibrate(dev_p, False, 0, 10e6, 0) 
result = liblimesdr.LMS_AGCStart(dev_p) 
print ("agc result: ", result)
stream = lms_stream_t(channel = 0, fifosize = 1024*1024, throughputVsLatency = 0.1, isTx = False, dataFmt = 2) 
result = liblimesdr.LMS_SetupStream(dev_p, byref(stream))
result = liblimesdr.LMS_StartStream(byref(stream))


#processing block
window = signal.hamming(SIZE)


print("Start thread")

#t_read_data.start()

rt = reading_thread()
rt.start()

plt.show()
root=tk.Tk()
app=Application(master=root)
app.master.title("Test")
app.mainloop()

print('ended')
