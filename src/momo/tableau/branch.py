from momo.tl.tl_set import TlSet


class Branch(list):
    def __init__(self, initial_set=None):
        super().__init__()
        self.remaining_eventualities = TlSet()
        self.eventualities = TlSet()  # Puede que no se haga asi
        self.literals = TlSet()
        if initial_set:
            for formula in initial_set:
                if formula.is_eventually() or formula.is_until():
                    self.remaining_eventualities.add(formula)
                    self.eventualities.add(formula)
                elif formula.is_atom():
                    self.literals.add(formula)

    def append(self, tl_Set):
        self.append(tl_Set)

    def pop(self):
        return self.pop()

    def has_fulfill_all_eventualities(self):
        return len(self.remaining_eventualities) == 0
