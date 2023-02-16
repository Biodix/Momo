import pytest
from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet


def test_parse_ltl_basic_formula():
    s2 = Formula(('X', Formula(('&', frozenset(
        [Formula(('|', frozenset([Atom('a'), Formula(('X', 'b'))]))), Atom('c')])))))
    print(s2)

    assert True


def test_tl_set():
    tl_set = TlSet()
    tl_set.add(Atom('a'))
    tl_set.add(Formula(('F', Atom('b'))))
    tl_set.add(Formula(('G', Atom('c'))))
    print(tl_set)
    tl_set.remove(Atom('a'))
    assert True


def test_next_stage():
    tl_set = TlSet()
    tl_set.add(Atom('a'))
    tl_set.add(Formula(('X', Atom('b'))))
    tl_set.add(Formula(('X', Atom('c'))))

    tl_set_res = TlSet()
    tl_set_res.add(Atom('b'))
    tl_set_res.add(Atom('c'))
    next_stage = tl_set.next_stage()
    assert next_stage == tl_set_res


def test_create_tl_set_with_iterable():
    formula_list = [Formula(('X', Atom('b'))), Atom('a'), Formula(
        ('U', Atom('a'), Formula(('|', frozenset([Atom('a'), Formula(('X', 'b'))])))))]

    tl_set_itr = TlSet(formula_list)
    tl_set = TlSet()
    for formula in formula_list:
        tl_set.add(formula)

    assert tl_set_itr == tl_set


def test_pop_formula():
    formula_list = [Formula(('F', Atom('b'))), Atom('a'), Formula(
        ('U', Atom('a'), Formula(('|', frozenset([Atom('a'), Formula(('X', 'b'))])))))]
    tl_set = TlSet(formula_list)
    assert tl_set.pop_formula() == formula_list[2]
    assert tl_set.pop_formula() == formula_list[0]
    # Not valid formulas to pop, catch the exception
    with pytest.raises(Exception) as e:
        tl_set.pop_formula()
