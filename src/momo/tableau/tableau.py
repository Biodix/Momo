from momo.tl.formula import Formula
from momo.tl.tl_set import TlSet
from momo.tableau.branch import Branch
from momo.tableau.closure import Closure, SatTable


def build_model(branch):
    pass


def build_proof(branch):
    pass


def and_expansion(formula: Formula, tl_set: TlSet, closure: Closure, branch: Branch):
    updated_elements = []
    for element in formula[1]:
        neg_formula = formula.neg()
        if not tl_set.contradicts(element, closure):
            node.update(element)
            updated_elements.append(element)
        else:
            and_rollback(node, updated_elements)
            return False, ('contradiction', formula, node.set_of_formulae.copy().union(formula), element)


def tableau_expansion(formula: Formula, branch: Branch):
    if formula.is_and():
        sat, proof = self.rules.and_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_always():
        sat, proof = self.rules.always_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_or():
        sat, proof = self.rules.or_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_release():
        sat, proof = self.rules.release_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_eventually():
        sat, proof = self.rules.eventually_expansion(formula, node)
        if sat:
            return True, 1
    elif formula.is_until():
        sat, proof = self.rules.until_expansion(formula, node)
        if sat:
            return True, 1
    else:
        return True, 1


def ltl2sat():
    pass


def sat_solver():
    pass


def sat2ltl():
    pass


def add_to_last_stage():
    pass


def tableau(phi: TlSet, branch: Branch):
    print(phi)
    if phi.is_empty():
        is_closed, model = False, build_model(branch)
    elif phi.is_inconsistent():
        is_closed, proof = True, build_proof(branch)
    elif phi.is_sat_elementary():
        if branch.has_fulfill_all_eventualities() and phi in branch:
            is_closed, model = False, build_model(branch)
        if phi.is_elementary():
            psi = phi.next_stage()
            branch.append(psi)
            is_closed, proof, model = tableau(psi, branch)
            if is_closed:
                # proof = build_proof(phi, 'X', proof)
                branch.pop()
        else:
            is_closed, proof_list = True, []
            alpha = ltl2sat(phi)
            is_sat, sat_model = sat_solver(alpha)
            while is_sat and is_closed:
                sat_phi = sat2ltl(sat_model)
                sat_branch = add_to_last_stage(branch, sat_phi)
                psi = sat_phi.next_stage()
                sat_branch.update(psi)
                is_closed, proof, model = tableau(psi, sat_branch)
                if is_closed:
                    proof_list.append(proof)
                    alpha.add(sat_model.neg())
                    is_sat, sat_model = sat_solver(alpha)
                    sat_branch.rollback(psi)
            # proof = build_proof(phi, 'sat', proof_list)
    else:
        formula = phi.pop_formula()
        tableau_expansion(formula, branch)
