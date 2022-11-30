# import tkinter
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
from multiprocessing.queues import Queue

class Display:
    def __init__(self, label_queue: Queue, period: float = 4, pause: float = 2):
        self.label_queue = label_queue
        self.parent = tk.Tk()
        self.parent.attributes("-fullscreen", True)
        # label displaying fixation cross
        self.label = tk.Label(self.parent, text="+", anchor='center', font=("Arial", 50))
        self.geom = True
        self.labels = []
        self.label.pack(fill="both", expand=True, padx=20, pady=20)
        # Model containing data

        #exit fullscreen after escape is pressed
        self.parent.bind('<Escape>', self.toggle)
        self.period = period
        self.pause = pause

    def refresh_label(self):
        """ refresh the content of the label every four seconds """
        # get random term
        if not self.label_queue.empty():
            term = self.label_queue.get()
            self.labels.append(term)
            if term is not None:
                # display the new term
                self.label.configure(text=term)
                # request tkinter to call self.refresh after 4s (the delay is given in ms)
                self.label.after(1000*self.period, self.refresh_label_pause)
            else:
                self.label.configure(text="Thank you for your participation")

    def refresh_label_pause(self):
        """ refresh the content of the label every four seconds """
        # display fixation cross
        self.label.configure(text='+')
        # request tkinter to call self.refresh after 4s (the delay is given in ms)
        self.label.after(1000*self.pause, self.refresh_label)

    def toggle(self, event):
       self.geom = not self.geom
       self.parent.attributes("-fullscreen",self.geom)



    def training(self, group = False):
        """
        Starts  Visualisations for both groups
        :param group: True if Robot Group; False if Control Group
        :return: None
        """
        if (group):
            pass
        else:
            # Give first term
            self.label.after(1000*self.pause, self.refresh_label)


if __name__ == "__main__":
    lq = Queue()

