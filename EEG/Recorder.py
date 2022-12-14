from EEGTools.Recorders.EEG_Recorders.LiveAmpRecorder.liveamp_recorder import LiveAmpRecorder
from EEGTools.Recorders.EEG_Recorders.LiveAmpRecorder.Backends import Sawtooth
from multiprocessing import Queue
import time
import numpy as np
import warnings


class Recorder:

    running = True
    last_got = 0

    def __init__(self, out_queue: Queue, run_queue: Queue, file_name: str = "test",
                 file_path: str = "C:\\Users\\johan\\PycharmProjects\\MA\\data\\" , description: str = None,
                 subject_info: dict = None, debug_mode: bool = True):

        if debug_mode:
            warnings.warn("Debug Mode Activated, not recording real data")
            self.recorder = LiveAmpRecorder(backend=Sawtooth.get_backend())
        else:
            self.recorder = LiveAmpRecorder()
        self.out_queue = out_queue
        self.run_queue = run_queue
        self.file_name = file_name
        self.file_path = file_path
        self.description = description
        self.subject_info = subject_info

    def main_loop(self):

        # connect to recorder
        self.recorder.connect()
        self.recorder.connect_plot()
        # start recording
        self.recorder.start_recording()

        # instantiate main loop
        while self.running:
            # we stop if sth is in the run queue
            if not self.run_queue.empty():
                # run_queue gets events of shape (event_id, timestamp)
                # event 0 means we stop after this execution
                event = self.run_queue.get()

                if event[0] == 0:
                    self.running = False

                delta_t = time.time() - event[1]
                sfreq = self.recorder.get_sfreq()

                sample_dist = np.ceil(sfreq * delta_t)

                self.recorder.set_event(event[0], sample_dist)

            # refresh recorder
            self.recorder.refresh()
            # get new data and update the sample we got last
            data = self.recorder.get_data(start_sample= self.last_got)
            print(data.shape)
            self.last_got += len(data[0])

            # put out data
            self.out_queue.put(data)

            # don't overload recorder with too many refreshes
            time.sleep(.1)

        print("Received closing event, closing Recorder")
        self.recorder.stop_recording()
        self.recorder.disconnect_plot()
        self.recorder.save(file_prefix=self.file_name, path=self.file_path, subject_info=self.subject_info,
                           description=self.description)

        self.recorder.disconnect()







def great_function(out_q, r_q):
    rec = Recorder(out_q, r_q)
    rec.main_loop()



if __name__ == "__main__":
    out_Q  = Queue()
    run_q = Queue()


    from multiprocessing import Process

    p = Process(target=great_function, args=(out_Q, run_q))
    p.start()

    for i in reversed(range(11)):
        print(i)
        time.sleep(1)

    run_q.put((0,0))