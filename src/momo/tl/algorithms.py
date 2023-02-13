def _nnf(formula):
    """
    Given a formula in binary tree form, convert it to their negation normal form

    Parameters
    ----------
    formula: list of list that represents a formula

    Returns
    -------
    formula: tree-like object that represents the formula at nnf
    """
    if formula.is_atom():
        return formula
    elif formula.is_neg():  # Negative cases
        subformula = formula[1]
        if subformula.is_neg():
            if subformula == Atom:
                return Atom(subformula[1:])
            return _nnf(subformula[1])
        elif subformula.is_boolean():
            return '1' if subformula == '0' else '0'
        elif subformula.is_atom():
            return subformula.neg()
        elif subformula.is_and():
            return _nnf_and_or('|', subformula, True)
        elif subformula.is_or():
            return _nnf_and_or('&', subformula, True)
        elif subformula.is_until():
            return Formula(('R', _nnf(subformula[1].neg()), _nnf(subformula[2].neg())))
        elif subformula.is_release():
            return Formula(('U', _nnf(subformula[1].neg()), _nnf(subformula[2].neg())))
        elif subformula.is_implication():
            return Formula(('&', frozenset([_nnf(subformula[1]), _nnf(subformula[2].neg())])))
        elif subformula.is_next():
            return Formula(('X', _nnf(subformula[1].neg())))
        elif subformula.is_eventually():
            return Formula(('G', _nnf(subformula[1].neg())))
        elif subformula.is_always():
            return Formula(('F', _nnf(subformula[1].neg())))
        elif subformula.is_iff():
            return _nnf_iff(subformula, True)
    elif not formula.is_neg():  # Positive Cases
        subformula = formula
        if subformula.is_atom():
            return subformula
        elif subformula.is_and():
            return _nnf_and_or('&', subformula, False)
        elif subformula.is_or():
            return _nnf_and_or('|', subformula, False)
        elif subformula.is_until():
            return Formula(('U', _nnf(subformula[1]), _nnf(subformula[2])))
        elif subformula.is_release():
            return Formula(('R', _nnf(subformula[1]), _nnf(subformula[2])))
        elif subformula.is_implication():
            return Formula(('|', frozenset([_nnf(subformula[1].neg()), _nnf(subformula[2])]))) \
                if subformula[1] != subformula[2] else Atom('1')
        elif subformula.is_next():
            return Formula(('X', _nnf(subformula[1])))
        elif subformula.is_eventually():
            return Formula(('F', _nnf(subformula[1])))
        elif subformula.is_always():
            return Formula(('G', _nnf(subformula[1])))
        elif subformula.is_iff():
            return _nnf_iff(subformula, False)