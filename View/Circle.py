

class Circle:

    redundant = False

    def __init__(self, x, y, first_encirclement, circle_colour, in_target_region = False):
        self.x = x
        self.y = y
        self.in_target_region = in_target_region
        self.first_encircelment = first_encirclement
        self.colour = circle_colour