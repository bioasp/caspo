from networkx.drawing.nx_pydot import write_dot

class DotWriter(object):
    
    def to_dot(self, filename):
        write_dot(self.graph, filename)