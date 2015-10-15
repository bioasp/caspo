import settings
from writer import DotWriter

class ColoredClamping(DotWriter):

    def __init__(self, graph, source="", target=""):
        self.graph = graph.__plot__(source, target)
        
        for node in self.graph.nodes():
            _type = 'DEFAULT'
            for attr, value in settings.NODES_ATTR[_type].items():
                self.graph.node[node][attr] = value
            
            if 'sign' in self.graph.node[node]:
                if self.graph.node[node]['sign'] == 1:
                    _type = 'STIMULI'
                elif self.graph.node[node]['sign'] == -1:
                    _type = 'INHIBITOR'
                    
                if _type != 'DEFAULT':
                    for attr, value in settings.NODES_ATTR[_type].items():
                        self.graph.node[node][attr] = value
                        self.graph.node[node]['shape'] = 'box'
