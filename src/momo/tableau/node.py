from momo.tl.tl_set import TlSet


class Node:
    def __init__(self, formula):

        self.set_of_formulae = TlSet()
        self.formulae_operators = {
            "U": TlSet(),
            "R": TlSet(),
            "&": TlSet(),
            "|": TlSet(),
            "G": TlSet(),
            "F": TlSet(),
            "X": TlSet(),
            "L": TlSet(),
        }

        self.closure = Closure(formula)
