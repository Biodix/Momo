
import pytest
from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet
from momo.tableau.tableau import Tableau
from multiset import Multiset, FrozenMultiset


def test_sat_formula_to_number():
    initial_formula = [Formula(('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('-a'))), Atom('b'),
                       Formula(('|', frozenset([Atom('a'), Formula(('X', Atom('a')))])))]

    tableau = Tableau(initial_formula)
    clause1 = tableau.sat_solver.formula_to_number(Formula(
        ('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))))
    clause2 = tableau.sat_solver.formula_to_number(
        Formula(('|', frozenset([Atom('a'), Formula(('X', Atom('a')))]))))
    clause3 = tableau.sat_solver.formula_to_number(Atom('b'))
    print("EEE")
