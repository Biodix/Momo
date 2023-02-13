class SatTable:
    def __init__(self):
        self.formula_to_sat = {}
        self.sat_to_formula = {}

    def add_entry(self, formula, nnf_formula):
        i = str(len(self.formula_to_sat) // 2 + 1)
        neg_i = "-" + i
        self.formula_to_sat[formula] = i
        self.formula_to_sat[nnf_formula] = neg_i
        self.sat_to_formula[i] = formula
        self.sat_to_formula[neg_i] = nnf_formula


class Closure(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sat_table = SatTable()

    def build_closure(self, formula):
        self._closure(formula)

    def add_entry(self, formula, neg_formula):
        self[formula] = {"nnf": neg_formula}
        self[neg_formula] = {"nnf": formula}
        self.sat_table.add_entry(formula, neg_formula)

    def _closure(self, formula):
        if formula.is_atom():
            nnf_formula = formula.neg()
            self.add_entry(formula, nnf_formula)
        elif formula.is_neg():
            self._closure(formula[1])
        elif formula.is_and() or formula.is_or():
            nnf_formula = formula.neg().nnf()
            self.add_entry(formula, nnf_formula)
            for element in formula[1]:
                self._closure(element)
        elif formula.is_next():
            nnf_formula = formula.neg().nnf()
            self.add_entry(formula, nnf_formula)
            self._closure(formula[1])
        elif formula.is_always():
            nnf_formula = formula.neg().nnf()
            # Already in nnf
            next_formula = formula.add_operator("X")
            nnf_next_formula = nnf_formula.add_operator("X")
            self.add_entry(formula, nnf_formula)
            self.add_entry(next_formula, nnf_next_formula)
            self._closure(formula[1])
        elif formula.is_eventually():
            nnf_formula = formula.neg().nnf()
            # Already in nnf
            next_formula = formula.add_operator("X")
            nnf_next_formula = nnf_formula.add_operator("X")
            self.add_entry(formula, nnf_formula)
            self.add_entry(next_formula, nnf_next_formula)
            self._closure(formula[1])
        elif formula.is_until() or formula.is_release():
            nnf_formula = formula.neg().nnf()
            # Already in nnf
            next_formula = formula.add_operator("X")
            nnf_next_formula = nnf_formula.add_operator("X")
            self.add_entry(formula, nnf_formula)
            self.add_entry(next_formula, nnf_next_formula)
            self._closure(formula[1])
            self._closure(formula[2])
