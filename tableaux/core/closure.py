i = 1


class Closure:
    def __init__(self, formula, execution_mode=0):
        self.formula_to_sat = {}
        self.sat_to_formula = {}
        closure, eventualities, n_nnf = self._calculate_closure(formula, execution_mode)
        self.closure = closure
        self.eventualities = eventualities
        self.n_nnf = n_nnf

    def __contains__(self, element):
        return element in self.closure

    def _calculate_closure(self, formula, execution_mode):
        closure = {}
        eventualities = set()
        formulae = set()
        n_nnf = {}
        self._closure(formula, closure, eventualities, execution_mode, formulae, n_nnf)
        return closure, eventualities, n_nnf

    def _closure(self, formula, closure, eventualities, execution_mode, formulae, n_nnf):
        global i
        formulae.add(formula)
        n_nnf[formula] = 0
        if formula.is_atom():
            nnf_neg_formula = formula.neg()
            closure[formula] = {'nnf': nnf_neg_formula}
            closure[nnf_neg_formula] = {'nnf': formula}
            if formula not in self.formula_to_sat:
                self.formula_to_sat[formula] = str(i)
                self.formula_to_sat[nnf_neg_formula] = str(-i)
                self.sat_to_formula[str(i)] = formula
                self.sat_to_formula[str(-i)] = nnf_neg_formula
                i += 1
        elif formula.is_and() or formula.is_or():
            nnf_neg_formula = formula.neg().nnf()
            closure[formula] = {'nnf': nnf_neg_formula}
            closure[nnf_neg_formula] = {'nnf': formula}
            if formula not in self.formula_to_sat:
                self.formula_to_sat[formula] = str(i)
                self.formula_to_sat[nnf_neg_formula] = str(-i)
                self.sat_to_formula[str(i)] = formula
                self.sat_to_formula[str(-i)] = nnf_neg_formula
                i += 1

            for f in formula[1]:
                self._closure(f, closure, eventualities, execution_mode, formulae, n_nnf)
        elif formula.is_next():
            subformula = formula[1]
            nnf_neg_formula = formula.neg().nnf()
            closure[formula] = {'nnf': nnf_neg_formula}
            if execution_mode != 0:
                closure[nnf_neg_formula] = {'nnf': formula}
            elif subformula.have_always():
                closure[nnf_neg_formula] = {'nnf': formula}
            if formula not in self.formula_to_sat:
                self.formula_to_sat[formula] = str(i)
                self.formula_to_sat[nnf_neg_formula] = str(-i)
                self.sat_to_formula[str(i)] = formula
                self.sat_to_formula[str(-i)] = nnf_neg_formula
                i += 1

            self._closure(subformula, closure, eventualities, execution_mode, formulae, n_nnf)
        elif formula.is_always():
            nnf_neg_formula = formula.neg().nnf()
            closure[formula] = {'nnf': nnf_neg_formula}
            if execution_mode != 0:
                closure[nnf_neg_formula] = {'nnf': formula}
                closure[nnf_neg_formula.add_operator('X')] = {'nnf': formula.add_operator('X')}
            closure[formula.add_operator('X')] = {'nnf': nnf_neg_formula.add_operator('X')}
            eventualities.add(nnf_neg_formula[1])
            if formula not in self.formula_to_sat:
                self.formula_to_sat[formula] = str(i)
                self.formula_to_sat[nnf_neg_formula] = str(-i)
                self.sat_to_formula[str(i)] = formula
                self.sat_to_formula[str(-i)] = nnf_neg_formula
                i += 1

            self._closure(formula[1], closure, eventualities, execution_mode, formulae, n_nnf)
        elif formula.is_until():
            nnf_neg_formula = formula.neg().nnf()
            next_formula = formula.add_operator('X')
            nnf_next_formula = nnf_neg_formula.add_operator('X')

            closure[formula] = {'nnf': nnf_neg_formula}
            closure[next_formula] = {'nnf': nnf_next_formula}
            closure[nnf_neg_formula] = {'nnf': formula}
            closure[nnf_next_formula] = {'nnf': next_formula}

            if formula not in self.formula_to_sat:
                self.formula_to_sat[formula] = str(i)
                self.formula_to_sat[nnf_neg_formula] = str(-i)
                self.sat_to_formula[str(i)] = formula
                self.sat_to_formula[str(-i)] = nnf_neg_formula
                i += 1
            if next_formula not in self.formula_to_sat:
                self.formula_to_sat[next_formula] = str(i)
                self.formula_to_sat[nnf_next_formula] = str(-i)
                self.sat_to_formula[str(i)] = next_formula
                self.sat_to_formula[str(-i)] = nnf_next_formula
                i += 1

            eventualities.add(formula[2])
            # eventualities.add(nnf_formula[2])
            self._closure(formula[1], closure, eventualities, execution_mode, formulae, n_nnf)
            self._closure(formula[2], closure, eventualities, execution_mode, formulae, n_nnf)
        elif formula.is_release():
            nnf_neg_formula = formula.neg().nnf()
            next_formula = formula.add_operator('X')
            nnf_next_formula = nnf_neg_formula.add_operator('X')

            closure[formula] = {'nnf': nnf_neg_formula}
            closure[next_formula] = {'nnf': nnf_next_formula}
            closure[nnf_neg_formula] = {'nnf': formula}
            closure[nnf_next_formula] = {'nnf': next_formula}
            eventualities.add(nnf_neg_formula[2])
            if formula not in self.formula_to_sat:
                self.formula_to_sat[formula] = str(i)
                self.formula_to_sat[nnf_neg_formula] = str(-i)
                self.sat_to_formula[str(i)] = formula
                self.sat_to_formula[str(-i)] = nnf_neg_formula
                i += 1
            if next_formula not in self.formula_to_sat:
                self.formula_to_sat[next_formula] = str(i)
                self.formula_to_sat[nnf_next_formula] = str(-i)
                self.sat_to_formula[str(i)] = next_formula
                self.sat_to_formula[str(-i)] = nnf_next_formula
                i += 1

            self._closure(formula[1], closure, eventualities, execution_mode, formulae, n_nnf)
            self._closure(formula[2], closure, eventualities, execution_mode, formulae, n_nnf)

        elif formula.is_eventually():
            next_formula = formula.add_operator('X')
            nnf_neg_formula = formula.neg().nnf()
            nnf_next_formula = nnf_neg_formula.add_operator('X')

            if formula not in self.formula_to_sat:
                self.formula_to_sat[formula] = str(i)
                self.formula_to_sat[nnf_neg_formula] = str(-i)
                self.sat_to_formula[str(i)] = formula
                self.sat_to_formula[str(-i)] = nnf_neg_formula
                i += 1
            if next_formula not in self.formula_to_sat:
                self.formula_to_sat[next_formula] = str(i)
                self.formula_to_sat[nnf_next_formula] = str(-i)
                self.sat_to_formula[str(i)] = next_formula
                self.sat_to_formula[str(-i)] = nnf_next_formula
                i += 1

            closure[formula] = {'nnf': nnf_neg_formula}
            closure[nnf_neg_formula] = {'nnf': formula}

            closure[next_formula] = {'nnf': nnf_next_formula}
            closure[nnf_next_formula] = {'nnf': next_formula}

            eventualities.add(formula[1])
            # eventualities.add(nnf_neg_formula[1])
            self._closure(formula[1], closure, eventualities, execution_mode, formulae, n_nnf)


if __name__ == '__main__':
    from tableaux.preproccesing.process_formula import process_formula

    formula = process_formula('(F(- d))&(G(F c))&(G(a -> (X(F e))))&(G(c -> (F a)))&(G((F e) -> d))')
    cl = Closure(formula)
