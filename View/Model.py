from random import choice


class Model:
    def __init__(self, allTerms, categories, path, period, pause_duration):

        # all terms in one list
        self.allTerms = allTerms
        self.count = {}
        #all terms in a list of lists by category
        self.categories = categories
        #the path to the data
        self.path = path
        #the time period for the test
        self.period = period

        #duration of pauses
        self.pause_duration = pause_duration

        self.labelorder=[]

        for term in allTerms:
            self.count[term] = 150

    def check_amt(self, rnd):
        val = self.count[rnd]
        if (val == 1):
            self.allTerms.remove(rnd)
        else:
            val = val - 1
            self.count[rnd] = val

    def get_random_term(self):
        if len(self.allTerms) != 0:
            random_choice = choice(self.allTerms)
            self.check_amt(random_choice)
            return random_choice
        else:
            return None



    def get_random_category(self):
        return choice(self.categories)


#test = Model(["1", "2", "Fuck off"], ["7","8","9"], 8, 9)
#print(test.get_random_category())
