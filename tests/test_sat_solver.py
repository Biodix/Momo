
import pytest
from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet
from momo.tableau.tableau import Tableau
from multiset import Multiset, FrozenMultiset
from pysat.formula import CNF
from pysat.solvers import Minisat22


def test_sat_translation():
    initial_formula = [Formula(('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('-a'))), Atom('b'),
                       Formula(('|', frozenset([Atom('a'), Formula(('X', Atom('a')))])))]

    tableau = Tableau(initial_formula)
    formula1 = Formula(
        ('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))])))))
    clause1 = tableau.sat_solver.formula_to_clause(formula1)
    assert formula1 == tableau.sat_solver.clause_to_formula(clause1)

    formula2 = Formula(
        ('|', frozenset([Atom('a'), Formula(('X', Atom('a')))])))
    clause2 = tableau.sat_solver.formula_to_clause(formula2)
    assert formula2 == tableau.sat_solver.clause_to_formula(clause2)

    formula3 = Atom('b')
    clause3 = tableau.sat_solver.formula_to_clause(formula3)
    assert formula3 == tableau.sat_solver.clause_to_formula(clause3)


def test_tl_set_to_sat():
    initial_formula = [Formula(('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('-a'))), Atom('b'),
                       Formula(('|', frozenset([Atom('a'), Formula(('X', Atom('a')))])))]
    tableau = Tableau(initial_formula)
    clauses = tableau.sat_solver.tl_set_to_sat(
        tableau.node.tl_set)
    tl_set = tableau.sat_solver.sat_to_tl_set(clauses)
    assert tableau.node.tl_set == tl_set


def test_sat_solver():
    initial_formula = [Formula(('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('-a'))), Atom('b'),
                       Formula(('|', frozenset([Atom('a'), Formula(('X', Atom('a'))), Atom('c')])))]
    tableau = Tableau(initial_formula)
    clauses = tableau.sat_solver.tl_set_to_sat(
        tableau.node.tl_set)
    tablea_sat_solver_models = tableau.sat_solver.solve(clauses)

    additional_solver = Minisat22()
    cnf = CNF(from_clauses=clauses)
    additional_solver.append_formula(cnf)

    for model in tablea_sat_solver_models:
        assert additional_solver.solve(assumptions=model)
