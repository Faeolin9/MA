from EEG.filter_data import filter_data


class Preprocessor:

    #TODO ONLINE EPOCHING; OFFLINE EPOCHING

    def __init__(self):
        pass

    def filter(self, raw, sampling_rate = 500):
        silent_data_filtered = filter_data(notch_type="butter_notch", filter_type="maurice",
                                           sampling_frequency=sampling_rate,
                                           overt_data=False, data=raw)
        return silent_data_filtered
