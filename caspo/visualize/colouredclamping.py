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

class ColouredClamping(object):
    """
    A coloured variables clamping to be written as a dot file
    
    Parameters
    ----------
    clamping : :class:`caspo.core.clamping.ClampingList`
        List of clampings to be coloured
    
    source : str
        Optional node name to be used as source
    
    target : str
        Optional node name to be used as target
    
    Attributes
    ----------
    graph : `networkx.DiGraph`_
    
    
    .. _networkx.DiGraph: https://networkx.readthedocs.io/en/stable/reference/classes.digraph.html#networkx.DiGraph
    """

    def __init__(self, clamping, source="", target=""):
        self.graph = clamping.__plot__(source=source, target=target)
        
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
