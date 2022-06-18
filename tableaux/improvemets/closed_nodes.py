class ClosedNodes:
    def __init__(self, threshold=2, shared_dict=False):
        self.threshold = threshold
        if shared_dict:
            self.shared_memory = True
            self.closed_nodes = shared_dict
        else:
            self.shared_memory = False
            self.closed_nodes = set()

    def update_closed_nodes(self, node):
        if node.depth >= self.threshold:
            closed_node = frozenset(node.set_of_formulae)
            if self.shared_memory:
                self.closed_nodes[closed_node] = 1
            else:
                self.closed_nodes.add(closed_node)

    def is_closed(self, node):
        if self.shared_memory:
            if frozenset(node.set_of_formulae) in self.closed_nodes:
                return True
            else:
                return False
        else:
            if node.set_of_formulae in self.closed_nodes:
                return True
            else:
                return False
