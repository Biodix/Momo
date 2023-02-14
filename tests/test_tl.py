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
