from momo.tl.formula import Formula
from momo.tl.tl_set import TlSet
from momo.tableau.branch import Branch
from momo.tableau.closure import Closure, SatTable
from momo.tableau.node import Node

from collections import deque
# for sat use enum_models()


class Tableau:
    def __init__(self, initial_formula: Formula):
        self.closure = Closure(initial_formula)
        initial_set = TlSet([initial_formula])
        self.branch = Branch(initial_set)
        self.node = Node(initial_set,
                         self.closure, self.branch, deque())

    def basic_step(self):
        can_expand = None
        formula = self.node.pop_formula()
        if formula.is_and():
            can_expand = self.and_expansion(formula)
        if formula.is_always():
            can_expand = self.always_expansion(formula)
        # if formula.is_or():
        #     sat, proof = or_expansion(formula, branch)
        # if formula.is_release():
        #     sat, proof = release_expansion(formula, branch)
        # if formula.is_eventually():
        #     sat, proof = eventually_expansion(formula, branch)
        # if formula.is_until():
        #     sat, proof = until_expansion(formula, branch)
        assert can_expand != None
        if can_expand:
            sat = self.tableau()
            return sat
        else:
            return False

    def _and_rollback(self, updated_elements):
        for updated_element in updated_elements:
            self.node.remove(updated_element)

    def and_expansion(self, formula):
        # self.traces.path.add_rule('And expansion')
        # self.traces.path.add_selected_formula(formula)
        # TODO: revisar el otro todo de abajo, aqui no se ha deshecho el cambio en caso de sat=false, hay que tratarlo de alguna forma
        if '0' in formula:
            return False
        updated_elements = []
        for element in formula[1]:
            if not self.node.contradicts(element):
                self.node.add(element)
                updated_elements.append(element)
            else:
                self._and_rollback(updated_elements)
                return False
        return True

    ##########################################
    # Always Expansion
    ##########################################
    # TODO: Hay que pensar que hacer con el rollback si sat = false, o se hace en la propia función, o hay que devolver algo para deshacer el cambio
    def always_expansion(self, formula):
        phi = formula[1]
        next_phi = formula.add_operator('X')
        if phi == '0':
            return False
        if self.node.contradicts(phi):
            return False
        else:
            self.node.add(phi)
            if self.node.contradicts(next_phi):
                self.node.remove(phi)
                return False
            else:
                self.node.add(next_phi)
                sat = self.tableau()
                if sat:
                    return True
                else:
                    self.node.remove(next_phi)
                    self.node.remove(phi)
        return False

    def _or_expansion(self, formula):
        # self.traces.path.add_rule('And expansion')
        # self.traces.path.add_selected_formula(formula)
        if '0' in formula:
            return False
        updated_elements = []
        for element in formula[1]:
            if not self.node.contradicts(element):
                self.node.add(element)
                updated_elements.append(element)
            else:
                self._or_rollback(updated_elements)
                return False
        sat = self.tableau.solve()
        return False

    def tableau(self):
        phi = self.node.tl_set
        if phi.is_empty():
            is_closed, model = False, build_model(self.branch)
        elif phi.is_inconsistent():
            is_closed, proof = True, build_proof(self.branch)
        elif phi.is_sat_elementary():
            if self.branch.has_fulfill_all_eventualities() and phi in self.branch:
                is_closed, model = False, build_model(self.branch)
            if phi.is_elementary():
                return True
                psi = phi.next_stage()
                branch.append(psi)
                is_closed, proof, model = tableau(psi, branch)
                if is_closed:
                    # proof = build_proof(phi, 'X', proof)
                    branch.pop()
            else:
                is_closed, proof_list = True, []
                alpha = ltl2sat(phi)
                is_sat, sat_model = sat_solver(alpha)
                while is_sat and is_closed:
                    sat_phi = sat2ltl(sat_model)
                    sat_branch = add_to_last_stage(branch, sat_phi)
                    psi = sat_phi.next_stage()
                    sat_branch.update(psi)
                    is_closed, proof, model = tableau(psi, sat_branch)
                    if is_closed:
                        proof_list.append(proof)
                        alpha.add(sat_model.neg())
                        is_sat, sat_model = sat_solver(alpha)
                        sat_branch.rollback(psi)
                # proof = build_proof(phi, 'sat', proof_list)
        else:
            self.basic_step()


def build_model(branch):
    pass


def build_proof(branch):
    pass


def tableau_expansion(formula: Formula, branch: Branch):
    if formula.is_and():
        sat, proof = _and_expansion(formula, branch)
        if sat:
            return True, 1
    elif formula.is_always():
        sat, proof = self.rules.always_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_or():
        sat, proof = self.rules.or_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_release():
        sat, proof = self.rules.release_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_eventually():
        sat, proof = self.rules.eventually_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_until():
        sat, proof = self.rules.until_expansion(formula, node)
        if sat:
            return True, 1
    else:
        return True, 1


def ltl2sat():
    pass


def sat_solver():
    pass


def sat2ltl():
    pass


def add_to_last_stage():
    pass


# def tableau(phi: TlSet, branch: Branch):
#     print(phi)
#     if phi.is_empty():
#         is_closed, model = False, build_model(branch)
#     elif phi.is_inconsistent():
#         is_closed, proof = True, build_proof(branch)
#     elif phi.is_sat_elementary():
#         if branch.has_fulfill_all_eventualities() and phi in branch:
#             is_closed, model = False, build_model(branch)
#         if phi.is_elementary():
#             return True
#             psi = phi.next_stage()
#             branch.append(psi)
#             is_closed, proof, model = tableau(psi, branch)
#             if is_closed:
#                 # proof = build_proof(phi, 'X', proof)
#                 branch.pop()
#         else:
#             is_closed, proof_list = True, []
#             alpha = ltl2sat(phi)
#             is_sat, sat_model = sat_solver(alpha)
#             while is_sat and is_closed:
#                 sat_phi = sat2ltl(sat_model)
#                 sat_branch = add_to_last_stage(branch, sat_phi)
#                 psi = sat_phi.next_stage()
#                 sat_branch.update(psi)
#                 is_closed, proof, model = tableau(psi, sat_branch)
#                 if is_closed:
#                     proof_list.append(proof)
#                     alpha.add(sat_model.neg())
#                     is_sat, sat_model = sat_solver(alpha)
#                     sat_branch.rollback(psi)
#             # proof = build_proof(phi, 'sat', proof_list)
#     else:
#         formula = phi.pop_formula()
#         tableau_expansion(formula, branch)
