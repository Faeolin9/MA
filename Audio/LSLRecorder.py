import os
import time
import matplotlib.pyplot
import numpy
from pylsl import StreamInlet, resolve_stream
import matplotlib
import threading
from threading import Condition
matplotlib.use("TkAgg")
from itertools import chain


class LSLRecorder:

    def __init__(self):
        self.inlet = None
        self.recording_thread = None
        self.recording = False
        self.__recorded_samples = []
        self.__recorded_timestamps = []
        self._condition = Condition()

        self.samples = []
        self.timestamps = []
        self.events = []

    def connect(self):
        # first resolve an EEG stream on the lab network
        print("looking for an EEG stream...")
        streams = resolve_stream()
        stream = streams[0]
        name = stream.source_id()
        #if name != "Mikrofon (SC420 USB Microphone)":
        #    raise ValueError(f"Expected SC420 USB mic got {name}")
        if stream.nominal_srate() != 48000:
            raise ValueError(f"Expected sfreq 48000, got {stream.nominal_srate()}")

        # create a new inlet to read from the stream
        self.inlet = StreamInlet(streams[0])

    def disconnect(self):
        self.inlet = None

    def start_recording(self):
        self.recording = True
        self.recording_thread = threading.Thread(target=self._recording_loop, name="Recording Thread")
        self.recording_thread.start()

    def stop_recording(self):
        self.recording = False
        self.recording_thread.join()

    def refresh(self):
        with self._condition:
            samples = self.__recorded_samples
            self.__recorded_samples = []
            timestamps = self.__recorded_timestamps
            self.__recorded_timestamps = []
        self.timestamps.extend(chain.from_iterable(timestamps))
        self.samples.extend(chain.from_iterable(samples))

    def get_sfreq(self):
        info = self.inlet.info()
        return info.nominal_srate()

    def _recording_loop(self):
        while self.recording:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            chunk, timestamps = self.inlet.pull_chunk()

            with self._condition:
                self.__recorded_timestamps.append(timestamps)
                self.__recorded_samples.append(chunk)
                time.sleep(0.01)

    def save(self, filepath, file_prefix):
        samples = numpy.array(self.samples)
        numpy.save(os.path.join(filepath, f"{file_prefix}_audio"), samples)
        audio = numpy.array(self.timestamps)
        numpy.save(os.path.join(filepath, f"{file_prefix}_timestamps"), audio)
        events = numpy.array(self.events)
        numpy.save(os.path.join(filepath, f"{file_prefix}_events"), events)

    def set_event(self, id, offset):
        self.events.append((id, 0, len(self.samples)-offset))

    def get_data(self, start_sample=0, end_sample=None):
        if end_sample is None:
            end_sample = len(self.samples)
        while end_sample < 0:
            end_sample += len(self.samples)
        while start_sample < 0:
            start_sample += len(self.samples)

        start_sample = int(start_sample)
        end_sample = int(end_sample)

        return numpy.array(self.samples[start_sample:end_sample])

    # Deprecated
    @staticmethod
    def main():
        # first resolve an EEG stream on the lab network
        print("looking for an audio stream...")
        streams = resolve_stream()

        # create a new inlet to read from the stream
        inlet = StreamInlet(streams[0])

        timestamps = []
        samples = []
        a = time.time()
        while True:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            sample, timestamp = inlet.pull_sample()
            timestamps.append(timestamp)
            samples.append(sample)
            if time.time() > a + 5:
                break
        timestamps = numpy.array(timestamps)
        samples = numpy.array(samples)
        print(numpy.sum((timestamps - numpy.roll(timestamps, 1))[1:]))
        matplotlib.pyplot.plot((timestamps - numpy.roll(timestamps, 1))[1:])
        #matplotlib.pyplot.plot(samples - numpy.mean(samples))
        matplotlib.pyplot.show(block=True)


def f(b):
    while True:
        print(b.recv())
        b.send("B")
    print("hey")


if __name__ == "__main__":
    from multiprocessing import Pipe, Process
    a, b = Pipe()

    prc = Process(target=f, args=(b,))
    prc.start()
    while True:
        a.send("A")
        print(b.recv())
