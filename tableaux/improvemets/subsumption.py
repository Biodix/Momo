from tableaux.tl_basics.formula import Formula, Atom
from tableaux.tl_basics.tl_set import TlSet


def op_is_and(phi):
    return phi[0] == '&'

def op_is_or(phi):
    return phi[0] == '|'

def subsumption2(phi1, phi2):
    if phi1 == '1':
        return phi2
    elif op_is_and(phi2):
        if op_is_and(phi1):
            if phi2[1].issuperset(phi1[1]):
                return phi2
            else:
                return phi1
        elif op_is_or(phi1):
            if phi2[1].issuperset(frozenset([phi1[1]])):
                return phi2
            else:
                return phi1
        elif type(phi1) == str:
            if phi1 == '1':
                return phi2
            elif phi2[1].issuperset(frozenset(phi1)):
                return phi2
            else:
                return phi1
        else:
            if op_is_and(phi2):
                if phi2[1].issuperset(frozenset([phi1[1]])):
                    return phi2
                else:
                    return phi1

def subsumption(phi_1, phi_2):
    if phi_1 == '1':
        return phi_2
    elif phi_2.is_and():
        if phi_1.is_and():
            return phi_2 if phi_2[1].issuperset(phi_1[1]) else phi_1
        elif phi_1.is_or():
            return phi_2 if phi_1 in phi_2[1] else phi_1
        elif phi_1.is_atom():
            return phi_2 if phi_1 in phi_2[1] else phi_1


def until_plus_subsumption(phi, psi, context):
    neg_context = nnf_set(context)
    if not neg_context:
        return Formula(('U', Atom('0'), psi))
    if phi == '1':
        f = Formula(('|', frozenset(neg_context)))
        return Formula(('U', f, psi))
    if neg_context == '1':
        return Formula(('U', phi, psi))
    s = _subsumption(phi, neg_context)
    return Formula(('U', s, psi))


def _subsumption(phi, context):
    new_phi = set()
    if phi.is_atom():
        if phi in context:
            return phi
        else:
            if len(context) == 1:
                return Formula(('&', frozenset([phi, context.pop()])))
            else:
                return Formula(('&', frozenset([phi, Formula(('|', frozenset(context)))])))
    elif phi.is_and():
        for formula in phi[1]:
            if formula.is_atom():
                if formula in context:
                    continue
                new_phi.add(formula)
            else:
                if formula.is_or():
                    context_2 = formula[1]
                else:
                    context_2 = frozenset([formula])
                if context_2.issubset(context):
                    return phi
                if context_2.issuperset(context):
                    continue
                new_phi.add(formula)
        if len(context) == 1:
            new_phi.add(next(iter(context)))
        else:
            new_phi.add(Formula(('|', frozenset(context))))
        return Formula(('&', frozenset(new_phi)))
    elif phi.is_or():
        context_2 = phi[1]
        if context_2.issuperset(context):
            return next(iter(context))
        elif context_2.issubset(context):
            return phi
        elif len(context) == 1:
            return Formula(('&', frozenset([phi, next(iter(context))])))
        else:
            return Formula(('&', frozenset([phi, Formula(('|', frozenset(context)))])))
    else:
        phi_set = {phi}
        if phi_set in context:
            return phi_set
        else:
            if len(context) == 1:
                return Formula(('&', frozenset([phi, context.pop()])))
            else:
                return Formula(('&', frozenset([phi, Formula(('|', frozenset(context)))])))


def nnf_set(context):
    neg_context = set()
    for formula in context:
        if not formula.is_always() and not formula.is_next_always():
            nnf_formula = formula.neg().nnf()
            neg_context.add(nnf_formula)
    return neg_context