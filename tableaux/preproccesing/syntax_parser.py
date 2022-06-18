from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


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
    grammar = '''\
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
    '''
    try:
        parsed_text = Evaluator(grammar, text.replace("\t","").replace(" ", "").replace("fUll","full")).op
        if not isinstance(text, list):
            parsed_text = parsed_text
    except Exception as e:
        print('Failed at: ' + str(e))
        parsed_text = None
        exit(0)
    return parsed_text