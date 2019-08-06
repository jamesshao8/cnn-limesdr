import time
import tensorflow as tf
import numpy as np
import os
import sys, argparse
from limesdr import *
import scipy.signal as signal


def read_samples(sdr, freq, stream):
    sdr.set_LO_frequency(False, 0, freq)
    time.sleep(0.04)
    #return sdr.read_samples(sample_rate * 0.25)
    #samples = sdr.read_samples(1221376)
    samples = sdr.receive_stream_iq(stream, 1200000, 1000)
    return samples



parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--ppm', type=int, default=0,
                    help='dongle ppm error correction')
parser.add_argument('--gain', type=int, default=20,
                    help='dongle gain level')
parser.add_argument('--threshold', type=float, default=0.75,
                    help='threshold to display/hide predictions')
parser.add_argument('--start', type=int, default=85000000,
                    help='begin scan here, in Hertz')
parser.add_argument('--stop', type=int, default=108000000,
                    help='stop scan here, in Hertz')
parser.add_argument('--step', type=int, default=100000,
                    help='step size for scan, in Hertz')

args = parser.parse_args()

sdr = LimeSDR()
sdr.enable_channel(False,0,True)
sdr.set_LO_frequency(False, 0, 434e6)
sdr.set_antenna(False, 0, 2)
sdr.set_sample_rate(4.8e6, 4)
sdr.set_LPF_BW(False, 0, 4.8e6)
sdr.set_normalized_gain(False, 0, 0.7)
sdr.calibrate(False, 0, 4.8e6, 0)
stream = sdr.setup_stream(0, 1024*1024, 0.5,  False, 2)
sdr.start_stream(stream)
    

classes = [d for d in os.listdir('training_data') if os.path.isdir(os.path.join('training_data', d))]
num_classes = len(classes)

sess = tf.Session()
saver = tf.train.import_meta_graph('rtlsdr-model.meta')
saver.restore(sess, tf.train.latest_checkpoint('./'))

graph = tf.get_default_graph()
y_pred = graph.get_tensor_by_name("y_pred:0")
x = graph.get_tensor_by_name("x:0")
y_true = graph.get_tensor_by_name("y_true:0")
y_test_samples = np.zeros((1, num_classes))

freq = args.start
while freq <= args.stop:
    samples = []
    iq_samples = read_samples(sdr, freq, stream)
    iq_samples = signal.decimate(iq_samples, 48)
    iq_samples = signal.decimate(iq_samples, 2)
    real = np.real(iq_samples)
    imag = np.imag(iq_samples)
    # iq_samples = np.concatenate((real, imag))
    # iq_samples = np.reshape(iq_samples, (-1, 2, 3200))

    iq_samples = []
    for i in range(0, np.ma.count(real) - 212):  # 128*192 magic
        iq_samples.append(real[i])
        iq_samples.append(imag[i])
    iq_samples = np.reshape(iq_samples, (-1, 128, 2))
    samples.append(iq_samples)

    samples = np.array(samples)

    # x_batch = samples.reshape(1, 1, 3200, 2)
    x_batch = samples.reshape(1, 96, 128, 2)

    feed_dict_testing = {x: x_batch, y_true: y_test_samples}
    result = sess.run(y_pred, feed_dict=feed_dict_testing)

    max = 0.0
    maxlabel = ""
    for sigtype, probability in zip(classes, result[0]):
        if probability >= max:
            max = probability
            maxlabel = sigtype

    if (maxlabel != 'other') and (max >= args.threshold):
        print('{:.3f} MHz - {} {:.2f}%'.format(freq / 1e6, maxlabel, max * 100))

    freq += args.step

sdr.close()
