# import tkinter
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
from multiprocessing.queues import Queue
import time

class Display:
    def __init__(self, label_queue: Queue,event_queue: Queue, end_queue:Queue,
                 event_dict: dict,period: float = 1, pause: float = 2, imagery_duration:float= 1.5):
        self.label_queue = label_queue
        self.parent = tk.Tk()
        self.parent.attributes("-fullscreen", True)
        # label displaying fixation cross
        self.label = tk.Label(self.parent, text="+", anchor='center', font=("Arial", 50))
        self.geom = True
        self.labels = []
        self.label.pack(fill="both", expand=True, padx=20, pady=20)
        # Model containing data

        # exit fullscreen after escape is pressed
        self.parent.bind('<Escape>', self.toggle)
        self.period = period
        self.pause = pause
        self.end_queue = end_queue
        self.event_queue = event_queue
        self.event_dict = event_dict

        self.imagery_duration = imagery_duration

        self.current_event = None


    def refresh_label(self):
        """ refresh the content of the label every four seconds """
        # get random term
        if not self.end_queue.empty():
            self.parent.destroy()

        elif not self.label_queue.empty():
            term = self.label_queue.get()
            self.labels.append(term)
            if term is not None:
                # display the new term
                self.label.configure(text=term)

                self.current_event = self.event_dict[f"start_{term}"]

                #self.event_queue.put((ev, delta_t))

                # request tkinter to call self.refresh after 4s (the delay is given in ms)

                self.label.after(1000*self.period, self.during_imagery)

            else:
                self.label.configure(text="Thank you for your participation")
        else:
            self.label.configure(text = '+')
            self.label.after(1000*self.period, self.refresh_queue_empty)

    def refresh_queue_empty(self):
        self.label.after(1000*self.period, self.refresh_label)


    def during_imagery(self):
        print("presenting")
        self.label.configure(text="+")
        self.label.after(1000,  self.first_blink)



    def first_blink(self):
        self.label.configure(text=" ")
        self.label.after(500, self.imagery_cross)

    def imagery_cross(self):
        delta_t = time.time()
        self.event_queue.put((self.current_event, delta_t))
        self.label.configure(text = '+')
        self.label.after(int(1000*self.imagery_duration), self.second_blink)

    def second_blink(self):
        self.label.configure(text=" ")
        self.label.after(500, self.refresh_label_pause)


    def refresh_label_pause(self):
        """ refresh the content of the label every four seconds """
        # display fixation cross
        delta_t = time.time()
        self.label.configure(text='+')
        ev = self.event_dict[f"end_{self.labels[-1]}"]
        self.event_queue.put((ev, delta_t))
        # request tkinter to call self.refresh after 4s (the delay is given in ms)
        self.label.after(1000*self.pause, self.refresh_label)

    def toggle(self, test):
        """

        :param test: does nothing but is needed due to TKinter UI
        :return:
        """
        self.geom = not self.geom
        self.parent.attributes("-fullscreen",self.geom)



    def training(self, group = False):
        """
        Starts  Visualisations for both groups
        :param group: True if Robot Group; False if Control Group
        :return: None
        """
        if group:
            pass
        else:
            # Give first term
            self.label.after(1000*self.pause, self.refresh_label)


if __name__ == "__main__":
    lq = Queue()

