class ClosedNodes:
    def __init__(self, threshold=2):
        self.threshold = threshold
        self.closed_nodes = set()

    def update_closed_nodes(self, node):
        if node.depth >= self.threshold:
            closed_node = frozenset(node.set_of_formulae)
            self.closed_nodes.add(closed_node)

    def is_closed(self, node, enhanced=False):
        if not enhanced:
            if node.set_of_formulae in self.closed_nodes:
                return True
            else:
                return False
        else:
            for closed_node in self.closed_nodes:
                if node.set_of_formulae <= closed_node:
                    return True
            return False
