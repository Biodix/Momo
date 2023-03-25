from momo.tl.tl_set import TlSet


class Branch(list):
    def __init__(self, initial_set=None, remaining_eventualities=(), fulfilled_eventualities=(), literals=()):
        super().__init__()
        self.remaining_eventualities = TlSet(remaining_eventualities)
        self.fulfilled_eventualities = TlSet(fulfilled_eventualities)
        self.eventualities = TlSet()  # Puede que no se haga asi
        self.literals = TlSet(literals)
        if initial_set:
            for formula in initial_set:
                if formula.is_eventually():
                    self.remaining_eventualities.add(formula[1])
                    self.eventualities.add(formula[1])
                elif formula.is_until():
                    self.remaining_eventualities.add(formula[2])
                    self.eventualities.add(formula[2])
                elif formula.is_atom():
                    self.literals.add(formula)

    def append(self, tl_Set):
        self.append(tl_Set)

    def pop(self):
        return self.pop()

    def add_remaining_eventuality(self, ev_formula):
        if ev_formula in self.fulfilled_eventualities:
            return False
        self.remaining_eventualities.add(ev_formula)

    def remove_remaining_eventuality(self, ev_formula, multiplicity=1):
        self.remaining_eventualities.remove(ev_formula, multiplicity)

    def fulfill_eventuality(self, ev_formula):
        if ev_formula in self.fulfilled_eventualities:
            return False
        multiplicity = self.remaining_eventualities.remove(ev_formula)
        self.fulfilled_eventualities.add(ev_formula, multiplicity)
        return True

    def neglect_eventuality(self, ev_formula, fulfilled):
        if not fulfilled:
            return False
        multiplicity = self.fulfilled_eventualities.remove(ev_formula)
        self.remaining_eventualities.add(ev_formula, multiplicity)

    def has_fulfill_all_eventualities(self):
        return len(self.remaining_eventualities) == 0
