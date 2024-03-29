import itertools

TEMPORAL_OPERATORS = {"G", "X", "F", "U", "R"}


class Formula(tuple):
    def __init__(self, formula):
        if formula[0] == "-":
            if formula[1] == "-":
                formula = formula[2]
            else:
                formula = formula[1]

    def operator(self):
        return self[0]

    def operands(self):
        return self[1:]

    def left(self):
        return self[1]

    def right(self):
        return self[2]

    def neg(self):
        return Formula(("-", self))

    def is_atom(self):
        return type(self) == Atom

    def is_boolean(self):
        return self == "0" or self == "1"

    def is_neg(self):
        return self[0] == "-"

    def is_and(self):
        return self[0] == "&"

    def is_or(self):
        return self[0] == "|"

    def is_until(self):
        return self[0] == "U"

    def is_eventually(self):
        return self[0] == "F"

    def is_release(self):
        return self[0] == "R"

    def is_implication(self):
        return self[0] == "->" or self[0] == ">"

    def is_iff(self):
        return self[0] == "=" or self[0] == "<->"

    def is_next(self):
        return self[0] == "X"

    def is_always(self):
        return self[0] == "G"

    def is_next_always(self):
        if self[0] == "X":
            if type(self[1]) == Formula and self[1][0] == "G":
                return True
        return False

    def have_always(self):
        if self.is_next():
            return self[1].have_always()
        elif self.is_always():
            return True
        else:
            return False

    def add_operator(self, operator, operand=None):
        if operand:
            return Formula((operator, self, operand))
        else:
            return Formula((operator, self))

    def nnf(self):
        return _nnf(self)

    def contains_false(self):
        return "0" in self

    def xnf(self):
        if self.is_next():
            return _xnf(self)
        else:
            return self


class Atom(str):
    type = "ppf"

    def is_neg(self):
        return self[0] == "-"

    def is_boolean(self):
        return self == "0" or self == "1"

    def neg(self):
        if self[0] == "1":
            return Atom("0")
        if self[0] == "0":
            return Atom("1")
        if self[0] == "-":
            return Atom(self[1:])
        return Atom("-" + self)

    @staticmethod
    def is_and():
        return False

    @staticmethod
    def is_or():
        return False

    @staticmethod
    def is_atom():
        return True

    @staticmethod
    def is_eventually():
        return False

    @staticmethod
    def is_until():
        return False

    @staticmethod
    def is_always():
        return False

    @staticmethod
    def is_next():
        return False

    @staticmethod
    def is_next_always():
        return False

    @staticmethod
    def have_always():
        return False

    @staticmethod
    def operator():
        return "L"

    def nnf(self):
        return self

    def xnf(self):
        return self

    def add_operator(self, operator, operand=None):
        if operand:
            return Formula((operator, self, operand))
        else:
            return Formula((operator, self))


def _xnf(formula):
    subformula = formula[1]
    if subformula.is_atom():
        return Formula(("X", subformula))
    elif subformula.is_boolean():
        return Formula(("X", subformula))
    elif subformula.is_neg():
        return Formula(("X", subformula))
    elif subformula.is_next():
        return Formula(("X", subformula))
    elif subformula.is_always():
        return Formula(("X", subformula))
    elif subformula.is_eventually():
        return Formula(("X", subformula))
    elif subformula.is_until():
        return Formula(("X", subformula))
    elif subformula.is_release():
        return Formula(("X", subformula))
    elif subformula.is_and():
        return _xnf_and_or("&", subformula)
    elif subformula.is_or():
        return _xnf_and_or("|", subformula)
    else:
        print("Something went wrong")


def _xnf_and_or(symbol, subformula):
    aux = []
    for sf in subformula[1]:
        aux.append(_xnf(("X", sf)))
    if len(aux) == 1:
        return Atom(aux[0])
    else:
        return Formula((symbol, frozenset(aux)))


def _nnf(formula):
    """
    Given a formula in binary tree form, convert it to their negation normal form

    Parameters
    ----------
    formula: list of list that represents a formula

    Returns
    -------
    formula: tree-like object that represents the formula at nnf
    """
    if formula.is_atom():
        return formula
    elif formula.is_neg():  # Negative cases
        subformula = formula[1]
        if subformula.is_neg():
            if subformula == Atom:
                return Atom(subformula[1:])
            return _nnf(subformula[1])
        elif subformula.is_boolean():
            return "1" if subformula == "0" else "0"
        elif subformula.is_atom():
            return subformula.neg()
        elif subformula.is_and():
            return _nnf_and_or("|", subformula, True)
        elif subformula.is_or():
            return _nnf_and_or("&", subformula, True)
        elif subformula.is_until():
            return Formula(("R", _nnf(subformula[1].neg()), _nnf(subformula[2].neg())))
        elif subformula.is_release():
            return Formula(("U", _nnf(subformula[1].neg()), _nnf(subformula[2].neg())))
        elif subformula.is_implication():
            return Formula(
                ("&", frozenset([_nnf(subformula[1]), _nnf(subformula[2].neg())]))
            )
        elif subformula.is_next():
            return Formula(("X", _nnf(subformula[1].neg())))
        elif subformula.is_eventually():
            return Formula(("G", _nnf(subformula[1].neg())))
        elif subformula.is_always():
            return Formula(("F", _nnf(subformula[1].neg())))
        elif subformula.is_iff():
            return _nnf_iff(subformula, True)
    elif not formula.is_neg():  # Positive Cases
        subformula = formula
        if subformula.is_atom():
            return subformula
        elif subformula.is_and():
            return _nnf_and_or("&", subformula, False)
        elif subformula.is_or():
            return _nnf_and_or("|", subformula, False)
        elif subformula.is_until():
            return Formula(("U", _nnf(subformula[1]), _nnf(subformula[2])))
        elif subformula.is_release():
            return Formula(("R", _nnf(subformula[1]), _nnf(subformula[2])))
        elif subformula.is_implication():
            return (
                Formula(
                    ("|", frozenset([_nnf(subformula[1].neg()), _nnf(subformula[2])]))
                )
                if subformula[1] != subformula[2]
                else Atom("1")
            )
        elif subformula.is_next():
            return Formula(("X", _nnf(subformula[1])))
        elif subformula.is_eventually():
            return Formula(("F", _nnf(subformula[1])))
        elif subformula.is_always():
            return Formula(("G", _nnf(subformula[1])))
        elif subformula.is_iff():
            return _nnf_iff(subformula, False)


def _nnf_and_or(symbol, subformula, negate):
    aux = []
    if negate:
        for sf in subformula[1]:
            aux.append(_nnf(sf.neg()))
    else:
        for sf in subformula[1]:
            aux.append(_nnf(sf))
    if len(aux) == 1:
        return Atom(aux[0])
    return Formula((symbol, frozenset(aux)))


def _nnf_iff(subformula, negate):
    # a <--> b = (a & b) | (-a & -b)
    if negate:
        if subformula[1] == subformula[2]:
            return Atom("0")
        aux = Formula(
            (
                "&",
                frozenset(
                    [
                        (
                            "|",
                            frozenset(
                                [_nnf(subformula[1].neg()), _nnf(subformula[2].neg())]
                            ),
                        ),
                        ("|", frozenset([_nnf(subformula[1]), _nnf(subformula[2])])),
                    ]
                ),
            )
        )
    else:
        if subformula[1] == subformula[2]:
            return Atom("1")
        aux = Formula(
            (
                "|",
                frozenset(
                    [
                        Formula(
                            ("&", frozenset([_nnf(subformula[1]), _nnf(subformula[2])]))
                        ),
                        Formula(
                            (
                                "&",
                                frozenset(
                                    [
                                        _nnf(subformula[1].neg()),
                                        _nnf(subformula[2].neg()),
                                    ]
                                ),
                            )
                        ),
                    ]
                ),
            )
        )
    return aux


if __name__ == "__main__":
    # subformula = Formula(('->', Formula(('F', Atom('e'))), Atom('d')))
    # s2 = subformula.nnf()

    # a = Formula(('|', frozenset([_nnf(subformula[1].neg()), _nnf(subformula[2])])))

    # print(s2.type)
    s2 = Formula(
        (
            "X",
            Formula(
                (
                    "&",
                    frozenset(
                        [
                            Formula(("|", frozenset([Atom("a"), Formula(("X", "b"))]))),
                            Atom("c"),
                        ]
                    ),
                )
            ),
        )
    )
    print(s2)
    print(s2.xnf())
