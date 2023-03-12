import collections
from momo.tl.tl_set import TlSet
from momo.tl.formula import Formula
from momo.tableau.branch import Branch
from momo.tableau.closure import Closure


class Node:
    def __init__(self, tl_set: TlSet, closure: Closure, branch: Branch, operations_history: collections.deque):
        self.tl_set = tl_set
        self.closure = closure
        self.branch = branch
        self.operations_history = operations_history

    def add(self, formula: Formula):
        self.tl_set.add(formula)

    def remove(self, formula: Formula):
        self.tl_set.remove(formula)

    def contradicts(self, formula: Formula):
        # if formula not in self.closure:
        #     return False
        nnf_neg_formula = self.closure[formula]['nnf']
        if nnf_neg_formula in self.tl_set:
            # self.traces.contradiction(formula, nnf_neg_formula)
            return True
        else:
            return False

    def pop_formula(self):
        return self.tl_set.pop_formula()
    # def rollback(self, next_stage=False):
    #     self.closed_nodes.update_closed_nodes(self)
    #     self.cycles.rollback(next_stage)
    #     self.remove_formula()
    #     self.eventualities.rollback()
    #     operations_stack = self.operations_stack
    #     if not next_stage:
    #         operations_stack.pop()
