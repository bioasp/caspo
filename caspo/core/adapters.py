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

from pyzcasp import asp, potassco

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
            self._termset.add(asp.Term('stimulus', [s]))
            
        for i in setup.inhibitors:
            self._termset.add(asp.Term('inhibitor', [i]))
            
        for r in setup.readouts:
            self._termset.add(asp.Term('readout', [r]))


class CompressedGraph(GraphAdapter):
    component.adapts(IGraph, ISetup)
    
    def __init__(self, graph, setup):
        super(CompressedGraph, self).__init__()
        self._forward = defaultdict(set)
        self._backward = defaultdict(set)
        
        designated = setup.stimuli + setup.inhibitors + setup.readouts
        marked = graph.nodes.difference(designated)
    
        for source,target,sign in graph.edges:
            self._forward[source].add((target, sign))
            self._backward[target].add((source, sign))

        compressed = self.__compress(marked)

        for source, targets in self._forward.iteritems():
            for target, sign in targets:
                self.graph.edges.add((source, target, sign))
        
        self.graph.nodes = graph.nodes.difference(compressed)
        
    def __compress(self, marked, compressed=set()):
        icompressed = set()

        for node in sorted(marked):
            backward = list(self._backward[node])
            forward = list(self._forward[node])
            
            if not backward or (len(backward) == 1 and not filter(lambda e: e[0] == backward[0][0], forward)):
                self.__merge_source_targets(node)
                icompressed.add(node)
            
            elif not forward or (len(forward) == 1 and not filter(lambda e: e[0] == forward[0][0], backward)):
                self.__merge_target_sources(node)
                icompressed.add(node)
            
        if icompressed:
            return self.__compress(marked.difference(icompressed), compressed.union(icompressed))
        else:
            return compressed
            
    def __merge_source_targets(self, node):
        source = None
        if self._backward[node]:
            source, sign = self._backward[node].pop()
            self._forward[source].remove((node, sign))
                
        for target,s in self._forward[node]:
            if source:
                self._forward[source].add((target, sign*s))
                self._backward[target].add((source, sign*s))
            
            self._backward[target].remove((node, s))
                    
        del self._forward[node]

    def __merge_target_sources(self, node):
        target = None
        if self._forward[node]:
            target, sign = self._forward[node].pop()
            self._backward[target].remove((node, sign))

        for source, s in self._backward[node]:
            if target:
                self._forward[source].add((target, sign*s))
                self._backward[target].add((source, sign*s))
                
            self._forward[source].remove((node, s))

        del self._backward[node]

class LogicalNames2TermSet(asp.TermSetAdapter):
    component.adapts(ILogicalNames)
    
    def __init__(self, names):
        super(LogicalNames2TermSet, self).__init__()
        
        for var_name, var in enumerate(names.variables):
            self._termset.add(asp.Term('node', [var, var_name]))
            for clause_name, clause in names.iterclauses(var):
                self._termset.add(asp.Term('hyper', [var_name, clause_name, len(clause)]))
                for lit in clause:
                    self._termset.add(asp.Term('edge', [clause_name, lit.variable, lit.signature]))

class LogicalNetwork2TermSet(asp.TermSetAdapter):
    component.adapts(ILogicalNetwork)
    
    def __init__(self, network):
        super(LogicalNetwork2TermSet, self).__init__()
        
        names = component.getUtility(ILogicalNames)
        
        for var in network.variables:
            self._termset.add(asp.Term('variable', [var]))
        
        for var, formula in network.mapping.iteritems():
            var_name = names.get_variable_name(var)
            self._termset.add(asp.Term('formula', [var, var_name]))
            for clause in formula:
                clause_name = names.get_clause_name(clause)
                self._termset.add(asp.Term('dnf', [var_name, clause_name]))
                for lit in clause:
                    self._termset.add(asp.Term('clause', [clause_name, lit.variable, lit.signature]))
        
class TermSet2LogicalNetwork(object):
    component.adapts(asp.ITermSet)
    interface.implements(ILogicalNetwork)
    
    def __init__(self, termset):
        super(TermSet2LogicalNetwork, self).__init__()
        
        names = component.getUtility(ILogicalNames)
        mapping = defaultdict(set)
        for term in termset:
            if term.pred == 'dnf':
                mapping[names.variables[term.arg(0)]].add(names.clauses[term.arg(1)])
                
        self._network = LogicalNetwork(names.variables, mapping)
        
    @property
    def variables(self):
        return self._network.variables
        
    @property
    def mapping(self):
        return self._network.mapping
        
class LogicalNetworksReader2LogicalNetworkSet(object):
    component.adapts(ILogicalNetworksReader)
    interface.implements(ILogicalNetworkSet)
    
    def __init__(self, reader):
        super(LogicalNetworksReader2LogicalNetworkSet, self).__init__()
        names = component.getUtility(ILogicalSetNames)
        names.load(reader.graph)
        
        self.networks = set()
        for mapping in reader:
            self.networks.add(LogicalNetwork(list(names.variables), mapping))
            names.add(map(frozenset, mapping.itervalues()))
        
    def __iter__(self):
        return iter(self.networks)

class LogicalNetworkInSet2TermSet(asp.TermSetAdapter):
    component.adapts(ILogicalNetwork, ILogicalNetworkSet)
    
    def __init__(self, network, networkset):
        super(LogicalNetworkInSet2TermSet, self).__init__()
        
        names = component.getUtility(ILogicalSetNames)
        
        for var, formula in network.mapping.iteritems():
            formula_name = names.get_formula_name(formula)
            self._termset.add(asp.Term('formula', [var, formula_name]))
            for clause in formula:
                clause_name = names.get_clause_name(clause)
                self._termset.add(asp.Term('dnf', [formula_name, clause_name]))
                for lit in clause:
                    self._termset.add(asp.Term('clause', [clause_name, lit.variable, lit.signature]))
                                
class LogicalNetworkSet2TermSet(asp.TermSetAdapter):
    component.adapts(ILogicalNetworkSet)
    
    def __init__(self, networks):
        super(LogicalNetworkSet2TermSet, self).__init__()
        
        names = component.getUtility(ILogicalSetNames)
        for var in names.variables:
            self._termset.add(asp.Term('variable', [var]))
        
        for i, network in enumerate(networks):
            for formula in network.mapping.itervalues():
                self._termset.add(asp.Term('model', [i, names.get_formula_name(formula)]))
                
            self._termset = self._termset.union(component.getMultiAdapter((network, networks), asp.ITermSet))
            
class TermSet2FixPoint(object):
    interface.implements(IFixPoint)
    component.adapts(asp.ITermSet)
    
    def __init__(self, termset):
        self.__fixpoint = defaultdict(int)
        for term in termset:
            self.__fixpoint[term.arg(0)] = term.arg(1)
        
    def __getitem__(self, item):
        return self.__fixpoint[item]
                    
class ClampingTerm2TermSet(asp.TermSetAdapter):
    component.adapts(IClamping, asp.ITerm)
    
    def __init__(self, clamping, term):
        super(ClampingTerm2TermSet, self).__init__()
        
        for var, val in clamping:
            self._termset.add(asp.Term(term.pred, [var, val]))

class ClampingTermInClampingList2TermSet(asp.TermSetAdapter):
    component.adapts(IClamping, IClampingList, asp.ITerm)
    
    def __init__(self, clamping, clist, term):
        super(ClampingTermInClampingList2TermSet, self).__init__()
        
        name = clist.clampings.index(clamping)
        for var, val in clamping:
            self._termset.add(asp.Term(term.pred, [name, var, val]))
            
class Clamping2TermSet(ClampingTerm2TermSet):
    component.adapts(IClamping)
    
    def __init__(self, clamping):
        super(Clamping2TermSet, self).__init__(clamping, asp.Term('clamped'))

class ClampingInClampingList2TermSet(ClampingTermInClampingList2TermSet):
    component.adapts(IClamping, IClampingList)
    
    def __init__(self, clamping, clist):
        super(ClampingInClampingList2TermSet, self).__init__(clamping, clist, asp.Term('clamped'))

class BooleLogicNetwork2FixPointer(object):
    interface.implements(IBooleFixPointer)
    component.adapts(IBooleLogicNetwork, potassco.IGringoGrounder, potassco.IClaspSolver)
    
    def __init__(self, network, gringo, clasp):
        self.termset = asp.ITermSet(network)
        self.grover = component.getMultiAdapter((gringo, clasp), asp.IGrounderSolver)
        
    @asp.cleanrun
    def fixpoint(self, clamping):
        reg = component.getUtility(asp.IEncodingRegistry, 'caspo')
        termset = asp.ITermSet(clamping).union(self.termset)
        programs = [termset.to_file(), reg.get_encoding('core.boole')]
        
        self.grover.run("#hide. #show eval(V,1).", grounder_args=programs)
        
        return IFixPoint(iter(self.grover).next())
