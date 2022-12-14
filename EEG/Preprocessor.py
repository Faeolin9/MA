from EEG.filter_data import filter_data
import mne
import datetime
import numpy as np


class Preprocessor:

    #TODO ONLINE EPOCHING; OFFLINE EPOCHING

    def __init__(self):
        pass

    def filter(self, raw, sampling_rate = 500):
        silent_data_filtered = filter_data(notch_type="butter_notch", filter_type="maurice",
                                           sampling_frequency=sampling_rate,
                                           overt_data=False, data=raw)
        return silent_data_filtered


    def load(self, path:str, file_name:str, id:int, events_dict:dict):
        fname = path+f"{file_name}_{datetime.date.today()}_{id}.fif"
        raw = mne.io.read_raw_fif(fname=fname, preload=True)
        try:
            channels_to_drop = ['x_dir', 'y_dir', 'z_dir']
            raw.drop_channels(channels_to_drop)
        except:
            pass
        raw_events = raw.info["events"]
        events = [event["list"].tolist() for event in raw_events]
        epochs = mne.Epochs(raw, events, event_id=events_dict, tmin=0, tmax=1.5, baseline=None)


        data = epochs.get_data()
        labels = []
        epochs_to_remove = []

        """event_dict = {"start of recording": 0,
                      "end of recording": 1,
                      "start_pick": 2,
                      "end_pick": 3,
                      "start_left": 4,
                      "end_left": 5,
                      "start_right": 6,
                      "end_right": 7,
                      "change_of_views": 8

                      }"""
        for index in range(len(events)):
            event = events[index]
            label = event[2]
            if label == 2:
                labels.append(0)
            elif label == 4:
                labels.append(1)
            elif label == 6:
                labels.append(2)
            else:
                epochs_to_remove.append(index)

        return data,np.array(labels)
