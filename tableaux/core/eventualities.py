import tableaux.utils.multiset as multiset
from tableaux.tl_basics.tl_set import TlSet


class Eventualities:
    def __init__(self, eventualities=None, remaining=None, fulfilled=None, stage_eventualities=None,
                 operations_stack=None):
        self.remaining = remaining if remaining else set()
        self.fulfilled = fulfilled if fulfilled else set()
        self.stage_eventualities = stage_eventualities if stage_eventualities else set()
        self.eventualities = {}
        self.operations_stack = operations_stack

        if eventualities:
            if type(eventualities) == Eventualities:
                self.eventualities = eventualities
            else:
                for ev in eventualities:
                    self.eventualities[ev] = set()

    def copy(self):
        return Eventualities(self.eventualities.copy(), self.remaining.copy(), self.fulfilled.copy(),
                             self.stage_eventualities.copy(), self.operations_stack)

    def update(self, formula, next_stage):
        if next_stage:
            if formula.is_eventually():
                if formula[1] not in self.remaining and formula[1] not in self.fulfilled:
                    self.remaining.add(formula[1])
                if formula not in self.eventualities[formula[1]]:
                    self.eventualities[formula[1]].add(formula)
            elif formula.is_until():
                if formula[2] not in self.remaining and formula[2] not in self.fulfilled:
                    self.remaining.add(formula[2])
                if formula not in self.eventualities[formula[2]]:
                    self.eventualities[formula[2]].add(formula)
            else:
                return
        else:
            if formula.is_eventually():
                if formula[1] not in self.remaining and formula[1] not in self.fulfilled:
                    self.operations_stack[-1]['add_remaining_eventuality'] = formula[1]
                    self.remaining.add(formula[1])
                if formula not in self.eventualities[formula[1]]:
                    self.operations_stack[-1]['add_eventuality'] = formula
                    self.eventualities[formula[1]].add(formula)
            elif formula.is_until():
                if formula[2] not in self.remaining and formula[2] not in self.fulfilled:
                    self.operations_stack[-1]['add_remaining_eventuality'] = formula[2]
                    self.remaining.add(formula[2])
                if formula not in self.eventualities[formula[2]]:
                    self.operations_stack[-1]['add_eventuality'] = formula
                    self.eventualities[formula[2]].add(formula)
            else:
                return

    def add(self, eventuality):
        if eventuality.is_until():
            self.eventualities[eventuality[2]].add(eventuality)
            if not self.fulfilled:
                self.remaining.add(eventuality[2])
        if eventuality.is_eventually():
            self.eventualities[eventuality[1]].add(eventuality)
            if not self.fulfilled:
                self.remaining.add(eventuality[1])

    def remove(self, eventuality):
        if eventuality.is_until():
            self.eventualities[eventuality[2]].remove(eventuality)
            if not self.eventualities[eventuality[2]] and eventuality[2] in self.remaining:
                self.remaining.remove(eventuality[2])
        if eventuality.is_eventually() and eventuality[1] in self.remaining:
            self.eventualities[eventuality[1]].remove(eventuality)
            if not self.eventualities[eventuality[1]]:
                self.remaining.remove(eventuality[1])

    def fulfill(self, formula):
        eventuality = formula[2] if formula.is_until() else formula[1]
        self.operations_stack.append({})
        if eventuality in self.remaining:
            self.remaining.remove(eventuality)
            self.operations_stack[-1]['remove_remaining_eventuality'] = eventuality
        if eventuality not in self.fulfilled:
            self.fulfilled.add(eventuality)
            self.operations_stack[-1]['add_fulfilled_eventuality'] = eventuality
        if formula.is_until() and formula not in self.stage_eventualities:
            self.stage_eventualities.add(formula)
            self.operations_stack[-1]['add_stage_eventuality'] = formula

    def neglect(self):
        if 'remove_remaining_eventuality' in self.operations_stack[-1]:
            remaining_ev = self.operations_stack[-1]['remove_remaining_eventuality']
            self.remaining.add(remaining_ev)
        if 'add_fulfilled_eventuality' in self.operations_stack[-1]:
            fulfilled_ev = self.operations_stack[-1]['add_fulfilled_eventuality']
            self.fulfilled.remove(fulfilled_ev)
        if 'add_stage_eventuality' in self.operations_stack[-1]:
            stage_ev = self.operations_stack[-1]['add_stage_eventuality']
            self.stage_eventualities.remove(stage_ev)
        self.operations_stack.pop()

    def rollback(self):
        if 'add_remaining_eventuality' in self.operations_stack[-1]:
            remaining_ev = self.operations_stack[-1]['add_remaining_eventuality']
            self.remaining.remove(remaining_ev)
        if 'add_eventuality' in self.operations_stack[-1]:
            ev = self.operations_stack[-1]['add_eventuality']
            self.eventualities[ev[1]].remove(ev) if ev.is_eventually() else self.eventualities[ev[2]].remove(ev)

    def fulfill_eventuality(self, ev, psi):
        if psi in self.remaining:
            self.remaining.remove(psi)
            self.fulfilled.add(psi)
            return True
        else:
            return False

    def neglect_eventuality(self, ev):
        if ev in self.fulfilled:
            self.fulfilled.remove(ev)
            return True
        else:
            return False
