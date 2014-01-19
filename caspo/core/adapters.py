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
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-

from collections import defaultdict

from zope import component

from pyzcasp import asp

from interfaces import *
from impl import *

class GraphAdapter(object):
    interface.implements(IGraph)
    
    def __init__(self):
        self.graph = Graph()
        
    @property
    def nodes(self):
        return self.graph.nodes
        
    @property
    def edges(self):
        return self.graph.edges

    def predecessors(self, node):
        return self.graph.predecessors(node)


class Sif2Graph(GraphAdapter):
    component.adapts(ISifReader)
    
    def __init__(self, sif):
        super(Sif2Graph, self).__init__()
                
        for source, sign, target in sif:
            sign = int(sign)
            
            self.graph.nodes.add(source)
            self.graph.nodes.add(target)
            self.graph.edges.add((source,target,sign))

class LogicalHeaderMapping2Graph(GraphAdapter):
    component.adapts(ILogicalHeaderMapping)
    
    def __init__(self, header):
        super(LogicalHeaderMapping2Graph, self).__init__()
        
        for m in header:
            clause, target = m.split('=')
            
            self.graph.nodes.add(target)
            for (source, signature) in Clause.from_str(clause):
                self.graph.nodes.add(source)
                self.graph.edges.add((source, target, signature))

class Graph2TermSet(asp.TermSetAdapter):
    component.adapts(IGraph)
    
    def __init__(self, graph):
        super(Graph2TermSet, self).__init__()
        
        for node in graph.nodes:
            self.termset.add(asp.Term('node', [node]))
            
        for source, target, sign in graph.edges:
            self.termset.add(asp.Term('edge', [source, target, sign]))

class Setup2TermSet(asp.TermSetAdapter):
    component.adapts(ISetup)
    
    def __init__(self, setup):
        super(Setup2TermSet, self).__init__()
        
        for s in setup.stimuli:
            self.termset.add(asp.Term('stimulus', [s]))
            
        for i in setup.inhibitors:
            self.termset.add(asp.Term('inhibitor', [i]))
            
        for r in setup.readouts:
            self.termset.add(asp.Term('readout', [r]))

class LogicalNames2TermSet(asp.TermSetAdapter):
    component.adapts(ILogicalNames)
    
    def __init__(self, names):
        super(LogicalNames2TermSet, self).__init__()
        
        for var_name, var in names.itervariables():
            self.termset.add(asp.Term('node', [var, var_name]))
            for clause_name, clause in names.iterclauses(var):
                self.termset.add(asp.Term('hyper', [var_name, clause_name, len(clause)]))
                for lit in clause:
                    self.termset.add(asp.Term('edge', [clause_name, lit.variable, lit.signature]))

class LogicalNetwork2TermSet(asp.TermSetAdapter):
    component.adapts(ILogicalNetwork)
    
    def __init__(self, network):
        super(LogicalNetwork2TermSet, self).__init__()
        
        names = component.getUtility(ILogicalNames)
        
        for var in network.variables:
            var_name = names.get_variable_name(var)
            self.termset.add(asp.Term('variable', [var, var_name]))
            for clause in network.mapping[var]:
                clause_name = names.get_clause_name(clause)
                self.termset.add(asp.Term('dnf', [var_name, clause_name]))
                for lit in clause:
                    self.termset.add(asp.Term('clause', [clause_name, lit.variable, lit.signature]))

class LogicalNetworkAdapter(object):
    interface.implements(ILogicalNetwork)

    def __init__(self):
        super(LogicalNetworkAdapter, self).__init__()
        
        self.names = component.getUtility(ILogicalNames)
        self.network = LogicalNetwork(self.names.variables)
                
    @property
    def variables(self):
        return self.network.variables
        
    @property
    def mapping(self):
        return self.network.mapping

class TermSet2LogicalNetwork(LogicalNetworkAdapter):
    component.adapts(asp.ITermSet)
    
    def __init__(self, termset):
        super(TermSet2LogicalNetwork, self).__init__()
        
        for term in termset:
            if term.pred == 'dnf':
                self.network.mapping[self.names.variables[term.arg(0)]].add(self.names.clauses[term.arg(1)])

class LogicalMapping2LogicalNetwork(LogicalNetworkAdapter):
    component.adapts(ILogicalMapping)
    
    def __init__(self, mapping):
        super(LogicalMapping2LogicalNetwork, self).__init__()
        
        for m,v in mapping.iteritems():
            if v == '1':
                clause, target = m.split('=')
                self.network.mapping[target].add(Clause.from_str(clause))
        
class LogicalNetworksReader2LogicalNetworkSet(set):
    component.adapts(ILogicalNetworksReader)
    interface.implements(ILogicalNetworkSet)
    
    def __init__(self, reader):
        super(LogicalNetworksReader2LogicalNetworkSet, self).__init__()
        names = component.getUtility(ILogicalNames)
        names.load(reader.graph)
        
        for mapping in reader:
            self.add(ILogicalNetwork(mapping))
