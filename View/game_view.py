# import the pygame module, so you can use it
import pygame
from multiprocessing import Queue
import time
from View.Circle import Circle
import numpy as np


class GameView:

    __CIRCLECOLOUR = (0,0,139)
    __PROGRAM_START = time.time()
    __last_tick_update = time.time()
    __target_box = None
    __last_frame_update = __last_tick_update
    __combo = 1
    __combo_state = 0
    __max_combo_this_level = 1

    __golds_collected_this_level = 0
    __gold_colour = (255, 215, 0)
    __gold_left = False
    __gold_right = False
    __gold_middle = False

    #Todo Statistics are currently hardcoded for 3 lane case, abstract this for extension to 5
    __correct_left = 0
    __total_left = 0
    __correct_right = 0
    __total_right = 0
    __correct_center =0
    __total_center = 0

    points = 0
    pos_pred_value = 100
    neg_pred_value = -10

    def __init__(self, label_queue : Queue, out_pueue : Queue, pred_queue : Queue, comm_queue: Queue, labels: dict,
                 events: dict,  box_size: float= 0.85, speed: float = 0.2, mimimum_distance_between: float = 0.33,
                 fps: int = 60, tps: int = 60, amt_golds: int = 3):

        """
        :param label_queue: A queue in which the next label to display is handed to the view
        :param out_pueue: A queue to give timestamps at which the prediction actually happend for what label
        :param pred_queue: A queue to feed the view the classifier's predictions
        :param comm_queue: A queue to transfer communication on speed, still running,...
        :param labels: A dict of form (label_name, label_value), as (key, value)
        :param events: A dict of form (event_name, event_value), as (key, value)
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
        self.comm_queue = comm_queue

        self.__label_dict = labels
        self.event_dict = events

        self.__FPS = fps
        self.__TPS = tps

        self.__level = 1
        self.__amt_golds = amt_golds


        # initialize the pygame module
        pygame.init()
        # load and set the logo
        logo = pygame.image.load("C:\\Users\\johan\\PycharmProjects\\MA\\View\\maffay.png")
        pygame.display.set_icon(logo)
        pygame.display.set_caption("EEG Hero")

        self.__label_font = pygame.font.SysFont(None, 50)
        self.__point_font = pygame.font.SysFont(None, 35) # initially 18
        self.__level_font = pygame.font.SysFont(None, 100)

        # create a surface on screen that has the size of 240 x 180
        self.__screen = pygame.display.set_mode((1200, 900))

        self.left = self.__screen.get_width() * 0.33 * 0.5

        self.center = (self.__screen.get_width() * 0.33 + self.__screen.get_width() * 0.67) * 0.5

        self.right = (self.__screen.get_width() * 0.67 ) + self.__screen.get_width() * 0.33 * 0.5

        self.__circle_width = self.__screen.get_width() * 0.33 * 0.1
        self.level_state = 0
        self.box_size = box_size
        self.__upper_box = - self.__screen.get_height()*0.1

        self.__update_screen(True)




    def __level_up(self):
        self.__existing_circles = []
        self.__last_label=None
        self.__combo = 1

        while not self.__event_queue.empty():
            self.__event_queue.get()

        helper = self.__level
        img = self.__level_font.render(f"Level {helper}", True, (255, 255, 255))

        self.__level += 1

        self.__screen.blit(img, (self.__screen.get_width() * 0.5 - img.get_width() * 0.5,
                                 (self.__screen.get_height() * 0.5 - img.get_height() * 0.5)))




        #time.sleep(3)











    def __draw_existing_circles(self):
        i = 0
        circles_to_remove = []
        for circle in self.__existing_circles:

            pygame.draw.circle(self.__screen, circle.colour, (self.label_to_position(circle.x),
                               circle.y * self.__screen.get_height()), self.__circle_width)
            if circle.in_target_region and not circle.predicted:
                self.__encircle(circle)

            if circle.predicted:
                if circle.redundant > 20:
                    circles_to_remove.append(i)
                else:
                    circle.redundant += 1

                    if circle.value > 0:
                        text = f"+{circle.value}"
                    else:
                        text = str(circle.value)
                    img = self.__point_font.render(text, True, circle.colour)
                    #print(f"blitting at point "
                    #      f"{(self.label_to_position(circle.x) + self.__circle_width,circle.y * self.__screen.get_height()+ self.__circle_width)}")

                    self.__screen.blit(img, (self.label_to_position(circle.x) + self.__circle_width, circle.y *
                                             self.__screen.get_height() - self.__circle_width))

            i+=1
        for index in reversed(circles_to_remove):
            self.__existing_circles.pop(index)
            self.__last_label -=1
            if len(self.__existing_circles)  == 0:
                self.__last_label = None

    def __recompute(self):
        self.left = self.__screen.get_width() * 0.33 * 0.5

        self.center = (self.__screen.get_width() * 0.33 + self.__screen.get_width() * 0.67) * 0.5

        self.right = (self.__screen.get_width() * 0.67) + self.__screen.get_width() * 0.33 * 0.5

        self.__circle_width = self.__screen.get_width() * 0.33 * 0.1

    def __update_screen(self, level_up:bool =False):
        self.__recompute()

        self.__screen.fill((0,0,10)) #(211, 211, 211)
        self.__draw_lines()
        self.__draw_target_box()
        if not level_up:
            self.__draw_existing_circles()
        else:
            if self.level_state % 2 == 0:
                self.__level_up()

            elif self.level_state % 2 == 1:
                self.__depict_level_up()

        self.__print_points_and_labels()

        pygame.display.flip()
        if level_up:
            time.sleep(1)
            if self.level_state % 2 == 1:
                time.sleep(9)
            if self.level_state != 0:
                self.level_state += 1
            else:
                self.level_state += 2
        #self.__level_up()

    def __depict_level_up(self):
        img = self.__level_font.render(f"Statistics", True, (255, 255, 255))

        self.__screen.blit(img, (self.__screen.get_width() * 0.5 - img.get_width() * 0.5,
                                 (self.__screen.get_height() * 0.1 - img.get_height() * 0.5)))

        img = self.__label_font.render("Correct Classfications", True, (255,255,255))
        self.__screen.blit(img, (self.__screen.get_width() * 0.5 - img.get_width() * 0.5,
                                 (self.__screen.get_height() * 0.2 - img.get_height() * 0.5)))

        if self.__total_left == 0:
            left_text = 'N/A'
        else:
            left_text = f'{np.round((self.__correct_left / self.__total_left) * 100, decimals=2)}%'
        img_left = self.__point_font.render(left_text, True, (255, 255, 255))
        self.__screen.blit(img_left, (self.left - img_left.get_width() * 0.5,
                                 (self.__screen.get_height() * 0.25 - img.get_height() * 0.5)))

        if self.__total_center == 0:
            center_text = 'N/A'
        else:
            center_text = f'{np.round((self.__correct_center / self.__total_center) * 100, decimals=2)}%'
        img_center = self.__point_font.render(center_text, True, (255, 255, 255))
        self.__screen.blit(img_center, (self.center - img_center.get_width() * 0.5,
                                      (self.__screen.get_height() * 0.25 - img.get_height() * 0.5)))

        if self.__total_right == 0:
            right_text = 'N/A'
        else:
            right_text = f'{np.round((self.__correct_right / self.__total_right) * 100, decimals=2)}%'
        img_right = self.__point_font.render(right_text, True, (255, 255, 255))
        self.__screen.blit(img_right, (self.right - img_right.get_width()*0.5,
                                      (self.__screen.get_height() * 0.25 - img.get_height() * 0.5)))
        pygame.draw.line(self.__screen, (255,255,255), (0, self.__screen.get_height() * 0.275 ),
                         (self.__screen.get_width(),
                          self.__screen.get_height() *0.275))

        img_combo = self.__label_font.render(f"Highest Combo: x{self.__max_combo_this_level}", True, (255, 255, 255))
        self.__screen.blit(img_combo, (self.__screen.get_width() * 0.5 - img_combo.get_width() * 0.5,
                                 (self.__screen.get_height() * 0.35 - img_combo.get_height() * 0.5)))

        img_golds = self.__label_font.render(f"Golden Circles", True, (255,255,255))
        self.__screen.blit(img_golds, (self.__screen.get_width() * 0.5 - img_golds.get_width() * 0.5,
                                       (self.__screen.get_height() * 0.45 - img_golds.get_height() * 0.5)))
        img_golds = self.__label_font.render(f"Collected", True, (255, 255, 255))
        self.__screen.blit(img_golds, (self.__screen.get_width() * 0.5 - img_golds.get_width() * 0.5,
                                       (self.__screen.get_height() * 0.5 - img_golds.get_height() * 0.5)))

        img_golds_col = self.__label_font.render(f"{self.__golds_collected_this_level}/{self.__amt_golds}", True, (255, 255, 255))
        self.__screen.blit(img_golds_col, (self.__screen.get_width() * 0.5 - img_golds_col.get_width() * 0.5,
                                       (self.__screen.get_height() * 0.55 - img_golds_col.get_height() * 0.5)))

        img_good_job = self.__level_font.render("Good Job!", True, (255,255,255))
        self.__screen.blit(img_good_job, (self.__screen.get_width() * 0.5 - img_good_job.get_width() * 0.5,
                                       (self.__screen.get_height() * 0.775 - img_good_job.get_height() * 0.5)))

        self.__golds_collected_this_level = 0
        self.__max_combo_this_level = 1



    def label_to_position(self, label):
        # TODO Solve this using label dict
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

            self.__draw_new_circle(label[0], label[1])

        else:

            last_circle = self.__existing_circles[self.__last_label]
            delta = last_circle.y

            if delta < self.min_distance:

                return

            else:
                label = self.__queue.get()

                self.__draw_new_circle(label[0], golden=label[1])

    def __draw_new_circle(self, label, golden = False):

        lab_pos = self.label_to_position(label)

        if not golden:
            pygame.draw.circle(self.__screen, self.__CIRCLECOLOUR, (lab_pos, 0), self.__circle_width)
            self.__existing_circles.append(Circle(label, 0, True, circle_colour=self.__CIRCLECOLOUR))
        else:
            pygame.draw.circle(self.__screen, self.__gold_colour, (lab_pos, 0), self.__circle_width)
            self.__existing_circles.append(Circle(label, 0, True, circle_colour=self.__gold_colour))



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
                self.__last_frame_update = new_time
            while not self.comm_queue.empty():
                ev = self.comm_queue.get()
                if ev[0] == 'speed_up':
                    if self.speed < 0.33:
                        self.speed += ev[1]
                        print('speed_at: ', self.speed)
                elif ev[0] == 'speed_down':
                    if self.speed >= 0.1:
                        self.speed -= ev[1]
                elif ev[0] == 'min_distance_up':
                    self.min_distance += ev[1]
                elif ev[0] == 'min_distance_down':
                    self.min_distance -= ev[1]
                elif ev[0] == 'level_up_start':
                    print('Leveling up')
                    self.__update_screen(level_up=True)
                    self.__update_screen(level_up=True)

    def __do_stats(self, label_pos, correct):
        if correct:
            if label_pos == self.left:
                self.__correct_left += 1
                self.__total_left += 1
            elif label_pos == self.center:
                self.__correct_center += 1
                self.__total_center +=1
            else:
                self.__correct_right += 1
                self.__total_right += 1
        else:
            if label_pos == self.left:

                self.__total_left += 1
            elif label_pos == self.center:
                self.__total_center += 1

            else:
                self.__total_right += 1

    def __check_for_prediction(self):
        if self.__event_queue.empty():
            return
        else:

            pred = self.__event_queue.get()
            circle = self.__existing_circles[0]
            for i in self.__existing_circles:
                circle = i
                if not circle.predicted:
                    break

            if pred == circle.x:
                if circle.get_colour_without_alpha() == self.__gold_colour:
                    is_golden = 1
                    self.__golds_collected_this_level += 1
                else:
                    is_golden = 1/3
                circle.set_colour((0,255, 0))

                circle.predicted = True
                print (f"Combo_state {self.__combo_state}")
                self.__combo_state += 1
                if self.__combo_state % 2 == 0 and self.__combo_state != 0 and self.__combo < 2:
                    self.__combo += 0.2
                    self.__combo = np.round(self.__combo, decimals = 1)
                    if self.__combo > self.__max_combo_this_level:
                        self.__max_combo_this_level = self.__combo

                add  = self.pos_pred_value * self.__combo * 3 * is_golden



                self.points += add
                circle.value += add

                self.__do_stats(self.label_to_position(pred), True)

            else:
                circle.set_colour((255, 0, 0))
                # circle.x = pred
                self.__combo_state = 0
                self.__combo = 1
                circle.predicted = True

                self.points += self.neg_pred_value
                circle.value += self.neg_pred_value
                self.__do_stats(self.label_to_position(circle.x), False)

    def __move_circle_positions(self):

        for circle in self.__existing_circles:
            circle_y_pos = circle.y
            circle_y_pos += self.speed * (1/self.__TPS)

            if not circle.predicted:
                circle.y = circle_y_pos

    def reverse_label(self,label):
        for tr_label,key in enumerate(self.__label_dict):
            if tr_label == label:
                return key
        raise ValueError

    def __encircle(self, circle):
        pygame.draw.circle(self.__screen, (0, 255, 0),
                           (self.label_to_position(circle.x), circle.y * self.__screen.get_height()),
                           self.__circle_width + 0.005 * 0.33 * self.__screen.get_width(), width=3)
        if circle.first_encircelment:
            event_text = "start_" + self.reverse_label(circle.x)
            event = self.event_dict[event_text]

            self.__out_queue.put((event, time.time()))
            circle.first_encircelment = False

    def __draw_lines(self):

        line_colour = (255,255,255)
        # upper lines
        pygame.draw.line(self.__screen,line_colour , (0.33 * self.__screen.get_width(),0),
                         (0.33* self.__screen.get_width(),self.box_size *self.__screen.get_height() + self.__upper_box))
        pygame.draw.line(self.__screen, line_colour, (0.67 * self.__screen.get_width(), 0),
                         (0.67 * self.__screen.get_width(), self.box_size * self.__screen.get_height() + self.__upper_box))

        # lower lines
        pygame.draw.line(self.__screen, line_colour, (0.33 * self.__screen.get_width(), self.__screen.get_height() + self.__upper_box),
                         (0.33 * self.__screen.get_width(),
                           self.__screen.get_height() - 0.05 * self.__screen.get_height()))
        pygame.draw.line(self.__screen, line_colour, (0.67 * self.__screen.get_width(), self.__screen.get_height() + self.__upper_box),
                         (0.67 * self.__screen.get_width(),
                          self.__screen.get_height() - 0.05* self.__screen.get_height()))

        # lower line across x-axis

        pygame.draw.line(self.__screen, line_colour, (0, self.__screen.get_height()-0.05 * self.__screen.get_height()),
                         (self.__screen.get_width(),self.__screen.get_height()-0.05 * self.__screen.get_height()) )

    def __print_points_and_labels(self, box_dist_from_bottom=0.1, point_offset = 0.05):

        img = self.__label_font.render(f"Points: {self.points}", True, (255, 255, 255))
        img_combo = self.__label_font.render(f"Combo: x{self.__combo}", True, (255, 255, 255))
        """
        if self.points >= 1000:
            self.__screen.blit(img, (self.__screen.get_width() * 0.97, self.box_size * self.__screen.get_height() +
                                 self.__upper_box +0.005 * self.__screen.get_height()))
        else:
            self.__screen.blit(img, (self.__screen.get_width() * 0.98, self.box_size * self.__screen.get_height() +
                                     self.__upper_box + 0.005 * self.__screen.get_height()))
                                     
        """
        self.__screen.blit(img, (self.__screen.get_width() * 0.33 - img.get_width() *0.5,
                                 (self.__screen.get_height() - 0.05 * self.__screen.get_height() +
                                  self.__screen.get_height()) * 0.5- img.get_height() * 0.5) )

        self.__screen.blit(img_combo, (self.__screen.get_width() * 0.66 - img_combo.get_width() * 0.5,
                                 (self.__screen.get_height() - 0.05 * self.__screen.get_height() +
                                  self.__screen.get_height()) * 0.5 - img_combo.get_height() * 0.5))

        label_y_pos = ((1-box_dist_from_bottom) * self.__screen.get_height() + self.__screen.get_height() -
                       point_offset * self.__screen.get_height()
                       ) * 0.5 + 0.01 * self.__screen.get_height()

        for key in self.__label_dict.keys():

            x_pos = self.label_to_position(self.__label_dict[key])
            img = self.__label_font.render(key, True, (255, 255, 255))

            self.__screen.blit(img, (x_pos - (img.get_width()/2), label_y_pos - img.get_height()/2))

    def __draw_target_box(self):
        self.__target_box = pygame.Rect(0 , self.__screen.get_height()* self.box_size + self.__upper_box,
                                        self.__screen.get_width(), self.__screen.get_height() * (1-self.box_size)
                                        )
        pygame.draw.rect(self.__screen, (255,255,255), self.__target_box, width=3,border_radius= 4)

    def __check_circle_collision(self):

        for circle in self.__existing_circles:
            leaving_target_region = circle.in_target_region

            circle_x = self.label_to_position(circle.x)
            circle_y = circle.y * self.__screen.get_height()

            circle.in_target_region = self.__target_box.collidepoint(circle_x, circle_y)
            if circle.in_target_region and circle.time_entered == 0:
                enter_time = time.time()
                circle.time_entered = enter_time

                #print(f"Circle entered target at {enter_time}")

            if not circle.in_target_region and leaving_target_region:
                """circle.predicted = True
                circle.colour = (255,0,0)
                self.points += self.neg_pred_value
                circle.value += self.neg_pred_value"""
                print(f"Circle needed {time.time() - circle.time_entered}s to leave target box")

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
    gv = GameView(laq, evq, pred_q, {})
    gv.put_label(0)
    gv.put_label(1)
    # p = Process(target=gv.main_loop)
    gv.put_predictions(1)

    gv.main_loop()