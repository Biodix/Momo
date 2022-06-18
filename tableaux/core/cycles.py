import collections
from tableaux.tl_basics.tl_set import TlSet


class Cycles:
    def __init__(self, formula, operations_stack):
        stack_set = TlSet()
        stack_set.add(formula)
        self.operations_stack = operations_stack
        self.previous_formulae = collections.deque()
        self.stage_literals = collections.deque()
        self.previous_formulae.append(stack_set)
        self.stage_literals.append(set())
        if formula.is_atom():
            self.stage_literals[-1].add(formula)

    def update(self, formula, next_stage):
        if next_stage:
            if formula not in self.previous_formulae[-1]:
                self.previous_formulae[-1].add(formula)
                if formula.is_atom():
                    self.stage_literals[-1].add(formula)
        else:
            if formula not in self.previous_formulae[-1]:
                self.previous_formulae[-1].add(formula)
                self.operations_stack[-1]['add_previous_formulae'] = formula
                if formula.is_atom():
                    self.stage_literals[-1].add(formula)
                    self.operations_stack[-1]['add_stage_literals'] = formula

    def update2(self, formula, next_stage):
        if next_stage:
            if formula not in self.previous_formulae[-1]:
                self.previous_formulae[-1].add(formula)
                if formula.is_atom():
                    self.stage_literals[-1].add(formula)
        else:
            if formula not in self.previous_formulae[-1]:
                self.previous_formulae[-1].add(formula)
                self.operations_stack[-1]['add_previous_formulae'] = formula
                if formula.is_atom():
                    self.stage_literals[-1].add(formula)
                    self.operations_stack[-1]['add_stage_literals'] = formula

    def rollback(self, next_stage):
        if not next_stage:
            if 'add_previous_formulae' in self.operations_stack[-1]:
                formula = self.operations_stack[-1]['add_previous_formulae']
                self.previous_formulae[-1].remove(formula)
            if 'add_stage_literals' in self.operations_stack[-1]:
                literal = self.operations_stack[-1]['add_stage_literals']
                self.stage_literals[-1].remove(literal)

    def add(self, formula):
        self.previous_formulae[-1].add(formula)
        if formula.is_atom():
            self.stage_literals[-1].add(formula)

    def remove(self, formula):
        if self.operations_stack[-1]['add_previous_formula']:
            self.previous_formulae[-1].remove(formula)
        if self.operations_stack[-1]['add_stage_literals']:
            if formula.is_atom():
                self.stage_literals[-1].remove(formula)
