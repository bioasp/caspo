import settings
from writer import DotWriter

class ColoredNetwork(DotWriter):
        
    def __init__(self, digraph, setup):
        self.graph = digraph.__plot__()

        for node in self.graph.nodes():
            _type = 'DEFAULT'
            for attr, value in settings.NODES_ATTR[_type].items():
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
                for attr, value in settings.NODES_ATTR[_type].items():
                    self.graph.node[node][attr] = value
            
        for source, target in self.graph.edges():
            for k in self.graph.edge[source][target]:
                for attr, value in settings.EDGES_ATTR['DEFAULT'].items():
                    self.graph.edge[source][target][k][attr] = value
                
                for attr, value in settings.EDGES_ATTR[self.graph.edge[source][target][k]['sign']].items():
                    self.graph.edge[source][target][k][attr] = value
                
                if 'weight' in self.graph.edge[source][target][k]:
                    self.graph.edge[source][target][k]['penwidth'] = 5 * self.graph.edge[source][target][k]['weight']

