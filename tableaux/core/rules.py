from tableaux.core.node import Node
from tableaux.improvemets.subsumption import until_plus_subsumption, nnf_set
from tableaux.tl_basics.formula import Formula, Atom


def and_rollback(node, updated_elements):
    for _ in updated_elements:
        node.rollback()

def build_until(neg_context, phi):
    if len(neg_context) > 1:
        formula = Formula(('&', frozenset(neg_context)))
    elif len(neg_context) == 1:
        formula = neg_context.pop()
    else:
        formula = Atom('0')
    next_of_until = formula.add_operator('U', phi)
    return next_of_until


class Rules:
    def __init__(self, tableau, closure, traces):
        self.tableau = tableau
        self.closure = closure
        self.traces = traces

    ##########################################
    # And Expansion
    ##########################################
    def and_expansion(self, formula, node):
        self.traces.path.add_rule('And expansion')
        self.traces.path.add_selected_formula(formula)
        if '0' in formula:
            return False
        updated_elements = []
        for element in formula[1]:
            if element == '1':  # Si vemos un 1 no lo añadimos, 1 and a equiv a.
                continue
            elif not node.contradicts(element):
                node.update(element)
                updated_elements.append(element)
            else:
                and_rollback(node, updated_elements)
                return False
        if self.tableau.solve():
            return True
        and_rollback(node, updated_elements)
        return False

    ##########################################
    # Always Expansion
    ##########################################
    def always_expansion(self, formula, node):
        self.traces.path.add_rule('Always expansion')
        self.traces.path.add_selected_formula(formula)
        phi = formula[1]
        next_of_formula = formula.add_operator('X')
        if phi == '0':
            return False
        if node.contradicts(phi):
            return False
        else:
            node.update(phi)
            if node.contradicts(next_of_formula):
                node.rollback()
                return False
            else:
                node.update(next_of_formula)
                if self.tableau.solve():
                    return True
                else:
                    node.rollback()
                    node.rollback()
        return False

    ##########################################
    # Or Expansion
    ##########################################
    def or_expansion(self, formula, node):
        self.traces.path.add_rule('Or expansion')
        self.traces.path.add_selected_formula(formula)
        if '1' in formula[1]:
            return True
        for element in formula[1]:
            if element == '0':
                continue
            if node.contradicts(element):
                continue
            node.update(element)
            if self.tableau.solve():
                return True
            node.rollback()
        return False

    ##########################################
    # Release Expansion
    ##########################################
    def release_expansion(self, formula, node):
        self.traces.path.add_rule('Release expansion')
        self.traces.path.add_selected_formula(formula)

        phi = formula[1]
        psi = formula[2]
        next_of_formula = formula.add_operator('X')

        if not node.contradicts(phi):
            node.update(phi)
            if node.contradicts(psi):
                node.rollback()
            else:
                node.update(psi)
                if self.tableau.solve():
                    return True
                node.rollback()
                node.rollback()

        if not node.contradicts(psi):
            node.update(psi)
            if node.contradicts(next_of_formula):
                node.rollback()
                return False
            else:
                node.update(next_of_formula)
                if self.tableau.solve():
                    return True
                node.rollback()
                node.rollback()
        return False

    ##########################################
    # Eventually Expansion
    ##########################################
    def eventually_expansion(self, formula, node):
        self.traces.path.add_rule('Eventually expansion')
        self.traces.path.add_selected_formula(formula)

        phi = formula[1]
        next_of_formula = formula.add_operator('X')
        if phi == '0':
            return False
        if not node.contradicts(phi):
            node.update(phi)
            node.eventualities.fulfill(formula)
            if self.tableau.solve():
                return True
            node.eventualities.neglect()
            node.rollback()
        if not node.contradicts(next_of_formula):
            node.update(next_of_formula)
            if self.tableau.solve():
                return True
            node.rollback()
        return False

    ##########################################
    # Until Expansion
    ##########################################
    def until_expansion(self, formula, node):
        self.traces.path.add_rule('Until expansion')
        self.traces.path.add_selected_formula(formula)

        phi = formula[1]
        psi = formula[2]
        next_of_formula = formula.add_operator('X')
        if not node.contradicts(psi):
            node.update(psi)
            node.eventualities.fulfill(formula)
            if self.tableau.solve():
                return True
            node.eventualities.neglect()
            node.rollback()
        if not node.contradicts(phi):
            node.update(phi)
            if node.contradicts(next_of_formula):
                node.rollback()
                return False
            else:
                node.update(next_of_formula)
                if self.tableau.solve():
                    return True
                node.rollback()
                node.rollback()

    ##########################################
    # Next Stage
    ##########################################
    def next_stage(self, node):
        self.traces.path.add_rule('Next Stage')
        self.traces.path.add_selected_formula('')
        new_node: Node = node.new_node()
        add_count = 0
        for next_element in node.formulae_operators['X']:
            element = next_element[1]
            if element.is_and():
                for and_element in element[1]:
                    if new_node.contradicts(and_element):
                        for _ in range(add_count):
                            new_node.rollback()
                        del new_node
                        return False
                    else:
                        add_count += 1
                        new_node.update(and_element)
            else:
                if new_node.contradicts(element):
                    for _ in range(add_count):
                        new_node.rollback()
                    del new_node
                    return False
                else:
                    add_count += 1
                    new_node.update(element)
        if new_node.contains_cycle():
            self.traces.print_model(node)
            return True
        else:
            node_copy = node
            self.tableau.node = new_node
            self.traces.print_trace(new_node, trace_type='next_stage_2')
            if self.tableau.solve():
                #self.traces.print_model(new_node)
                return True
            else:
                for _ in range(add_count):
                    new_node.rollback()
                self.tableau.node = node_copy
                del new_node
                return False

        ##########################################
        # SAT Next Stage
        ##########################################

    def next_stage_sat(self, node):
        self.traces.path.add_rule('Next Stage')
        self.traces.path.add_selected_formula('')
        new_node: Node = node.new_node()
        add_count = 0
        for next_element in node.formulae_operators['X']:
            element = next_element[1]
            if element.is_and():
                for and_element in element[1]:
                    if new_node.contradicts(and_element):
                        for _ in range(add_count):
                            new_node.rollback()
                        del new_node
                        return False
                    else:
                        add_count += 1
                        new_node.update(and_element)
            else:
                if new_node.contradicts(element):
                    for _ in range(add_count):
                        new_node.rollback()
                    del new_node
                    return False
                else:
                    add_count += 1
                    new_node.update(element)
        if new_node.contains_cycle():
            return True
        else:
            node_copy = node
            self.tableau.node = new_node
            self.traces.print_trace(new_node, trace_type='next_stage_2')
            if self.tableau.solve():
                return True
            else:
                for _ in range(add_count):
                    new_node.rollback()
                self.tableau.node = node_copy
                del new_node
                return False

    ##########################################
    # z3 Next Stage
    ##########################################
    def next_stage_z3(self, node):
        self.traces.path.add_rule('Next Stage')
        self.traces.path.add_selected_formula('')
        new_node: Node = node.new_node()
        add_count = 0
        for next_element in node.formulae_operators['X']:
            element = next_element[1]
            if element.is_and():
                for and_element in element[1]:
                    if new_node.contradicts(and_element):
                        for _ in range(add_count):
                            new_node.rollback()
                        del new_node
                        return False
                    else:
                        add_count += 1
                        new_node.update(and_element)
            else:
                if new_node.contradicts(element):
                    for _ in range(add_count):
                        new_node.rollback()
                    del new_node
                    return False
                else:
                    add_count += 1
                    new_node.update(element)
        if new_node.contains_cycle():
            return True
        else:
            node_copy = node
            self.tableau.node = new_node
            self.traces.print_trace(new_node, trace_type='next_stage_2')
            if self.tableau.solve():
                return True
            else:
                for _ in range(add_count):
                    new_node.rollback()
                self.tableau.node = node_copy
                del new_node
                return False

    ##########################################
    # Until Plus Expansion
    ##########################################
    def until_plus_expansion(self, formula, node):
        self.traces.path.add_rule('Until+ expansion')
        self.traces.path.add_selected_formula(formula)
        phi = formula[1]
        psi = formula[2]

        if not node.contradicts(psi):
            node.update(psi)
            node.eventualities.fulfill(formula)
            if self.tableau.solve():
                return True
            node.eventualities.neglect()
            node.rollback()

        context = node.set_of_formulae
        if not node.contradicts(phi):
            subsumption = until_plus_subsumption(phi, psi, context)
            node.update(phi)
            next_of_formula = subsumption.add_operator('X')
            if node.contradicts(next_of_formula):
                node.rollback()
                return False
            else:
                node.update(next_of_formula)
                node.marked_until = subsumption if subsumption.is_until() else None
                if self.tableau.solve():
                    return True
                node.rollback()
                node.rollback()
                node.marked_until = None

    ##########################################
    # Eventually Plus Expansion
    ##########################################
    def eventually_plus_expansion(self, formula, node):
        self.traces.path.add_rule('Eventually+ expansion')
        self.traces.path.add_selected_formula(formula)
        phi = formula[1]
        if not node.contradicts(phi):
            node.update(phi)
            node.eventualities.fulfill(formula)
            if self.tableau.solve():
                return True
            node.eventualities.neglect()
            node.rollback()
        context = node.set_of_formulae
        neg_context = nnf_set(context)
        until = build_until(neg_context, phi)
        node.marked_until = until if until.is_until() else None
        next_of_until = until.add_operator('X')
        if not node.contradicts(next_of_until):
            node.update(next_of_until)
            if self.tableau.solve():
                return True
            node.rollback()
            node.marked_until = None

    ##########################################
    # Marked Until Expansion
    ##########################################
    def marked_until_expansion(self, node, formula):
        formula = node.pop_formula(formula)
        node.eventualities.remove(formula)
        self.traces.print_trace(node, formula)
        if self.until_plus_expansion(formula, node):
            return True
        node.eventualities.add(formula)
        #node.marked_until = formula

    ##########################################
    # Mark and Expand Until
    ##########################################
    def select_marked_until_and_expand(self, node, formula):
        self.traces.print_trace(node, formula)
        if formula.is_until():
            if node.eventually_subsumption(formula):
                node.eventualities.eventualities[formula[2]].remove(formula)
                self.traces.path.add_rule('Until+ subsumption')
                self.traces.path.add_selected_formula(formula)
                if self.tableau.solve():
                    return True
                node.eventualities.eventualities[formula[2]].add(formula)
            else:
                return self.until_plus_expansion(formula, node)

        else:
            if node.eventually_subsumption(formula):
                node.eventualities.eventualities[formula[1]].remove(formula)
                self.traces.path.add_rule('Eventually+ subsumption')
                self.traces.path.add_selected_formula(formula)
                if self.tableau.solve():
                    return True
                node.eventualities.eventualities[formula[1]].add(formula)
            else:
                return self.eventually_plus_expansion(formula, node)

    def zero(self):
        self.traces.path.rules.append('Zero')
        self.traces.path.selected_formulae.append('0')

    def closed_node(self):
        self.traces.path.rules.append('Closed Node')
        self.traces.path.selected_formulae.append('-')