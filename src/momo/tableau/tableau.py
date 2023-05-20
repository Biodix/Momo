from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet
from momo.tableau.branch import Branch
from momo.tableau.closure import Closure, SatTable
from momo.tableau.node import Node
from multiset import Multiset
from momo.tableau.sat_solver import SatSolver
from momo.tableau.preprocess import process_formula, read_file

import time
from collections import deque

# for sat use enum_models()


class Tableau:
    def __init__(self, initial_formula):
        if isinstance(initial_formula, Formula) or isinstance(initial_formula, Atom):
            self.closure = Closure(initial_formula)
            initial_set = TlSet([initial_formula])
            self.branch = Branch(initial_set)
            self.node = Node(initial_set, self.closure, self.branch, deque())
            self.sat_solver = SatSolver(self)
        elif isinstance(initial_formula, list):
            self.closure = Closure()
            for formula in initial_formula:
                self.closure.build_closure(formula)
            initial_set = TlSet(initial_formula)
            self.branch = Branch(initial_set)
            self.node = Node(initial_set, self.closure, self.branch, deque())
            self.sat_solver = SatSolver(self)

    def basic_step(self):
        formula, multiplicity = self.node.pop_formula()
        sat = False
        if formula.is_and():
            sat = self.and_expansion(formula)
        elif formula.is_always():
            sat = self.always_expansion(formula)
        elif formula.is_or():
            sat = self.or_expansion(formula)
        elif formula.is_release():
            sat = self.release_expansion(formula)
        elif formula.is_eventually():
            sat = self.eventually_expansion(formula)
        elif formula.is_until():
            sat = self.until_expansion(formula)
        else:
            raise Exception("Formula is not valid")
        self.node.push_formula(formula, multiplicity)
        return sat

    def expand(self):
        sat = self.tableau()
        if sat:
            return sat

    def rollback(self, added_formulas):
        for added_formula in added_formulas:
            self.node.remove(added_formula)

    ##########################################
    # And Expansion
    ##########################################

    def _and_rollback(self, updated_elements):
        for updated_element in updated_elements:
            self.node.remove(updated_element)

    def and_expansion(self, formula):
        """Expand the formula removing the formula and addind all and subformulas

        Args:
            formula (Formula | Atom): And formula

        Returns:
            sat: True if a model was found, else False.
        """
        # Expand the formula removing the formula and addind all and (&) subformulas
        can_expand, added_formulas = self._and_expansion(formula)
        if can_expand:
            sat = self.tableau()
            if sat:
                return sat
        self.rollback(added_formulas)
        return False

    def _and_expansion(self, formula):
        """Extract all the subformulas from the and formula and add it to the node

        Args:
            formula (Formula | Atom): And formula

        Returns:
            can_expand (Boolean): True if the formula expands correctly, i.e., there are not contradictions
                or inconsistencies.
            added_formulas (List): List of added formulas to remove in case of closed node.
        """
        added_formula = []
        if "0" in formula:
            return False, added_formula
        for element in formula[1]:
            if not self.node.contradicts(element):
                self.node.add(element)
                added_formula.append(element)
            else:
                return False, added_formula
        return True, added_formula

    ##########################################
    # Always Expansion
    ##########################################

    def always_expansion(self, formula):
        """
        Expands the given formula using the always rule.
        If the expansion is successful, returns the satisfiability of the tableau.
        Otherwise, rolls back the expansion and returns False.

        Args:
            formula: The formula to expand.

        Returns:
            The satisfiability of the tableau if the expansion is successful, False otherwise.
        """
        can_expand, added_formulas = self._always_expansion(formula)
        if can_expand:
            sat = self.tableau()
            if sat:
                return sat
        self.rollback(added_formulas)
        return False

    def _always_expansion(self, formula):
        """
        Expands the given formula and returns a tuple with a boolean indicating whether the formula
        can be expanded and a list of added formulas.

        Args:
            formula: A formula to expand.

        Returns:
            A tuple of a boolean indicating whether the formula can be expanded and a list of added formulas.
        """
        phi = formula[1]
        next_phi = formula.add_operator("X")
        if phi == "0":
            return False, []
        if self.node.contradicts(phi):
            return False, []
        else:
            self.node.add(phi)
            if self.node.contradicts(next_phi):
                return False, [phi]
            else:
                self.node.add(next_phi)
                return True, [phi, next_phi]

    ##########################################
    # Or Expansion
    ##########################################

    def _or_expansion(self, element):
        if element == "0":
            return False
        elif self.node.contradicts(element):
            return False
        else:
            self.node.add(element)
            return element

    def or_expansion(self, formula):
        if "1" in formula[1]:
            return True

        for element in formula[1]:
            added_formula = self._or_expansion(element)
            if added_formula:
                sat = self.tableau()
                if sat:
                    return sat
                else:
                    self.node.remove(added_formula)
        return False

    ##########################################
    # Release Expansion
    ##########################################
    def release_expansion(self, formula):
        can_left_expand, left_expand_added_formulas = self._release_expansion_left(
            formula
        )
        if can_left_expand:
            sat = self.tableau()
            if sat:
                return sat
        self.rollback(left_expand_added_formulas)

        can_right_expand, right_expand_added_formulas = self._release_expansion_right(
            formula
        )
        if can_right_expand:
            sat = self.tableau()
            if sat:
                return sat
        self.rollback(right_expand_added_formulas)
        return False

    def _release_expansion_left(self, formula):
        phi = formula[1]
        psi = formula[2]
        added_formulas = []
        if self.node.contradicts(phi):
            return False, added_formulas
        else:
            self.node.add(phi)
            added_formulas.append(phi)
            if self.node.contradicts(psi):
                return False, added_formulas
            else:
                self.node.add(psi)
                added_formulas.append(psi)
                return True, added_formulas

    def _release_expansion_right(self, formula):
        phi = formula[1]
        psi = formula[2]
        next_of_formula = formula.add_operator("X")
        added_formulas = []
        if self.node.contradicts(psi):
            return False, added_formulas
        else:
            self.node.add(psi)
            added_formulas.append(psi)
            if self.node.contradicts(next_of_formula):
                return False, added_formulas
            else:
                self.node.add(next_of_formula)
                added_formulas.append(next_of_formula)
                return True, added_formulas

    ##########################################
    # Eventually Expansion
    ##########################################
    def _eventually_expansion_left(self, formula):
        phi = formula[1]
        added_formulas = []

        if phi == "0":
            return False, added_formulas
        if self.node.contradicts(phi):
            return False, added_formulas
        else:
            self.node.add(phi)
            # Aqui tengo que hacer algo con las eventualidades
            added_formulas.append(phi)
            return True, added_formulas

    def _eventually_expansion_right(self, formula):
        next_of_formula = formula.add_operator("X")
        added_formulas = []
        if self.node.contradicts(next_of_formula):
            return False, added_formulas
        else:
            self.node.add(next_of_formula)
            added_formulas.append(next_of_formula)
            return True, added_formulas

    def eventually_expansion(self, formula):
        ev_formula = formula[1]
        can_left_expand, left_expand_added_formulas = self._eventually_expansion_left(
            formula
        )
        if can_left_expand:
            fulfilled = self.branch.fulfill_eventuality(ev_formula)
            sat = self.tableau()
            if sat:
                return sat
            else:  # Remove the eventuallity for the set of fullfilled eventualities and add it to the remaining
                self.branch.neglect_eventuality(ev_formula, fulfilled)

        self.rollback(left_expand_added_formulas)

        (
            can_right_expand,
            right_expand_added_formulas,
        ) = self._eventually_expansion_right(formula)
        if can_right_expand:
            sat = self.tableau()
            if sat:
                return sat
        self.rollback(right_expand_added_formulas)
        return False

    ##########################################
    # Until Expansion
    ##########################################

    def _until_expansion_left(self, formula):
        psi = formula[2]
        added_formulas = []
        if psi == "0":
            return False, added_formulas
        if self.node.contradicts(psi):
            return False, added_formulas
        else:
            self.node.add(psi)
            # Aqui tengo que hacer algo con las eventualidades
            added_formulas.append(psi)
            return True, added_formulas

    def _until_expansion_right(self, formula):
        phi = formula[1]
        next_of_formula = formula.add_operator("X")
        added_formulas = []
        if self.node.contradicts(phi):
            return False, added_formulas
        else:
            self.node.add(phi)
            added_formulas.append(phi)
            if self.node.contradicts(next_of_formula):
                return False, added_formulas
            else:
                self.node.add(next_of_formula)
                added_formulas.append(next_of_formula)
                return True, added_formulas

    def until_expansion(self, formula):
        ev_formula = formula[2]
        can_left_expand, left_expand_added_formulas = self._until_expansion_left(
            formula
        )
        if can_left_expand:
            fulfilled = self.branch.fulfill_eventuality(ev_formula)
            sat = self.tableau()
            if sat:
                return sat
            else:  # Remove the eventuallity for the set of fullfilled eventualities and add it to the remaining
                self.branch.neglect_eventuality(ev_formula, fulfilled)
        self.rollback(left_expand_added_formulas)

        can_right_expand, right_expand_added_formulas = self._until_expansion_right(
            formula
        )
        if can_right_expand:
            sat = self.tableau()
            if sat:
                return sat
        self.rollback(right_expand_added_formulas)
        return False

    ##########################################
    # Next Stage
    ##########################################

    def next_stage(self):
        self.branch.append(Multiset())
        can_expand, new_node = self._next_stage()
        if can_expand:
            has_cycle = self.branch.check_cycles(new_node.tl_set)
            if has_cycle:
                return True
            else:
                old_node = self.node
                self.node = new_node
                sat = self.tableau()
                if sat:
                    return sat
                else:
                    self.node = old_node
        self.branch.pop()
        return False

    def _next_stage(self):
        # Creation of new node
        new_node: Node = self.node.new_node()
        added_formulas = []
        for next_element in self.node.tl_set.operators["X"]:
            element = next_element[1]
            if element.is_and():
                # If the element is an and, we try to add directly the and elements
                can_expand, added_formulas = new_node._node_and_expansion(element)
                if not can_expand:
                    return False, self.node
            else:
                if new_node.contradicts(element):
                    return False, self.node
                else:
                    new_node.add(element)
                    added_formulas.append(element)
        return True, new_node

    def sat_expansion(self, phi):
        clauses = self.sat_solver.tl_set_to_sat(phi)
        for model in self.sat_solver.solve(clauses):
            tl_set = self.sat_solver.model_to_tl_set(model)
            for formula in tl_set:
                self.branch.add_to_stage(formula)
                # Augment with new stage
            sat = self.next_stage()
            if sat:
                return sat
        return False

    def tableau(self):
        phi = self.node.tl_set
        sat = False
        if phi.is_empty():
            is_closed, model = False, build_model(self.branch)
        elif phi.is_inconsistent():
            is_closed, proof = True, build_proof(self.branch)
        elif phi.is_sat_elementary():
            # has_cycle = self.branch.check_cycles(self.node.tl_set)
            # if has_cycle:
            #     return True
            if phi.is_elementary():
                # Augment with new stage
                sat = self.next_stage()
            else:
                sat = self.sat_expansion(phi)

        else:
            sat = self.basic_step()

        if sat:
            print("Model Found")
        return sat

    def tableau2(self):
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
                # alpha = ltl2sat(phi)
                # is_sat, sat_model = sat_solver(alpha)
                # while is_sat and is_closed:
                #     sat_phi = sat2ltl(sat_model)
                #     sat_branch = add_to_last_stage(branch, sat_phi)
                #     psi = sat_phi.next_stage()
                #     sat_branch.update(psi)
                #     is_closed, proof, model = tableau(psi, sat_branch)
                #     if is_closed:
                #         proof_list.append(proof)
                #         alpha.add(sat_model.neg())
                #         is_sat, sat_model = sat_solver(alpha)
                #         sat_branch.rollback(psi)
                # proof = build_proof(phi, 'sat', proof_list)
        else:
            self.basic_step()

    # def tableau(self):
    #     phi = self.node.tl_set
    #     if phi.is_empty():
    #         is_closed, model = False, build_model(self.branch)
    #     elif phi.is_inconsistent():
    #         is_closed, proof = True, build_proof(self.branch)
    #     elif phi.is_sat_elementary():
    #         if self.branch.has_fulfill_all_eventualities() and phi in self.branch:
    #             is_closed, model = False, build_model(self.branch)
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
    #         self.basic_step()


def build_model(branch):
    pass


def build_proof(branch):
    pass


def ltl2sat():
    pass


def sat_solver():
    pass


def sat2ltl():
    pass


def add_to_last_stage():
    pass


def test_formula(test_formula):
    formula = process_formula(test_formula)
    tableau = Tableau(formula)
    tableau_result = tableau.tableau()
    del tableau
    return tableau_result


def test_file(file):
    with open(file) as f:
        input_text = f.read()
        input_text = input_text.replace("\n\n", "\n").replace("\n", "").replace(" ", "")
    formula = process_formula(input_text)
    tableau = Tableau(formula)
    tableau_result = tableau.tableau()
    del tableau
    return tableau_result


def execute_tableau(input_file):
    if "." in input_file:
        return test_file(input_file)
    else:
        return test_formula(input_file)

    # Done test('a&-a') # Done test('a&b&c&Gd') # Done test('a&b&G(-a)') # Done test('a|b|c') # Done
    # test('a&b&c')
    # test('(Fc&G-a)|(Xb&-Fb)') test('aRb&-a') test('(G((f0 > -(f1))) & -(u) & f0 & -(b0) & -(b1) & -(up) & G((u = -(
    # X(u)))) & G(((u > ((f0 = X(f0)) & (f1 = X(f1)))) & (f0 > X((f0 | f1))) & (f1 > X((f0 | f1))))) & G(((-(u) > ((
    # b0 = X(b0)) & (b1 = X(b1)))) & ((b0 & -(f0)) > X(b0)) & ((b1 & -(f1)) > X(b1)))) & G((((f0 & X(f0)) > (up = X(
    # up))) & ((f1 & X(f1)) > (up = X(up))) & ((f0 & X(f1)) > up) & ((f1 & X(f0)) > -(up)))) & G((sb = (b0 | b1))) &
    # G((((f0 & -(sb)) > (f0 U (sb | (F(f0) & -(up))))) & ((f1 & -(sb)) > (f1 U (sb | (F(f0) & -(up))))))) & G(((b0 >
    # F(f0)) & (b1 > F(f1)))))') test_file(
    # '/home/daniel/Escritorio/Algorithms/Momo/momo_v1.0/tableaux/test/satisfiable/s14.txt') test('(((a U z ) U b ) U
    # c ) U ( - z ) &F z& G a& G b& F (- c)') test('(F(- d))&(G(F c))&(G(a -> (X(F e))))&(G(c -> (F a)))&(G((F e) ->
    # d))')

    # execute_file('../../benchmarks/crafted/schuppan_O1formula/O1formula200.pltl')

    # execute_file('../../test/antiblack/O1formula8_modified.pltl')


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
