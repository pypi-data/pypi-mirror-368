from zwergetl.engine.phase import Phase

class Graph:
    """An object that defines a data transformation process.
    """

    def __init__(self)->None:
        self._phases = list()
        #self._nodes = dict()
        self._connections = dict()

    def get_current_phase(self):
        """Returns the last phase of the graph"""
        res = None
        phases_count = len(self._phases)
        if phases_count > 0:
            res = self._phases[phases_count-1]
        return res

    def add_phase(self, phase):
        """Adds an already created phase"""
        self._phases.append(phase)

    def new_phase(self):
        """Creates a new phase and returns it"""
        phases_count = len(self._phases)
        phase = Phase(phases_count)
        phase.graph = self
        self._phases.append(phase)
        return phase

    def add_node(self, node):
        """Adds node to the last phase of the graph"""
        ph = self.get_current_phase()
        if ph is None:
            ph = self.new_phase()
        ph.add_node(node)

    def add_connection(self, conn):
        """Adds or replaces a connection to the graph"""
        self._connections[conn.conn_id] = conn

    #def get_node(self, node_id):
    #    return self._nodes[node_id]

    def get_connection(self, conn_id):
        """Returns connection object by it's id"""
        return self._connections[conn_id]

    #def get_nodes(self):
    #    return self._nodes

    def get_phases(self):
        """Returns list of graph's phases"""
        return self._phases
