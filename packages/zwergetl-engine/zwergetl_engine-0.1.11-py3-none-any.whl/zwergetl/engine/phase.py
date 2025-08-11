
class Phase:
    """Phase is a group of nodes in a graph. Phases are executed sequentially.
    If a phase fails, the graph is stopped.
    """
    
    def __init__(self, phase_number)->None:
        self.phase_number = phase_number
        self._nodes = dict()
        self.graph = None

    def add_node(self, node):
        """Add node to the phase"""
        self._nodes[node.node_id] = node
        node.graph = self.graph

    def get_node(self, node_id):
        """Get node by node_id"""
        return self._nodes[node_id]

    def get_nodes(self):
        """Get all nodes of the phase"""
        return self._nodes
