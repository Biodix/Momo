from momo.tl.formula import Formula, Atom
from itertools import islice
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

BINARY_OPERATORS = ["|", "&"]
UNARY_OPERATORS = ["G", "X", "F", "-"]
SPECIAL_OPERATORS = [">", "->", "U", "R", "="]


def read_file(file):
    with open(file) as f:
        content = f.read()
    return content


def reformat(formula):
    reformatted_formula = formula.replace("\n", "").replace(" ", "").replace("!", "-")
    return reformatted_formula


def process_formula(formula):
    formula = reformat(formula)
    parsed_formula = parse_formula(formula)
    n_ary_formula = bin_to_n(parsed_formula)
    nnf_formula = n_ary_formula.nnf()
    return nnf_formula


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
    if operator == "-" and get_operator(formula[1]) == operator:
        return bin_to_n(formula[1][1])
    if operator in SPECIAL_OPERATORS:
        return Formula((operator, bin_to_n(formula[1]), bin_to_n(formula[2])))

    for node in islice(formula, 1, None):
        flat_node = bin_to_n(node)
        op_flat_node = get_operator(flat_node)
        if op_flat_node != operator or (op_flat_node == "X" and operator == "X"):
            out.append(flat_node)
        else:
            if get_operator(out) == "|" or get_operator(out) == "&":
                out.extend(flat_node[1])
            else:
                out.extend(islice(flat_node, 1, None))
    out_op = get_operator(out)
    if out_op == "|" or out_op == "&":
        return Formula([out_op, frozenset(islice(out, 1, None))])
    else:
        return Formula(out)


class Evaluator(NodeVisitor):
    def __init__(self, grammar, text):
        ast = Grammar(grammar).parse(text)
        # print ast
        self.op = self.visit(ast)

    def generic_visit(self, node, children):
        if len(children) == 0:
            return node.text
        elif len(children) == 1:
            return children[0]
        elif len(children) == 2:
            return [children[0], children[1]]
        elif children[0] == "(":
            return children[1]
        else:
            return [children[1], children[0], children[2]]


def parse_formula(text):
    # The lower the higher the precedence
    grammar = """\
            exprIMP = (exprOR (">" / "->" / "=") exprIMP) / exprOR
            exprOR = (exprAND "|" exprOR) / exprAND
            exprAND = (exprBIN "&" exprAND) / exprBIN
            exprBIN = (exprUNA simbBIN exprBIN) / exprUNA
            exprUNA = (simbUNA (exprTERM / exprUNA)) / exprPAR
            exprPAR = ("(" exprIMP ")") / exprTERM
            simbUNA = "-" / "G" / "F" / "X"
            simbBIN = "U" / "R"
            exprTERM = "true" / "false" / "1" / "0" /var
            var = ~"(([a-z_AP]|(G\d+))+\d*(\_\d*)?)"
            _ = ~"\s*"
    """
    try:
        parsed_text = Evaluator(
            grammar, text.replace("\t", "").replace(" ", "").replace("fUll", "full")
        ).op
        if not isinstance(text, list):
            parsed_text = parsed_text
    except Exception as e:
        print("Failed at: " + str(e))
        parsed_text = None
        exit(0)
    return parsed_text
