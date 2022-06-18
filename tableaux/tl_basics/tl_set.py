from tableaux.tl_basics.formula import Atom, Formula

class TlSet(set):
    pp_set = set()
    tl_set = set()
    def __init__(self):
        super().__init__()
        self.pp_set = set()
        self.tl_set = set()

    def __copy__(self):
        new_tl_set = TlSet()
        new_tl_set.pp_set = self.pp_set.copy()
        new_tl_set.tl_set = self.tl_set.copy()
        return new_tl_set

    def copy(self):
        new_tl_set = TlSet()
        for x in self:
            new_tl_set.add(x)
        new_tl_set.pp_set = self.pp_set.copy()
        new_tl_set.tl_set = self.tl_set.copy()
        return new_tl_set


    def __deepcopy__(self, memodict={}):
        new_tl_set = TlSet()
        for x in self:
            new_tl_set.add(x)
        return new_tl_set

    def add(self, formula):
        if formula.type == 'ppf':
            self.pp_set.add(formula)
        else:
            self.tl_set.add(formula)
        super().add(formula)

    def remove(self, formula):
        if formula.type == 'ppf':
            self.pp_set.remove(formula)
        else:
            self.tl_set.remove(formula)
        super().remove(formula)



if __name__ == '__main__':
    tl_set = TlSet()
    tl_set.add(Atom('a'))
    tl_set.add(Formula(('F', Atom('b'))))
    tl_set.add(Formula(('G', Atom('c'))))
    print(tl_set)
    print(tl_set.pp_set)
    print(tl_set.tl_set)
    tl_set.remove(Atom('a'))
    print('----------------')
    print(tl_set)
    print(tl_set.pp_set)
    print(tl_set.tl_set)
