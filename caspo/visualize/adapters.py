# Copyright (c) 2014, Santiago Videla
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
import os
from zope import component, interface
from caspo import core, control, analyze
import networkx as nx

from interfaces import *

class DotWriterAdapter(object):
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
    
    def write(self, filename, path="./"):
        if not os.path.exists(path):
            os.mkdir(path)

        nx.write_dot(self.graph, os.path.join(path, filename))
        printer = component.getUtility(core.IPrinter)
        printer.pprint("Wrote %s" % os.path.join(path, filename))

class Graph2MultiDiGraph(object):
    component.adapts(core.IGraph)
    interface.implements(IMultiDiGraph)
    
    def __init__(self, graph):
        self.nxGraph = nx.MultiDiGraph()
        self.nxGraph.add_nodes_from(graph.nodes)
        for source, target, sign in graph.edges:
            self.nxGraph.add_edge(source, target, sign=sign)
            
class LogicalNetwork2MultiDiGraph(object):
    component.adapts(core.ILogicalNetwork)
    interface.implements(IMultiDiGraph)
    
    def __init__(self, network):
        self.nxGraph = nx.MultiDiGraph()
        gaten = 1
        for target, formula in network.mapping.iteritems():
            self.nxGraph.add_node(target)
            for clause in formula:
                if len(clause) > 1:
                    gate = 'gate-%s' % gaten
                    gaten += 1
                    self.nxGraph.add_node(gate, gate=True)
                    self.nxGraph.add_edge(gate, target, sign=1)
                    
                    for var,sign in clause:
                        self.nxGraph.add_node(var)
                        self.nxGraph.add_edge(var, gate, sign=sign)
                else:
                    var, sign = list(clause)[0]
                    self.nxGraph.add_node(var)
                    self.nxGraph.add_edge(var, target, sign=sign)

class LogicalNetworkSet2MultiDiGraph(object):
    component.adapts(core.ILogicalNetworkSet)
    interface.implements(IMultiDiGraph)
    
    def __init__(self, networks):
        self.nxGraph = nx.MultiDiGraph()
        gaten = 1
        stats = analyze.IStats(networks)
        added = set()
        for network in networks:
            for target, formula in network.mapping.iteritems():
                self.nxGraph.add_node(target)
                for clause in formula:
                    if (target, clause) not in added:
                        added.add((target, clause))
                        if len(clause) > 1:
                            gate = 'gate-%s' % gaten
                            gaten += 1
                            self.nxGraph.add_node(gate, gate=True)
                            self.nxGraph.add_edge(gate, target, sign=1, weight=stats.frequency((clause, target)))
                    
                            for var,sign in clause:
                                self.nxGraph.add_node(var)
                                self.nxGraph.add_edge(var, gate, sign=sign, weight=stats.frequency((clause, target)))
                        else:
                            var, sign = list(clause)[0]
                            self.nxGraph.add_node(var)
                            self.nxGraph.add_edge(var, target, sign=sign, weight=stats.frequency((clause, target)))
        
        
class MultiDiGraphSetup2DotWriter(DotWriterAdapter):
    component.adapts(IMultiDiGraph, core.ISetup)
    interface.implements(IDotWriter)
    
    def __init__(self, graph, setup):
        self.graph = graph.nxGraph
        self.setup = setup
        
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

class StrategySet2DiGraph(object):
    component.adapts(control.IStrategySet)
    interface.implements(IDiGraph)

    def __init__(self, strategies):
        self.nxGraph = nx.DiGraph()
        self.CONSTRAINTS = 'constraints'
        self.nxGraph.add_node(self.CONSTRAINTS, label='SCENARIOS CONSTRAINTS')

        self.GOALS = 'goals'
        self.nxGraph.add_node(self.GOALS, label='SCENARIOS GOALS')
        
        self.__create_tree__(self.CONSTRAINTS, strategies)
        
    def __create_tree__(self, parent, strategies=None):
        if strategies:
            stats = analyze.IStats(strategies)
            ssorted = sorted(stats.frequencies(), key=lambda (k,f): f)
        
            root, freq = ssorted.pop()
            root_in = filter(lambda strategy: root in strategy, strategies)

            name = "%s-%s" % (parent, root)
            self.nxGraph.add_node(name, label=root.variable, sign=root.signature)            
            self.nxGraph.add_edge(parent, name)
            
            remaining = control.StrategySet(filter(lambda strategy: len(strategy),
                                                   map(lambda strategy: strategy.difference([root]), root_in)))    
            self.__create_tree__(name, remaining)

            root_out = filter(lambda strategy: root not in strategy, strategies)
            if root_out:
                self.__create_tree__(parent, control.StrategySet(root_out))
            
        else:
            self.nxGraph.add_edge(parent, self.GOALS)

class DiGraph2DotWriter(DotWriterAdapter):
    component.adapts(IDiGraph)
    interface.implements(IDotWriter)
    
    def __init__(self, graph):
        self.graph = graph.nxGraph
        
        for node in self.graph.nodes():
            _type = 'DEFAULT'
            for attr, value in self.NODES_ATTR[_type].items():
                self.graph.node[node][attr] = value
            
            if 'sign' in self.graph.node[node]:
                if self.graph.node[node]['sign'] == 1:
                    _type = 'STIMULI'
                elif self.graph.node[node]['sign'] == -1:
                    _type = 'INHIBITOR'
                    
                if _type != 'DEFAULT':
                    for attr, value in self.NODES_ATTR[_type].items():
                        self.graph.node[node][attr] = value
                        self.graph.node[node]['shape'] = 'box'

