import networkx as nx

class DotWriter(object):
    
    def to_dot(self, filename):
        nx.write_dot(self.graph, filename)