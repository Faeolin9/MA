from EEG.Recorder import Recorder

from multiprocessing import Queue, Process
from EEG.Preprocessor import Preprocessor
from Feature_Extraction.Feature_Extractor import FeatureExtractor
from Classifier.Classfier_Interface import ClassifierInterface
from View.standard_view import Display
from View.game_view import GameView
from Model import Model
import time
import numpy as np


class Controller:
    class_dict = {"pick": 0,
                  "left": 1,
                  "right": 2
                }

    event_dict = { "start of recording" : 0,
                   "end of recording": 1,
                   "start_pick": 2,
                   "end_pick": 3,
                   "start_left":4,
                   "end_left": 5,
                   "start_right":6,
                   "end_right" : 7,
                   "change_of_views": 8


    }

    def __init__(self, save_path, mode= 'debug', training = 'game'):
        self.save_path = save_path
        self.mode = mode
        self.training = training

    @staticmethod
    def rec_process(rec, rev, save_path, subject_id= "test"):
        rec = Recorder(rec, rev, file_name=subject_id, file_path=save_path)
        rec.main_loop()

    @staticmethod
    def standard_view_process(label_queue,event_queue, end_queue, event_dict):
        sv = Display(label_queue,event_queue, end_queue, event_dict)
        sv.training()
        sv.parent.mainloop()

    @staticmethod
    def game_view_process(label_queue, event_queue, prediction_queue, label_dict):
        gv = GameView(label_queue, event_queue, prediction_queue, label_dict)
        gv.main_loop()

    def game_loop(self, subject_id="test"):
        m = Model(self.class_dict, 3, n_samples_per_class=49)

        # instantiate processes

        rec_q = Queue()
        rec_event_queue = Queue()

        recorder_process = Process(target=self.rec_process, args=(rec_q, rec_event_queue, self.save_path, subject_id),
                                   name="recorder_process")

        classifier = ClassifierInterface(sid=subject_id)
        feature_extraction = FeatureExtractor()
        prep = Preprocessor()

        labelqueue_standard = Queue()
        end_queue_standard = Queue()
        event_queue_standard = Queue()

        standard_view_process = Process(target=self.standard_view_process, args=(labelqueue_standard,
                                                                                 event_queue_standard,
                                                                                 end_queue_standard,
                                                                                 self.event_dict),
                                        name="standard_view_process")

        label_queue_game = Queue()
        event_queue_game = Queue()
        prediction_queue_game = Queue()

        game_view_process = Process(target=self.game_view_process, args=(label_queue_game, event_queue_game,
                                                                         prediction_queue_game, self.class_dict),
                                    name="game_view_process")

        # start recorder process and standard view process

        standard_view_process.start()

        recorder_process.start()

        rec_event_queue.put((self.event_dict["start of recording"], time.time()))

        perm = list(self.class_dict.keys())
        np.random.shuffle(perm)
        for i in perm:

            labelqueue_standard.put(i)
        st_events = []
        while not event_queue_standard.empty():
            t = event_queue_standard.get()
            print(t)
            st_events.append(t)
        if len(st_events) >= 6:
            end_queue_standard.put("Peter Maffay")
            print("Closing Standard View")

        










if __name__ == "__main__":

    c = Controller(".\\data\\")
    c.game_loop()

