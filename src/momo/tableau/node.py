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

    def add(self, formula):
        self.tl_set.add(formula)

    def remove(self, formula):
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

    def _node_and_expansion(self, formula):
        """Extract all the subformulas from the and formula and add it to the node

        Args:
            formula (Formula | Atom): And formula

        Returns:
            can_expand (Boolean): True if the formula expands correctly, i.e., there are not contradictions
                or inconsistencies.
            added_formulas (List): List of added formulas to remove in case of closed node.
        """
        added_formula = []
        if '0' in formula:
            return False, added_formula
        for element in formula[1]:
            if not self.contradicts(element):
                self.add(element)
                added_formula.append(element)
            else:
                return False, added_formula
        return True, added_formula

    def is_elementary(self):
        return self.tl_set.is_elementary()

    def new_node(self):
        return Node(TlSet(), self.closure, self.branch, self.operations_history)

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
