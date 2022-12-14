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
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import random


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

    events_used = {
        "start_pick": 2,
        "start_left":4,
        "start_right": 6,

    }

    __n_samples = 100
    __n_samples_per_level = 5
    __min_sample_duration = 1.5

    def __init__(self, save_path, mode= 'debug', training = 'game'):
        self.save_path = save_path
        self.mode = mode
        self.training = training

    @staticmethod
    def rec_process(rec, rev, save_path, mode, subject_id= "test"):
        rec = Recorder(rec, rev, file_name=subject_id, file_path=save_path, debug_mode=mode)
        rec.main_loop(sample_time=1.1)

    @staticmethod
    def standard_view_process(label_queue,event_queue, end_queue, event_dict):
        sv = Display(label_queue,event_queue, end_queue, event_dict)
        sv.training()
        sv.parent.mainloop()

    @staticmethod
    def game_view_process(label_queue, event_queue, prediction_queue, comm_queue, label_dict, event_dict):
        gv = GameView(label_queue, event_queue, prediction_queue,comm_queue, label_dict, event_dict)
        gv.main_loop()

    def game_loop(self, subject_id="test", pron_seconds = 1.1):
        m = Model(self.class_dict, 3, n_samples_per_class=self.__n_samples,
                  n_samples_per_level=self.__n_samples_per_level)

        # instantiate processes

        rec_q = Queue()
        rec_event_queue = Queue()
1
        recorder_process = Process(target=self.rec_process, args=(rec_q, rec_event_queue, self.save_path, self.mode, f"{subject_id}_initial"),
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
        comm_queue_game = Queue()

        game_view_process = Process(target=self.game_view_process, args=(label_queue_game, event_queue_game,
                                                                         prediction_queue_game, comm_queue_game,
                                                                         self.class_dict, self.event_dict),
                                    name="game_view_process")

        # start recorder process and standard view process

        recorder_process.start()
        time.sleep(5)

        standard_view_process.start()

        rec_event_queue.put((self.event_dict["start of recording"], time.time()))

        perm = list(self.class_dict.keys())
        np.random.shuffle(perm)
        for i in perm:

            labelqueue_standard.put(i)
        st_events = []
        raw_data= []
        labels = []
        while len(st_events )<6:
            while not event_queue_standard.empty():
                t = event_queue_standard.get()
                print(t)
                st_events.append(t)
                rec_event_queue.put(t)
                if t[0] in [2,4,6]:
                    while rec_q.empty():
                        # print("Awaiting Recorder Response in Standard")
                        continue
                    data = rec_q.get()
                    print(f"Received data has shape {data.shape}")
                    raw_data.append(np.array(data[:, :int(np.ceil(pron_seconds*500))]))
                    labels.append(t[0]/2-1)




        if len(st_events) >= 6:
            end_queue_standard.put("Peter Maffay")
            print("Closing Standard View")

            standard_view_process.terminate()

        # end recording to get training data for initial classification
        rec_event_queue.put((self.event_dict["change_of_views"], time.time()))



        #data, labels = prep.load(self.save_path, f"{subject_id}_initial", 0, self.events_used)

        #recorder_process.terminate()
        #recorder_process.kill()
        st_data= np.array(raw_data)
        data = prep.filter(st_data, sampling_rate=500)
        data = feature_extraction.extract(data, labels)
        print("did filter and extraction")
        classifier.fit_one(data,labels)

        # print('restarting recorder')
        """rec_q = Queue()
        rec_event_queue = Queue()

        recorder_process = Process(target=self.rec_process, args=(rec_q, rec_event_queue, self.save_path, subject_id),
                                   name="recorder_process_new")
        recorder_process.start()"""

        print('starting game')
        data_collected = data

        game_view_process.start()
        samples_presented = 0

        while samples_presented < self.__n_samples * 3:
            level = m.create_level()
            np.random.shuffle(level)

            amt_dict = { 'left': 0,
                         'right': 0,
                         'pick': 0

            }
            for label in level:

                amt_dict[label] += 1
                if amt_dict[label] == 5:
                    label_queue_game.put((self.class_dict[label], True))
                else:
                    label_queue_game.put((self.class_dict[label], False))

            samples_presented_this_level = 0
            data_collected = list(data_collected)
            last_acc = -1
            while self.__n_samples_per_level * 3 > samples_presented_this_level:
                if event_queue_game.empty():
                    continue
                else:
                    event = event_queue_game.get()
                    print("Sent event to recorder")
                    rec_event_queue.put(event)

                    time_initial = time.time()
                    # await response
                    while rec_q.empty():
                        #print(f"Awaiting Response for {time.time()-time_initial}s")
                        continue
                    data = rec_q.get()

                    filtered_data = prep.filter(data[:, 550:])


                    features = feature_extraction.extract([filtered_data], None)

                    data_collected.extend(features)
                    labels.append(int(event[0]/2-1))

                    prediction = classifier.predict(features)[0]

                    #fake_array = [labels[-1]]*42
                    #fake_array.extend([prediction]*58)

                    #game_pred = random.choice(fake_array)
                    prediction_queue_game.put(prediction)

                    time_done = time.time() - time_initial
                    # print(f"Time needed for classification with 1.5 s of data collected: {time_done}")

                    samples_presented_this_level += 1

            samples_presented += samples_presented_this_level

            if samples_presented < self.__n_samples * 3:
                delta = time.time()
                time.sleep(2)
                comm_queue_game.put(('level_up_start', time.time()))
                data_collected = np.array(data_collected)

                X_train, X_test, y_train, y_test = train_test_split(data_collected, labels, test_size=0.2)

                classifier.fit(X_train, y_train, X_test, y_test)

                predictions = classifier.predict(X_test)

                acc = accuracy_score(y_test, predictions) * 100

                # TODO get some score for this
                if acc > 50:
                    comm_queue_game.put(('speed_up', 0.01))
                if last_acc - acc > 5:
                    comm_queue_game.put(('speed_down', 0.01))

                comm_queue_game.put(('level_up_end', time.time()))
                print(f"Time needed for classification with 1.5 s of data collected: {time.time()-delta}")

        print("Saving Data")
        rec_q.put((self.event_dict['end of recording'], time.time()))





























        









if __name__ == "__main__":

    c = Controller("C:\\Users\\johan\\PycharmProjects\\MA\\data\\", mode='study')
    c.game_loop(subject_id='Test_Tobi')

