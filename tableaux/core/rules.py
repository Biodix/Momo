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
            return False, ('false',formula , node.set_of_formulae.copy().union(formula), False)
        updated_elements = []
        for element in formula[1]:
            if element == '1':  # Si vemos un 1 no lo añadimos, 1 and a equiv a.
                continue
            elif not node.contradicts(element):
                node.update(element)
                updated_elements.append(element)
            else:
                and_rollback(node, updated_elements)
                return False, ('contradiction',formula , node.set_of_formulae.copy().union(formula), element)
        sat, proof = self.tableau.solve()
        if sat:
            return True, 1
        and_rollback(node, updated_elements)
        return False, proof

    ##########################################
    # Always Expansion
    ##########################################
    def always_expansion(self, formula, node):
        self.traces.path.add_rule('Always expansion')
        self.traces.path.add_selected_formula(formula)
        phi = formula[1]
        next_of_formula = formula.add_operator('X')
        if phi == '0':
            return False, ('false',formula , node.set_of_formulae.copy().union(formula), False)
        if node.contradicts(phi):
            return False, ('contradiction',formula , node.set_of_formulae.copy().union(formula), phi)
        else:
            node.update(phi)
            if node.contradicts(next_of_formula):
                node.rollback()
                return False, ('contradiction',formula , node.set_of_formulae.copy().union(formula), next_of_formula)
            else:
                node.update(next_of_formula)
                sat, proof = self.tableau.solve()
                if sat:
                    return True, 1
                else:
                    node.rollback()
                    node.rollback()
        return False, proof

    ##########################################
    # Or Expansion old
    ##########################################
    def or_expansion_old(self, formula, node):
        self.traces.path.add_rule('Or expansion')
        self.traces.path.add_selected_formula(formula)
        if '1' in formula[1]:
            return True, 1
        for element in formula[1]:
            if element == '0':
                continue
            if node.contradicts(element):
                continue
            node.update(element)
            if self.tableau.solve():
                return True, 1
            node.rollback()
        return False

    ##########################################
    # Or Expansion Enhanced
    ##########################################
    def or_expansion(self, formula, node):
        self.traces.path.add_rule('Or expansion')
        self.traces.path.add_selected_formula(formula)
        proofs = []
        if '1' in formula[1]:
            return True, 1
        if (formula[1] & node.set_of_formulae):
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            else:
                return False, proof
        else:
            for element in formula[1]:
                if element == '0':
                    proofs.append(('false',formula , node.set_of_formulae.copy().union(formula), False))
                    continue
                if node.contradicts(element):
                    proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), element))
                    continue
                node.update(element)
                
                sat, proof = self.tableau.solve()
                proofs.append(proof)
                if sat:
                    return True, 1
                node.rollback()
        return False, proofs

    ##########################################
    # Release Expansion
    ##########################################
    def release_expansion(self, formula, node):
        self.traces.path.add_rule('Release expansion')
        self.traces.path.add_selected_formula(formula)

        phi = formula[1]
        psi = formula[2]
        next_of_formula = formula.add_operator('X')
        proofs = []
        if not node.contradicts(phi):
            node.update(phi)
            if node.contradicts(psi):
                node.rollback()
                proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), psi))
            else:
                node.update(psi)
                sat, proof = self.tableau.solve()
                if sat:
                    return True, 1
                node.rollback()
                node.rollback()
                proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), phi))

        if not node.contradicts(psi):
            node.update(psi)
            if node.contradicts(next_of_formula):
                node.rollback()
                proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), next_of_formula))
                return False, proofs
            else:
                node.update(next_of_formula)
                sat, proof = self.tableau.solve()
                if sat:
                    return True, 1
                proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), next_of_formula))
                node.rollback()
                node.rollback()
                proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), psi))
        return False, proofs

    ##########################################
    # Eventually Expansion
    ##########################################
    def  eventually_expansion(self, formula, node):


        phi = formula[1]
        next_of_formula = formula.add_operator('X')
        proofs = []
        if phi == '0':
            return False, ('false',formula , node.set_of_formulae.copy().union(formula), False)

        if self.is_subsum(formula, node):
            self.traces.path.add_rule('Eventually subsum')
            self.traces.path.add_selected_formula(formula)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            return False, proof
        self.traces.path.add_rule('Eventually expansion')
        self.traces.path.add_selected_formula(formula)
        if not node.contradicts(phi):
            node.update(phi)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            node.rollback()
            proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), phi))
        if not node.contradicts(next_of_formula):
            node.update(next_of_formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.rollback()
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), phi))
        return False, proofs

    ##########################################
    # Until Expansion
    ##########################################
    def until_expansion(self, formula, node):

        phi = formula[1]
        psi = formula[2]
        next_of_formula = formula.add_operator('X')
        proofs = []
        if self.is_subsum(formula, node):
            self.traces.path.add_rule('Until subsum')
            self.traces.path.add_selected_formula(formula)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            return False, proof
        self.traces.path.add_rule('Until expansion')
        self.traces.path.add_selected_formula(formula)

        if not node.contradicts(psi):
            node.update(psi)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            node.rollback()
            proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), psi))

        if not node.contradicts(phi):
            node.update(phi)
            if node.contradicts(next_of_formula):
                node.rollback()
                proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), next_of_formula))
                return False, proofs
            else:
                node.update(next_of_formula)
                sat, proof = self.tableau.solve()
                if sat:
                    return True, 1
                node.rollback()
                node.rollback()
                proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), phi))
        return False, proofs

    ##########################################
    # Next Stage
    ##########################################
    # TODO: Revisar estas dos primeras proofs

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
                        return False, ('contradiction','next stage' , node.set_of_formulae.copy(), and_element)
                    else:
                        add_count += 1
                        new_node.update(and_element)
            else:
                if new_node.contradicts(element):
                    for _ in range(add_count):
                        new_node.rollback()
                    del new_node
                    return False, ('contradiction','next stage' , node.set_of_formulae.copy(), element)
                else:
                    add_count += 1
                    new_node.update(element)
        if new_node.contains_cycle():
            self.traces.print_model(node)
            return True, 1
        else:
            node_copy = node
            self.tableau.node = new_node
            self.traces.print_trace(new_node, trace_type='next_stage_2')
            sat, proof = self.tableau.solve()
            if sat:
                #self.traces.print_model(new_node)
                return True, 1
            else:
                for _ in range(add_count):
                    new_node.rollback()
                self.tableau.node = node_copy
                del new_node
                return False, proof

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
            return True, 1
        else:
            node_copy = node
            self.tableau.node = new_node
            self.traces.print_trace(new_node, trace_type='next_stage_2')
            if self.tableau.solve():
                return True, 1
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
            return True, 1
        else:
            node_copy = node
            self.tableau.node = new_node
            self.traces.print_trace(new_node, trace_type='next_stage_2')
            if self.tableau.solve():
                return True, 1
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

        phi = formula[1]
        psi = formula[2]
        proofs = []
        if self.is_subsum(formula, node):
            self.traces.path.add_rule('Until+ subsum')
            self.traces.path.add_selected_formula(formula)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            return False, proof
        self.traces.path.add_rule('Until+ expansion')
        self.traces.path.add_selected_formula(formula)
        if not node.contradicts(psi):
            node.update(psi)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            node.rollback()
            proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), psi))

        context = node.set_of_formulae
        if not node.contradicts(phi):
            subsumption = until_plus_subsumption(phi, psi, context)
            node.update(phi)
            next_of_formula = subsumption.add_operator('X')
            if node.contradicts(next_of_formula):
                node.rollback()
                proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), next_of_formula))
            else:
                node.update(next_of_formula)
                node.marked_until = subsumption if subsumption.is_until() else None
                sat, proof = self.tableau.solve()
                if sat:
                    return True, 1
                node.rollback()
                node.rollback()
                node.marked_until = None
                proofs.append(proof)

        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), phi))
        return False, proofs

    ##########################################
    # Eventually Plus Expansion
    ##########################################
    def eventually_plus_expansion(self, formula, node):
        phi = formula[1]
        proofs = []
        if self.is_subsum(formula, node):
            self.traces.path.add_rule('Eventually+ subsum')
            self.traces.path.add_selected_formula(formula)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            return False, proof
        self.traces.path.add_rule('Eventually+ expansion')
        self.traces.path.add_selected_formula(formula)
        if not node.contradicts(phi):
            node.update(phi)
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            node.rollback()
            proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), phi))
        context = node.set_of_formulae
        neg_context = nnf_set(context)
        until = build_until(neg_context, phi)
        node.marked_until = until if until.is_until() else None
        next_of_until = until.add_operator('X')
        if not node.contradicts(next_of_until):
            node.update(next_of_until)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.rollback()
            node.marked_until = None
            proofs.append(proof)
        else:
            proofs.append(('contradiction',formula , node.set_of_formulae.copy().union(formula), next_of_until))
        return False, proofs
    
    ##########################################
    # Marked Until Expansion
    ##########################################
    def marked_until_expansion(self, node, formula):
        formula = node.pop_formula(formula)
        node.eventualities.remove(formula)
        self.traces.print_trace(node, formula)
        sat, proof = self.until_plus_expansion(formula, node)
        if sat:
            return True, 1
        node.eventualities.add(formula)
        #node.marked_until = formula
        return False, proof

    ##########################################
    # Mark and Expand Until
    ##########################################
    def select_marked_until_and_expand(self, node, formula):
        self.traces.print_trace(node, formula)
        if self.is_subsum(formula, node):
            node.eventualities.fulfill(formula)
            sat, proof = self.tableau.solve()
            if sat:
                return True, 1
            node.eventualities.neglect()
            return False, proof
        if formula.is_until():
            if node.eventually_subsumption(formula):
                node.eventualities.eventualities[formula[2]].remove(formula)
                self.traces.path.add_rule('Until+ subsumption')
                self.traces.path.add_selected_formula(formula)
                sat, proof = self.tableau.solve()
                if sat:
                    return True, 1
                node.eventualities.eventualities[formula[2]].add(formula)
            else:
                sat, proof = self.until_plus_expansion(formula, node)
                if sat:
                    return True, 1
        
        else:
            if node.eventually_subsumption(formula):
                node.eventualities.eventualities[formula[1]].remove(formula)
                self.traces.path.add_rule('Eventually+ subsumption')
                self.traces.path.add_selected_formula(formula)
                sat, proof = self.tableau.solve()
                if sat:
                    return True, 1
                node.eventualities.eventualities[formula[1]].add(formula)
            else:
                sat, proof = self.eventually_plus_expansion(formula, node)
                if sat:
                    return True, 1
        return False, proof

    def is_subsum(self, formula, node):
        if formula.is_eventually():
            if formula[1] in node.set_of_formulae:
                return True, 1
            for until_formula in node.formulae_operators['U']:
                if until_formula[2] == formula[1]:
                    return True, 1
        elif formula.is_until():
            if formula[2] in node.set_of_formulae:
                return True, 1
        return False
        


    def zero(self):
        self.traces.path.rules.append('Zero')
        self.traces.path.selected_formulae.append('0')

    def closed_node(self):
        self.traces.path.rules.append('Closed Node')
        self.traces.path.selected_formulae.append('-')
