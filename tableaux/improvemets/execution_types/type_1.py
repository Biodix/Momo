# Bet to close
class Type1:
    def __init__(self, tableau, closure, traces):
        self.tableau = tableau
        self.closure = closure
        self.traces = traces

    def or_expansion(self, formula, node):
        self.traces.path.add_rule('Or expansion')
        self.traces.path.add_selected_formula(formula)
        if '1' in formula[1]:
            return True
        delayed_elements = []

        for element in formula[1]:
            if element == '0':
                continue
            if self.closure[element]['nnf'] not in node.eventualities.eventualities:
                delayed_elements.append(element)
                continue
            if node.contradicts(element):
                continue
            node.update(element)
            if self.tableau.solve():
                return True
            node.rollback()

        for element in delayed_elements:
            if element == '0':
                continue
            if node.contradicts(element):
                continue
            node.update(element)
            if self.tableau.solve():
                return True
            node.rollback()
        return False

    ########################
    # Eventually Expansion #
    ########################
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

