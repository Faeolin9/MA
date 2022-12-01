from Feature_Extraction.Wavelet_Decomposition import Wavelet_Decomposition


class FeatureExtractor:

    def __init__(self, mode_id='wav'):
        if mode_id == "wav":
            self.prep = Wavelet_Decomposition()
        else:
            raise NotImplementedError

    def extract(self, data, labels):
        return self.prep.fit_transform(data, labels)
