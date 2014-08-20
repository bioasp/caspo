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
        
        self._network = self._klass(names.variables, mapping)
        
    @property
    def variables(self):
        return self._network.variables
        
    @property
    def mapping(self):
        return self._network.mapping
        
    def __len__(self):
        return len(self._network)
        
class LogicalMapping2BooleLogicNetwork(LogicalMapping2LogicalNetwork):
    component.adapts(ILogicalMapping)
    interface.implements(IBooleLogicNetwork)

    _klass = BooleLogicNetwork
    
    def prediction(self, var, clamping):
        return self._network.prediction(var, clamping)
        
    def mse(self, dataset, time):
        return self._network.mse(dataset, time)
        
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
        self._networks = LogicalNetworkSet(map(lambda row: ILogicalNetwork(LogicalMapping(row)), reader))
        
    def __iter__(self):
        return iter(self._networks)
        
    def __len__(self):
        return len(self._networks)
        
class CsvReader2BooleLogicNetworkSet(CsvReader2LogicalNetworkSet):
    component.adapts(ICsvReader)
    interface.implements(IBooleLogicNetworkSet)

    def _read(self, reader):
        self._networks = BooleLogicNetworkSet(map(lambda row: IBooleLogicNetwork(LogicalMapping(row)), reader))
        
    def itermses(self, dataset, time):
        return self._networks.itermses(dataset, time)

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
            raise ValueError("The time-point %s does not exists in the dataset. Available time-points are: %s" % (time, list(self.times)))
                                  
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

class AnswerSet2Clamping(object):
    component.adapts(asp.IAnswerSet)
    interface.implements(IClamping)
    
    def __init__(self, answer):
        parser = asp.Grammar()
        literals = []
        parser.function.setParseAction(lambda t: Literal(t['args'][0],t['args'][1]))
        [literals.append(parser.parse(atom)) for atom in answer.atoms]
                
        self.clamping = Clamping(literals)
        
    def __iter__(self):
        return iter(self.clamping)
        
class AnswerSet2ClampingList(object):
    component.adapts(asp.IAnswerSet)
    interface.implements(IClampingList)
    
    def __init__(self, answer):
        clampings = defaultdict(list)
        parser = asp.Grammar()
        parser.function.setParseAction(lambda t: (t['args'][0], Literal(t['args'][1],t['args'][2])))
        for atom in answer.atoms:
            key, lit = parser.parse(atom)
            clampings[key].append(lit)

        self.clampings = map(lambda literals: Clamping(literals), clampings.values())

class TermSet2LogicalNetwork(object):
    component.adapts(asp.ITermSet)
    interface.implements(ILogicalNetwork)
    
    def __init__(self, termset):
        formula = filter(lambda t: t.pred == 'formula', termset)
        dnf = filter(lambda t: t.pred == 'dnf', termset)
        clause = filter(lambda t: t.pred == 'clause', termset)
        
        mapping = defaultdict(set)
        
        for f in formula:
            for d in filter(lambda t: t.arg(0) == f.arg(1), dnf):
                literals = [Literal(c.arg(1), c.arg(2)) for c in filter(lambda t: t.arg(0) == d.arg(1), clause)]
                mapping[f.arg(0)].add(Clause(literals))
                
        self._network = LogicalNetwork([t.arg(0) for t in formula], mapping)

    @property
    def variables(self):
        return self._network.variables

    @property
    def mapping(self):
        return self._network.mapping

    def __len__(self):
        return len(self._network)
