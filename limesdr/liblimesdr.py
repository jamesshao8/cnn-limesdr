import sys
import os
from ctypes import *

class lms_stream_t(Structure):
    _fields_ = [("handle", c_size_t),
                ("isTx", c_bool),
                ("channel", c_uint32),
                ("fifoSize", c_uint32),
                ("throughputVsLatency", c_float),
                ("dataFmt", c_int)]

def load_liblimesdr():
    driver_files = []
    driver_files += ['libLimeSuite.so']

    dll = None

    for driver in driver_files:
        try:
            dll = CDLL(driver)
            break
        except:
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

f = liblimesdr.LMS_SetupStream
f.restype, f.argtypes = c_int, [p_limesdr_dev, POINTER(lms_stream_t)]

f = liblimesdr.LMS_StartStream
f.restype, f.argtypes = c_int, [POINTER(lms_stream_t)]


f = liblimesdr.LMS_RecvStream
f.restype, f.argtypes = c_int, [POINTER(lms_stream_t), c_void_p , c_size_t, p_null, c_uint]

__all__  = ['liblimesdr', 'p_limesdr_dev', 'p_null', 'lms_stream_t']
