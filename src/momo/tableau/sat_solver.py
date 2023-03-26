from pysat.solvers import Glucose4


class SatSolver:
    def __init__(self, tableau):
        self.tableau = tableau

    def formula_to_number(self, formula):
        clause = []
        added_formulas = []
        if formula.is_or():
            for or_element in formula[1]:
                if or_element == '1':  # Clause is True
                    clause = []
                    break
                elif or_element == '0':  # Doesn't add information
                    continue
                else:
                    self.add_to_clause(or_element, clause)
                    added_formulas.append(or_element)
        elif formula.is_next():
            self.add_to_clause(formula, clause)
            added_formulas.append(formula)
        elif formula.is_atom():
            self.add_to_clause(formula, clause)
            added_formulas.append(formula)
        return clause

    def add_to_clause(self, formula, clause):
        formula_to_number = self.tableau.closure.sat_table.formula_to_number
        number_to_formula = self.tableau.closure.sat_table.number_to_formula
        clause.append(formula_to_number[formula])
        # formula_to_number = self.tableau.closure.formula_to_number
        # number_to_formula = self.tableau.closure.number_to_formula
        # if sat_index in sat_to_glucose:
        #     clause.append(sat_to_glucose[sat_index])
        # else:
        #     glucose_to_sat[glucose_index] = sat_index
        #     glucose_to_sat[-glucose_index] = -sat_index
        #     sat_to_glucose[sat_index] = glucose_index
        #     sat_to_glucose[-sat_index] = -glucose_index
        #     clause.append(sat_to_glucose[sat_index])

    def solve(self, sat_solver, added_formulas):
        with Glucose4(bootstrap_with=sat_solver) as g:
            for m in g.enum_models():
                model = [l for l in m if abs(l) in added_formulas]
                print(model)


def add_to_closure(formula, clause, formula_to_sat, sat_to_formula, sat_to_glucose, glucose_to_sat, sat_index, glucose_index):
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


def call_sat_solver(node):
    formula_to_sat = node.closure.formula_to_sat
    sat_to_formula = node.closure.sat_to_formula
    sat_to_glucose = {}
    glucose_to_sat = {}
    added_formulas = set()

    glucose_index = 1
    g = Glucose4()
    for formula in node.formulae_operators['|']:
        clause = []
        for or_element in formula[1]:
            or_element = or_element.xnf()
            if or_element == '1':  # Clause is True
                break
            elif or_element == '0':  # Doesn't add information
                continue
            elif or_element in formula_to_sat:
                sat_index = int(formula_to_sat[or_element])
                add_to_clause(or_element, clause, sat_to_glucose,
                              glucose_to_sat, sat_index, glucose_index)
            else:
                add_to_closure(or_element, clause, formula_to_sat, sat_to_formula,
                               sat_to_glucose, glucose_to_sat, sat_index, glucose_index)
            sat_index += 1
            glucose_index += 1
            added_formulas.add(or_element)
        g.add_clause(clause)
    for formula in node.formulae_operators['X']:
        clause = []
        next_element = formula.xnf()
        if next_element == '1':  # Clause is True
            break
        elif next_element == '0':  # Doesn't add information
            continue
        elif next_element in formula_to_sat:
            sat_index = int(formula_to_sat[next_element])
            self.add_to_clause(next_element, clause, sat_to_glucose,
                               glucose_to_sat, sat_index, glucose_index)
        else:
            self.add_to_closure(next_element, clause, formula_to_sat, sat_to_formula,
                                sat_to_glucose, glucose_to_sat, sat_index, glucose_index)
        sat_index += 1
        glucose_index += 1
        added_formulas.add(next_element)
        g.add_clause(clause)
    for formula in node.formulae_operators['L']:
        clause = []
        literal = formula.xnf()
        if literal == '1':  # Clause is True
            break
        elif literal == '0':  # Doesn't add information
            continue
        elif literal in formula_to_sat:
            sat_index = int(formula_to_sat[literal])
            self.add_to_clause(literal, clause, sat_to_glucose,
                               glucose_to_sat, sat_index, glucose_index)
        else:
            self.add_to_closure(literal, clause, formula_to_sat, sat_to_formula,
                                sat_to_glucose, glucose_to_sat, sat_index, glucose_index)
            sat_index += 1
        glucose_index += 1
        added_formulas.add(literal)
        g.add_clause(clause)
