def and_rollback(node, updated_elements):
    for _ in updated_elements:
        node.rollback()


def and_expansion(self, formula, node):
    self.traces.path.add_rule("And expansion")
    self.traces.path.add_selected_formula(formula)
    if "0" in formula:
        return False, (
            "false",
            formula,
            node.set_of_formulae.copy().union(formula),
            False,
        )
    updated_elements = []
    for element in formula[1]:
        if not node.contradicts(element):
            node.update(element)
            updated_elements.append(element)
        else:
            and_rollback(node, updated_elements)
            return False, (
                "contradiction",
                formula,
                node.set_of_formulae.copy().union(formula),
                element,
            )
    sat, proof = self.tableau.solve()
    if sat:
        return True, 1
    and_rollback(node, updated_elements)
    return False, proof
