from itertools import islice
from tableaux.tl_basics.formula import Formula, Atom
from tableaux.preproccesing.syntax_parser import parse_formula

BINARY_OPERATORS = ['|', '&']
UNARY_OPERATORS = ['G', 'X', 'F', '-']
SPECIAL_OPERATORS = ['>', '->', 'U', 'R', '=']


def read_file(file):
    with open(file) as f:
        content = f.read()
    return content


def process_formula(formula):
    formula = reformat(formula)
    parsed_formula = parse_formula(formula)
    n_ary_formula = bin_to_n(parsed_formula)
    nnf_formula = n_ary_formula.nnf()
    return nnf_formula

def reformat(formula):
    reformatted_formula = formula.replace('\n', '').replace(' ', '').replace('!','-')
    return reformatted_formula

def get_operator(tree):
    return 0 if type(tree) != Formula and type(tree) != list else tree[0]


def bin_to_n(formula):
    """
    Convert a binary tree formula into n-ary tree.

    Parameters
    ----------
    formula: list
        PLTL formula represented as tuple of tuples.

    Returns
    -------
    tree: tuple
        Input binary tree as n-ary tree.

    Examples
    --------
    >>> bin_to_n(['&', 'a', ['&', 'b' ,'c']])
    ('&', 'a', 'b', 'c')

    """
    if get_operator(formula) == 0:
        return Atom(formula)

    operator = formula[0]
    out = [operator]
    if operator == '-' and get_operator(formula[1]) == operator:
        return bin_to_n(formula[1][1])
    if operator in SPECIAL_OPERATORS:
        return Formula((operator, bin_to_n(formula[1]), bin_to_n(formula[2])))

    for node in islice(formula, 1, None):
        flat_node = bin_to_n(node)
        op_flat_node = get_operator(flat_node)
        if op_flat_node != operator or (op_flat_node == 'X' and operator == 'X'):
            out.append(flat_node)
        else:
            if get_operator(out) == '|' or get_operator(out) == '&':
                out.extend(flat_node[1])
            else:
                out.extend(islice(flat_node, 1, None))
    out_op = get_operator(out)
    if out_op == '|' or out_op == '&':
        return Formula([out_op, frozenset(islice(out, 1, None))])
    else:
        return Formula(out)



if __name__ == '__main__':
    formula = process_formula(
        '(G((f0 > -(f1))) & -(u) & f0 & -(b0) & -(b1) & -(up) & G((u = -(X(u)))) & G(((u > ((f0 = X(f0)) & (f1 = X('
        'f1)))) & (f0 > X((f0 | f1))) & (f1 > X((f0 | f1))))) & G(((-(u) > ((b0 = X(b0)) & (b1 = X(b1)))) & ((b0 & -('
        'f0)) > X(b0)) & ((b1 & -(f1)) > X(b1)))) & G((((f0 & X(f0)) > (up = X(up))) & ((f1 & X(f1)) > (up = X(up))) '
        '& ((f0 & X(f1)) > up) & ((f1 & X(f0)) > -(up)))) & G((sb = (b0 | b1))) & G((((f0 & -(sb)) > (f0 U (sb | (F('
        'f0) & -(up))))) & ((f1 & -(sb)) > (f1 U (sb | (F(f0) & -(up))))))) & G(((b0 > F(f0)) & (b1 > F(f1)))))')
    # formula = process_formula('(a&a&a)|(a&a&a)|(b|b|b)')
    print(formula)
