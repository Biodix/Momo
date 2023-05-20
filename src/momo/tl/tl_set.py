from momo.tl.formula import Formula, Atom
import copy
from multiset import Multiset


def classify_formula_by_operator(formula, operators):
    if isinstance(formula, Formula):
        operators[formula.operator()] = formula
    else:  # isinstance(formula, Atom)
        operators["L"] = formula


class TlSet(Multiset):
    def __init__(self, itr=None):
        self.operators = {
            "U": Multiset(),
            "R": Multiset(),
            "&": Multiset(),
            "|": Multiset(),
            "G": Multiset(),
            "F": Multiset(),
            "X": Multiset(),
            "L": Multiset(),
        }
        if itr:  # Constructor by passing an iterable
            super().__init__(itr)
            for formula in itr:
                self.add_to_operators(formula)
        else:  # Empty constructor (regular)
            super().__init__()

    def __copy__(self):
        new_tl_set = copy.deepcopy(self)
        return new_tl_set

    # def __deepcopy__(self, memodict={}):
    #     new_tl_set = TlSet()
    #     for x in self:
    #         new_tl_set.add(x)
    #     return new_tl_set

    def __eq__(self, other):
        return self.operators == other.operators

    def __ne__(self, other):
        return self.operators != other.operators

    def clone(self):
        new_tl_set = copy.deepcopy(self)
        new_tl_set.operators = copy.deepcopy(self.operators)
        return new_tl_set

    def add(self, formula, multiplicity=1):
        super().add(formula, multiplicity)
        self.add_to_operators(formula)

    def get(self, formula, default=None):
        return super().get(formula, default)

    def add_to_operators(self, formula):
        self.operators[formula.operator()].add(formula)
        # if isinstance(formula, Formula):
        # self.operators[formula.operator()].add(formula)
        # else:  # isinstance(formula, Atom)
        #     self.operators['L'].add(formula)

    def remove_from_operators(self, formula, multiplicity):
        self.operators[formula.operator()].remove(formula, multiplicity)

    def remove_from_set(self, formula, multiplicity=None):
        return super().remove(formula, multiplicity)

    def remove(self, formula, multiplicity=1, default=None):
        # Return the multiplicity of the removed formula
        self.remove_from_operators(formula, multiplicity)
        return super().remove(formula, multiplicity)

    def is_empty(self):
        return len(self) == 0

    def is_inconsistent(self):
        return False

    def is_elementary(self):
        return (
            len(self.operators["U"]) == 0
            and len(self.operators["R"]) == 0
            and len(self.operators["F"]) == 0
            and len(self.operators["G"]) == 0
            and len(self.operators["&"]) == 0
            and len(self.operators["|"]) == 0
        )

    def is_sat_elementary(self):
        if len(self.operators["X"]) + len(self.operators["L"]) + len(
            self.operators["|"]
        ) == len(self):
            for or_formula in self.operators["|"]:
                for or_element in or_formula[1]:
                    if not (or_element.is_next() or or_element.is_atom()):
                        return False
            return True
        return False

    def next_stage(self):
        next_stage = []
        for formula in self:
            if formula.is_next():
                next_stage.append(formula[1])
        return TlSet(next_stage)

    def contradicts(self, formula, closure):
        nnf_neg_formula = closure[formula]["nnf"]
        if nnf_neg_formula in self:
            return True
        else:
            return False

    # Get one random formula. There is a operator preference
    # U >> F >> & >> G >> R >> |
    def pop_formula(self):
        if self.operators["U"]:  # type: ignore
            selected_formula = next(iter(self.operators["U"]))
            multiplicity = self.operators["U"].remove(selected_formula)
        elif self.operators["F"]:  # type: ignore
            selected_formula = next(iter(self.operators["F"]))
            multiplicity = self.operators["F"].remove(selected_formula)
        elif self.operators["&"]:  # type: ignore
            selected_formula = next(iter(self.operators["&"]))
            multiplicity = self.operators["&"].remove(selected_formula)
        elif self.operators["G"]:  # type: ignore
            selected_formula = next(iter(self.operators["G"]))
            multiplicity = self.operators["G"].remove(selected_formula)
        elif self.operators["R"]:  # type: ignore
            selected_formula = next(iter(self.operators["R"]))
            multiplicity = self.operators["R"].remove(selected_formula)
        elif self.operators["|"]:  # type: ignore
            selected_formula = next(iter(self.operators["|"]))
            multiplicity = self.operators["|"].remove(selected_formula)
        else:  # Impossible reachable code in the application
            raise Exception("There are not valid formulas to pop", self)
        self.remove_from_set(selected_formula)
        return selected_formula, multiplicity

    def push_formula(self, formula, multiplicity=1):
        if formula.is_atom():
            self.operators["L"].add(formula, multiplicity)
        else:
            self.operators[formula[0]].add(formula, multiplicity)
        self.add(formula, multiplicity)


if __name__ == "__main__":
    tl_set = TlSet()
    tl_set.add(Atom("a"))
    tl_set.add(Formula(("F", Atom("b"))))
    tl_set.add(Formula(("G", Atom("c"))))
    print(tl_set)
    tl_set.remove(Atom("a"))
    print("----------------")
    print(tl_set)
