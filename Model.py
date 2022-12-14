import numpy as np


class Model:

    def __init__(self, classes:dict,  n_classes: int, n_samples_per_class:int = 100, n_samples_per_level:int = 5):
        self.classes = classes
        self.n_samples_level = n_samples_per_level
        self.sample_list = []
        for i in classes.keys():
            ext = [i] * n_samples_per_level
            self.sample_list.extend(ext)

    def create_level(self):
        return self.sample_list




if __name__ == "__main__":
    print("Peter Maffay")
    m = Model({"pick":  0,
               "left":  1,
               "right": 2
              }, 3)
    print(len(m.sample_list))

