from momo.tl.formula import Formula
from momo.tl.tl_set import TlSet
from momo.tableau.branch import Branch

def build_model(branch):
    pass

def build_proof(branch):
    pass

def tableau_expansion(f, branch):
    pass

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
    # elif phi.is_inconsistent():
    #     is_closed, proof = True, build_proof(branch)
    elif phi.is_sat_elementary():
        if branch.has_fulfill_all_eventualities() and branch.contains(phi):
            is_closed, model = False, build_model(branch)
        elif phi.is_elementary():
            psi = phi.next_stage()
            branch.update(psi)
            is_closed, proof, model = tableau(psi, branch)
            if is_closed:
                proof = build_proof(phi,'X',proof)
                branch.rollback(psi)
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
            proof = build_proof(phi, 'sat', proof_list)
    else:
        f, rule = phi.pop_formula()
        tableau_expansion(f,rule,branch)

            