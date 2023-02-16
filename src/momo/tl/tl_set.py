from momo.tl.formula import Formula, Atom


def classify_formula_by_operator(formula, operators):
    if isinstance(formula, Formula):
        operators[formula.operator()] = formula
    else:  # isinstance(formula, Atom)
        operators['L'] = formula


class TlSet(set):
    def __init__(self, itr=None):
        self.operators = {'U': set(), 'R': set(), '&': set(), '|': set(),
                          'G': set(), 'F': set(), 'X': set(), 'L': set()}
        if itr:  # Constructor by passing an iterable
            super().__init__(itr)
            for formula in itr:
                self.add_to_operators(formula)
        else:  # Empty constructor (regular)
            super().__init__()

    def __copy__(self):
        new_tl_set = TlSet()
        return new_tl_set.copy()

    def __deepcopy__(self, memodict={}):
        new_tl_set = TlSet()
        for x in self:
            new_tl_set.add(x)
        return new_tl_set

    def add(self, formula):
        super().add(formula)
        self.add_to_operators(formula)

    def add_to_operators(self, formula):
        if isinstance(formula, Formula):
            self.operators[formula.operator()].add(formula)
        else:  # isinstance(formula, Atom)
            self.operators['L'].add(formula)

    def remove(self, formula):
        super().remove(formula)

    def is_empty(self):
        return len(self) == 0

    def is_inconsistent(self):
        return False

    def is_elementary(self):
        return False

    def is_sat_elementary(self):
        return False

    def next_stage(self):
        next_stage = []
        for formula in self:
            if formula.is_next():
                next_stage.append(formula[1])
        return TlSet(next_stage)

    def contradicts(self, formula, closure):
        nnf_neg_formula = closure[formula]['nnf']
        if nnf_neg_formula in self:
            return True
        else:
            return False

    # Get one random formula. There is a operator preference
    # U >> F >> & >> G >> R >> |
    def pop_formula(self):
        if self.operators['U']:
            selected_formula = self.operators['U'].pop()
        elif self.operators['F']:
            selected_formula = self.operators['F'].pop()
        elif self.operators['&']:
            selected_formula = self.operators['&'].pop()
        elif self.operators['G']:
            selected_formula = self.operators['G'].pop()
        elif self.operators['R']:
            selected_formula = self.operators['R'].pop()
        elif self.operators['|']:
            selected_formula = self.operators['|'].pop()
        else:  # Impossible reachable code in the application
            raise Exception("There are not valid formulas to pop", self)
        self.remove(selected_formula)
        return selected_formula


if __name__ == '__main__':
    tl_set = TlSet()
    tl_set.add(Atom('a'))
    tl_set.add(Formula(('F', Atom('b'))))
    tl_set.add(Formula(('G', Atom('c'))))
    print(tl_set)
    tl_set.remove(Atom('a'))
    print('----------------')
    print(tl_set)
