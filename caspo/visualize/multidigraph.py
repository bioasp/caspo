
import networkx as nx

class ColoredMultiDiGraph(object):
    
    NODES_ATTR = {
        'DEFAULT':   {'color': 'black', 'fillcolor': 'white', 'style': 'filled, bold', 'fontname': 'Helvetica', 'fontsize': 18, 'shape': 'ellipse'},
        'STIMULI':   {'color': 'olivedrab3', 'fillcolor': 'olivedrab3'},
        'INHIBITOR': {'color': 'orangered',  'fillcolor': 'orangered'},
        'READOUT':   {'color': 'lightblue',  'fillcolor': 'lightblue'},
        'INHOUT':    {'color': 'orangered',  'fillcolor': 'SkyBlue2', 'style': 'filled, bold, diagonals'},
        'GATE' :     {'fillcolor': 'black', 'fixedsize': True, 'width': 0.2, 'height': 0.2, 'label': '.'}
    }
    
    EDGES_ATTR = {
        'DEFAULT': {'dir': 'forward', 'penwidth': 2.5},
         1  : {'color': 'forestgreen', 'arrowhead': 'normal'},
        -1  : {'color': 'red', 'arrowhead': 'tee'}
    }
    
    def __init__(self, digraph, setup):
        self.graph = digraph.__plot__()

        for node in self.graph.nodes():
            _type = 'DEFAULT'
            for attr, value in self.NODES_ATTR[_type].items():
                self.graph.node[node][attr] = value
            
            if 'gate' in self.graph.node[node]:
                _type = 'GATE'
            elif node in setup.stimuli:
                _type = 'STIMULI'
            elif node in setup.readouts and node in setup.inhibitors:
                _type = 'INHOUT'
            elif node in setup.readouts:
                _type = 'READOUT'
            elif node in setup.inhibitors:
                _type = 'INHIBITOR'    

            if _type != 'DEFAULT':
                for attr, value in self.NODES_ATTR[_type].items():
                    self.graph.node[node][attr] = value
            
        for source, target in self.graph.edges():
            for k in self.graph.edge[source][target]:
                for attr, value in self.EDGES_ATTR['DEFAULT'].items():
                    self.graph.edge[source][target][k][attr] = value
                
                for attr, value in self.EDGES_ATTR[self.graph.edge[source][target][k]['sign']].items():
                    self.graph.edge[source][target][k][attr] = value
                
                if 'weight' in self.graph.edge[source][target][k]:
                    self.graph.edge[source][target][k]['penwidth'] = 5 * self.graph.edge[source][target][k]['weight']

    def to_dot(self,filename):
        nx.write_dot(self.graph, filename)
