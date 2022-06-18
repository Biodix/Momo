def until_expansion_type_0(node, formula):
    phi = formula[1]
    psi = formula[2]
    next_of_formula = formula.add_operator('X')

    if phi == '0' or phi == psi:  # F U psi or psi U psi
        if self.trivial_until_expansion(formula, psi):
            return True
    else:
        if psi == '0':
            return False
        '''Expansion for the first child (phi)'''
        if self.until_left_child_expansion(formula, psi):
            return True
        '''Expansion for second child and next of the formula'''
        if self.until_right_child_expansion(next_of_formula, phi):
            return True
    return False