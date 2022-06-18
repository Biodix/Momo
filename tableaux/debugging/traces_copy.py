from itertools import islice



colors = {
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

backgrounds = {
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
reset = '\u001b[0m'

def print_trace(self, node=None, formula=None, trace_type='regular_trace'):
    if self.traces:
        if trace_type == 'regular_trace':
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
            _print('Remaining eventualities: {}\nFulfilled eventualities: {}'
                       .format(remaining_eventualities, fulfilled_eventualities), 'blue')
            _print('Set of formulae:', 'yellow')
            if self.line_by_line:
                for f in infix_set:
                    _print(f, 'yellow')
            else:
                _print(infix_set, 'yellow')
            _print('\nSelected formula: \n{}'.format(self.prefix_to_infix(formula)), 'green')
            if node.marked_until:
                _print('Marked Until infix: {}'.format(self.prefix_to_infix(node.marked_until)), 'magenta')
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
            _print('Node previously closed', 'red')
            _print(self.prefix_to_infix_set(node.set_of_formulae), 'red')
        elif trace_type == 'domination':
            _print('0 in set of formulae', 'red')

def contradiction(self, formula, neg_formula):
    if self.traces:
        _print('Contradiction between {} and {}'.format(formula, neg_formula), 'red')




def _print(self, text, color=None, background=None):
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
    if type(formula) == str:
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


if __name__ == '__main__':
    colors = TraceColors()
    print(colors.green + 'Esto es una prueba de los colores' + colors.reset)
    print(colors.bright_green + 'Esto es una prueba de los colores' + colors.reset)
    print(colors.yellow + 'Esto es una prueba de los colores' + colors.reset)
    print(colors.blue + 'Esto es una prueba de los colores' + colors.reset)
    print(colors.bright_blue + 'Esto es una prueba de los colores' + colors.reset)
    print(colors.cyan + 'Esto es una prueba de los colores' + colors.reset)
