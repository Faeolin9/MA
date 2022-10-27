# import the pygame module, so you can use it
import pygame
from multiprocessing import Queue, Process
import time
from View.Circle import Circle


class GameView:

    __CIRCLECOLOUR = (0,0,139)
    __PROGRAM_START = time.time()
    __last_tick_update = time.time()
    __target_box = None
    __last_frame_update = __last_tick_update

    def __init__(self, label_queue : Queue, out_pueue : Queue, pred_queue : Queue,
                 box_size: float= 0.85, speed: float = 0.1, mimimum_distance_between: float = 0.33,
                 fps: int = 60, tps: int = 60):

        """
        :param label_queue: A queue in which the next label to display is handed to the view
        :param out_pueue: A queue to give timestamps at which the prediction actually happend for what label
        :param pred_queue: A queue to feed the view the classifier's predictions
        :param box_size: At what point of the image the target box is supposed to appear
        :param speed: How fast (window_size per second) the target values are supposed to appear
        :param mimimum_distance_between: The minimum distance to insert the next target value, must be between 0 and 1
        :param fps: Frame updates per second
        :param tps: Game updates per second

        """

        if mimimum_distance_between < 0 or mimimum_distance_between > 1:
            raise ValueError(f"minimum_distance_between must be between 0 and 1. Got {mimimum_distance_between}")

        self.speed = speed
        self.min_distance = mimimum_distance_between
        self.fullscreen = False

        self.__existing_circles = []

        self.__last_label = None

        self.__queue = label_queue
        self.__out_queue = out_pueue
        self.__event_queue = pred_queue

        self.__FPS = fps
        self.__TPS = tps

        # initialize the pygame module
        pygame.init()
        # load and set the logo
        logo = pygame.image.load("C:\\Users\\johan\\PycharmProjects\\MA\\View\\maffay.png")
        pygame.display.set_icon(logo)
        pygame.display.set_caption("EEG Hero")

        # create a surface on screen that has the size of 240 x 180
        self.__screen = pygame.display.set_mode((1200, 900))

        self.left = self.__screen.get_width() * 0.33 * 0.5

        self.center = (self.__screen.get_width() * 0.33 + self.__screen.get_width() *0.67) * 0.5

        self.right = (self.__screen.get_width() * 0.67 ) +self.__screen.get_width() * 0.33 * 0.5

        self.__circle_width = self.__screen.get_width() * 0.33 * 0.1

        self.box_size = box_size
        self.__update_screen()

    def __draw_existing_circles(self):
        for circle in self.__existing_circles:
            print(circle.colour)
            pygame.draw.circle(self.__screen, circle.colour, (self.label_to_position(circle.x),
                                                                    circle.y * self.__screen.get_height()),
                               self.__circle_width)
            if circle.in_target_region:
                self.__encircle(circle)

    def __recompute(self):
        self.left = self.__screen.get_width() * 0.33 * 0.5

        self.center = (self.__screen.get_width() * 0.33 + self.__screen.get_width() * 0.67) * 0.5

        self.right = (self.__screen.get_width() * 0.67 )  +self.__screen.get_width() * 0.33 * 0.5

        self.__circle_width = self.__screen.get_width() * 0.33 * 0.1


    def __update_screen(self):
        self.__recompute()
        self.__screen.fill((211, 211, 211))
        self.__draw_lines()
        self.__draw_target_box()
        self.__draw_existing_circles()

        pygame.display.flip()

    def label_to_position(self, label):
        #TODO Solve this using passable dict
        if label == 0:
            return self.center
        elif label == 1:
            return self.left
        elif label == 2:
            return self.right

    def __enter_new_label(self):

        if self.__queue.empty():
            return

        elif self.__last_label is None:

            label = self.__queue.get()

            self.__draw_new_circle(label)

        else:

            last_circle = self.__existing_circles[self.__last_label]
            delta = last_circle.y

            if delta <  self.min_distance:

                return

            else:
                label = self.__queue.get()

                self.__draw_new_circle(label)

    def __draw_new_circle(self, label):
        lab_pos = self.label_to_position(label)

        pygame.draw.circle(self.__screen, self.__CIRCLECOLOUR, (lab_pos, 0), self.__circle_width)

        self.__existing_circles.append(Circle(label, 0, True, circle_colour=self.__CIRCLECOLOUR))
        self.__last_label = len(self.__existing_circles) - 1
        self.__update_screen()

    def main_loop(self):
        # define a variable to control the main loop
        running = True

        # main loop
        while running:
            new_time = time.time()
            # event handling, gets all event from the event queue
            for event in pygame.event.get():
                # only do something if the event is of type QUIT
                if event.type == pygame.QUIT:
                    # change the value to False, to exit the main loop
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.fullscreen:

                            pygame.display.set_mode(flags=pygame.FULLSCREEN)
                            self.__update_screen()

                        else:

                            pygame.display.set_mode((1200, 900))

                            self.__update_screen()
                        self.fullscreen = not self.fullscreen

                    if event.key == pygame.K_END:
                       pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
            if new_time - self.__PROGRAM_START < 2:
                continue
            if (new_time - self.__last_tick_update) > (1/self.__TPS):
                self.__enter_new_label()
                self.__check_for_prediction()
                self.__move_circle_positions()

                self.__check_circle_collision()
                self.__last_tick_update = new_time
            if (new_time - self.__last_frame_update) > (1/self.__FPS):
                self.__update_screen()
                #print(f"Updated at diff {new_time-self.__last_frame_update} should be {1/self.__FPS}")
                self.__last_frame_update = new_time

    def __check_for_prediction(self):
        if self.__event_queue.empty():
            return
        else:

            pred = self.__event_queue.get()
            circle = self.__existing_circles[0]

            if pred == circle.x:
                circle.set_colour((0,255, 0))

                circle.predicted = True

            else:
                circle.set_colour((255, 0, 0))

                circle.predicted = True

    def __move_circle_positions(self):

        for circle in self.__existing_circles:
            circle_y_pos = circle.y
            circle_y_pos += self.speed * (1/self.__TPS)

            if not circle.predicted:
                circle.y = circle_y_pos

    def __encircle(self, circle):
        pygame.draw.circle(self.__screen, (0,255,0),
                           (self.label_to_position(circle.x), circle.y * self.__screen.get_height()),
                           self.__circle_width + 0.005 * 0.33 * self.__screen.get_width(), width=3)
        if circle.first_encircelment:
            self.__out_queue.put((circle.x, time.time(), 'in'))
            circle.first_encircelment = False

    def __draw_lines(self):

        pygame.draw.line(self.__screen, (0,0,0), (0.33 * self.__screen.get_width(),0),
                         (0.33* self.__screen.get_width(),self.box_size *self.__screen.get_height()))
        pygame.draw.line(self.__screen, (0, 0, 0), (0.67 * self.__screen.get_width(), 0),
                         (0.67 * self.__screen.get_width(), self.box_size * self.__screen.get_height()))

    def __draw_target_box(self):
        self.__target_box = pygame.Rect(0, self.__screen.get_height()* self.box_size,
                                        self.__screen.get_width(), self.__screen.get_height() * (1-self.box_size))
        pygame.draw.rect(self.__screen, (0,0,0), self.__target_box,
                         width=3)

    def __check_circle_collision(self):
        for circle in self.__existing_circles:
            circle_x = self.label_to_position(circle.x)
            circle_y = (circle.y) * self.__screen.get_height()

            circle.in_target_region  = self.__target_box.collidepoint(circle_x, circle_y)



    def put_label(self, label):
        self.__queue.put(label)

    def put_predictions(self, prediction):
        self.__event_queue.put(prediction)


    def get_out_event(self):
        if self.__out_queue.empty():
            return None
        else:
            return self.__out_queue.get()

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    laq = Queue()
    evq = Queue()
    pred_q = Queue()
    gv = GameView(laq, evq, pred_q)
    gv.put_label(0)
    gv.put_label(1)
    #p = Process(target=gv.main_loop)
    gv.put_predictions(1)

    gv.main_loop()