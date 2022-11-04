from View.game_view import GameView
from multiprocessing import Queue, Process
import random
import time

def great_function(la_q, ev_q, pred_q):
    gv = GameView(la_q, ev_q, pred_q)
    gv.main_loop()


if __name__ == "__main__":
    laq = Queue()
    evq = Queue()
    pred_q  = Queue()

    t = time.time()
    delta = 0
    c_arr = [0,1,2]

    p = Process( target=great_function, args=(laq, evq, pred_q))
    p.start()

    while(True):
        if not evq.empty():

            ch = random.choice(c_arr)

            print(f"True: {evq.get()} Predicted {ch}")
            time.sleep(.5)
            pred_q.put(ch)
        delta = time.time() - t
        if delta > 0.5:
            ch = random.choice(c_arr)
            #print("Put ", ch)
            laq.put(ch)
