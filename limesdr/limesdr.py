from __future__ import division, print_function
from ctypes import *
import sys
import numpy as np

from .liblimesdr import (
    liblimesdr,
    p_limesdr_dev,
    p_null,
    lms_stream_t,
)

PY3 = sys.version_info.major >= 3

def packed_bytes_to_iq(bytes):
    iq = np.empty(len(bytes)//2, 'complex')
    iq.real, iq.imag = bytes[::2], bytes[1::2]
    iq /= (255/2)

    return iq

class LimeSDR(object):
    bfr = (c_ubyte * 2560)()
    
    range_p = (c_double * 3)()
   
    device_opened = False

    
    def get_first_device(self):
        num_devices = liblimesdr.LMS_GetDeviceList(self.bfr)
        counter = 0
        first_limesdr = ''
        num = 0 
        for b in self.bfr:
            first_limesdr = first_limesdr + chr(b)
            counter = counter + 1
            if counter % 256 == 0:
                break
        if PY3:
            first_limesdr = bytes(first_limesdr, 'UTF-8')

        return first_limesdr

    def __init__(self):
        self.open()

    def open(self):
        first_limesdr = self.get_first_device()
        
        self.dev_p = p_limesdr_dev(None)
        self.null_p = p_null(None)

        result = liblimesdr.LMS_Open(self.dev_p, first_limesdr, self.null_p)
        if result < 0:
            raise IOError('Error code %d when opening SDR ' % (result))

    

        self.device_opened = True
        #self.init_device_values()
    '''
    def init_device_values(self):
        self.gain_values = self.get_gains()
        self.valid_gains_db = [val/10 for val in self.gain_values]

        # set default state
        self.set_sample_rate(self.DEFAULT_RS)
        self.set_center_freq(self.DEFAULT_FC)
        self.set_gain(self.DEFAULT_GAIN)
    '''

    def close(self):
        if not self.device_opened:
            return

        result = liblimesdr.LMS_Close(self.dev_p)
        if result < 0:
            raise IOError('Error code %d when closing SDR ' % (result))

        self.device_opened = False

    def __del__(self):
        self.close()

    def get_num_channels(self, direction):
        num_channels = liblimesdr.LMS_GetNumChannels(self.dev_p , direction)
        return num_channels


    def enable_channel(self, direction, channel, enabled):
        #direction 0 for RX, direction 1 for TX
        result = liblimesdr.LMS_EnableChannel(self.dev_p, direction, channel, enabled)
        if result < 0:
            raise IOError('Error code %d when enabling channel ' % (result))
        return

    def set_LO_frequency(self, direction, channel, frequency):
        result = liblimesdr.LMS_SetLOFrequency(self.dev_p, direction, channel, frequency)
        if result < 0:
            raise IOError('Error code %d when setting LO freq ' % (result))
        return

    def get_LO_frequency(self, direction, channel):
        lo_freq = (c_double * 1)()
        result = liblimesdr.LMS_GetLOFrequency(self.dev_p, direction, channel, lo_freq)
        if result < 0:
            raise IOError('Error code %d when getting LO freq ' % (result))
        return lo_freq[0]

    def set_antenna(self, direction, channel, antenna):
        # antenna = 2 for LNAL
        result = liblimesdr.LMS_SetAntenna(self.dev_p, direction, channel, antenna)
        if result < 0:
            raise IOError('Error code %d when setting antenna ' % (result))
        return 

    def get_antenna(self, direction, channel):
        result = liblimesdr.LMS_GetAntenna(self.dev_p, direction, channel)

        return result

    def set_sample_rate(self, sample_rate, oversample):
        result = liblimesdr.LMS_SetSampleRate(self.dev_p, sample_rate, oversample)
        if result < 0:
            raise IOError('Error code %d when setting sample rate ' % (result))
        return

    def get_LPF_BW_range(self, direction):
        range_p = (c_double * 3)()
        result = liblimesdr.LMS_GetLPFBWRange(self.dev_p, direction, range_p)
        if result < 0:
            raise IOError('Error code %d when getting LPF BW range ' % (result))
        return range_p[0],range_p[1],range_p[2]

    def set_LPF_BW(self, direction, channel, bandwidth):  
        result = liblimesdr.LMS_SetLPFBW(self.dev_p, direction, channel, bandwidth)
        if result < 0:
            raise IOError('Error code %d when setting LPF BW ' % (result))
        return

    def set_normalized_gain(self, direction, channel, gain):  
        result = liblimesdr.LMS_SetNormalizedGain(self.dev_p, direction, channel, gain)
        if result < 0:
            raise IOError('Error code %d when setting normalized gain ' % (result))
        return

    def calibrate(self, direction, channel, bandwidth, flags):
        result = liblimesdr.LMS_Calibrate(self.dev_p, direction, channel, bandwidth, flags) 
        if result < 0:
            raise IOError('Error code %d when calibrating ' % (result))
        return

    def setup_stream(self, channel, fifosize, throughputVsLatency, isTx, dataFmt):
        stream = lms_stream_t(channel = channel, fifosize = fifosize, throughputVsLatency = throughputVsLatency, isTx = isTx, dataFmt = dataFmt)
        result = liblimesdr.LMS_SetupStream(self.dev_p, byref(stream))
        if result < 0:
            raise IOError('Error code %d when setuping stream ' % (result))
        return stream

    def start_stream(self, stream):
        result = liblimesdr.LMS_StartStream(byref(stream))
        if result < 0:
            raise IOError('Error code %d when starting stream ' % (result))
        return

    def receive_stream_iq(self, stream, samples_count, timeout_ms):
        buffer_count = samples_count * 2
        self.null_p = p_null(None)
        array_type = (c_int16* buffer_count)
        recv_buf = array_type()
        samplesRead=liblimesdr.LMS_RecvStream(byref(stream), recv_buf, samples_count, self.null_p, timeout_ms)
        samples = packed_bytes_to_iq(recv_buf)
        #iq = np.empty(len(recv_buf)//2, 'complex')
        #iq.real, iq.imag = recv_buf[::2], recv_buf[1::2]
        #iq /= (255/2)

        return samples



    

