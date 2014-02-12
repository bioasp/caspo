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

import math

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
    component.adapts(IFileReader)
    
    def __init__(self, sif):
        super(Sif2Graph, self).__init__()
                
        for line in sif:
            line = line.strip()
            if line:
                try:
                    source, rel, target = line.split('\t')
                except Exception, e:
                    raise IOError("Cannot read line %s in SIF file: %s" % (line, str(e)))
                    
                sign = int(rel)
            
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
        self._mapping = defaultdict(set)
        for term in termset:
            if term.pred == 'dnf':
                self._mapping[names.variables[term.arg(0)]].add(names.clauses[term.arg(1)])
        
    @property
    def variables(self):
        return self._network.variables
        
    @property
    def mapping(self):
        return self._network.mapping

class TermSet2BooleLogicNetwork(TermSet2LogicalNetwork):
    component.adapts(asp.ITermSet)
    interface.implements(IBooleLogicNetwork)
    
    def __init__(self, termset):
        super(TermSet2BooleLogicNetwork, self).__init__(termset)
        names = component.getUtility(ILogicalNames)        
        self._network = BooleLogicNetwork(names.variables, self._mapping)
        
    def prediction(self, var, clamping):
        return self._network.prediction(var, clamping)

class LogicalMapping2LogicalNetwork(object):
    component.adapts(ILogicalMapping)
    interface.implements(ILogicalNetwork)

    _klass = LogicalNetwork
    
    def __init__(self, rawmap):
        mapping = defaultdict(set)
        names = component.getUtility(ILogicalNames)
        for m,v in rawmap.iteritems():
            if v == '1':
                clause, target = m.split('=')
                mapping[target].add(Clause.from_str(clause))
        
        names.add(map(frozenset, mapping.itervalues()))
        self._network = self._klass(names.variables, mapping)
        
    @property
    def variables(self):
        return self._network.variables
        
    @property
    def mapping(self):
        return self._network.mapping
        
class LogicalMapping2BooleLogicNetwork(LogicalMapping2LogicalNetwork):
    component.adapts(ILogicalMapping)
    interface.implements(IBooleLogicNetwork)

    _klass = BooleLogicNetwork
    
    def prediction(self, var, clamping):
        return self._network.prediction(var, clamping)
        
class LogicalNetwork2LogicalMapping(object):
    component.adapts(ILogicalNetwork, ILogicalHeaderMapping)
    interface.implements(ILogicalMapping)
    
    def __init__(self, network, header):
        mapping = dict.fromkeys(header, 0)
        for var, formula in network.mapping.iteritems():
            for clause in formula:
                mapping["%s=%s" % (str(clause),var)] = 1
                
        self.mapping = LogicalMapping(mapping)
        
class CsvReader2LogicalNetworkSet(object):
    component.adapts(ICsvReader)
    interface.implements(ILogicalNetworkSet)
    
    def __init__(self, reader):
        super(CsvReader2LogicalNetworkSet, self).__init__()
        names = component.getUtility(ILogicalNames)
        names.load(IGraph(LogicalHeaderMapping(reader.fieldnames)))
        
        self._read(reader)
        
    def _read(self, reader):
        self.networks = set(map(lambda row: ILogicalNetwork(LogicalMapping(row)), reader))
        
    def __iter__(self):
        return iter(self.networks)
        
    def __len__(self):
        return len(self.networks)
        
class CsvReader2BooleLogicNetworkSet(CsvReader2LogicalNetworkSet):
    component.adapts(ICsvReader)
    interface.implements(IBooleLogicNetworkSet)

    def _read(self, reader):
        self.networks = set(map(lambda row: IBooleLogicNetwork(LogicalMapping(row)), reader))

class LogicalNames2HeaderMapping(object):
    component.adapts(ILogicalNames)
    interface.implements(ILogicalHeaderMapping)
    
    def __init__(self, names):
        self.__header = LogicalHeaderMapping()
        for var in names.variables:
            for cname, clause in names.iterclauses(var):
                self.__header.append("%s=%s" % (str(clause),var))
                
    def __iter__(self):
        return iter(self.__header)
        
class LogicalNetworkSet2CsvWriter(object):
    component.adapts(ILogicalNetworkSet)
    interface.implements(ICsvWriter)
            
    def __init__(self, networks):
        self.header = ILogicalHeaderMapping(component.getUtility(ILogicalNames))
        self.networks = networks
        
    def __iter__(self):
        for network in self.networks:
            row = component.getMultiAdapter((network, self.header), ILogicalMapping)
            yield row.mapping
        
    def write(self, filename, path="./"):
        self.writer = component.getUtility(ICsvWriter)
        self.writer.load(self, self.header)
        self.writer.write(filename, path)
        
class LogicalNetworkSet2TermSet(asp.TermSetAdapter):
    component.adapts(ILogicalNetworkSet)
    
    def __init__(self, networks):
        super(LogicalNetworkSet2TermSet, self).__init__()
        
        names = component.getUtility(ILogicalNames)
        for var in names.variables:
            self._termset.add(asp.Term('variable', [var]))
        
        for i, network in enumerate(networks):
            for var,formula in network.mapping.iteritems():
                formula_name = names.get_formula_name(formula)
                self._termset.add(asp.Term('formula', [i, var, names.get_formula_name(formula)]))
                for clause in formula:
                    clause_name = names.get_clause_name(clause)
                    self._termset.add(asp.Term('dnf', [formula_name, clause_name]))
                    for lit in clause:
                        self._termset.add(asp.Term('clause', [clause_name, lit.variable, lit.signature]))


class CsvReader2Dataset(object):
    component.adapts(ICsvReader)
    interface.implements(IDataset, IClampingList)
    
    def __init__(self, reader):
        #Header without the CellLine column
        species = reader.fieldnames[1:]    
        stimuli = map(lambda name: name[3:], filter(lambda name: name.startswith('TR:') and not name.endswith('i'), species))
        inhibitors = map(lambda name: name[3:-1], filter(lambda name: name.startswith('TR:') and name.endswith('i'), species))
        readouts = map(lambda name: name[3:], filter(lambda name: name.startswith('DV:'), species))

        self.setup = Setup(stimuli, inhibitors, readouts)

        self.cues = []
        self.obs = []
        self.nobs = defaultdict(int)
                
        times = []
        for row in reader:
            literals = []
            for s in stimuli:
                if row['TR:' + s] == '1':
                    literals.append(Literal(s,1))
                else:
                    literals.append(Literal(s,-1))
                    
            for i in inhibitors:
                if row['TR:' + i + 'i'] == '1':
                    literals.append(Literal(i,-1))

            clamping = Clamping(literals)
            obs = defaultdict(dict)
            for r in readouts:
                if not math.isnan(float(row['DV:' + r])):
                    time = int(row['DA:' + r])
                    times.append(time)
                    obs[time][r] = float(row['DV:' + r])
                    self.nobs[time] += 1
                    
            if clamping in self.cues:
                index = self.cues.index(clamping)
                self.obs[index].update(obs)
            else:
                self.cues.append(clamping)
                self.obs.append(obs)
                
        self.times = frozenset(times)
        self.nexps = len(self.cues)
        
    @property
    def clampings(self):
        return self.cues
        
    def at(self, time):
        if time not in self.times:
            raise ValueError("The time-point %s does not exists in the dataset. \
                              Available time-points are: %s" % (time, list(self.times)))
                                  
        for i, (cues, obs) in enumerate(zip(self.cues, self.obs)):
            yield i, cues, obs[time]
            
                    
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

class TermSet2Clamping(object):
    component.adapts(asp.ITermSet)
    interface.implements(IClamping)
    
    def __init__(self, termset):
        literals = []
        for term in termset:
            if term.pred == 'clamped':
                literals.append(Literal(term.arg(0), term.arg(1)))
                
        self.clamping = Clamping(literals)
        
    def __iter__(self):
        return iter(self.clamping)
        