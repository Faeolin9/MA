import numpy as np


class Model:

    def __init__(self, classes:dict,  n_classes: int, n_samples_per_class:int = 50 ):
        self.classes = classes
        self.sample_list = []
        for i in classes.values():
            ext = [i] * n_samples_per_class
            self.sample_list.extend(ext)

    def draw_random_sample(self):
        val = np.random.choice(self.sample_list)
        self.sample_list.remove(val)
        return val


if __name__ == "__main__":
    print("Peter Maffay")
    m = Model({"pick":  0,
               "left":  1,
               "right": 2
              }, 3)
    print(len(m.sample_list))

    for j in range(5):
        sa = m.draw_random_sample()
        print(sa)


