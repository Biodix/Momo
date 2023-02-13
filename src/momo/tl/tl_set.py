from momo.tl.formula import Formula, Atom

class TlSet(set):
    def __init__(self):
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

    def remove(self, formula):
        super().remove(formula)
        
    def is_empty(self):
        return len(self) == 0

    def is_inconsistent(self):
        return False



if __name__ == '__main__':
    tl_set = TlSet()
    tl_set.add(Atom('a'))
    tl_set.add(Formula(('F', Atom('b'))))
    tl_set.add(Formula(('G', Atom('c'))))
    print(tl_set)
    tl_set.remove(Atom('a'))
    print('----------------')
    print(tl_set)