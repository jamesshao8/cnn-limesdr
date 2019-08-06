from limesdr import *
import pylab as mpl
import datetime

def main():
    sdr = LimeSDR()


    sdr.enable_channel(False,0,True)
    sdr.set_LO_frequency(False, 0, 434e6)

    sdr.set_antenna(False, 0, 2)

    sdr.set_sample_rate(10e6, 4)
    a,b,c = sdr.get_LPF_BW_range(False)


    sdr.set_LPF_BW(False, 0, 10e6)
    sdr.set_normalized_gain(False, 0, 0.7)

    sdr.calibrate(False, 0, 10e6, 0)
    stream = sdr.setup_stream(0, 1024*1024, 0.5,  False, 2)
    sdr.start_stream(stream)
    
    

    start_time = datetime.datetime.now()
    current_time = datetime.datetime.now()
    while ((current_time - start_time).seconds < 2):
        iq = sdr.receive_stream_iq(stream, 1024, 1000)
        mpl.figure()
        mpl.psd(iq, NFFT=1024, Fc=434, Fs=10)
        mpl.show()
        print('  signal mean:', sum(iq)/len(iq))
        current_time = datetime.datetime.now()

    sdr.close()

if __name__ == '__main__':
    main()
