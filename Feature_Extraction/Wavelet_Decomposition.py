from pywt import wavedec
import pywt
import numpy as np


class Wavelet_Decomposition:
    def __init__(self,  max_level=4, m_wavelet='bior2.2'):
        self.max_level = max_level
        self.m_wavelet = m_wavelet


    def parse(self):
        pass

    def decompose(self, data, max_level = 4, m_wavelet = 'bior2.2'):

        return wavedec(data= data, wavelet=m_wavelet,level= max_level)

    def set_params(self, max_level, mwavelet):
        self.max_level = max_level
        self.m_wavelet = mwavelet

    def from_dict(self, src):
        print(src)
        self.m_wavelet = src['mwavelet']
        self.max_level = src['max_level']



    def feature_vector(self, data, max_level=4, m_wavelet='bior2.2'):

        output = []
        for sample in data:
            feature_vector = []
            wav = self.decompose(sample, max_level= max_level, m_wavelet=m_wavelet)
            level_helper = max_level
            for level in wav:
                feature_vector.append(level.max())
                feature_vector.append(level.min())
                feature_vector.append(np.average(level))
                feature_vector.append(np.std(level))
                feature_vector.append(self.energy(level, level_helper))
                level_helper -= 1
            output.append(np.array(feature_vector))
        #print(len(output))
        return np.array(output)

    def energy(self, coeffs, k):
        k = min(len(coeffs), k)
        if coeffs[-k] is int or coeffs[-k].dtype == np.float64:
            return np.sqrt(np.sum(np.array(coeffs[-k]) ** 2)) / len([coeffs[-k]])

        return np.sqrt(np.sum(np.array(coeffs[-k]) ** 2)) / len(coeffs[-k])

    def fit_transform(self, data, labels=4):
        return self.feature_vector(data, max_level=self.max_level, m_wavelet=self.m_wavelet)

    def fit(self, data, labels):
        """
            Dummy method allowing use of sklearn's Pipeline method for tuning params
        """
        return

    def transform(self, data):
        return self.fit_transform(data)
