
import pytest
from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet
from momo.tableau.tableau import Tableau
from multiset import Multiset, FrozenMultiset


def test_branch_eventualities():
    initial_formula = [
        Formula(('X', Formula(('F', Atom('a'))))),
        Formula(('X', Formula(('G', Atom('-a'))))),
        Formula(('F', Atom('b'))),
        Formula(('F', Atom('-c')))]

    tableau = Tableau(initial_formula)
    sat = tableau.tableau()
    assert sat == False
    assert tableau.branch.remaining_eventualities == TlSet(
        [Atom('b'), Atom('-c')])
    assert tableau.branch.fulfilled_eventualities == TlSet([])


def test_branch_until():
    initial_formula = [
        Formula(('X', Formula(('F', Atom('a'))))),
        Formula(('X', Formula(('G', Atom('-a'))))),
        Formula(('U', Atom('d'), Atom('b'))),
        Formula(('U', Atom('d'), Atom('-c')))]

    tableau = Tableau(initial_formula)
    sat = tableau.tableau()
    assert sat == False
    assert tableau.branch.remaining_eventualities == TlSet(
        [Atom('b'), Atom('-c')])
    assert tableau.branch.fulfilled_eventualities == TlSet([])


def test_branch_stages():
    initial_formula = [
        Formula(('X', Formula(('F', Atom('a'))))),
        Formula(('X', Formula(('G', Atom('-a'))))),
        Formula(('U', Atom('d'), Atom('b'))),
        Formula(('U', Atom('d'), Atom('-c')))]

    tableau = Tableau(initial_formula)
    sat = tableau.tableau()
    assert sat == False


def test_branch_cycle():
    initial_formula = [
        Formula(('G', Formula(('F', Atom('a'))))),
        Formula(('G', Formula(('F', Atom('-a')))))]

    tableau = Tableau(initial_formula)
    sat = tableau.tableau()
    assert sat == True
