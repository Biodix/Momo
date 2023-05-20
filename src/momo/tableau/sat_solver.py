from pysat.solvers import Glucose4
from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet


class SatSolver:
    def __init__(self, tableau):
        self.tableau = tableau
        self.n_f = 0
        self.formula_to_int_map = {}
        self.int_to_formula_map = {}

    def formula_to_clause(self, formula):
        clause = []
        if formula.is_or():
            for or_element in formula[1]:
                if or_element == "1":  # Clause is True
                    clause = []
                    break
                elif or_element == "0":  # Doesn't add information
                    continue
                else:
                    self.add_to_clause(or_element, clause)
        elif formula.is_next():
            self.add_to_clause(formula, clause)
        elif formula.is_atom():
            self.add_to_clause(formula, clause)
        return clause

    def clause_to_formula(self, clause):
        formula = []
        if len(clause) > 1:
            for n in clause:
                f = self.int_to_formula_map[n]
                formula.append(f)
            return Formula(("|", frozenset(formula)))
        else:
            n = clause[0]
            f = self.int_to_formula_map[n]
            return f

    def add_to_clause(self, formula, clause):
        if formula not in self.formula_to_int_map:
            self.n_f += 1
            self.formula_to_int_map[formula] = self.n_f
            self.int_to_formula_map[self.n_f] = formula

            neg_formula = self.tableau.closure[formula]["nnf"]
            self.formula_to_int_map[neg_formula] = -self.n_f
            self.int_to_formula_map[-self.n_f] = neg_formula

        number = self.formula_to_int_map[formula]
        clause.append(number)

    # def add_to_clause(self, formula, clause, added_sat_formulas):
    #     formula_to_number = self.tableau.closure.sat_table.formula_to_number
    #     number = formula_to_number[formula]
    #     clause.append(number)
    #     added_sat_formulas.add(number)

    # def tl_set_to_sat(self, tl_set):
    #     self.n_f = 1
    #     self.formula_to_int_map = {}
    #     self.int_to_formula_map = {}

    #     added_sat_formulas = set()
    #     clauses = [self.formula_to_clause(
    #         formula, added_sat_formulas) for formula in tl_set]
    #     return clauses, added_sat_formulas

    def tl_set_to_sat(self, tl_set):
        self.n_f = 0
        self.formula_to_int_map = {}
        self.int_to_formula_map = {}

        clauses = [self.formula_to_clause(formula) for formula in tl_set]
        return clauses

    def sat_to_tl_set(self, clauses):
        tl_set = TlSet()
        for clause in clauses:
            formula = self.clause_to_formula(clause)
            tl_set.add(formula)
        return tl_set

    def model_to_tl_set(self, clause):
        tl_set = TlSet()
        for number in clause:
            formula = self.int_to_formula_map[number]
            tl_set.add(formula)
        return tl_set

    def solve(self, clauses):
        # TODO: Esto esta fallando, me esta devolviendo muchos modelos redundantes por la tonteria de que rellena
        # la solución con integer que no le he pasado. Revisarlo y hacer un reductor de integer a integer
        with Glucose4(bootstrap_with=clauses) as g:
            for model in g.enum_models():
                yield model


def add_to_closure(
    formula,
    clause,
    formula_to_sat,
    sat_to_formula,
    sat_to_glucose,
    glucose_to_sat,
    sat_index,
    glucose_index,
):
    formula_nnf = formula.neg.nnf()
    formula_to_sat[formula] = str(sat_index)
    formula_to_sat[formula_nnf] = str(-sat_index)
    sat_to_formula[str(sat_index)] = formula
    sat_to_formula[str(-sat_index)] = formula_nnf

    glucose_to_sat[glucose_index] = sat_index
    glucose_to_sat[-glucose_index] = -sat_index
    sat_to_glucose[sat_index] = glucose_index
    sat_to_glucose[-sat_index] = -glucose_index

    clause.append(sat_to_glucose[sat_index])
