import tableaux.improvemets.subsumption as subsumption
import random
import collections
import copy
from itertools import islice
from tableaux.core.eventualities import Eventualities
from tableaux.core.closure import Closure
from tableaux.tl_basics.tl_set import TlSet
from tableaux.core.cycles import Cycles


class Node:
    def __init__(self, formula=None, eventualities=None, marked_until=None, depth=None, closure=None, cycles=None, sat_solver = None,
                 operations_stack=None, configuration=None, closed_nodes=None, traces=None):

        self.set_of_formulae = TlSet()
        self.formulae_operators = {'U': TlSet(), 'R': TlSet(), '&': TlSet(), '|': TlSet(),
                                   'G': TlSet(), 'F': TlSet(), 'X': TlSet(), 'L': TlSet()}
        self.operations_stack = operations_stack if operations_stack else collections.deque()
        self.sat_models_stack = collections.deque()
       
        if type(eventualities) == Eventualities:
            self.eventualities = eventualities
            self.eventualities = eventualities.copy()
            self.eventualities.stage_eventualities = TlSet()
        else:
            self.eventualities = Eventualities(eventualities=eventualities, operations_stack=self.operations_stack)
        self.marked_until = marked_until if marked_until else None
        self.closed_nodes = closed_nodes
        self.depth = depth if depth else 0
        self.sat_solver = sat_solver
        if formula:
            self.closure = closure if closure else Closure(formula)
            self.cycles = cycles if cycles else Cycles(formula, self.operations_stack)
            self.update(formula)
        else:
            self.closure = closure
            self.cycles = cycles
        if configuration:
            self.configuration = configuration
        else:
            self.configuration = {'execution_type': 0, 'sat_solver': True, 'non_determinism': False, 'z3': False}
        self.traces = traces



    def __del__(self):
        self.cycles.previous_formulae.pop()
        self.cycles.stage_literals.pop()

    def is_pp_set(self):
        return True if len(self.set_of_formulae.tl_set) == len(self.formulae_operators['X']) else False

    def new_node(self):
        new_node = Node(eventualities=self.eventualities, closure=self.closure, cycles=self.cycles,
                        operations_stack=self.operations_stack, closed_nodes=self.closed_nodes, sat_solver=self.sat_solver, configuration=self.configuration, traces=self.traces)
        new_node.cycles.previous_formulae.append(TlSet())
        new_node.cycles.stage_literals.append(TlSet())
        new_node.depth = self.depth
        new_node.marked_until = self.marked_until
        return new_node

    def contains_cycle_copy(self):
        if self.eventualities.remaining:
            return False
        else:
            stage_nodes = self.cycles.previous_formulae
            for stage_node in islice(stage_nodes, 0, len(stage_nodes) - 1):
                if self.set_of_formulae.issubset(stage_node):
                    return True
            return False

    def issubset_enhanced(self, set_of_formulae2):
        if self.sat_solver.z3:
            set_of_formulae1 = self.set_of_formulae
            if set_of_formulae1.issubset(set_of_formulae2):
                if self.sat_solver.z3_implication(set_of_formulae1, set_of_formulae2):
                    return True
            return False
        else:
            return self.set_of_formulae.issubset(set_of_formulae2)

    def contains_cycle_sat2(self):
        if self.eventualities.remaining:
            return False
        else:
            stage_nodes = self.cycles.previous_formulae
            for stage_node in islice(stage_nodes, 0, len(stage_nodes) - 1):
                if self.set_of_formulae.issubset(stage_node):
                    return True
            return False

    def contains_cycle(self):
        if self.eventualities.remaining:
            return False
        else:
            stage_nodes = self.cycles.previous_formulae
            for stage_node in islice(stage_nodes, 0, len(stage_nodes) - 1):
                if self.issubset_enhanced(stage_node):
                    return True
            return False

    def add_formula(self, formula, next_stage):
        if next_stage:
            if formula not in self.set_of_formulae:
                self.set_of_formulae.add(formula)
                self.formulae_operators[formula.operator()].add(formula)
        else:
            if formula not in self.set_of_formulae:
                self.operations_stack[-1]['add_formula'] = formula
                self.set_of_formulae.add(formula)
                self.formulae_operators[formula.operator()].add(formula)

    def remove_formula(self):
        if 'add_formula' in self.operations_stack[-1]:
            formula = self.operations_stack[-1]['add_formula']
            self.set_of_formulae.remove(formula)
            self.formulae_operators[formula.operator()].remove(formula)

    def update(self, formula, no_stack=False):
        if not no_stack:
            operations_stack = self.operations_stack
            operations_stack.append({})
        self.cycles.update(formula, no_stack)
        self.add_formula(formula, no_stack)
        self.eventualities.update(formula, no_stack)

    def rollback(self, next_stage=False):
        self.closed_nodes.update_closed_nodes(self)
        self.cycles.rollback(next_stage)
        self.remove_formula()
        self.eventualities.rollback()
        operations_stack = self.operations_stack
        if not next_stage:
            operations_stack.pop()

    def contradicts(self, formula):
        if formula not in self.closure.closure:
            return False
        nnf_neg_formula = self.closure.closure[formula]['nnf']
        if nnf_neg_formula in self.set_of_formulae:
            self.traces.contradiction(formula, nnf_neg_formula)
            return True
        else:
            return False

    def is_elemental(self):
        return len(self.formulae_operators['X']) + len(self.formulae_operators['L']) == len(self.set_of_formulae)

    def remove_marked_until(self):
        marked_until = self.marked_until
        self.marked_until = None
        return marked_until

    # TODO: aun hay que determinar que hacer con el quasi elemental
    def is_quasi_elemental(self):
        return (len(self.formulae_operators['X']) + len(self.formulae_operators['L']) + len(
            self.formulae_operators['|']) == len(self.set_of_formulae)) and len(self.formulae_operators['|']) > 0

    def is_quasi_elemental2(self):
        return len(self.formulae_operators['X']) + len(self.set_of_formulae.pp_set) == len(self.set_of_formulae)

    def contains_marked_until(self):
        return self.marked_until in self.set_of_formulae

    def push_formula(self, formula):
        # if formula.is_eventually():
        #     print('bbb')
        #     pass
        # elif formula.is_until():
        #     print('aa')
        #     pass
        self.set_of_formulae.add(formula)
        self.formulae_operators[formula.operator()].add(formula)
        if formula.is_eventually():
            if formula[1] not in self.eventualities.fulfilled:
                self.eventualities.remaining.add(formula[1])
            self.eventualities.eventualities[formula[1]].add(formula)
        elif formula.is_until():
            if formula[2] not in self.eventualities.fulfilled:
                self.eventualities.remaining.add(formula[2])
            self.eventualities.eventualities[formula[2]].add(formula)

    def pop_formula(self, formula=None):
        if formula:
            self.formulae_operators[formula.operator()].remove(formula)
            self.set_of_formulae.remove(formula)
            if formula == self.marked_until:
                self.marked_until = None
            return formula
        else:
            if self.configuration['z3']:
                if self.formulae_operators['U']:
                    selected_formula = random.sample(self.formulae_operators['U'], 1)[0]
                    self.formulae_operators['U'].remove(selected_formula)
                elif self.formulae_operators['F']:
                    selected_formula = random.sample(self.formulae_operators['F'], 1)[0]
                    self.formulae_operators['F'].remove(selected_formula)
                elif self.formulae_operators['G']:
                    selected_formula = random.sample(self.formulae_operators['G'], 1)[0]
                    self.formulae_operators['G'].remove(selected_formula)
                elif self.formulae_operators['R']:
                    selected_formula = random.sample(self.formulae_operators['R'], 1)[0]
                    self.formulae_operators['R'].remove(selected_formula)
                elif self.formulae_operators['&']:
                    selected_formula = random.sample(self.formulae_operators['&'].tl_set, 1)[0]
                    self.formulae_operators['&'].remove(selected_formula)
                else:
                    selected_formula = random.sample(self.formulae_operators['|'].tl_set, 1)[0]
                    self.formulae_operators['|'].remove(selected_formula)
            elif self.configuration['non_determinism']:
                if self.formulae_operators['U']:
                    selected_formula = random.sample(self.formulae_operators['U'], 1)[0]
                    self.formulae_operators['U'].remove(selected_formula)
                elif self.formulae_operators['F']:
                    selected_formula = random.sample(self.formulae_operators['F'], 1)[0]
                    self.formulae_operators['F'].remove(selected_formula)
                elif self.formulae_operators['&']:
                    selected_formula = random.sample(self.formulae_operators['&'], 1)[0]
                    self.formulae_operators['&'].remove(selected_formula)
                elif self.formulae_operators['G']:
                    selected_formula = random.sample(self.formulae_operators['G'], 1)[0]
                    self.formulae_operators['G'].remove(selected_formula)
                elif self.formulae_operators['R']:
                    selected_formula = random.sample(self.formulae_operators['R'], 1)[0]
                    self.formulae_operators['R'].remove(selected_formula)
                else:
                    selected_formula = random.sample(self.formulae_operators['|'], 1)[0]
                    self.formulae_operators['|'].remove(selected_formula)
            else:
                if self.formulae_operators['U']:
                    selected_formula = self.formulae_operators['U'].pop()
                elif self.formulae_operators['F']:
                    selected_formula = self.formulae_operators['F'].pop()
                elif self.formulae_operators['&']:
                    selected_formula = self.formulae_operators['&'].pop()
                elif self.formulae_operators['G']:
                    selected_formula = self.formulae_operators['G'].pop()
                elif self.formulae_operators['R']:
                    selected_formula = self.formulae_operators['R'].pop()
                else:
                    selected_formula = self.formulae_operators['|'].pop()
            self.set_of_formulae.remove(selected_formula)
            return selected_formula

    def have_until(self):
        return self.formulae_operators['U']

    def have_eventually(self):
        return self.formulae_operators['F']

    def get_eventually(self):
        if self.eventualities.remaining:
            if self.configuration['non_determinism']:
                ev = random.sample(self.eventualities.remaining, 1)[0]
                selected_formula = random.sample(self.eventualities.eventualities[ev], 1)[0]
            else:
                ev = self.eventualities.remaining.pop()
                selected_formula = self.eventualities.eventualities[ev].pop()
            # readme: aqui en vez de remove habia un discar, por si falla
            if selected_formula.is_until():
                self.formulae_operators['U'].remove(selected_formula)
            else:
                self.formulae_operators['F'].remove(selected_formula)
        else:
            if self.have_until():
                operator = 'U'
            else:
                operator = 'F'
            if self.configuration['non_determinism']:
                selected_formula = self.formulae_operators[operator].pop()
            else:
                selected_formula = random.sample(self.formulae_operators[operator], 1)[0]
                self.formulae_operators[operator].remove(selected_formula)
        self.set_of_formulae.remove(selected_formula)
        return selected_formula

    def eventually_subsumption(self, formula):
        if formula.is_eventually():
            phi_1 = '1'
            psi_1 = formula[1]
        else:
            phi_1 = formula[1]
            psi_1 = formula[2]
        for eventuality in self.eventualities.stage_eventualities:
            phi_2 = eventuality[1]
            psi_2 = eventuality[2]
            if psi_1 == psi_2:
                phi = subsumption.subsumption(phi_1, phi_2)
                return True if phi == phi_2 else False
        return False
