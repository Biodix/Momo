import collections
from momo.tl.tl_set import TlSet
from momo.tl.formula import Formula
from momo.tableau.branch import Branch
from momo.tableau.closure import Closure


class Node:
    def __init__(
        self,
        tl_set: TlSet,
        closure: Closure,
        branch: Branch,
        operations_history: collections.deque,
        marked_eventuality=None,
    ):
        self.tl_set = tl_set
        self.closure = closure
        self.branch = branch
        self.operations_history = operations_history
        self.marked_eventuality = marked_eventuality

    def add(self, formula):
        if formula.is_eventually():
            self.branch.add_remaining_eventuality(formula[1])
        if formula.is_until():
            self.branch.add_remaining_eventuality(formula[2])
        self.tl_set.add(formula)
        self.branch.add_to_stage(formula)

    def remove(self, formula):
        if formula.is_eventually():
            self.branch.remove_remaining_eventuality(formula[1])
        if formula.is_until():
            self.branch.remove_remaining_eventuality(formula[2])
        self.tl_set.remove(formula)
        self.branch.remove_from_stage(formula)

    def contradicts(self, formula: Formula):
        # if formula not in self.closure:
        #     return False
        nnf_neg_formula = self.closure[formula]["nnf"]
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
        if "0" in formula:
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

    def is_sat_elementary(self):
        return self.tl_set.is_sat_elementary()

    def new_node(self):
        branch_remaining_eventualities = self.branch.remaining_eventualities.copy()
        branch_fulfilled_eventualities = self.branch.fulfilled_eventualities.copy()
        branch_literals = self.branch.literals.copy()
        new_branch = Branch(
            remaining_eventualities=branch_remaining_eventualities,
            fulfilled_eventualities=branch_fulfilled_eventualities,
            literals=branch_literals,
        )
        return Node(TlSet(), self.closure, new_branch, self.operations_history)

    def pop_formula(self):
        return self.tl_set.pop_formula()

    def push_formula(self, formula, multiplicity):
        return self.tl_set.push_formula(formula, multiplicity)

    def can_apply_beta_plus(self):
        pass
        # def rollback(self, next_stage=False):
        #     self.closed_nodes.update_closed_nodes(self)
        #     self.cycles.rollback(next_stage)
        #     self.remove_formula()
        #     self.eventualities.rollback()
        #     operations_stack = self.operations_stack
        #     if not next_stage:
        #         operations_stack.pop()
