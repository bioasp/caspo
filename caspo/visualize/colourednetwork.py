# Copyright (c) 2014-2016, Santiago Videla
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
import settings

class ColouredNetwork(object):
    """
    A coloured (hyper-)graph to be written as a dot file
    
    Parameters
    ----------
    network : object
        An object implementing a `__plot__` which must return the `networkx.MultiDiGraph`_ instance to be coloured
    
    Attributes
    ----------
    graph : `networkx.MultiDiGraph`_
    
    
    .. _networkx.MultiDiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.multidigraph.html#networkx.MultiDiGraph
    """
    
        
    def __init__(self, network, setup):
        self.graph = network.__plot__()

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

