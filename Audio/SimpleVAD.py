
from scipy.signal import hilbert
import numpy
import time

class SimpleVAD:

    def __init__(self):
        pass

    def vad(self, audio_data, sfreq):
        #audio_data = self.noise_reduction(audio_data, sfreq)
        feature = self.audio_feature(audio_data)
        print(feature)

        clf = self.classify(feature)

        return clf


    def audio_feature(self, data):
        #data = numpy.abs(hilbert(data))
        data = data / 32767  # 16 bit normalization
        rms = numpy.sqrt(numpy.mean(data ** 2))
        spl = 20 * numpy.log10(rms / 0.00002)  # Compute SPL
        return spl

    def classify(self, feature):
        return feature > 40
