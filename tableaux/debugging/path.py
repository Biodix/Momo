from itertools import islice


class Path:
    def __init__(self):
        self.path = []
        self.rules = []
        self.selected_formulae = []

    def add_step(self, step):
        self.path.append(step)

    def add_rule(self, rule):
        self.rules.append(rule)

    def add_selected_formula(self, selected_formula):
        self.selected_formulae.append(selected_formula)
