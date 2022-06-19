import copy
from pysat.solvers import Glucose4
from tableaux.tl_basics.tl_set import TlSet
import z3

class SatSolver:
    def __init__(self, tableau, sat=False, z3=False, get_model=True):
        self.tableau = tableau
        self.sat = sat
        self.z3 = z3
        self.get_model = get_model
        self.sat_models = []


    def z3_implication(self, set_of_formulae1, set_of_formulae2):
        z3_translated_formulae1 = []
        z3_translated_formulae2 = []
        for formula in set_of_formulae1.pp_set:
            z3_translated_formulae1.append(self.z3_sat_translation(formula))
        z3_formula1 = z3.And(z3_translated_formulae1)
        for formula in set_of_formulae2.pp_set:
            z3_translated_formulae2.append(self.z3_sat_translation(formula))
        z3_formula2 = z3.And(z3_translated_formulae2)
        implication = z3.Implies(z3_formula2, z3_formula1)
        z = z3.Solver()
        z.add(implication)
        if z.check().r != -1:
            return True
        else:
            return False

    def z3_sat_translation(self, formula):
        if formula.is_atom():
            formula_to_sat = self.tableau.closure.formula_to_sat[formula]
            if formula_to_sat[0] == '-':
                return z3.Not(z3.Bool(formula_to_sat[1:]))
            else:
                return z3.Bool(formula_to_sat)

        else:
            if formula.is_and():
                aux = []
                for subformula in formula[1]:
                    aux.append(self.z3_sat_translation(subformula))
                return z3.And(aux)
            elif formula.is_or():
                aux = []
                for subformula in formula[1]:
                    aux.append(self.z3_sat_translation(subformula))
                return z3.Or(aux)


    def translation(self, node):
        g = Glucose4()
        closure = node.closure.closure
        formula_to_sat = {}
        sat_to_formula = {}
        sat_index = 0
        formulae = TlSet()

        for formula in node.formulae_operators['|']:
            clause = []
            for subformula in formula[1]:
                if subformula == '1':
                    break
                elif subformula == '0':
                    continue
                elif subformula in formula_to_sat:
                    clause.append(formula_to_sat[subformula])
                else:
                    if subformula in closure:
                        nnf_subformula = closure[subformula]['nnf']
                    else:
                        nnf_subformula = subformula.neg().nnf()
                    if nnf_subformula in formula_to_sat:
                        clause.append(-formula_to_sat[nnf_subformula])
                    else:
                        sat_index += 1
                        formula_to_sat[subformula] = sat_index
                        formula_to_sat[nnf_subformula] = -sat_index
                        sat_to_formula[sat_index] = subformula
                        sat_to_formula[-sat_index] = nnf_subformula
                        clause.append(sat_index)
                formulae.add(subformula)
            g.add_clause(clause)
        for formula in node.formulae_operators['X']:
            clause = []
            if formula in formula_to_sat:
                clause.append(formula_to_sat[formula])
            else:
                if formula in closure:
                    nnf_formula = closure[formula]['nnf']
                else:
                    nnf_formula = formula.neg().nnf()
                if nnf_formula in formula_to_sat:
                    clause.append(-formula_to_sat[nnf_formula])
                else:
                    sat_index += 1
                    formula_to_sat[formula] = sat_index
                    formula_to_sat[nnf_formula] = -sat_index
                    sat_to_formula[sat_index] = formula
                    sat_to_formula[-sat_index] = nnf_formula
                    clause.append(sat_index)
            formulae.add(formula)
            g.add_clause(clause)
        for literal in node.formulae_operators['L']:
            clause = []
            if literal in formula_to_sat:
                clause.append(formula_to_sat[literal])
            elif closure[literal]['nnf'] in formula_to_sat:
                clause.append(-formula_to_sat[closure[literal]['nnf']])
            else:
                sat_index += 1
                formula_to_sat[literal] = sat_index
                formula_to_sat[closure[literal]['nnf']] = -sat_index
                sat_to_formula[sat_index] = literal
                sat_to_formula[-sat_index] = closure[literal]['nnf']
                clause.append(sat_index)
            formulae.add(literal)
            g.add_clause(clause)
        return g

    def call_sat_no_model(self, node):
        traces = node.traces
        closure = node.closure.closure

        traces.path.add_rule('Sat-Solver no model')
        traces.path.add_selected_formula('')
        traces.sat_trace(node)

        g = self.translation(node)
        if g.solve():
            self.sat_models.append(g)
            if self.tableau.solve():
                return True

    def get_models(self):
        while self.sat_models:
            g = self.sat_models.pop()
            model = g.get_model()
            print(model)


    def call_z3_sat(self, node):
        traces = node.traces

        traces.path.add_rule('Sat-Solver')
        traces.path.add_selected_formula('')
        traces.sat_trace(node)
        z = z3.Solver()
        if len(node.set_of_formulae.pp_set) <= 1:
            z.add(self.z3_sat_translation(next(iter(node.set_of_formulae.pp_set))))
            node.sat_models_stack.append(z)
            if self.tableau.rules.next_stage(node):
                return True
            node.sat_models_stack.pop()
            return False

        z3_translated_formulae = []
        for formula in node.set_of_formulae.pp_set:
            z3_translated_formulae.append(self.z3_sat_translation(formula))
        z3_formula = z3.And(z3_translated_formulae)
        z.add(z3_formula)
        if z.check().r != -1:
            node.sat_models_stack.append(z)
            if self.tableau.rules.next_stage(node):
                return True
            node.sat_models_stack.pop()
        return False


    def call_sat_without_model(self, node):
        traces = node.traces

        traces.path.add_rule('Sat-Solver')
        traces.path.add_selected_formula('')
        traces.sat_trace(node)

        closure = node.closure.closure
        g = Glucose4()
        formula_to_sat = {}
        sat_to_formula = {}
        sat_index = 0
        formulae = TlSet()

        for formula in node.formulae_operators['|']:
            clause = []
            for subformula in formula[1]:
                if subformula == '1':
                    break
                elif subformula == '0':
                    continue
                elif subformula in formula_to_sat:
                    clause.append(formula_to_sat[subformula])
                else:
                    if subformula in closure:
                        nnf_subformula = closure[subformula]['nnf']
                    else:
                        nnf_subformula = subformula.neg().nnf()
                    if nnf_subformula in formula_to_sat:
                        clause.append(-formula_to_sat[nnf_subformula])
                    else:
                        sat_index += 1
                        formula_to_sat[subformula] = sat_index
                        formula_to_sat[nnf_subformula] = -sat_index
                        sat_to_formula[sat_index] = subformula
                        sat_to_formula[-sat_index] = nnf_subformula
                        clause.append(sat_index)
                formulae.add(subformula)
            g.add_clause(clause)
        for literal in node.formulae_operators['L']:
            clause = []
            if literal in formula_to_sat:
                clause.append(formula_to_sat[literal])
            elif closure[literal]['nnf'] in formula_to_sat:
                clause.append(-formula_to_sat[closure[literal]['nnf']])
            else:
                sat_index += 1
                formula_to_sat[literal] = sat_index
                formula_to_sat[closure[literal]['nnf']] = -sat_index
                sat_to_formula[sat_index] = literal
                sat_to_formula[-sat_index] = closure[literal]['nnf']
                clause.append(sat_index)
            formulae.add(literal)
            g.add_clause(clause)
        if g.solve():
            node.sat_models_stack.append(g)
            if self.tableau.rules.next_stage(node):
                return True
            node.sat_models_stack.pop()
        return False

    def call_sat(self, node):
        traces = node.traces

        traces.path.add_rule('Sat-Solver')
        traces.path.add_selected_formula('')
        traces.sat_trace(node)

        closure = node.closure.closure
        g = Glucose4()
        formula_to_sat = {}
        sat_to_formula = {}
        sat_index = 0
        formulae = TlSet()

        for formula in node.formulae_operators['|']:
            clause = []
            for subformula in formula[1]:
                if subformula == '1':
                    break
                elif subformula == '0':
                    continue
                elif subformula in formula_to_sat:
                    clause.append(formula_to_sat[subformula])
                else:
                    if subformula in closure:
                        nnf_subformula = closure[subformula]['nnf']
                    else:
                        nnf_subformula = subformula.neg().nnf()
                    if nnf_subformula in formula_to_sat:
                        clause.append(-formula_to_sat[nnf_subformula])
                    else:
                        sat_index += 1
                        formula_to_sat[subformula] = sat_index
                        formula_to_sat[nnf_subformula] = -sat_index
                        sat_to_formula[sat_index] = subformula
                        sat_to_formula[-sat_index] = nnf_subformula
                        clause.append(sat_index)
                formulae.add(subformula)
            g.add_clause(clause)
        for formula in node.formulae_operators['X']:
            clause = []
            if formula in formula_to_sat:
                clause.append(formula_to_sat[formula])
            else:
                if formula in closure:
                    nnf_formula = closure[formula]['nnf']
                else:
                    nnf_formula = formula.neg().nnf()
                if nnf_formula in formula_to_sat:
                    clause.append(-formula_to_sat[nnf_formula])
                else:
                    sat_index += 1
                    formula_to_sat[formula] = sat_index
                    formula_to_sat[nnf_formula] = -sat_index
                    sat_to_formula[sat_index] = formula
                    sat_to_formula[-sat_index] = nnf_formula
                    clause.append(sat_index)
            formulae.add(formula)
            g.add_clause(clause)
        for literal in node.formulae_operators['L']:
            clause = []
            if literal in formula_to_sat:
                clause.append(formula_to_sat[literal])
            elif closure[literal]['nnf'] in formula_to_sat:
                clause.append(-formula_to_sat[closure[literal]['nnf']])
            else:
                sat_index += 1
                formula_to_sat[literal] = sat_index
                formula_to_sat[closure[literal]['nnf']] = -sat_index
                sat_to_formula[sat_index] = literal
                sat_to_formula[-sat_index] = closure[literal]['nnf']
                clause.append(sat_index)
            formulae.add(literal)
            g.add_clause(clause)

        set_of_formulae_copy = node.set_of_formulae.copy()
        #print(node.formulae_operators)
        operators_in_formulas_copy = copy.deepcopy(node.formulae_operators)
        eventualities_copy = node.eventualities.copy()
        i = 1
        while g.solve():
            model = g.get_model()
            #node.set_of_formulae = set_of_formulae_copy.copy()
            node.formulae_operators = copy.deepcopy(operators_in_formulas_copy)
            node.set_of_formulae = TlSet()
            node.formulae_operators['|'] = TlSet()
            node.formulae_operators['L'] = TlSet()
            node.formulae_operators['X'] = TlSet()
            node.eventualities = eventualities_copy.copy()
            model_negation = []
            for sat_formula in model:
                formula = sat_to_formula[sat_formula]
                model_negation.append(-sat_formula)
                if formula in formulae:
                    node.update(formula, True)
            traces.sat_trace_i(node, set_of_formulae_copy, i)
            if self.tableau.solve():
                return True
            else:
                i += 1
                g.add_clause(model_negation)
                self.tableau.closed_nodes.update_closed_nodes(node)
        node.eventualities = eventualities_copy
        node.set_of_formulae = set_of_formulae_copy
        node.formulae_operators = operators_in_formulas_copy
        traces.path.add_rule('SAT-Solver fail')
        traces.path.add_selected_formula('')
        # print(debugging_set)
        return False


#
# import time
# import z3
#
# x = z3.Bool('1')
# y = z3.Bool('2')
# z = z3.Bool('3')
# x_or_y = z3.Or([x, y])
# not_x = z3.Not(x)
# not_z = z3.Not(z)
# s = z3.Solver()
# s.add(x_or_y)
# s.add(not_x)
# s.add(not_z)
#
# ini = time.time()
# s.check()
# print(s.model())
# end = time.time() - ini
# print(end)
#
# g = Glucose4()
# g.add_clause([1, 2])
# g.add_clause([-2])
# g.add_clause([-3])
#
# ini2 = time.time()
# g.solve()
# print(g.get_model())
# end2 = ini2 - time.time()
# print(end2)
#
# solver = z3.Solver()
