import pytest
from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet


def test_parse_ltl_basic_formula():
    s2 = Formula(
        (
            "X",
            Formula(
                (
                    "&",
                    frozenset(
                        [
                            Formula(("|", frozenset([Atom("a"), Formula(("X", "b"))]))),
                            Atom("c"),
                        ]
                    ),
                )
            ),
        )
    )
    print(s2)

    assert True


def test_tl_set():
    tl_set = TlSet()
    tl_set.add(Atom("a"))
    tl_set.add(Formula(("F", Atom("b"))))
    tl_set.add(Formula(("G", Atom("c"))))
    print(tl_set)
    tl_set.remove(Atom("a"))
    assert True


def test_next_stage():
    tl_set = TlSet()
    tl_set.add(Atom("a"))
    tl_set.add(Formula(("X", Atom("b"))))
    tl_set.add(Formula(("X", Atom("c"))))

    tl_set_res = TlSet()
    tl_set_res.add(Atom("b"))
    tl_set_res.add(Atom("c"))
    next_stage = tl_set.next_stage()
    assert next_stage == tl_set_res


def test_create_tl_set_with_iterable():
    formula_list = [
        Formula(("X", Atom("b"))),
        Atom("a"),
        Formula(
            (
                "U",
                Atom("a"),
                Formula(("|", frozenset([Atom("a"), Formula(("X", "b"))]))),
            )
        ),
    ]

    tl_set_itr = TlSet(formula_list)
    tl_set = TlSet()
    for formula in formula_list:
        tl_set.add(formula)

    assert tl_set_itr == tl_set


def test_pop_formula():
    formula_list = [
        Formula(("F", Atom("b"))),
        Atom("a"),
        Formula(
            (
                "U",
                Atom("a"),
                Formula(("|", frozenset([Atom("a"), Formula(("X", "b"))]))),
            )
        ),
    ]
    tl_set = TlSet(formula_list)
    assert tl_set.pop_formula()[0] == formula_list[2]
    assert tl_set.pop_formula()[0] == formula_list[0]
    # Not valid formulas to pop, catch the exception
    with pytest.raises(Exception) as e:
        tl_set.pop_formula()


def test_multiset_multiplicity():
    formula_list = [
        Formula(("F", Atom("b"))),
        Atom("a"),
        Formula(
            (
                "U",
                Atom("a"),
                Formula(("|", frozenset([Atom("a"), Formula(("X", "b"))]))),
            )
        ),
        Atom("a"),
        Atom("a"),
    ]
    tl_set = TlSet(formula_list)
    assert tl_set.get(Atom("a")) == 3
    assert tl_set.remove(Atom("a")) == 3
    assert tl_set.get(Formula(("F", Atom("b")))) == 1
    assert tl_set.remove(Formula(("F", Atom("b")))) == 1


def test_copy():
    formula_list = [
        Formula(("F", Atom("b"))),
        Atom("a"),
        Formula(
            (
                "U",
                Atom("a"),
                Formula(("|", frozenset([Atom("a"), Formula(("X", "b"))]))),
            )
        ),
    ]

    tl_set = TlSet(formula_list)
    tl_set_copy = tl_set.clone()
    assert tl_set == tl_set_copy
    tl_set_copy.operators["L"].add(Atom("b"))
    assert tl_set != tl_set_copy
    tl_set_copy.operators["L"].remove(Atom("b"))
    assert tl_set == tl_set_copy
    tl_set.add(Atom("c"))
    assert tl_set != tl_set_copy
    assert tl_set.operators != tl_set_copy.operators


def test_sat_elementary():
    formula1 = [Formula(("F", Atom("b"))), Atom("a")]
    tl_set1 = TlSet(formula1)
    assert tl_set1.is_sat_elementary() == False

    formula2 = [Formula(("|", frozenset([Atom("a"), Formula(("X", "b"))])))]
    tl_set2 = TlSet(formula2)
    assert tl_set2.is_sat_elementary() == True

    formula3 = [
        Atom("a"),
        Formula(("X", "b")),
        Formula(
            (
                "|",
                frozenset(
                    [Atom("a"), Atom("b"), Formula(("X", "b")), Formula(("X", "c"))]
                ),
            )
        ),
    ]
    tl_set3 = TlSet(formula3)
    assert tl_set3.is_sat_elementary() == True

    formula4 = [
        Atom("a"),
        Formula(
            (
                "|",
                frozenset(
                    [Atom("a"), Atom("b"), Formula(("G", "b")), Formula(("X", "c"))]
                ),
            )
        ),
    ]
    tl_set4 = TlSet(formula4)
    assert tl_set4.is_sat_elementary() == False

    formula5 = [Formula(("X", "b"))]
    tl_set5 = TlSet(formula5)
    assert tl_set5.is_sat_elementary() == True

    formula6 = [Formula(("X", "b")), Formula(("X", "b")), Formula(("X", "b"))]
    tl_set6 = TlSet(formula6)
    assert tl_set6.is_sat_elementary() == True
