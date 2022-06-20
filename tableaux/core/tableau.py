import time

from tableaux.core.node import Node
from tableaux.core.closure import Closure
from tableaux.improvemets.closed_nodes import ClosedNodes
from tableaux.improvemets.sat_solver import SatSolver
from tableaux.core.rules import Rules
from tableaux.debugging.traces import Trace
from tableaux.preproccesing.process_formula import process_formula, read_file


class Tableau:
    def __init__(self, formula, trace=False, configuration=None):
        # Traces
        self.traces = Trace(trace)

        self.steps = 0
        self.closure = Closure(formula)

        self.rules = Rules(self, self.closure, self.traces)

        # Improvements
        self.closed_nodes = ClosedNodes(5)
        self.sat = SatSolver(self, True, False, False)

        self.node = Node(formula, closure=self.closure, eventualities=self.closure.eventualities,
                         sat_solver=self.sat, closed_nodes=self.closed_nodes,tableau=self, traces=self.traces)

        if not configuration:
            self.configuration = {'execution_type': 0, 'sat_solver': False, 'non_determinism': True,
                                  'closed_nodes': ClosedNodes(5), 'z3': True}

    def tableau(self):
        if self.solve():
            self.traces.print_path()
            print('Model Found')
            return 1
        else:
            print('Model not found')
            return 0

    def solve(self):
        node = self.node
        self.steps += 1
        node.depth += 1
        self.traces.print_trace(node)
        self.traces.path.add_step(node)
        if self.closed_nodes.is_closed(node):
            self.rules.closed_node()
            self.traces.print_trace(node, trace_type='closed_node')
        elif '0' in node.set_of_formulae:
            self.rules.zero()
            self.traces.print_trace(node, trace_type='domination')
        elif node.is_elemental():
            self.traces.print_trace(node, trace_type='next_stage_1')
            if self.rules.next_stage(node):
                return True
        # elif self.configuration['z3'] and node.is_pp_set():
        #     if self.sat.call_z3_sat(node): return True
        # elif self.sat.sat and node.is_quasi_elemental():
        #     if self.sat.call_sat(node): return True
        else:
            if node.contains_marked_until():
                formula = node.remove_marked_until()
                if self.rules.marked_until_expansion(node, formula):
                    return True
            elif not node.marked_until and (self.node.have_until() or self.node.have_eventually()):
                formula = node.get_eventually()
                if self.rules.select_marked_until_and_expand(node, formula):
                    return True
            else:
                formula = node.pop_formula()
                self.traces.print_trace(node, formula)
                if formula.is_and():
                    if self.rules.and_expansion(formula, node):
                        return True
                elif formula.is_always():
                    if self.rules.always_expansion(formula, node):
                        return True
                elif formula.is_or():
                    if self.rules.or_expansion(formula, node):
                        return True
                elif formula.is_release():
                    if self.rules.release_expansion(formula, node):
                        return True
                elif formula.is_eventually():
                    if self.rules.eventually_expansion(formula, node):
                        return True
                elif formula.is_until():
                    if self.rules.until_expansion(formula, node):
                        return True
                else:
                    return True
            node.push_formula(formula)
        self.traces.pop_path()
        self.traces.close(node.depth)
        node.depth -= 1
        self.steps -= 1
        return False


def test(input_file, trace=False):
    if '.' in input_file:
        test_file(input_file, trace)
    else:
        test_formula(input_file, trace)


def test_formula(test_formula, trace):
    formula = process_formula(test_formula)
    tableau = Tableau(formula, trace)
    tableau.tableau()
    del tableau


def test_file(file, trace, line_by_line=True):
    with open(file) as f:
        input_text = f.read()
        input_text = input_text.replace(
            '\n\n', '\n').replace('\n', '').replace(' ', '')
    formula = process_formula(input_text)
    tableau = Tableau(formula, trace)
    tableau.tableau()


def execute_file(file, q=None):
    file_content = read_file(file)
    formula = process_formula(file_content)
    init_time = time.time()
    print("Init time: ", time.time())
    tableau = Tableau(formula)
    end_time = time.time() - init_time
    print("End time: ", time.time())
    res = tableau.tableau()
    if q:
        q.put([file, end_time, res])


if __name__ == '__main__':
    # test('a&b&c') # Done test('a&-a') # Done test('a&b&c&Gd') # Done test('a&b&G(-a)') # Done test('a|b|c') # Done
    # test('(Fc&G-a)|(Xb&-Fb)') test('aRb&-a') test('(G((f0 > -(f1))) & -(u) & f0 & -(b0) & -(b1) & -(up) & G((u = -(
    # X(u)))) & G(((u > ((f0 = X(f0)) & (f1 = X(f1)))) & (f0 > X((f0 | f1))) & (f1 > X((f0 | f1))))) & G(((-(u) > ((
    # b0 = X(b0)) & (b1 = X(b1)))) & ((b0 & -(f0)) > X(b0)) & ((b1 & -(f1)) > X(b1)))) & G((((f0 & X(f0)) > (up = X(
    # up))) & ((f1 & X(f1)) > (up = X(up))) & ((f0 & X(f1)) > up) & ((f1 & X(f0)) > -(up)))) & G((sb = (b0 | b1))) &
    # G((((f0 & -(sb)) > (f0 U (sb | (F(f0) & -(up))))) & ((f1 & -(sb)) > (f1 U (sb | (F(f0) & -(up))))))) & G(((b0 >
    # F(f0)) & (b1 > F(f1)))))') test_file(
    # '/home/daniel/Escritorio/Algorithms/Momo/momo_v1.0/tableaux/test/satisfiable/s14.txt') test('(((a U z ) U b ) U
    # c ) U ( - z ) &F z& G a& G b& F (- c)') test('(F(- d))&(G(F c))&(G(a -> (X(F e))))&(G(c -> (F a)))&(G((F e) ->
    # d))')

    # execute_file('../../benchmarks/crafted/schuppan_O1formula/O1formula200.pltl')

    execute_file('../../test/antiblack/O1formula8_modified.pltl')
    # test('G(-a|Fe)&G-a&GFa&X(((Fe&-d)&X((-a|(-a|Fe)|(d|G-e))R-a)&a&((-a|(-a|Fe)|(d|G-e))R-a))Ue)&(((Fe&-d)&(
    # G-e&a)&a)Ua)&((Fe&-d)&X((-a|(-a|Fe)|(d|G-e))R-a)&a)&G(d|G-e)') ## test('XG-a&X((a&(-d&Fe))Ua)&G-e') test('G(
    # -a|Fe)&GFa&((X((-a|(-a|Fe))R-a)&a&(-d&Fe))Ue)&G(G-e|d)&G-a&((a&(G-e&a))Ua)') test('G-e&G(d|G-e)&((-a&d&(
    # Fe&-d))Ue)&GFa&G(Fe|-a)') test('G-a&((a)Ua)') test('e&(d|G-e)&G-e&GFa') test('G(F a)&G(F(-a))') test('(F(-
    # d))&(G(F c))&(G(a -> (X(F e))))&(G(c -> (F a)))&(G((F e) -> d))') test('c&G-e&XG(XFe|-a)&-e&XG(Fa|-c)&XG(
    # d|G-e)&XG-e&X((XFG-c&-c)Uc)&(Fa|-c)&(XFe|-a)&XGFc')
    # test('-a&XG-e&Xe&XG-e&XFa&-e&XG(G-e|d)&XGFa&XG(-a|Fe)')

    # Remaining
    # eventualities: {'e'}
    # Fulfilled
    # eventualities: {'-d', 'a'}
