
import pytest
from momo.tl.formula import Formula, Atom
from momo.tl.tl_set import TlSet
from momo.tableau.tableau import Tableau
from multiset import Multiset, FrozenMultiset


def test_tableau_definition():
    formula = Formula(("&", frozenset(
        [Formula(("F", Atom("a"))), Formula(("F", Atom("a"))), Atom("b")])))
    tableau = Tableau(formula)
    assert tableau.closure == {
        ("&", frozenset({("F", "a"), ("F", "a"), "b"})): {"nnf": ("|", frozenset({("G", "-a"), "-b"}))},
        ("|", frozenset({("G", "-a"), "-b"})): {"nnf": ("&", frozenset({("F", "a"), ("F", "a"), "b"}))},
        ("F", "a"): {"nnf": ("G", "-a")},
        ("G", "-a"): {"nnf": ("F", "a")},
        ("X", ("F", "a")): {"nnf": ("X", ("G", "-a"))},
        ("X", ("G", "-a")): {"nnf": ("X", ("F", "a"))},
        "a": {"nnf": "-a"},
        "-a": {"nnf": "a"},
        "b": {"nnf": "-b"},
        "-b": {"nnf": "b"},
    }

    assert tableau.node.tl_set == TlSet({formula})
    assert tableau.branch.remaining_eventualities == TlSet(
        {})
    assert tableau.branch.literals == TlSet({})


def test_tableau_and_expansion():
    formula = Formula(("&", frozenset(
        [Formula(("G", Atom("a"))), Formula(("G", Atom("a"))), Atom("b")])))
    tableau = Tableau(formula)
    and_formula = tableau.node.pop_formula()
    tableau.and_expansion(and_formula)
    assert tableau.node.tl_set == TlSet(
        [Formula(("G", Atom("a"))), Atom("b")])


def test_tableau_always_expansion():
    formula = Formula(("G", Atom("a")))
    tableau = Tableau(formula)
    and_formula = tableau.node.pop_formula()
    tableau.always_expansion(and_formula)
    assert tableau.node.tl_set == TlSet(
        [Formula(("X", Formula(("G", Atom("a"))))), Atom("a")])
