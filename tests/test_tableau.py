
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
    tableau._and_expansion(and_formula)
    assert tableau.node.tl_set == TlSet(
        [Formula(("G", Atom("a"))), Atom("b")])


def test_tableau_always_expansion():
    formula = Formula(("G", Atom("a")))
    tableau = Tableau(formula)
    always_formula = tableau.node.pop_formula()
    tableau._always_expansion(always_formula)
    assert tableau.node.tl_set == TlSet(
        [Formula(("X", Formula(("G", Atom("a"))))), Atom("a")])


def test_tableau_or_expansion():
    formula = Formula(
        ("|", frozenset([Formula(("F", Atom("a"))), Formula(("G", Atom("a")))])))
    tableau = Tableau(formula)
    or_formula = tableau.node.pop_formula()
    assert or_formula.is_or()
    elements = [Formula(("F", Atom("a"))), Formula(("G", Atom("a")))]
    tableau._or_expansion(elements[0])
    assert tableau.node.tl_set == TlSet(
        [Formula(("F", Atom("a")))])
    tableau.node.remove(Formula(("F", Atom("a"))))
    assert tableau.node.tl_set.is_empty()
    tableau._or_expansion(elements[1])
    assert tableau.node.tl_set == TlSet(
        [Formula(("G", Atom("a")))])


def test_tableau_release_expansion():
    formula = Formula(("R", Formula(("G", Atom("a"))),
                      Formula(("F", Atom("a")))))
    tableau = Tableau(formula)
    release_formula = tableau.node.pop_formula()
    assert release_formula.is_release()
    tableau._release_expansion_left(release_formula)
    assert tableau.node.tl_set == TlSet(
        [Formula(("F", Atom("a"))), Formula(("G", Atom("a")))])
    tableau.node.remove(Formula(("F", Atom("a"))))
    tableau.node.remove(Formula(("G", Atom("a"))))
    assert tableau.node.tl_set.is_empty()
    tableau._release_expansion_right(release_formula)
    assert tableau.node.tl_set == TlSet(
        [formula.add_operator('X'), Formula(("F", Atom("a")))])


def test_tableau_eventually_expansion():
    formula = Formula(("F", Atom("a")))
    tableau = Tableau(formula)
    eventually_formula = tableau.node.pop_formula()
    assert eventually_formula.is_eventually()
    tableau._eventually_expansion_left(eventually_formula)
    assert tableau.node.tl_set == TlSet([Atom("a")])
    tableau.node.remove(Atom("a"))
    assert tableau.node.tl_set.is_empty()
    tableau._eventually_expansion_right(eventually_formula)
    assert tableau.node.tl_set == TlSet(
        [formula.add_operator('X')])


def test_tableau_until_expansion():
    formula = Formula(("U", Formula(("G", Atom("a"))),
                      Formula(("F", Atom("a")))))
    tableau = Tableau(formula)
    until_formula = tableau.node.pop_formula()
    assert until_formula.is_until()
    tableau._until_expansion_left(until_formula)
    assert tableau.node.tl_set == TlSet([Formula(("F", Atom("a")))])
    tableau.node.remove(Formula(("F", Atom("a"))))
    assert tableau.node.tl_set.is_empty()
    tableau._until_expansion_right(until_formula)
    assert tableau.node.tl_set == TlSet(
        [formula.add_operator('X'), Formula(("G", Atom("a")))])


def test_tableau_until_expansion_fail():
    initial_formula = [Formula(("U", Formula(("G", Atom("a"))),
                                Formula(("F", Atom("a"))))),
                       Formula(("G", Atom("-a"))), Formula(("F", Atom("-a")))]
    tableau = Tableau(initial_formula)
    tableau_copy = Tableau(initial_formula)
    until_formula = tableau.node.pop_formula()
    assert until_formula.is_until()
    can_expand_left, _ = tableau._until_expansion_left(
        until_formula)
    assert not can_expand_left
    can_expand_right, _ = tableau._until_expansion_right(
        until_formula)
    assert not can_expand_right


def test_tableau_next_stage_expansion():
    initial_formula = [Formula(('X', Atom('a'))),
                       Formula(('X', Atom('b'))), Atom('b')]
    tableau = Tableau(initial_formula)

    assert tableau.node.is_elementary()
    can_expand, new_node = tableau._next_stage()
    assert can_expand
    assert new_node.tl_set == TlSet([Atom('b'), Atom('a')])


def test_tableau_next_stage_expansion_and():
    initial_formula = [Formula(('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('b'))), Atom('b')]
    tableau = Tableau(initial_formula)

    assert tableau.node.is_elementary()
    can_expand, new_node = tableau._next_stage()
    assert can_expand
    assert new_node.tl_set == TlSet(
        [Atom('b'), Atom('a'), Formula(('G', 'a'))])


def test_tableau_next_stage_expansion_and_2():
    initial_formula = [Formula(('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('a'))), Atom('b')]
    tableau = Tableau(initial_formula)

    assert tableau.node.is_elementary()
    can_expand, new_node = tableau._next_stage()
    assert can_expand
    assert new_node.tl_set == TlSet(
        [Atom('a'), Atom('a'), Formula(('G', 'a'))])


def test_tableau_next_stage_expansion_fail():
    initial_formula = [Formula(('X', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('-a'))), Atom('b')]
    tableau = Tableau(initial_formula)
    tableau_copy = Tableau(initial_formula)
    assert tableau.node.is_elementary()
    can_expand, new_node = tableau._next_stage()
    assert not can_expand
    assert new_node.tl_set == tableau_copy.node.tl_set


def test_basic_closed_tableau():
    initial_formula = [
        Formula(('X', Atom('-a'))), Formula(('G', Atom('a')))]

    tableau = Tableau(initial_formula)
    sat = tableau.tableau()
    assert sat == False


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


def test_basic_tableau():
    initial_formula = [Formula(('G', Formula(('&', frozenset([Atom('a'), Formula(('G', Atom('a')))]))))),
                       Formula(('X', Atom('-a'))), Atom('b')]

    tableau = Tableau(initial_formula)
    tableau.tableau()
