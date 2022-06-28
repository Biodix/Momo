from itertools import islice
from tableaux.tl_basics.formula import Formula, Atom

class Path:
    def __init__(self):
        self.path = []
        self.rules = []
        self.selected_formulae = []

    def add_step(self, step):
        pass

    def pop_step(self):
        pass

    def add_rule(self, rule):
        pass

    def pop_rule(self):
        pass

    def add_selected_formula(self, selected_formula):
        pass

    def pop_selected_formula(self):
        pass

####################### BACKUP #########################
    # def add_step(self, step):
    #     self.path.append(step.set_of_formulae.copy())

    # def pop_step(self):
    #     self.path.pop()

    # def add_rule(self, rule):
    #     self.rules.append(rule)

    # def pop_rule(self):
    #     self.rules.pop()

    # def add_selected_formula(self, selected_formula):
    #     self.selected_formulae.append(selected_formula)

    # def pop_selected_formula(self):
    #     self.selected_formulae.pop()


class Trace:
    def __init__(self, traces=False, line_by_line=False):
        self.traces = traces
        self.path = Path()
        self.line_by_line = line_by_line
        self.colors2 = {
            'white': '\u001b[37m',
            'black': '\u001b[30m',
            'red': '\u001b[31m',
            'green': '\u001b[32m',
            'blue': '\u001b[34m',
            'yellow': '\x1b[38;5;226m',
            'magenta': '\u001b[35m',
            'pink': '\x1b[38;5;200m',
            'cyan': '\u001b[36m',
            'bright_green': '\x1b[38;5;82m',
            'dark_yellow': '\u001b[33m',
            'bright_blue': '\x1b[38;5;195m',
            'dark_blue': '\x1b[38;5;21m',
            'reset': '\u001b[0m'
        }

        self.backgrounds2 = {
            'black': '\u001b[40;1m',
            'white': '\u001b[47;1m',
            'grey': '\u001b[48;5;239m',
            'red': '\u001b[41;1m',
            'green': '\u001b[42;1m',
            'yellow': '\u001b[43;1m',
            'blue': '\u001b[44;1m',
            'magenta': '\u001b[45;1m',
            'cyan': '\u001b[46;1m',
            'reset': '\u001b[0m'
        }
        self.reset2 = '\u001b[0m'


        self.colors = {
            'white': '',
            'black': '',
            'red': '',
            'green': '',
            'blue': '',
            'yellow': '',
            'magenta': '',
            'pink': '',
            'cyan': '',
            'bright_green': '',
            'dark_yellow': '',
            'bright_blue': '',
            'dark_blue': '',
            'reset': ''
        }

        self.backgrounds = {
            'black': '',
            'white': '',
            'grey': '',
            'red': '',
            'green': '',
            'yellow': '',
            'blue': '',
            'magenta': '',
            'cyan': '',
            'reset': ''
        }
        self.reset = ''

    #TODO: Fix model print
    def print_model(self, node):
        i = 0
        found = False
        node.cycles.stage_literals[-1].update(node.formulae_operators['L'])
        pf = node.cycles.previous_formulae.pop()
        sl = node.cycles.stage_literals.pop()
        cycle_start = 0
        for set_of_formulas, literals in zip(node.cycles.previous_formulae, node.cycles.stage_literals):
            if node.set_of_formulae.issubset(set_of_formulas) and not found:
                cycle_start = i
                found = True
            print('stage {}:'.format(i))
            print(self.prefix_to_infix_set(literals))
            i += 1
        node.cycles.previous_formulae.append(pf)
        node.cycles.stage_literals.append(sl)
        print('\nCycle starts at stage {}'.format(cycle_start))

    # TODO: CUIDADO CON ESTE COMENTARIO, HAY QUE ARREGLARLO
    def pop_path(self):
        return
        self.path.path.pop()
        self.path.rules.pop()
        self.path.selected_formulae.pop()

    def print_path(self):
        if self.traces:
            for s, r, sf in zip(self.path.path, self.path.rules, self.path.selected_formulae):
                # print(str(self.prefix_to_infix_set(s.set_of_formulae)) + str(r) + str(sf))
                step = self.prefix_to_infix_set(s)
                selected_formula = self.prefix_to_infix(sf)
                step_str = '{'
                for f in step:
                    if f == selected_formula:
                        step_str += '\u001b[42;1m' + f + '\u001b[0m, '
                    else:
                        step_str += f + ', '
                step_str = step_str[:-2] + '}'
                print('{}, \u001b[31m{}\u001b[0m'.format(step_str, r))

    def print_trace(self, node=None, formula=None, trace_type='regular_trace'):
        if self.traces:
            if not formula and trace_type == 'regular_trace':
                print('\n\n-----------------------------------------------')
                print('Recursion depth = {}'.format(node.depth))
                infix_set = set()
                remaining_eventualities = set()
                fulfilled_eventualities = set()
                for f in node.set_of_formulae:
                    infix_set.add(self.prefix_to_infix(f))
                for f in node.eventualities.remaining:
                    remaining_eventualities.add(self.prefix_to_infix(f))
                for f in node.eventualities.fulfilled:
                    fulfilled_eventualities.add(self.prefix_to_infix(f))
                self.print('Remaining eventualities: {}\nFulfilled eventualities: {}'
                           .format(remaining_eventualities, fulfilled_eventualities), 'blue')
                #self.print('Eventualities: {}'.format(self.prefix_to_infix_set(node.eventualities.eventualities)), 'blue')
                self.print('Set of formulae:', 'yellow')
                if self.line_by_line:
                    for f in infix_set:
                        self.print(f, 'yellow')
                else:
                    self.print(infix_set, 'yellow')
            elif formula and trace_type == 'regular_trace':
                self.print('\nSelected formula: \n{}'.format(self.prefix_to_infix(formula)), 'green')
                if node.marked_until:
                    self.print('Marked Until infix: {}'.format(self.prefix_to_infix(node.marked_until)), 'magenta')
                if formula.is_and():
                    print('and Expansion')
                elif formula.is_or():
                    print('or Expansion')
                elif formula.is_always():
                    print('always Expansion')
                elif formula.is_release():
                    print('release Expansion')
                elif formula.is_eventually():
                    if formula == node.marked_until or node.marked_until is None:
                        print('eventually+ Expansion')
                    else:
                        print('eventually Expansion')
                elif formula.is_until():
                    if formula == node.marked_until or node.marked_until is None:
                        print('until+ Expansion')
                    else:
                        print('until Expansion')
            elif trace_type == 'closed_node':
                self.print('Node previously closed', 'red')
            elif trace_type == 'domination':
                self.print('0 in set of formulae', 'red')
            elif trace_type == 'next_stage_1':
                self.next_stage_1(node)
            elif trace_type == 'next_stage_2':
                self.next_stage_2(node)

    def next_stage_1(self, node):
        infix_set_next = set()
        infix_set_literals = set()
        for f in node.formulae_operators['X']:
            infix_set_next.add(self.prefix_to_infix(f))
        for f in node.formulae_operators['L']:
            infix_set_literals.add(self.prefix_to_infix(f))
        self.print('\nCurrent Stage\nNext: {}\nLiterals: {}'.format(infix_set_next, infix_set_literals), 'green')

    def next_stage_2(self, node):
        if self.traces:
            infix_set = set()
            for f in node.set_of_formulae:
                infix_set.add(self.prefix_to_infix(f))
            self.print('\nNext Stage: {}'.format(infix_set), 'pink')

    def contradiction(self, formula, neg_formula):
        if self.traces:
            self.print('Contradiction between {} and {}'.format(formula, neg_formula), 'red')

    def close(self, depth):
        if self.traces:
            self.print('Closed branch, back to n: {}'.format(depth - 1), 'white')

    def print(self, text, color=None, background=None):
        if color:
            colored_text = '{}{}{}'.format(self.colors[color], text, self.reset)
            print(colored_text)
        elif background:
            background_text = '{}{}{}'.format(self.backgrounds[background], text, self.reset)
            print(background_text)
        else:
            print(text)

    def prefix_to_infix(self, formula):
        if not formula:
            return
        if type(formula) == Atom:
            return formula
        element = formula[0]
        if element in {'&', '|'}:
            sol = []
            sol.append('(')
            f = formula[1]
            sol.append(self.prefix_to_infix(next(iter(f))))
            for e in islice(f, 1, None):
                sol.append(element)
                sol.append(self.prefix_to_infix(e))
            sol.append(')')
            # return sol
            return ''.join(map(str, sol))
        elif element in {'U', 'R'}:
            sol = []
            sol.append('(')
            sol.append(self.prefix_to_infix(formula[1]))
            sol.append(element)
            sol.append(self.prefix_to_infix(formula[2]))
            sol.append(')')
            # return sol
            return ''.join(map(str, sol))
        elif element in {'-', 'G', 'F', 'X'}:
            sol = []
            sol.append(element)
            sol.append(self.prefix_to_infix(formula[1]))
            # return sol
            return ''.join(map(str, sol))
        else:
            return element

    def prefix_to_infix_set(self, set_of_formulae):
        set_of_formulas_infix = []
        for formula in set_of_formulae:
            set_of_formulas_infix.append(self.prefix_to_infix(formula))
        return set_of_formulas_infix

    def sat_trace(self, node):
        if self.traces:
            self.print('SAT-Solver: Glucose 4', color='red')

    def sat_trace_i(self, node, set_of_formulae_copy, i):
        if self.traces:
            print('Set of formulas: {}'.format(self.prefix_to_infix_set(set_of_formulae_copy)))
            print('SAT Model {}: {}'.format(i, self.prefix_to_infix_set(node.set_of_formulae)))


class TraceColors:
    white = '\u001b[37m'
    black = '\u001b[30m'
    red = '\u001b[31m'
    green = '\u001b[32m'
    blue = '\u001b[34m'
    yellow = '\x1b[38;5;226m'
    magenta = '\u001b[35m'
    pink = '\x1b[38;5;200m'
    cyan = '\u001b[36m'

    bright_green = '\x1b[38;5;82m'
    dark_yellow = '\u001b[33m'
    bright_blue = '\x1b[38;5;195m'
    dark_blue = '\x1b[38;5;21m'

    reset = '\u001b[0m'


class TraceBackgrounds:
    black = '\u001b[40;1m'
    white = '\u001b[47;1m'
    grey = '\u001b[48;5;239m'
    red = '\u001b[41;1m'
    green = '\u001b[42;1m'
    yellow = '\u001b[43;1m'
    blue = '\u001b[44;1m'
    magenta = '\u001b[45;1m'
    cyan = '\u001b[46;1m'

    reset = '\u001b[0m'

    def print_trace_copy(self, node=None, formula=None, trace_type='regular_trace'):
        if self.traces:
            if not formula and trace_type == 'regular_trace':
                print('\n\n-----------------------------------------------')
                print('Recursion depth = {}'.format(node.depth))
                infix_set = set()
                remaining_eventualities = set()
                fulfilled_eventualities = set()
                infix_set.add(self.prefix_to_infix(formula))
                for f in node.set_of_formulae:
                    infix_set.add(self.prefix_to_infix(f))
                for f in node.eventualities.remaining:
                    remaining_eventualities.add(self.prefix_to_infix(f))
                for f in node.eventualities.fulfilled:
                    fulfilled_eventualities.add(self.prefix_to_infix(f))
                self.print('Remaining eventualities: {}\nFulfilled eventualities: {}'
                           .format(remaining_eventualities, fulfilled_eventualities), 'blue')
            elif trace_type == 'regular_trace':
                print('\n\n-----------------------------------------------')
                print('Recursion depth = {}'.format(node.depth))
                infix_set = set()
                remaining_eventualities = set()
                fulfilled_eventualities = set()
                infix_set.add(self.prefix_to_infix(formula))
                for f in node.set_of_formulae:
                    infix_set.add(self.prefix_to_infix(f))
                for f in node.eventualities.remaining:
                    remaining_eventualities.add(self.prefix_to_infix(f))
                for f in node.eventualities.fulfilled:
                    fulfilled_eventualities.add(self.prefix_to_infix(f))
                self.print('Remaining eventualities: {}\nFulfilled eventualities: {}'
                           .format(remaining_eventualities, fulfilled_eventualities), 'blue')
                self.print('Set of formulae:', 'yellow')
                if self.line_by_line:
                    for f in infix_set:
                        self.print(f, 'yellow')
                else:
                    self.print(infix_set, 'yellow')
                self.print('\nSelected formula: \n{}'.format(self.prefix_to_infix(formula)), 'green')
                if node.marked_until:
                    self.print('Marked Until infix: {}'.format(self.prefix_to_infix(node.marked_until)), 'magenta')
                if formula.is_and():
                    print('and Expansion')
                elif formula.is_or():
                    print('or Expansion')
                elif formula.is_always():
                    print('always Expansion')
                elif formula.is_release():
                    print('release Expansion')
                elif formula.is_eventually():
                    if formula == node.marked_until or node.marked_until is None:
                        print('eventually+ Expansion')
                    else:
                        print('eventually Expansion')
                elif formula.is_until():
                    if formula == node.marked_until or node.marked_until is None:
                        print('until+ Expansion')
                    else:
                        print('until Expansion')
            elif trace_type == 'closed_node':
                self.print('Node previously closed', 'red')
                self.print(self.prefix_to_infix_set(node.set_of_formulae), 'red')
            elif trace_type == 'domination':
                self.print('0 in set of formulae', 'red')
            elif trace_type == 'next_stage_1':
                self.next_stage_1(node)
            elif trace_type == 'next_stage_2':
                self.next_stage_2(node)


if __name__ == '__main__':
    pass
