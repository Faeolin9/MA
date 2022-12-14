from Audio.SimpleVAD import SimpleVAD
from Audio.LSLRecorder import LSLRecorder
from View.standard_view import Display
from multiprocessing import  Process, Queue
import time
import numpy as np

class ReactionTimeTest:


    event_dict = {"start of recording": 0,
                  "end of recording": 1,
                  "start_pick": 2,
                  "end_pick": 3,
                  "start_left": 4,
                  "end_left": 5,
                  "start_right": 6,
                  "end_right": 7,
                  "change_of_views": 8

                  }

    class_dict = {"pick": 0,
                  "left": 1,
                  "right": 2
                  }

    @staticmethod
    def standard_view_process(label_queue, event_queue, end_queue, event_dict):
        sv = Display(label_queue, event_queue, end_queue, event_dict)
        sv.training()
        sv.parent.mainloop()


    @staticmethod
    def recorder_process(comm_queue: Queue, data_queue: Queue):
        rec = LSLRecorder()
        rec.connect()
        rec.start_recording()
        t_last = time.time()

        vad = SimpleVAD()

        running = True
        while running:
            while comm_queue.empty():
                if time.time() -t_last < 0.5:
                    continue
                else:
                    t_last = time.time()
                    rec.refresh()
                    #print("Comm_queue Empty")
                    #data_queue.put(rec.get_data(start_sample=-0.5 * rec.get_sfreq()))
            ev = comm_queue.get()
            #print(f"Got Event in Recorder : {ev}")

            if ev[0] == 1:
                running = False
            else:
                t_now = time.time()
                t_then = ev[1]

                delta_t = t_now - t_then

                while delta_t < 0.5:
                    t_now = time.time()
                    delta_t = t_now - t_then

                detected = False
                first_detection = True
                stopped_detecting = False
                time_detected = 0
                time_first_detection = 0

                while not detected and not stopped_detecting:

                    rec.refresh()

                    sample_dist = np.floor(delta_t * rec.get_sfreq())
                    data = rec.get_data(start_sample=-sample_dist)
                    if not detected:
                        detected = vad.vad(data, rec.get_sfreq())
                    else:
                        stopped_detecting = not vad.vad(data, rec.get_sfreq())
                    time.sleep(.5)
                    sample_dist += np.floor(0.5 * rec.get_sfreq())

                    if detected and first_detection:
                        first_detection = False
                        time_first_detection = time.time()
                        time_detected = time_first_detection - t_then
                        print(time_detected)
                        data_queue.put(time_detected)

                time_stopped = time.time() - time_first_detection
                data_queue.put(time_stopped)




















    def __init__(self, n_trials= 10):


        self.n_trials = n_trials





    def main_loop(self):

        trials = 0

        comm_q = Queue()
        data_q = Queue()

        rec_p = Process(target=self.recorder_process, args=(comm_q, data_q))
        rec_p.start()
        time.sleep(5)

        label_queue = Queue()
        event_queue = Queue()
        end_queue = Queue()

        view_p = Process(target=self.standard_view_process, args=(label_queue, event_queue,end_queue, self.event_dict))
        view_p.start()
        k = self.class_dict.keys()
        trial_list = []
        reaction_times = []
        pronounciation_times = []
        for i in k:
            trial_list.extend([i]*self.n_trials)

        np.random.shuffle(trial_list)

        for i in trial_list:
            label_queue.put(i)
            trials += 1
            waiting = True
            ev = None
            while waiting:
                while event_queue.empty():
                    continue

                ev = event_queue.get()
                print(ev)

                if ev[0] in [2,4,6]:
                    waiting = False

            comm_q.put(ev)



            while data_q.empty():
                continue
            t = data_q.get()
            reaction_times.append(t)

            while data_q.empty():
                continue
            t = data_q.get()
            pronounciation_times.append(t)

        comm_q.put((1, time.time()))
        end_queue.put("Peter Maffay")
        print(f"Times needed reaction: {np.round(np.mean(reaction_times), 3)} \n pronounciation: {np.round(np.mean(pronounciation_times), 3)}")






if __name__ == "__main__":
    test = ReactionTimeTest()
    test.main_loop()