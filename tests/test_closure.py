from momo.tableau.closure import Closure, SatTable
from momo.tl.formula import Formula, Atom


def test_sat_table1():
    formula1 = Formula(("F", Atom("a")))

    formula1_nnf = formula1.neg().nnf()
    sat_table = SatTable()
    sat_table.add_entry(formula1, formula1_nnf)

    assert sat_table.formula_to_number == {
        Formula(("F", Atom("a"))): "1",
        Formula(("G", Atom("-a"))): "-1",
    }


def test_sat_table2():
    formula1 = Formula(("F", Atom("a")))
    formula2 = Formula(("F", Formula(("G", Atom("a")))))
    formula1_nnf = formula1.neg().nnf()
    formula2_nnf = formula2.neg().nnf()
    sat_table = SatTable()
    sat_table.add_entry(formula1, formula1_nnf)
    sat_table.add_entry(formula2, formula2_nnf)

    assert sat_table.formula_to_number == {
        Formula(("F", Atom("a"))): "1",
        Formula(("G", Atom("-a"))): "-1",
        Formula(("F", Formula(("G", Atom("a"))))): "2",
        Formula(("G", Formula(("F", Atom("-a"))))): "-2",
    }


def test_closure_build():
    closure = Closure()
    formula = Formula(("-", Formula(("F", Formula(("G", Atom("a")))))))
    closure.build_closure(formula)
    print(closure)
    assert closure == {
        ("F", ("G", "a")): {"nnf": ("G", ("F", "-a"))},
        ("G", ("F", "-a")): {"nnf": ("F", ("G", "a"))},
        ("X", ("F", ("G", "a"))): {"nnf": ("X", ("G", ("F", "-a")))},
        ("X", ("G", ("F", "-a"))): {"nnf": ("X", ("F", ("G", "a")))},
        ("G", "a"): {"nnf": ("F", "-a")},
        ("F", "-a"): {"nnf": ("G", "a")},
        ("X", ("G", "a")): {"nnf": ("X", ("F", "-a"))},
        ("X", ("F", "-a")): {"nnf": ("X", ("G", "a"))},
        "a": {"nnf": "-a"},
        "-a": {"nnf": "a"},
    }


def test_closure_build2():
    closure = Closure()
    formula = Formula(
        (
            "|",
            frozenset(
                (
                    Formula(
                        ("U", Formula(("G", Atom("a"))), Formula(("X", Atom("b"))))
                    ),
                    Formula(("R", Formula(("F", Atom("a"))), Atom("b"))),
                )
            ),
        )
    )
    closure.build_closure(formula)
    print(closure)
    assert closure == {
        ("|", frozenset({("U", ("G", "a"), ("X", "b")), ("R", ("F", "a"), "b")})): {
            "nnf": (
                "&",
                frozenset({("R", ("F", "-a"), ("X", "-b")), ("U", ("G", "-a"), "-b")}),
            )
        },
        ("&", frozenset({("R", ("F", "-a"), ("X", "-b")), ("U", ("G", "-a"), "-b")})): {
            "nnf": (
                "|",
                frozenset({("U", ("G", "a"), ("X", "b")), ("R", ("F", "a"), "b")}),
            )
        },
        ("U", ("G", "a"), ("X", "b")): {"nnf": ("R", ("F", "-a"), ("X", "-b"))},
        ("R", ("F", "-a"), ("X", "-b")): {"nnf": ("U", ("G", "a"), ("X", "b"))},
        ("X", ("U", ("G", "a"), ("X", "b"))): {
            "nnf": ("X", ("R", ("F", "-a"), ("X", "-b")))
        },
        ("X", ("R", ("F", "-a"), ("X", "-b"))): {
            "nnf": ("X", ("U", ("G", "a"), ("X", "b")))
        },
        ("G", "a"): {"nnf": ("F", "-a")},
        ("F", "-a"): {"nnf": ("G", "a")},
        ("X", ("G", "a")): {"nnf": ("X", ("F", "-a"))},
        ("X", ("F", "-a")): {"nnf": ("X", ("G", "a"))},
        "a": {"nnf": "-a"},
        "-a": {"nnf": "a"},
        ("X", "b"): {"nnf": ("X", "-b")},
        ("X", "-b"): {"nnf": ("X", "b")},
        "b": {"nnf": "-b"},
        "-b": {"nnf": "b"},
        ("R", ("F", "a"), "b"): {"nnf": ("U", ("G", "-a"), "-b")},
        ("U", ("G", "-a"), "-b"): {"nnf": ("R", ("F", "a"), "b")},
        ("X", ("R", ("F", "a"), "b")): {"nnf": ("X", ("U", ("G", "-a"), "-b"))},
        ("X", ("U", ("G", "-a"), "-b")): {"nnf": ("X", ("R", ("F", "a"), "b"))},
        ("F", "a"): {"nnf": ("G", "-a")},
        ("G", "-a"): {"nnf": ("F", "a")},
        ("X", ("F", "a")): {"nnf": ("X", ("G", "-a"))},
        ("X", ("G", "-a")): {"nnf": ("X", ("F", "a"))},
    }
