

class Circle:

    redundant = 0
    predicted = False
    alpha = 0.5
    value = 0

    def __init__(self, x, y, first_encirclement, circle_colour, in_target_region = False):
        self.x = x
        self.y = y
        self.in_target_region = in_target_region
        self.first_encircelment = first_encirclement
        self.colour = (circle_colour[0], circle_colour[1], circle_colour[2], self.alpha)
        self.__c_colour = circle_colour


    def set_colour(self, circle_colour):
        self.colour = (circle_colour[0], circle_colour[1], circle_colour[2], self.alpha)
        self.__c_colour = circle_colour

    def dec_alpha(self, dec_by):
        self.alpha += dec_by
        circle_colour = self.__c_colour
        self.colour = (circle_colour[0], circle_colour[1], circle_colour[2], self.alpha)