from View.game_view import GameView
from multiprocessing import Queue, Process
import random
import time
from View.standard_view import Display
import keyboard
def great_function(la_q, ev_q, pred_q, comm_q, la_dict, event_dict):
    gv = GameView(la_q, ev_q, pred_q,comm_q, la_dict, event_dict)
    gv.main_loop()

def another_great_function(la_q):
    sv = Display(la_q)
    sv.training()
    sv.parent.mainloop()


if __name__ == "__main__":
    import pygame
    print(pygame.font.get_fonts())
    laq = Queue()
    evq = Queue()
    pred_q  = Queue()

    comm_q = Queue()
    t = time.time()
    delta = 0
    c_arr = [0,1,2]
    la_dict = {"pick":  0,
               "left":  1,
               "right": 2
              }

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
    p = Process(target=great_function, args=(laq, evq, pred_q,comm_q , la_dict, event_dict))
    p.start()
    continue_loop = True
    while(continue_loop):
        try:
            if keyboard.is_pressed('End'):
                break
            if keyboard.is_pressed('L'):
                comm_q.put(('level_up_start', time.time()))
                time.sleep(6)


        except:
            pass

        if not evq.empty():
            sol = int(evq.get()[0]/2-1)
            ch_arr = [sol]*50
            ch_arr.extend([random.choice(c_arr)] * 50)
            ch = random.choice(ch_arr)
            a = random.randint(0,1)
            if a == 0:

                print(f"True: {sol} Predicted {ch}")
                time.sleep(.5)
                pred_q.put(ch)
                if ch == sol:
                    comm_q.put(('speed_up', 0.01))
                else:
                    comm_q.put(('speed_down', 0.005))
            else:

                print(f"True: {sol} Predicted {sol}")
                time.sleep(.5)
                pred_q.put(sol)
                comm_q.put(('speed_up', 0.01))



        delta = time.time() - t
        if delta > 0.5:
            ch = random.choice(c_arr)

            laq.put((ch, False))

"""if __name__ == "__main__":
    laq = Queue()

    t = time.time()
    delta = 0
    c_arr = ["pick", "left", "right"]


    p = Process(target=another_great_function, args=(laq,))
    p.start()
    for counter in range(5):
        ch = random.choice(c_arr)
        laq.put(ch)
"""